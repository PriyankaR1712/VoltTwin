from copy import deepcopy

import pytest
import torch

from backend.twin_registry import TwinRegistry
from digital_twin import goal_directed_orchestrator as planner
from digital_twin import twin_manager as twin_manager_module
from digital_twin.baseline_relative_utility import UtilityRanking
from digital_twin.counterfactual_service import simulate_registered_twin
from digital_twin.goal_spec import GoalSpec
from digital_twin.scenario_validation import EXPECTED_SCENARIOS


def make_snapshot(soh=0.9, prediction_count=4, trend=0.0):
    predictions = [
        {"observation_index": index, "predicted_soh": soh}
        for index in range(prediction_count)
    ]
    degradation = (
        {
            "observation_count": prediction_count,
            "window_size_used": min(25, prediction_count),
            "latest_observed_soh": round(soh, 6),
            "trend_per_sample": trend,
            "is_historical_estimate": True,
            "is_future_forecast": False,
        }
        if prediction_count >= 3 and trend is not None
        else None
    )
    return {
        "battery_id": "battery-1",
        "version": 12,
        "_manager_identity": 99,
        "state": {
            "battery_id": "battery-1",
            "twin_state": {
                "battery_id": "battery-1",
                "soh": soh,
                "soh_percent": soh * 100,
                "cycle_count": 0,
            },
            "last_observation_index": prediction_count + 5,
            "prediction_count": prediction_count,
            "degradation": degradation,
            "rul": None,
            "state_source": "cnn_prediction",
        },
        "history": {
            "battery_id": "battery-1",
            "prediction_history": predictions,
            "observation_history": [],
            "observation_count": prediction_count,
            "state_source": "cnn_prediction",
        },
        "simulation_assumptions": {
            "degradation_per_cycle": 0.0001,
            "maintenance_recovery": 0.0,
        },
    }


def make_counterfactual_response(snapshot, horizon):
    initial = snapshot["state"]["twin_state"]["soh"]
    baseline = max(0.0, initial - 0.01)
    rows = [
        ("No maintenance", 0.0, baseline),
        ("Maintenance A", 0.005, min(1.0, baseline + 0.005)),
        ("Maintenance B", 0.01, min(1.0, baseline + 0.01)),
    ]
    return {
        "battery_id": snapshot["battery_id"],
        "snapshot_version": snapshot["version"],
        "snapshot_soh": initial,
        "state_source": "cnn_prediction",
        "latest_observation_index": snapshot["state"]["last_observation_index"],
        "prediction_count": snapshot["state"]["prediction_count"],
        "is_simulation": True,
        "is_physically_validated": False,
        "scenarios": [
            {
                "scenario": name,
                "initial_soh": initial,
                "projected_soh": projected,
                "additional_cycles": horizon,
                "recovery_assumption": recovery,
                "difference_vs_baseline": projected - baseline,
                "is_simulation": True,
            }
            for name, recovery, projected in rows
        ],
    }


def make_baseline_response(snapshot, horizon):
    initial = snapshot["state"]["twin_state"]["soh"]
    projected = max(0.0, initial - 0.01)
    return {
        "scenario": "No maintenance",
        "initial_soh": initial,
        "projected_soh": projected,
        "projected_soh_percent": projected * 100,
        "additional_cycles": horizon,
        "recovery_assumption": 0.0,
        "difference_vs_baseline": 0.0,
        "is_simulation": True,
        "snapshot_version": snapshot["version"],
    }


class FakeManager:
    def __init__(self, snapshot=None):
        self.snapshot = snapshot or make_snapshot()
        self.snapshot_calls = 0
        self.last_returned_snapshot = None

    def get_snapshot(self):
        self.snapshot_calls += 1
        self.last_returned_snapshot = deepcopy(self.snapshot)
        return self.last_returned_snapshot


class FakeRegistry:
    def __init__(self, manager):
        self.manager = manager
        self.get_calls = []

    def get(self, battery_id):
        self.get_calls.append(battery_id)
        if battery_id != self.manager.snapshot["battery_id"]:
            raise KeyError(battery_id)
        return self.manager


