"""Deterministic experimental goal-directed assessment orchestration."""

import math
import uuid
from typing import Any, Optional

from backend.twin_registry import twin_registry as shared_twin_registry
from digital_twin.baseline_relative_utility import (
    calculate_baseline_relative_utility,
)
from digital_twin.decision_models import ExperimentalDecisionResult
from digital_twin.goal_spec import GoalSpec
from digital_twin.planner_config import DEFAULT_PLANNER_CONFIG, PlannerConfig
from digital_twin import planner_tool_registry
from digital_twin.scenario_validation import (
    EXPECTED_SCENARIOS,
    validate_counterfactual_response,
)


def _valid_fraction(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and 0.0 <= value <= 1.0
    )


def _new_result(
    battery_id: str,
    assessment_path: str = "baseline_only",
    termination_status: str = "failed",
    **kwargs,
) -> ExperimentalDecisionResult:
    safe_battery_id = battery_id if isinstance(battery_id, str) and battery_id else "unknown"
    if assessment_path == "baseline_only":
        kwargs.setdefault(
            "policy_comparison",
            {
                "status": "not_applicable_baseline_only",
                "comparison_status": "not_applicable",
                "policy_availability": "not_invoked",
            },
        )
        kwargs.setdefault("selected_action", "no_intervention_selected")
    return ExperimentalDecisionResult(
        decision_id=str(uuid.uuid4()),
        battery_id=safe_battery_id,
        assessment_path=assessment_path,
        termination_status=termination_status,
        **kwargs,
    )


def _validate_goal(goal: object, config: PlannerConfig) -> GoalSpec:
    if not isinstance(goal, GoalSpec):
        raise ValueError("goal must be a GoalSpec.")
    # Reconstruct so mutable evidence dictionaries cannot bypass validation.
    validated = GoalSpec(
        goal_id=goal.goal_id,
        horizon_cycles=goal.horizon_cycles,
        target_soh=goal.target_soh,
        assessment_scope=goal.assessment_scope,
        diagnostic_evidence=goal.diagnostic_evidence,
        goal_version=goal.goal_version,
        config_version=goal.config_version,
    )
    if validated.config_version != config.config_version:
        raise ValueError(
            "Goal configuration version does not match the active planner config."
        )
    return validated


def _validate_snapshot(snapshot: object, battery_id: str) -> dict:
    if not isinstance(snapshot, dict):
        raise ValueError("TwinManager returned an invalid snapshot.")
    if snapshot.get("battery_id") != battery_id:
        raise ValueError("Twin snapshot belongs to another battery.")
    if type(snapshot.get("version")) is not int:
        raise ValueError("Twin snapshot version is invalid.")
    state = snapshot.get("state")
    history = snapshot.get("history")
    if not isinstance(state, dict) or not isinstance(history, dict):
        raise ValueError("Twin snapshot is missing state or history.")
    if (
        state.get("battery_id") != battery_id
        or state.get("state_source") != "cnn_prediction"
        or history.get("battery_id") != battery_id
        or history.get("state_source") != "cnn_prediction"
    ):
        raise ValueError("Twin snapshot identity or CNN provenance is invalid.")
    twin_state = state.get("twin_state")
    if not isinstance(twin_state, dict) or twin_state.get("battery_id") != battery_id:
        raise ValueError("Twin snapshot operational state is inconsistent.")
    if not _valid_fraction(twin_state.get("soh")):
        raise ValueError("Twin snapshot SOH is invalid.")
    count = state.get("prediction_count")
    predictions = history.get("prediction_history")
    if (
        type(count) is not int
        or count < 1
        or not isinstance(predictions, list)
        or len(predictions) != count
    ):
        raise ValueError("Twin snapshot prediction history is inconsistent.")
    index = state.get("last_observation_index")
    if index is not None and (type(index) is not int or index < 0):
        raise ValueError("Twin snapshot observation index is invalid.")
    return snapshot


