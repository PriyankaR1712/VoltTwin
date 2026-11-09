from backend.adaptive_evaluation_store import AdaptiveEvaluationStore
import subprocess
import sys
from pathlib import Path


def test_event_reservation_and_recovery_are_idempotent(tmp_path):
    path = tmp_path / "adaptive.db"
    store = AdaptiveEvaluationStore(path)
    fields = dict(
        event_key="event-1", battery_id="b1", generation_id="gen-1",
        goal_fingerprint="goal-hash", goal_spec={"goal_id": "g"},
        event_watermark={"version": 1, "prediction_count": 1, "observation_index": 2},
        predicted_soh=0.9, minimum_gap=3, epsilon_soh=0.01,
        policy_version="adaptive-v1", prior_decision_id=None,
    )
    evaluation_id, existing = store.reserve(**fields)
    assert existing is None
    repeated_id, existing = store.reserve(**fields)
    assert repeated_id == "existing"
    assert existing["status"] == "in_progress"
    store.finish(evaluation_id, status="held", reasons=["minimum_gap_not_met"],
                 decision_snapshot_watermark={"prediction_count": 1, "version": 1, "observation_index": 2})
    latest = store.get_latest("b1", "gen-1")
    assert latest["status"] == "held"
    assert latest["decision_snapshot_watermark"]["prediction_count"] == 1

    restarted = AdaptiveEvaluationStore(path)
    assert restarted.get_event("event-1")["status"] == "held"


def test_in_progress_events_become_indeterminate_after_restart(tmp_path):
    path = tmp_path / "adaptive.db"
    store = AdaptiveEvaluationStore(path)
    store.reserve(
        event_key="event-2", battery_id="b1", generation_id="gen-1",
        goal_fingerprint="goal-hash", goal_spec={"goal_id": "g"},
        event_watermark={"version": 2, "prediction_count": 2, "observation_index": 3},
        predicted_soh=0.8, minimum_gap=3, epsilon_soh=0.01,
        policy_version="adaptive-v1", prior_decision_id=None,
    )
    # Closing the last store releases the process lease, as a genuine process
    # exit would. The next owner recovers the uncertain reservation.
    store.close()
    restarted = AdaptiveEvaluationStore(path)
    assert restarted.get_event("event-2")["status"] == "indeterminate"


def test_opening_another_store_instance_does_not_recover_live_reservation(tmp_path):
    path = tmp_path / "active.db"
    first = AdaptiveEvaluationStore(path)
    first.reserve(
        event_key="live", battery_id="b", generation_id="g",
        goal_fingerprint="goal", goal_spec={"goal_id": "g"},
        event_watermark={"version": 1, "prediction_count": 1, "observation_index": 1},
        predicted_soh=.9, minimum_gap=3, epsilon_soh=.01,
        policy_version="v1", prior_decision_id=None,
    )
    second = AdaptiveEvaluationStore(path)
    assert first.get_event("live")["status"] == "in_progress"
    assert second.get_event("live")["status"] == "in_progress"


def test_second_process_cannot_own_the_same_adaptive_store(tmp_path):
    path = tmp_path / "single-worker.db"
    store = AdaptiveEvaluationStore(path)
    root = Path(__file__).resolve().parents[1]
    code = (
        "from backend.adaptive_evaluation_store import AdaptiveEvaluationStore; "
        "AdaptiveEvaluationStore(r'" + str(path) + "')"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code], cwd=root, capture_output=True, text=True
    )
    assert completed.returncode != 0
    assert "already owned by another worker" in completed.stderr