@pytest.fixture
def harness(monkeypatch):
    manager = FakeManager()
    registry = FakeRegistry(manager)
    calls = {"baseline": [], "counterfactual": [], "policy": []}
    calls["policy_result"] = {
        "recommended_scenario": "Maintenance B",
        "recommended_action": "Battery Health Diagnostics",
        "status": "acceptable_under_assumptions",
        "reason": "fixture policy result",
    }

    def baseline_service(**kwargs):
        calls["baseline"].append(kwargs)
        return make_baseline_response(
            kwargs["state_snapshot"], kwargs["additional_cycles"]
        )

    def counterfactual_service(**kwargs):
        calls["counterfactual"].append(kwargs)
        return make_counterfactual_response(
            kwargs["state_snapshot"], kwargs["additional_cycles"]
        )

    def policy_service(**kwargs):
        calls["policy"].append(kwargs)
        return calls["policy_result"]

    monkeypatch.setattr(planner, "assess_registered_baseline", baseline_service)
    monkeypatch.setattr(planner, "simulate_registered_twin", counterfactual_service)
    monkeypatch.setattr(planner, "recommend_maintenance", policy_service)
    return manager, registry, calls


def run(goal, harness, **kwargs):
    _, registry, _ = harness
    return planner.run_goal_directed_orchestrator(
        "battery-1", goal, twin_registry=registry, **kwargs
    )


def test_explicit_baseline_only_calls_baseline_once_with_captured_snapshot(harness):
    manager, _, calls = harness
    result = run(GoalSpec("baseline", 100, assessment_scope="baseline_only"), harness)

    assert manager.snapshot_calls == 1
    assert len(calls["baseline"]) == 1
    assert calls["baseline"][0]["state_snapshot"] is manager.last_returned_snapshot
    assert result.assessment_path == "baseline_only"
    assert result.candidate_evaluations[0]["scenario"] == "No maintenance"


def test_baseline_only_never_calls_counterfactual_or_policy(harness):
    _, _, calls = harness
    run(GoalSpec("baseline", 100, assessment_scope="baseline_only"), harness)
    assert len(calls["baseline"]) == 1
    assert calls["counterfactual"] == []
    assert calls["policy"] == []


def test_explicit_counterfactual_calls_service_once_and_policy_once(harness):
    manager, _, calls = harness
    result = run(
        GoalSpec("compare", 100, assessment_scope="counterfactual_comparison"),
        harness,
    )

    assert manager.snapshot_calls == 1
    assert calls["baseline"] == []
    assert len(calls["counterfactual"]) == 1
    assert calls["counterfactual"][0]["state_snapshot"] is manager.last_returned_snapshot
    assert len(calls["policy"]) == 1
    assert result.assessment_path == "counterfactual_comparison"
    assert [row["scenario"] for row in result.candidate_evaluations] == list(
        EXPECTED_SCENARIOS
    )


def test_counterfactual_requires_complete_valid_scenario_set(harness, monkeypatch):
    _, _, calls = harness
    original = planner.simulate_registered_twin

    def partial_service(**kwargs):
        response = original(**kwargs)
        response["scenarios"].pop()
        return response

    monkeypatch.setattr(planner, "simulate_registered_twin", partial_service)
    result = run(GoalSpec("compare", 100, assessment_scope="counterfactual_comparison"), harness)

    assert result.termination_status == "invalid_scenario_evidence"
    assert result.utility_ranking is None
    assert calls["policy"] == []


def test_counterfactual_rejects_pairwise_inconsistent_initial_soh(harness, monkeypatch):
    original = planner.simulate_registered_twin

    def inconsistent_service(**kwargs):
        response = original(**kwargs)
        response["scenarios"][0]["initial_soh"] += 0.00009
        response["scenarios"][1]["initial_soh"] -= 0.00009
        return response

    monkeypatch.setattr(planner, "simulate_registered_twin", inconsistent_service)
    result = run(
        GoalSpec("compare", 100, assessment_scope="counterfactual_comparison"),
        harness,
    )

    assert result.termination_status == "invalid_scenario_evidence"
    assert result.errors[0]["code"] == "inconsistent_scenario_initial_soh"
    assert result.utility_ranking is None


def test_auto_selects_counterfactual_when_current_soh_is_below_target(harness):
    manager, _, calls = harness
    manager.snapshot = make_snapshot(soh=0.7)
    result = run(GoalSpec("target", 100, target_soh=0.8), harness)
    assert result.assessment_path == "counterfactual_comparison"
    assert len(calls["counterfactual"]) == 1


def test_missing_target_does_not_trigger_counterfactual(harness):
    _, _, calls = harness
    result = run(GoalSpec("no-target", 100), harness)
    assert result.assessment_path == "baseline_only"
    assert result.candidate_evaluations[0]["target_attainment"] is None
    assert calls["counterfactual"] == []