def _trend(snapshot: dict) -> tuple[Optional[float], str]:
    """Return the existing TwinManager trend, without fitting a new estimator."""
    state = snapshot["state"]
    history = snapshot["history"]
    predictions = history["prediction_history"]
    count = state["prediction_count"]
    if count < 3 or len(predictions) < 3:
        return None, "unknown"
    prediction_soh = []
    for prediction in predictions:
        if not isinstance(prediction, dict):
            return None, "unknown"
        soh = prediction.get("predicted_soh")
        if (
            isinstance(soh, bool)
            or not isinstance(soh, (int, float))
            or not math.isfinite(soh)
            or not 0.0 <= soh <= 1.0
        ):
            return None, "unknown"
        prediction_soh.append(soh)
    degradation = state.get("degradation")
    if not isinstance(degradation, dict):
        return None, "unknown"
    value = degradation.get("trend_per_sample")
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        return None, "unknown"
    # DegradationEstimator.estimate() reports the full history length, the
    # fitting window, its latest (six-decimal) SOH, and historical/forecast
    # flags. Require those values to describe this same atomic snapshot.
    observation_count = degradation.get("observation_count")
    window_size_used = degradation.get("window_size_used")
    latest_soh = degradation.get("latest_observed_soh")
    if (
        type(observation_count) is not int
        or observation_count != count
        or type(window_size_used) is not int
        or not 3 <= window_size_used <= count
        or isinstance(latest_soh, bool)
        or not isinstance(latest_soh, (int, float))
        or not math.isfinite(latest_soh)
        or abs(latest_soh - round(prediction_soh[-1], 6)) > 1e-12
        or degradation.get("is_historical_estimate") is not True
        or degradation.get("is_future_forecast") is not False
    ):
        return None, "unknown"
    # DegradationEstimator fits SOH ordered oldest-to-newest; negative slope declines.
    return float(value), "declining" if value < 0 else "not_declining"


def _has_diagnostic_trigger(evidence: dict) -> bool:
    return any(
        (
            evidence.get("thermal_alert", False),
            bool(evidence.get("bms_fault_codes", [])),
            evidence.get("cell_voltage_imbalance", False),
            evidence.get("charging_anomaly", False),
            evidence.get("confirmed_fault", False),
        )
    )


def _select_path(goal: GoalSpec, snapshot: dict, trend_status: str) -> str:
    if goal.assessment_scope == "baseline_only":
        return "baseline_only"
    if goal.assessment_scope == "counterfactual_comparison":
        return "counterfactual_comparison"
    current_soh = snapshot["state"]["twin_state"]["soh"]
    if goal.target_soh is not None and current_soh < goal.target_soh:
        return "counterfactual_comparison"
    if trend_status == "declining":
        return "counterfactual_comparison"
    if _has_diagnostic_trigger(goal.diagnostic_evidence or {}):
        return "counterfactual_comparison"
    return "baseline_only"


def _snapshot_metadata(snapshot: dict, trend: Optional[float], trend_status: str) -> dict:
    state = snapshot["state"]
    return {
        "version": snapshot["version"],
        "state_source": state["state_source"],
        "history_state_source": snapshot["history"]["state_source"],
        "observation_index": state["last_observation_index"],
        "prediction_count": state["prediction_count"],
        "current_soh": state["twin_state"]["soh"],
        "trend_per_sample": trend,
        "trend_status": trend_status,
    }


def _available_evidence(goal: GoalSpec, trend: Optional[float], trend_status: str) -> list:
    evidence = [
        {
            "type": "trend",
            "status": trend_status,
            "trend_per_sample": trend,
            "unit": "SOH_fraction_per_prediction_sample",
        }
    ]
    for key, value in (goal.diagnostic_evidence or {}).items():
        if value:
            evidence.append({"type": "diagnostic", "field": key, "value": value})
    return evidence


