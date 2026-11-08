from copy import deepcopy
import pytest

from digital_twin.baseline_relative_utility import (
    calculate_baseline_relative_utility,
)
from digital_twin.decision_models import ExperimentalDecisionResult
from digital_twin.goal_spec import GoalSpec
from digital_twin.planner_config import DEFAULT_PLANNER_CONFIG
from digital_twin.planner_tool_registry import PLANNER_TOOLS, get_planner_tool
from digital_twin.scenario_validation import validate_counterfactual_response


def make_snapshot():
    return {
        "battery_id": "battery-1",
        "version": 8,
        "state": {
            "battery_id": "battery-1",
            "twin_state": {"battery_id": "battery-1", "soh": 0.8},
            "state_source": "cnn_prediction",
            "last_observation_index": 21,
            "prediction_count": 4,
        },
        "history": {"state_source": "cnn_prediction"},
    }


def make_response():
    return {
        "battery_id": "battery-1",
        "snapshot_version": 8,
        "snapshot_soh": 0.8,
        "state_source": "cnn_prediction",
        "latest_observation_index": 21,
        "prediction_count": 4,
        "scenarios": [
            {
                "scenario": "No maintenance",
                "initial_soh": 0.8,
                "projected_soh": 0.79,
                "additional_cycles": 100,
                "recovery_assumption": 0.0,
                "difference_vs_baseline": 0.0,
            },
            {
                "scenario": "Maintenance A",
                "initial_soh": 0.8,
                "projected_soh": 0.795,
                "additional_cycles": 100,
                "recovery_assumption": 0.005,
                "difference_vs_baseline": 0.005,
            },
            {
                "scenario": "Maintenance B",
                "initial_soh": 0.8,
                "projected_soh": 0.8,
                "additional_cycles": 100,
                "recovery_assumption": 0.01,
                "difference_vs_baseline": 0.01,
            },
        ],
    }


@pytest.mark.parametrize(
    "value",
    [True, 1.5, "10", -1, 100001],
)
def test_goal_spec_rejects_invalid_horizon(value):
    with pytest.raises(ValueError):
        GoalSpec("projected_soh_at_least", horizon_cycles=value)


@pytest.mark.parametrize("value", [0, 100000])
def test_goal_spec_accepts_horizon_boundaries(value):
    assert GoalSpec("projected_soh_at_least", horizon_cycles=value).horizon_cycles == value


@pytest.mark.parametrize("value", [True, float("nan"), -0.1, 1.1, "0.8"])
def test_goal_spec_rejects_invalid_optional_target(value):
    with pytest.raises(ValueError):
        GoalSpec("projected_soh_at_least", horizon_cycles=10, target_soh=value)


def test_missing_target_is_unavailable_and_not_a_failure_trigger():
    goal = GoalSpec("assess_projection", horizon_cycles=10)
    assert goal.target_attainment(0.2) is None
    assert goal.target_failure_requires_counterfactual() is False


def test_supplied_target_attainment_is_separate_boolean():
    goal = GoalSpec("projected_soh_at_least", horizon_cycles=10, target_soh=0.8)
    assert goal.target_attainment(0.8) is True
    assert goal.target_attainment(0.79) is False


def test_tool_registry_is_an_allowlist_of_existing_callables():
    assert set(PLANNER_TOOLS) == {
        "registered_twin_snapshot",
        "baseline_assessment",
        "counterfactual_simulation",
        "maintenance_policy",
    }
    assert callable(get_planner_tool("counterfactual_simulation").function)
    with pytest.raises(ValueError, match="not allowed"):
        get_planner_tool("other")


def test_planner_configuration_centralizes_versioned_limits():
    config = DEFAULT_PLANNER_CONFIG
    assert config.scenario_soh_rounding_tolerance == 0.0001
    assert config.baseline_delta_consistency_tolerance == 0.0001
    assert config.recovery_assumption_tolerance == 0.000000001
    assert config.expected_recovery_assumptions == (0.0, 0.005, 0.01)
    assert config.maximum_planning_iterations == 3
    assert config.maximum_service_tool_invocations == 3
    assert config.maximum_counterfactual_invocations == 1
    assert config.expected_scenario_count == 3
    assert config.utility_formula_version == "baseline_relative_v1"


def test_valid_complete_scenario_set_is_accepted():
    validated = validate_counterfactual_response(
        make_response(), make_snapshot(), requested_horizon=100
    )
    assert tuple(validated.scenarios) == (
        "No maintenance",
        "Maintenance A",
        "Maintenance B",
    )


def test_complete_scenario_set_accepts_different_list_order():
    response = make_response()
    response["scenarios"] = [
        response["scenarios"][2],
        response["scenarios"][0],
        response["scenarios"][1],
    ]
    validated = validate_counterfactual_response(
        response, make_snapshot(), requested_horizon=100
    )
    assert set(validated.scenarios) == {
        "No maintenance",
        "Maintenance A",
        "Maintenance B",
    }


@pytest.mark.parametrize("field,value", [("initial_soh", True), ("projected_soh", float("nan")), ("projected_soh", 1.01), ("projected_soh", -0.01)])
def test_validation_rejects_invalid_soh_and_booleans(field, value):
    response = make_response()
    response["scenarios"][1][field] = value
    with pytest.raises(ValueError):
        validate_counterfactual_response(response, make_snapshot(), 100)


