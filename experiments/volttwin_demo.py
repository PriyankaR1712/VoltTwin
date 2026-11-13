"""Small end-to-end demonstration of the existing VoltTwin workflow.

This script injects only the external checkpoint path into TwinRegistry's
existing TwinManager constructor. The operational, decision, and persistence
logic remains in the project modules.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_CHECKPOINT = ROOT / "models" / "soh_cnn_xjtu_batch1_clean.pt"
DEFAULT_WORKBOOK = (
    ROOT
    / "reference"
    / "SOHbenchmark"
    / "data"
    / "XJTU"
    / "handcraft_features"
    / "batch-1_features.xlsx"
)
DEMO_MINIMUM_GAP = 3
DEMO_EPSILON_SOH = 0.01
DEMO_POLICY_VERSION = "volttwin-demo-v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
    parser.add_argument("--sheet", default="Sheet1")
    parser.add_argument("--observations", type=int, default=5)
    parser.add_argument(
        "--minimum-gap", type=int, default=DEMO_MINIMUM_GAP,
        help="demonstration setting only; not a calibrated policy threshold",
    )
    parser.add_argument(
        "--epsilon-soh", type=float, default=DEMO_EPSILON_SOH,
        help="demonstration setting only; not a calibrated policy threshold",
    )
    return parser


def run(args: argparse.Namespace) -> None:
    if not args.checkpoint.is_file():
        raise FileNotFoundError(f"CNN checkpoint is unavailable: {args.checkpoint}")
    if not args.workbook.is_file():
        raise FileNotFoundError(f"XJTU workbook is unavailable: {args.workbook}")
    if args.observations < 3:
        raise ValueError("Use at least three observations for the demonstration.")
    if args.minimum_gap < 1 or not 0 <= args.epsilon_soh < 1:
        raise ValueError("Adaptive policy demonstration settings are invalid.")

    from backend import agent_api
    import backend.twin_registry as registry_module
    from backend.adaptive_decision_service import AdaptiveDecisionService
    from backend.adaptive_evaluation_store import AdaptiveEvaluationStore
    from backend.decision_history_store import DecisionHistoryStore
    from backend.streaming.stream_processor import StreamProcessor
    from backend.streaming.stream_reader import XJTUBatchReader
    from digital_twin.goal_spec import GoalSpec
    from digital_twin.twin_manager import TwinManager
    from backend.twin_registry import TwinRegistry

    reader = XJTUBatchReader(
        batch_number=1,
        sheet_name=args.sheet,
        workbook_path=args.workbook,
    )
    if args.observations > reader.total_observations:
        raise ValueError(
            f"Requested {args.observations} observations, but {args.sheet} has "
            f"{reader.total_observations}."
        )

    battery_id = f"DEMO-XJTU-B1-{args.sheet}"
    registry = TwinRegistry()

    # TwinRegistry.initialize remains the registration path. Its public
    # signature does not expose checkpoint_path, so inject that one constructor
    # argument for this demonstration process only.
    def manager_factory(*, battery_id: str, initial_soh: float = 1.0):
        return TwinManager(
            battery_id=battery_id,
            initial_soh=initial_soh,
            checkpoint_path=args.checkpoint,
        )

    with patch.object(registry_module, "TwinManager", new=manager_factory):
        manager = registry.initialize(battery_id)

    processor = StreamProcessor(
        batch_number=1,
        sheet_name=args.sheet,
        battery_id=battery_id,
        registry=registry,
        reader=reader,
    )
    processor.start()

    old_registry = agent_api.twin_registry
    old_history_store = agent_api._history_store
    old_adaptive_service = agent_api._adaptive_service
    env_keys = (
        "VOLTTWIN_ADAPTIVE_DB_PATH",
        "VOLTTWIN_ADAPTIVE_MINIMUM_GAP",
        "VOLTTWIN_ADAPTIVE_EPSILON_SOH",
        "VOLTTWIN_ADAPTIVE_POLICY_VERSION",
    )
    old_env = {key: os.environ.get(key) for key in env_keys}
    adaptive_service = None

    temp_directory = tempfile.TemporaryDirectory(prefix="volttwin-demo-")
    temp = Path(temp_directory.name)
    try:
        agent_api.twin_registry = registry
        agent_api._history_store = DecisionHistoryStore(
            temp / "stage4-decisions.sqlite"
        )
        agent_api._adaptive_service = None

        # These are explicit demo settings, matching the existing Stage 5
        # service-test fixture. They are not threshold-selection results.
        os.environ["VOLTTWIN_ADAPTIVE_DB_PATH"] = str(
            temp / "stage5-adaptive-events.sqlite"
        )
        os.environ["VOLTTWIN_ADAPTIVE_MINIMUM_GAP"] = str(args.minimum_gap)
        os.environ["VOLTTWIN_ADAPTIVE_EPSILON_SOH"] = str(args.epsilon_soh)
        os.environ["VOLTTWIN_ADAPTIVE_POLICY_VERSION"] = DEMO_POLICY_VERSION
        adaptive_service = agent_api._get_adaptive_service()

        goal = GoalSpec(
            goal_id="volttwin-final-demo",
            horizon_cycles=100,
            assessment_scope="counterfactual_comparison",
        )

        evaluation_rows = []
        decision_results = []
        pre_decision_snapshot = None

        for processed in range(1, args.observations + 1):
            observation = processor.process_next()
            if observation is None:
                raise RuntimeError("The stream ended before the requested count.")

            snapshot = manager.get_snapshot()
            if snapshot["state"]["prediction_count"] != processed:
                raise RuntimeError("Prediction count did not advance sequentially.")
            if snapshot["state"]["last_observation_index"] != processed - 1:
                raise RuntimeError("Observation index did not advance sequentially.")

            # The first assessment is made after three observations so its
            # Stage 3 snapshot includes the existing trend estimates.
            if processed < 3:
                continue
            if processed == 3:
                pre_decision_snapshot = snapshot

            watermark = {
                "prediction_count": snapshot["state"]["prediction_count"],
                "version": snapshot["version"],
                "observation_index": snapshot["state"]["last_observation_index"],
            }
            before = manager.get_snapshot()
            outcome = adaptive_service.evaluate(
                battery_id=battery_id,
                goal=goal,
                event_watermark=watermark,
                twin_registry=registry,
                run_decision=lambda: agent_api._run_and_persist_decision(
                    battery_id, goal
                ),
            )
            after = manager.get_snapshot()
            if before != after:
                raise RuntimeError(
                    "Agent/counterfactual evaluation mutated operational Twin state."
                )

            evaluation_rows.append(outcome)
            decision = outcome.get("decision_result")
            if decision is not None:
                decision_results.append(decision)
                decision_snapshot = decision.snapshot_metadata
                actual_version = decision_snapshot.get(
                    "snapshot_version", decision_snapshot.get("version")
                )
                if actual_version != snapshot["version"]:
                    raise RuntimeError(
                        "Stage 3 decision snapshot does not match the captured Twin snapshot."
                    )
                if decision_snapshot.get("prediction_count") != watermark["prediction_count"]:
                    raise RuntimeError(
                        "Stage 3 decision prediction count does not match the event."
                    )

        if pre_decision_snapshot is None or not decision_results:
            raise RuntimeError("The initial adaptive decision did not execute.")

        decision = decision_results[0]
        history_store = agent_api._history_store
        stored = history_store.get_decision(decision.decision_id)
        if stored is None:
            raise RuntimeError("Stage 4 did not persist the decision record.")
        if not stored.get("explanation"):
            raise RuntimeError("Stage 4 decision record has no explanation.")

        final_snapshot = manager.get_snapshot()
        latest_state = final_snapshot["state"]
        print("VoltTwin final demonstration")
        print(f"sheet={args.sheet} observations_processed={args.observations}")
        print(f"workbook={args.workbook}")
        print(f"checkpoint={args.checkpoint}")
        print(f"checkpoint_sha256={sha256_file(args.checkpoint)}")
        print(f"predicted_soh={latest_state['twin_state']['soh']:.6f}")
        print(
            "twin_observation_index="
            f"{latest_state['last_observation_index']} "
            f"version={final_snapshot['version']} "
            f"prediction_count={latest_state['prediction_count']}"
        )
        print(
            f"decision_id={decision.decision_id} "
            f"path={decision.assessment_path} "
            f"status={decision.termination_status} "
            f"goal_status={decision.goal_status} "
            f"selected_action={decision.selected_action}"
        )
        print(f"decision_explanation={stored['explanation']}")
        print(f"stage4_persistence=verified record_id={stored['decision_id']}")
        print(f"snapshot_metadata={decision.snapshot_metadata}")
        print(f"candidate_evaluations={decision.candidate_evaluations}")
        print(f"utility_ranking={decision.utility_ranking}")
        print("stage5_evaluations=")
        for row in evaluation_rows:
            print(
                f"  status={row['evaluation_status']} "
                f"reasons={row.get('trigger_reasons', [])} "
                f"event={row.get('event_watermark')} "
                f"decision_snapshot={row.get('decision_snapshot_watermark')}"
            )
        print(f"stage3_invocations={len(decision_results)}")
        print("counterfactual_mutation_check=passed")
        print("physical_maintenance_effectiveness=not_established")
    finally:
        if adaptive_service is not None:
            adaptive_service.store.close()
        agent_api.twin_registry = old_registry
        agent_api._history_store = old_history_store
        agent_api._adaptive_service = old_adaptive_service
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        temp_directory.cleanup()


if __name__ == "__main__":
    run(make_parser().parse_args())