def _validate_baseline_result(
    result: object,
    snapshot: dict,
    requested_horizon: int,
    config: PlannerConfig,
) -> dict:
    if not isinstance(result, dict):
        raise ValueError("Baseline assessment did not return a result dictionary.")
    if result.get("scenario") != "No maintenance":
        raise ValueError("Baseline assessment returned an unexpected scenario.")
    if type(result.get("snapshot_version")) is not int or result[
        "snapshot_version"
    ] != snapshot["version"]:
        raise ValueError("Baseline assessment snapshot version is inconsistent.")
    if type(result.get("additional_cycles")) is not int or result[
        "additional_cycles"
    ] != requested_horizon:
        raise ValueError("Baseline assessment horizon is inconsistent.")
    initial = result.get("initial_soh")
    projected = result.get("projected_soh")
    if not _valid_fraction(initial) or not _valid_fraction(projected):
        raise ValueError("Baseline assessment contains invalid SOH values.")
    snapshot_soh = snapshot["state"]["twin_state"]["soh"]
    if abs(initial - snapshot_soh) > config.scenario_soh_rounding_tolerance + 1e-12:
        raise ValueError("Baseline initial SOH does not match the snapshot.")
    recovery = result.get("recovery_assumption")
    if (
        isinstance(recovery, bool)
        or not isinstance(recovery, (int, float))
        or not math.isfinite(recovery)
        or abs(recovery) > config.recovery_assumption_tolerance
    ):
        raise ValueError("Baseline recovery assumption is inconsistent.")
    delta = result.get("difference_vs_baseline")
    if (
        isinstance(delta, bool)
        or not isinstance(delta, (int, float))
        or not math.isfinite(delta)
        or abs(delta) > config.baseline_delta_consistency_tolerance
    ):
        raise ValueError("Baseline delta is inconsistent.")
    return result


def _target_status(goal: GoalSpec, projected_soh: float) -> str:
    if goal.target_soh is None:
        return "target_unavailable"
    return "goal_met" if projected_soh >= goal.target_soh else "goal_unmet"


def _error_result(
    battery_id: str,
    status: str,
    code: str,
    message: str,
    *,
    assessment_path: str = "baseline_only",
    snapshot_metadata: Optional[dict] = None,
    tool_outcomes: Optional[list] = None,
) -> ExperimentalDecisionResult:
    return _new_result(
        battery_id,
        assessment_path=assessment_path,
        termination_status=status,
        snapshot_metadata=snapshot_metadata or {},
        errors=[{"code": code, "message": message}],
        explanation=[message],
        tool_outcomes=tool_outcomes or [],
    )