def test_valid_declining_trend_with_consistent_metadata_triggers_counterfactual(harness):
    manager, _, calls = harness
    manager.snapshot = make_snapshot(prediction_count=3, trend=-0.00000001)
    result = run(GoalSpec("trend", 100), harness)
    assert result.assessment_path == "counterfactual_comparison"
    assert result.snapshot_metadata["trend_status"] == "declining"
    assert result.snapshot_metadata["trend_per_sample"] == -0.00000001
    assert len(calls["counterfactual"]) == 1


def test_insufficient_trend_history_is_unknown_not_declining(harness):
    manager, _, calls = harness
    manager.snapshot = make_snapshot(prediction_count=2, trend=-0.1)
    result = run(GoalSpec("short-history", 100), harness)
    assert result.assessment_path == "baseline_only"
    assert result.snapshot_metadata["trend_status"] == "unknown"
    assert result.snapshot_metadata["trend_per_sample"] is None
    assert calls["counterfactual"] == []


@pytest.mark.parametrize(
    "mutation",
    [
        lambda degradation: degradation.pop("trend_per_sample"),
        lambda degradation: degradation.update(trend_per_sample=float("nan")),
        lambda degradation: degradation.update(trend_per_sample=float("inf")),
        lambda degradation: degradation.update(trend_per_sample=float("-inf")),
        lambda degradation: degradation.update(trend_per_sample=True),
        lambda degradation: degradation.update(observation_count=3),
    ],
    ids=["missing", "nan", "positive-infinity", "negative-infinity", "boolean", "stale-count"],
)
def test_invalid_or_inconsistent_trend_is_unknown_and_does_not_trigger(
    harness, mutation
):
    manager, _, calls = harness
    manager.snapshot["state"]["degradation"] = {
        **manager.snapshot["state"]["degradation"]
    }
    mutation(manager.snapshot["state"]["degradation"])

    result = run(GoalSpec("invalid-trend", 100), harness)

    assert result.snapshot_metadata["trend_status"] == "unknown"
    assert result.snapshot_metadata["trend_per_sample"] is None
    assert result.assessment_path == "baseline_only"
    assert calls["counterfactual"] == []


@pytest.mark.parametrize("invalid_soh", [True, float("nan"), 1.1])
def test_invalid_prediction_history_makes_trend_unknown(harness, invalid_soh):
    manager, _, calls = harness
    manager.snapshot["history"]["prediction_history"][-1]["predicted_soh"] = invalid_soh
    manager.snapshot["state"]["degradation"]["trend_per_sample"] = -0.001

    result = run(GoalSpec("invalid-prediction-history", 100), harness)

    assert result.snapshot_metadata["trend_status"] == "unknown"
    assert result.snapshot_metadata["trend_per_sample"] is None
    assert result.assessment_path == "baseline_only"
    assert calls["counterfactual"] == []


@pytest.mark.parametrize("trend", [0.0, 0.0001])
def test_stable_or_increasing_trend_does_not_trigger_comparison(harness, trend):
    manager, _, calls = harness
    manager.snapshot = make_snapshot(trend=trend)
    result = run(GoalSpec("stable", 100), harness)
    assert result.assessment_path == "baseline_only"
    assert result.snapshot_metadata["trend_status"] == "not_declining"
    assert calls["counterfactual"] == []


def test_supported_diagnostic_evidence_triggers_counterfactual(harness):
    _, _, calls = harness
    result = run(
        GoalSpec("diagnostics", 100, diagnostic_evidence={"thermal_alert": True}),
        harness,
    )
    assert result.assessment_path == "counterfactual_comparison"
    assert len(calls["counterfactual"]) == 1


def test_explicit_comparison_scope_triggers_counterfactual(harness):
    result = run(
        GoalSpec("explicit", 100, assessment_scope="counterfactual_comparison"),
        harness,
    )
    assert result.assessment_path == "counterfactual_comparison"


def test_auto_uses_baseline_when_no_trigger_exists(harness):
    result = run(GoalSpec("quiet", 100), harness)
    assert result.assessment_path == "baseline_only"


def test_baseline_target_miss_returns_goal_unmet_without_second_call(harness):
    manager, _, calls = harness
    manager.snapshot = make_snapshot(soh=0.82, trend=0.0)
    result = run(
        GoalSpec(
            "high-target",
            100,
            target_soh=0.9,
            assessment_scope="baseline_only",
        ),
        harness,
    )
    assert result.termination_status == "goal_unmet"
    assert result.goal_status == "goal_unmet"
    assert len(calls["baseline"]) == 1
    assert calls["counterfactual"] == []