@pytest.mark.parametrize(
    "mutation,match",
    [
        (lambda data: data["scenarios"].pop(), "exactly three"),
        (
            lambda data: data["scenarios"].__setitem__(2, deepcopy(data["scenarios"][1])),
            "Duplicate",
        ),
        (
            lambda data: data["scenarios"][1].__setitem__("additional_cycles", 99),
            "horizon",
        ),
        (
            lambda data: data["scenarios"][1].__setitem__("initial_soh", 0.8002),
            "initial SOH",
        ),
        (
            lambda data: data["scenarios"][1].__setitem__("recovery_assumption", 0.006),
            "recovery assumption",
        ),
        (
            lambda data: data["scenarios"][1].__setitem__("difference_vs_baseline", 0.02),
            "baseline delta",
        ),
        (lambda data: data.__setitem__("battery_id", "other"), "battery identity"),
        (lambda data: data.__setitem__("snapshot_version", 7), "version"),
        (lambda data: data.__setitem__("state_source", "manual"), "provenance"),
        (lambda data: data.__setitem__("latest_observation_index", 22), "observation index"),
        (lambda data: data.__setitem__("prediction_count", 3), "prediction count"),
    ],
)
def test_validation_rejects_incomplete_or_inconsistent_scenario_set(mutation, match):
    response = make_response()
    mutation(response)
    with pytest.raises(ValueError, match=match):
        validate_counterfactual_response(response, make_snapshot(), 100)


def test_initial_soh_within_configured_rounding_tolerance_is_accepted():
    response = make_response()
    response["scenarios"][1]["initial_soh"] += 0.0001
    validated = validate_counterfactual_response(
        response, make_snapshot(), requested_horizon=100
    )
    assert validated.scenarios["Maintenance A"]["initial_soh"] == pytest.approx(0.8001)


def test_recovery_assumption_just_inside_configured_tolerance_is_accepted():
    response = make_response()
    tolerance = DEFAULT_PLANNER_CONFIG.recovery_assumption_tolerance
    expected = DEFAULT_PLANNER_CONFIG.expected_recovery_assumptions[1]
    response["scenarios"][1]["recovery_assumption"] = expected + tolerance * 0.5

    validated = validate_counterfactual_response(
        response,
        make_snapshot(),
        requested_horizon=100,
        config=DEFAULT_PLANNER_CONFIG,
    )

    assert validated.scenarios["Maintenance A"]["recovery_assumption"] == (
        expected + tolerance * 0.5
    )


def test_recovery_assumption_just_outside_configured_tolerance_is_rejected():
    response = make_response()
    tolerance = DEFAULT_PLANNER_CONFIG.recovery_assumption_tolerance
    expected = DEFAULT_PLANNER_CONFIG.expected_recovery_assumptions[1]
    response["scenarios"][1]["recovery_assumption"] = expected + tolerance * 1.5

    with pytest.raises(ValueError, match="recovery assumption"):
        validate_counterfactual_response(
            response,
            make_snapshot(),
            requested_horizon=100,
            config=DEFAULT_PLANNER_CONFIG,
        )


def test_baseline_relative_utility_uses_full_projection_values():
    validated = validate_counterfactual_response(
        make_response(), make_snapshot(), requested_horizon=100
    )
    ranking = calculate_baseline_relative_utility(
        validated,
        GoalSpec("projected_soh_at_least", 100, target_soh=0.8),
    )
    assert ranking.utilities["Maintenance A"] == pytest.approx(0.5)
    assert ranking.utilities["Maintenance B"] == pytest.approx(1.0)
    assert ranking.ranked_groups == (("Maintenance B",), ("Maintenance A",))
    assert ranking.target_attainment == {
        "No maintenance": False,
        "Maintenance A": False,
        "Maintenance B": True,
    }


def test_equal_utility_candidates_remain_tied():
    response = make_response()
    response["scenarios"][2]["projected_soh"] = 0.795
    response["scenarios"][2]["difference_vs_baseline"] = 0.005
    validated = validate_counterfactual_response(
        response, make_snapshot(), requested_horizon=100
    )
    ranking = calculate_baseline_relative_utility(
        validated, GoalSpec("projection", 100)
    )
    assert ranking.ranked_groups == (("Maintenance A", "Maintenance B"),)
    assert "No maintenance" not in ranking.utilities
    assert ranking.target_attainment == {
        "No maintenance": None,
        "Maintenance A": None,
        "Maintenance B": None,
    }


def test_shared_decision_result_supports_baseline_and_counterfactual_paths():
    baseline = ExperimentalDecisionResult(
        decision_id="d1",
        battery_id="battery-1",
        assessment_path="baseline_only",
        termination_status="completed",
        goal_status="unavailable_target",
        candidate_evaluations=[{"scenario": "No maintenance", "status": "valid"}],
        policy_comparison={"status": "not_applicable_baseline_only"},
    )
    assert baseline.utility_ranking is None
    with pytest.raises(ValueError, match="only the No maintenance baseline"):
        ExperimentalDecisionResult(
            decision_id="d2",
            battery_id="battery-1",
            assessment_path="baseline_only",
            termination_status="completed",
            candidate_evaluations=[{"scenario": "Maintenance A"}],
            policy_comparison={"status": "not_applicable_baseline_only"},
        )
    counterfactual = ExperimentalDecisionResult(
        decision_id="d3",
        battery_id="battery-1",
        assessment_path="counterfactual_comparison",
        termination_status="completed",
        candidate_evaluations=[{"scenario": "Maintenance A"}],
        utility_ranking={"status": "ranked"},
        policy_comparison={"status": "conflict", "policy_action": "x"},
    )
    assert counterfactual.policy_comparison["status"] == "conflict"