def run_goal_directed_orchestrator(
    battery_id: str,
    goal: GoalSpec,
    minimum_acceptable_soh: float = 0.80,
    twin_registry=None,
    config: PlannerConfig = DEFAULT_PLANNER_CONFIG,
) -> ExperimentalDecisionResult:
    """Execute a goal-directed decision through the allowlisted tool registry."""
    outcomes = []
    try:
        validated_goal = _validate_goal(goal, config)
    except (AttributeError, TypeError, ValueError) as exc:
        return _error_result(battery_id, "invalid_goal", "invalid_goal", str(exc))
    if not isinstance(battery_id, str) or not battery_id.strip():
        return _error_result(battery_id, "invalid_snapshot", "invalid_battery_id", "Battery ID cannot be empty.")
    registry = shared_twin_registry if twin_registry is None else twin_registry

    def execute(name, arguments):
        outcome = planner_tool_registry.execute_planner_tool(
            name, arguments, execution_order=len(outcomes) + 1
        )
        outcomes.append(outcome)
        return outcome

    snapshot_outcome = execute(
        "registered_twin_snapshot",
        {"twin_registry": registry, "battery_id": battery_id},
    )
    if snapshot_outcome.status != "success":
        return _error_result(
            battery_id, "invalid_snapshot", snapshot_outcome.error["code"],
            snapshot_outcome.error["message"], tool_outcomes=outcomes,
        )
    snapshot = snapshot_outcome.result
    try:
        snapshot = _validate_snapshot(snapshot, battery_id)
    except (TypeError, ValueError) as exc:
        snapshot_outcome.status = "invalid_result"
        snapshot_outcome.error = {"code": "invalid_snapshot", "message": str(exc)}
        snapshot_outcome.result = None
        return _error_result(
            battery_id, "invalid_snapshot", "invalid_snapshot", str(exc),
            tool_outcomes=outcomes,
        )
    # The full snapshot stays local to this run. Never duplicate histories in the result.
    snapshot_outcome.result = {
        "battery_id": snapshot["battery_id"],
        "version": snapshot["version"],
        "state_source": snapshot["state"]["state_source"],
        "prediction_count": snapshot["state"]["prediction_count"],
    }

    trend_per_sample, trend_status = _trend(snapshot)
    path = _select_path(validated_goal, snapshot, trend_status)
    metadata = _snapshot_metadata(snapshot, trend_per_sample, trend_status)
    available_evidence = _available_evidence(validated_goal, trend_per_sample, trend_status)
    current_soh = snapshot["state"]["twin_state"]["soh"]
    diagnostic_evidence = validated_goal.diagnostic_evidence or {}

    baseline_outcome = execute(
        "baseline_assessment",
        {
            "twin_registry": registry,
            "battery_id": battery_id,
            "additional_cycles": validated_goal.horizon_cycles,
            "state_snapshot": snapshot,
        },
    )
    if baseline_outcome.status != "success":
        return _error_result(
            battery_id, "service_failure", "baseline_assessment_failed",
            baseline_outcome.error["message"], assessment_path=path,
            snapshot_metadata=metadata, tool_outcomes=outcomes,
        )
    try:
        baseline = _validate_baseline_result(
            baseline_outcome.result, snapshot, validated_goal.horizon_cycles, config
        )
    except (TypeError, ValueError) as exc:
        baseline_outcome.status = "invalid_result"
        baseline_outcome.error = {"code": "invalid_baseline_result", "message": str(exc)}
        baseline_outcome.result = None
        return _error_result(
            battery_id, "invalid_service_result", "invalid_baseline_result", str(exc),
            assessment_path=path, snapshot_metadata=metadata, tool_outcomes=outcomes,
        )

    if path == "baseline_only":
        projected = float(baseline["projected_soh"])
        target_status = _target_status(validated_goal, projected)
        candidate = {
            "scenario": "No maintenance", "initial_soh": baseline["initial_soh"],
            "projected_soh": projected, "additional_cycles": baseline["additional_cycles"],
            "target_attainment": validated_goal.target_attainment(projected),
            "eligibility": "baseline_comparator",
        }
        return _new_result(
            battery_id, assessment_path=path,
            termination_status="goal_unmet" if target_status == "goal_unmet" else "completed",
            goal_status=target_status, selected_action="no_intervention_selected",
            available_evidence=available_evidence, candidate_evaluations=[candidate],
            policy_comparison={"status": "not_applicable_baseline_only", "comparison_status": "not_applicable", "policy_availability": "not_invoked"},
            explanation=["Baseline projection was assessed from one captured snapshot.", "No intervention utility was calculated or intervention selected."],
            snapshot_metadata={**metadata, "snapshot_version": baseline["snapshot_version"]},
            tool_outcomes=outcomes,
        )

    counterfactual_outcome = execute(
        "counterfactual_simulation",
        {
            "twin_registry": registry,
            "battery_id": battery_id,
            "additional_cycles": validated_goal.horizon_cycles,
            "state_snapshot": snapshot,
        },
    )
    if counterfactual_outcome.status != "success":
        return _error_result(
            battery_id, "service_failure", "counterfactual_simulation_failed",
            counterfactual_outcome.error["message"], assessment_path=path,
            snapshot_metadata=metadata, tool_outcomes=outcomes,
        )
    response = counterfactual_outcome.result
    try:
        scenarios = validate_counterfactual_response(
            response, captured_snapshot=snapshot,
            requested_horizon=validated_goal.horizon_cycles, config=config,
        )
        cf_baseline = scenarios.baseline
        tolerance = max(config.scenario_soh_rounding_tolerance, config.baseline_delta_consistency_tolerance) + 1e-12
        if (
            abs(float(cf_baseline["initial_soh"]) - float(baseline["initial_soh"])) > tolerance
            or abs(float(cf_baseline["projected_soh"]) - float(baseline["projected_soh"])) > tolerance
            or cf_baseline["additional_cycles"] != baseline["additional_cycles"]
            or abs(float(cf_baseline["recovery_assumption"]) - float(baseline["recovery_assumption"])) > config.recovery_assumption_tolerance
        ):
            raise ValueError("Counterfactual baseline is inconsistent with the mandatory baseline assessment.")
        initial_soh_values = [row["initial_soh"] for row in scenarios.scenarios.values()]
        if max(initial_soh_values) - min(initial_soh_values) > config.scenario_soh_rounding_tolerance + 1e-12:
            raise ValueError("Counterfactual scenarios do not share a consistent initial SOH.")
    except (TypeError, ValueError, KeyError) as exc:
        counterfactual_outcome.status = "invalid_result"
        error_code = (
            "inconsistent_scenario_initial_soh"
            if "share a consistent initial SOH" in str(exc)
            else "invalid_counterfactual_result"
        )
        counterfactual_outcome.error = {"code": error_code, "message": str(exc)}
        counterfactual_outcome.result = None
        return _error_result(
            battery_id, "invalid_scenario_evidence", error_code, str(exc),
            assessment_path=path, snapshot_metadata=metadata, tool_outcomes=outcomes,
        )

    try:
        utility = calculate_baseline_relative_utility(scenarios, validated_goal, config=config)
    except (TypeError, ValueError, KeyError) as exc:
        return _error_result(
            battery_id, "invalid_service_result", "utility_calculation_failed", str(exc),
            assessment_path=path, snapshot_metadata=metadata, tool_outcomes=outcomes,
        )
    ranked_groups = [list(group) for group in utility.ranked_groups]
    utility_preferred = utility.ranked_groups[0][0] if utility.ranked_groups and len(utility.ranked_groups[0]) == 1 else None
    selection_status = "tie" if utility.ranked_groups and len(utility.ranked_groups[0]) > 1 else "feasibility_unknown" if utility_preferred else "no_eligible_candidates"
    utility_payload = {
        "formula_version": utility.formula_version,
        "formula": "100 * (projected_soh_i - projected_soh_baseline)",
        "utilities": dict(utility.utilities), "ranked_groups": ranked_groups,
        "selection_status": selection_status,
        "analytical_preferred_candidate": utility_preferred,
        "selected_candidate": None, "feasibility_status": "unknown",
        "target_attainment": dict(utility.target_attainment),
        "is_simulated_utility": True, "is_physically_validated": False,
        "is_feasibility_assessed": False,
    }
    candidate_evaluations = [
        {
            "scenario": name, "initial_soh": row["initial_soh"],
            "projected_soh": row["projected_soh"], "additional_cycles": row["additional_cycles"],
            "recovery_assumption": row["recovery_assumption"],
            "utility": utility.utilities.get(name), "target_attainment": utility.target_attainment[name],
            "eligibility": "baseline_comparator" if name == "No maintenance" else "not_eligible_unknown_feasibility",
            "feasibility_status": "not_applicable_baseline_comparator" if name == "No maintenance" else "unknown",
        }
        for name, row in scenarios.scenarios.items()
    ]

    policy_outcome = execute(
        "maintenance_policy",
        {
            "scenario_results": list(scenarios.scenarios.values()),
            "minimum_acceptable_soh": minimum_acceptable_soh,
            "current_soh": current_soh,
            "trend_per_sample": trend_per_sample,
            "diagnostic_evidence": diagnostic_evidence,
        },
    )
    errors = []
    policy = policy_outcome.result
    if policy_outcome.status == "success":
        malformed_reason = None
        if not isinstance(policy, dict):
            malformed_reason = "Maintenance policy must return a result dictionary."
        elif (
            "recommended_scenario" not in policy
            or policy["recommended_scenario"] is not None
            and policy["recommended_scenario"] not in EXPECTED_SCENARIOS
        ):
            malformed_reason = "Maintenance policy returned an invalid recommendation."
        elif (
            not isinstance(policy.get("recommended_action"), str)
            or not policy["recommended_action"].strip()
            or not isinstance(policy.get("status"), str)
            or not policy["status"].strip()
            or not isinstance(policy.get("reason"), str)
            or not policy["reason"].strip()
        ):
            malformed_reason = "Maintenance policy result is missing required fields."
        if malformed_reason:
            policy_outcome.status = "execution_failure"
            policy_outcome.error = {
                "code": "invalid_tool_result",
                "message": malformed_reason,
            }
            policy_outcome.result = None
    if policy_outcome.status == "success":
        policy_scenario = policy.get("recommended_scenario") if isinstance(policy, dict) else None
        policy_availability = "available" if policy_scenario in EXPECTED_SCENARIOS else "unavailable"
        comparison_status = "tie" if selection_status == "tie" else "unavailable" if utility_preferred is None or policy_availability == "unavailable" else "agreement" if policy_scenario == utility_preferred else "disagreement"
        policy_comparison = {
            "status": comparison_status, "comparison_status": comparison_status,
            "policy_availability": policy_availability, "utility_selected_candidate": None,
            "utility_preferred_candidate": utility_preferred, "utility_ranked_groups": ranked_groups,
            "policy_recommended_scenario": policy_scenario,
            "policy_recommended_action": policy.get("recommended_action") if isinstance(policy, dict) else None,
            "policy_status": policy.get("status") if isinstance(policy, dict) else None,
            "policy_reason": policy.get("reason") if isinstance(policy, dict) else None,
            "policy_matches_utility_tie": policy_scenario in utility.ranked_groups[0] if selection_status == "tie" and policy_availability == "available" else None,
            "policy_output": policy,
        }
    else:
        comparison_status = "tie" if selection_status == "tie" else "unavailable"
        policy_comparison = {
            "status": comparison_status, "comparison_status": comparison_status,
            "policy_availability": "unavailable", "utility_selected_candidate": None,
            "utility_preferred_candidate": utility_preferred, "utility_ranked_groups": ranked_groups,
            "policy_recommended_scenario": None, "policy_output": None,
        }
        error_code = (
            "maintenance_policy_invalid_result"
            if policy_outcome.error["code"] == "invalid_tool_result"
            else "maintenance_policy_failed"
        )
        errors.append({"code": error_code, "message": policy_outcome.error["message"]})

    target_values = utility.target_attainment
    if validated_goal.target_soh is None:
        goal_status = "target_unavailable"
    elif any(value is True for value in target_values.values()):
        goal_status = "goal_met"
    else:
        goal_status = "goal_unmet"
    return _new_result(
        battery_id, assessment_path=path,
        termination_status="completed_with_policy_error" if errors else "tie" if selection_status == "tie" else "completed",
        goal_status=goal_status, selected_action=None, available_evidence=available_evidence,
        candidate_evaluations=candidate_evaluations, utility_ranking=utility_payload,
        policy_comparison=policy_comparison,
        explanation=[
            "Counterfactual utility compares simulated projected SOH against No maintenance.",
            "Utility is relative to illustrative assumptions and is not a physical-safety guarantee.",
            "Utility ranking is analytical only; intervention feasibility is unknown, so no intervention is selected.",
            "The maintenance-policy recommendation is preserved separately from the utility ranking.",
        ],
        snapshot_metadata={**metadata, "snapshot_version": scenarios.snapshot_version, "is_simulation": response.get("is_simulation"), "is_physically_validated": response.get("is_physically_validated")},
        errors=errors, tool_outcomes=outcomes,
    )