def test_baseline_missing_target_is_unavailable(harness):
    result = run(GoalSpec("no-target", 100, assessment_scope="baseline_only"), harness)
    assert result.goal_status == "target_unavailable"
    assert result.candidate_evaluations[0]["target_attainment"] is None


def test_equal_utility_preserves_tie_and_selects_no_unique_candidate(harness):
    _, _, _ = harness
    original_response = planner.simulate_registered_twin

    def tied_service(**kwargs):
        response = original_response(**kwargs)
        response["scenarios"][2]["projected_soh"] = response["scenarios"][1][
            "projected_soh"
        ]
        response["scenarios"][2]["difference_vs_baseline"] = response[
            "scenarios"
        ][1]["difference_vs_baseline"]
        return response

    # The harness service is already a fake; the service contract/utility remain real.
    planner.simulate_registered_twin = tied_service
    try:
        result = run(
            GoalSpec("compare", 100, assessment_scope="counterfactual_comparison"),
            harness,
        )
    finally:
        planner.simulate_registered_twin = original_response

    assert result.utility_ranking["ranked_groups"][0] == [
        "Maintenance A",
        "Maintenance B",
    ]
    assert result.utility_ranking["selection_status"] == "tie"
    assert result.selected_action is None
    assert result.termination_status == "tie"
    assert result.policy_comparison["status"] == "tie"


def test_policy_agreement_is_reported_without_replacing_utility_selection(harness):
    _, _, calls = harness
    result = run(
        GoalSpec("compare", 100, assessment_scope="counterfactual_comparison"),
        harness,
    )
    assert result.selected_action == "Maintenance B"
    assert result.policy_comparison["status"] == "agreement"
    assert result.policy_comparison["policy_recommended_scenario"] == "Maintenance B"
    assert len(calls["policy"]) == 1


def test_policy_disagreement_preserves_both_recommendations(harness):
    _, _, calls = harness
    calls["policy_result"] = {
        **calls["policy_result"],
        "recommended_scenario": "Maintenance A",
    }
    result = run(
        GoalSpec("compare", 100, assessment_scope="counterfactual_comparison"),
        harness,
    )
    assert result.selected_action == "Maintenance B"
    assert result.policy_comparison["status"] == "disagreement"
    assert result.policy_comparison["policy_recommended_scenario"] == "Maintenance A"


def test_baseline_policy_status_is_not_applicable(harness):
    result = run(GoalSpec("baseline", 100, assessment_scope="baseline_only"), harness)
    assert result.policy_comparison["status"] == "not_applicable_baseline_only"


def test_both_paths_return_the_shared_result_model(harness):
    baseline = run(GoalSpec("base", 100, assessment_scope="baseline_only"), harness)
    comparison = run(
        GoalSpec("cf", 100, assessment_scope="counterfactual_comparison"), harness
    )
    assert type(baseline) is type(comparison)
    assert baseline.assessment_path == "baseline_only"
    assert comparison.assessment_path == "counterfactual_comparison"


def test_snapshot_metadata_and_provenance_are_preserved(harness):
    result = run(
        GoalSpec("compare", 100, assessment_scope="counterfactual_comparison"),
        harness,
    )
    assert result.snapshot_metadata["snapshot_version"] == 12
    assert result.snapshot_metadata["state_source"] == "cnn_prediction"
    assert result.snapshot_metadata["history_state_source"] == "cnn_prediction"
    assert result.snapshot_metadata["observation_index"] == 9
    assert result.snapshot_metadata["prediction_count"] == 4
    assert result.snapshot_metadata["is_physically_validated"] is False


@pytest.mark.parametrize(
    "bad_response",
    [
        "duplicate-name",
        "unexpected-name",
        "missing-row",
        "non-finite-soh",
        "wrong-version",
        "malformed-row",
    ],
)
def test_invalid_counterfactual_result_abstains_without_policy(
    harness, monkeypatch, bad_response
):
    _, _, calls = harness
    original = planner.simulate_registered_twin

    def malformed_service(**kwargs):
        response = original(**kwargs)
        if bad_response == "duplicate-name":
            response["scenarios"][2]["scenario"] = response["scenarios"][1]["scenario"]
        elif bad_response == "unexpected-name":
            response["scenarios"][2]["scenario"] = "Maintenance C"
        elif bad_response == "missing-row":
            response["scenarios"].pop()
        elif bad_response == "non-finite-soh":
            response["scenarios"][1]["projected_soh"] = float("nan")
        elif bad_response == "wrong-version":
            response["snapshot_version"] += 1
        else:
            response["scenarios"][1] = {"scenario": "Maintenance A"}
        return response

    monkeypatch.setattr(planner, "simulate_registered_twin", malformed_service)
    result = run(
        GoalSpec("compare", 100, assessment_scope="counterfactual_comparison"),
        harness,
    )
    assert result.termination_status == "invalid_scenario_evidence"
    assert result.selected_action is None
    assert result.utility_ranking is None
    assert result.policy_comparison["status"] == "unavailable"
    assert result.candidate_evaluations == []
    assert len(calls["counterfactual"]) == 1
    assert calls["baseline"] == []
    assert calls["policy"] == []


def test_no_eligible_candidate_does_not_select_intervention(harness, monkeypatch):
    def no_utility_candidates(scenarios, goal, config):
        return UtilityRanking(
            formula_version=config.utility_formula_version,
            utilities={},
            ranked_groups=(),
            target_attainment={name: None for name in EXPECTED_SCENARIOS},
        )

    monkeypatch.setattr(planner, "calculate_baseline_relative_utility", no_utility_candidates)
    result = run(
        GoalSpec("compare", 100, assessment_scope="counterfactual_comparison"),
        harness,
    )
    assert result.selected_action is None
    assert result.utility_ranking["selection_status"] == "no_eligible_candidates"
    assert result.policy_comparison["status"] == "unavailable"


def test_counterfactual_service_failure_is_reported_without_retry(harness, monkeypatch):
    manager, _, calls = harness

    def failing_service(**kwargs):
        calls["counterfactual"].append(kwargs)
        raise RuntimeError("simulator unavailable")

    monkeypatch.setattr(planner, "simulate_registered_twin", failing_service)
    result = run(
        GoalSpec("compare", 100, assessment_scope="counterfactual_comparison"),
        harness,
    )
    assert result.termination_status == "service_failure"
    assert result.errors[0]["code"] == "counterfactual_simulation_failed"
    assert len(calls["counterfactual"]) == 1
    assert calls["baseline"] == []
    assert calls["policy"] == []
    assert manager.snapshot_calls == 1


class ConstantPredictor:
    def predict(self, features):
        return torch.tensor([0.92], dtype=torch.float32)


def test_real_registered_counterfactual_is_non_mutating_and_validated(monkeypatch):
    monkeypatch.setattr(
        twin_manager_module,
        "SOHPredictor",
        lambda checkpoint_path=None: ConstantPredictor(),
    )
    registry = TwinRegistry()
    manager = registry.initialize("battery-1")
    for index in range(3):
        manager.process_observation([0.5] * 67, observation_index=index + 10)
    snapshot_before = manager.get_snapshot()
    state_before = deepcopy(manager.twin.get_state())
    history_before = deepcopy(manager.get_history())
    observation_index_before = manager.last_observation_index

    result = planner.run_goal_directed_orchestrator(
        "battery-1",
        GoalSpec("real-integration", 50, assessment_scope="counterfactual_comparison"),
        twin_registry=registry,
    )

    assert result.termination_status == "completed"
    assert set(row["scenario"] for row in result.candidate_evaluations) == set(
        EXPECTED_SCENARIOS
    )
    assert result.snapshot_metadata["snapshot_version"] == snapshot_before["version"]
    assert result.snapshot_metadata["observation_index"] == observation_index_before
    assert all(
        abs(row["initial_soh"] - snapshot_before["state"]["twin_state"]["soh"])
        <= planner.DEFAULT_PLANNER_CONFIG.scenario_soh_rounding_tolerance
        for row in result.candidate_evaluations
    )
    assert manager.twin.get_state() == state_before
    assert manager.get_history() == history_before
    assert manager.last_observation_index == observation_index_before


def test_invalid_goal_returns_structured_error_without_snapshot(harness):
    manager, _, _ = harness
    result = run(object(), harness)
    assert result.termination_status == "invalid_goal"
    assert manager.snapshot_calls == 0


def test_invalid_snapshot_returns_structured_error_without_assessment(harness):
    manager, _, calls = harness
    manager.snapshot["history"]["state_source"] = "manual"
    result = run(GoalSpec("invalid-snapshot", 100), harness)
    assert result.termination_status == "invalid_snapshot"
    assert calls["baseline"] == []
    assert calls["counterfactual"] == []
