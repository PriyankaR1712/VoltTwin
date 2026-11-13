"""Deterministic serialization for persisted Agentic AI decision history."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, is_dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Optional

from digital_twin.decision_models import ExperimentalDecisionResult
from digital_twin.goal_spec import GoalSpec


RECORD_VERSION = 1
_BASELINE_TOOL = "baseline_assessment"
_COUNTERFACTUAL_TOOL = "counterfactual_simulation"


@dataclass(frozen=True)
class FrozenDecisionPayload:
    """Immutable persisted JSON bytes plus their stable digest representation."""

    decision_id: str
    database_json: bytes
    canonical_digest_bytes: bytes
    payload_digest: str


def _json_value(value: Any) -> Any:
    """Convert supported result values to ordinary JSON data without coercion."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Decision payload cannot contain non-finite floats.")
        return value
    if is_dataclass(value) and not isinstance(value, type):
        return _json_value(asdict(value))
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("Decision payload object keys must be strings.")
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    raise ValueError(f"Unsupported decision payload value: {type(value).__name__}.")


def serialize_goal_spec(goal: GoalSpec) -> dict[str, Any]:
    if not isinstance(goal, GoalSpec):
        raise ValueError("Original goal must be a GoalSpec.")
    return {
        "goal_id": goal.goal_id,
        "horizon_cycles": goal.horizon_cycles,
        "target_soh": goal.target_soh,
        "assessment_scope": goal.assessment_scope,
        "diagnostic_evidence": _json_value(goal.diagnostic_evidence),
        "goal_version": goal.goal_version,
        "config_version": goal.config_version,
    }


def _baseline_outcome(result: ExperimentalDecisionResult) -> Optional[dict[str, Any]]:
    for outcome in result.tool_outcomes:
        if outcome.tool_name == _BASELINE_TOOL:
            return {
                "status": outcome.status,
                "result": outcome.result,
                "error": outcome.error,
            }
    return None


def _has_successful_validated_baseline(
    result: ExperimentalDecisionResult,
) -> bool:
    baseline = _baseline_outcome(result)
    return bool(
        baseline
        and baseline["status"] == "success"
        and isinstance(baseline["result"], dict)
        and baseline["result"].get("scenario") == "No maintenance"
    )


def map_decision_status(result: ExperimentalDecisionResult) -> str:
    """Map a Stage 3 termination using both its status and executed evidence."""
    termination = result.termination_status
    if termination in {"completed", "goal_unmet", "tie"}:
        return "completed"
    if termination == "completed_with_policy_error":
        return "incomplete"
    if termination in {"service_failure", "invalid_service_result"}:
        return (
            "incomplete"
            if _has_successful_validated_baseline(result)
            else "failed"
        )
    if termination == "invalid_scenario_evidence":
        return (
            "incomplete"
            if _has_successful_validated_baseline(result)
            else "failed"
        )
    if termination in {"invalid_goal", "invalid_snapshot"}:
        return "failed"
    return "failed"


def _canonical_value(value: Any) -> Any:
    """Encode JSON types distinctly; floats use exact, finite IEEE hex values."""
    if value is None:
        return ["null"]
    if isinstance(value, bool):
        return ["boolean", value]
    if isinstance(value, int):
        return ["integer", str(value)]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("Decision payload cannot contain non-finite floats.")
        return ["float64", value.hex()]
    if isinstance(value, str):
        return ["string", value]
    if isinstance(value, list):
        return ["array", [_canonical_value(item) for item in value]]
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ValueError("Decision payload object keys must be strings.")
        return [
            "object",
            [[key, _canonical_value(value[key])] for key in sorted(value)],
        ]
    raise ValueError(f"Unsupported canonical value: {type(value).__name__}.")


def canonical_digest_bytes(payload: Mapping[str, Any]) -> bytes:
    """Return deterministic UTF-8 digest bytes, excluding any digest field."""
    without_digest = {key: value for key, value in payload.items() if key != "payload_digest"}
    tagged = _canonical_value(_json_value(without_digest))
    return json.dumps(
        tagged,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _utc_timestamp(value: datetime) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("decision_started_at must be a timezone-aware datetime.")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _tool_outcome_rows(
    result: ExperimentalDecisionResult,
    planned_tools: Optional[tuple[str, ...]],
) -> list[dict[str, Any]]:
    outcomes = list(result.tool_outcomes)
    by_order = {outcome.execution_order: outcome for outcome in outcomes}
    if len(by_order) != len(outcomes):
        raise ValueError("Tool outcomes contain duplicate execution orders.")

    if planned_tools is None:
        return [
            {
                "tool_name": outcome.tool_name,
                "planned": None,
                "executed": True,
                "execution_order": outcome.execution_order,
                "status": outcome.status,
                "validated_arguments": _json_value(outcome.validated_arguments),
                "result_summary": _json_value(outcome.result),
                "error_details": _json_value(outcome.error),
            }
            for outcome in outcomes
        ]

    if any(not isinstance(name, str) or not name for name in planned_tools):
        raise ValueError("Planned tool names must be non-empty strings.")
    if len(set(planned_tools)) != len(planned_tools):
        raise ValueError("Planned tool names must be unique within a decision.")

    rows = []
    for order, name in enumerate(planned_tools, start=1):
        outcome = by_order.pop(order, None)
        if outcome is not None:
            if outcome.tool_name != name:
                raise ValueError("Executed tool does not match the recorded plan.")
            rows.append(
                {
                    "tool_name": name,
                    "planned": True,
                    "executed": True,
                    "execution_order": order,
                    "status": outcome.status,
                    "validated_arguments": _json_value(outcome.validated_arguments),
                    "result_summary": _json_value(outcome.result),
                    "error_details": _json_value(outcome.error),
                }
            )
        else:
            rows.append(
                {
                    "tool_name": name,
                    "planned": True,
                    "executed": False,
                    "execution_order": order,
                    "status": "not_executed",
                    "validated_arguments": None,
                    "result_summary": None,
                    "error_details": None,
                }
            )
    if by_order:
        raise ValueError("Executed tool outcome is absent from the recorded plan.")
    return rows


def _scenario_rows(result: ExperimentalDecisionResult) -> list[dict[str, Any]]:
    evidence: dict[str, dict[str, Any]] = {}
    for candidate in result.candidate_evaluations:
        if isinstance(candidate, dict) and isinstance(candidate.get("scenario"), str):
            evidence[candidate["scenario"]] = dict(candidate)

    baseline = _baseline_outcome(result)
    if (
        "No maintenance" not in evidence
        and baseline
        and baseline["status"] == "success"
        and isinstance(baseline["result"], dict)
        and baseline["result"].get("scenario") == "No maintenance"
    ):
        evidence["No maintenance"] = dict(baseline["result"])

    for outcome in result.tool_outcomes:
        if outcome.tool_name != _COUNTERFACTUAL_TOOL or outcome.status != "success":
            continue
        response = outcome.result
        rows = response.get("scenarios") if isinstance(response, dict) else None
        if not isinstance(rows, list):
            continue
        for scenario in rows:
            if isinstance(scenario, dict) and isinstance(scenario.get("scenario"), str):
                name = scenario["scenario"]
                evidence[name] = {**scenario, **evidence.get(name, {})}

    normalized = []
    for name, row in evidence.items():
        projected_soh = row.get("projected_soh")
        if (
            isinstance(projected_soh, bool)
            or not isinstance(projected_soh, (int, float))
            or not math.isfinite(projected_soh)
            or not 0.0 <= projected_soh <= 1.0
        ):
            continue
        normalized.append(
            {
                "scenario_type": "baseline" if name == "No maintenance" else "counterfactual",
                "scenario_name": name,
                "projected_soh": projected_soh,
                "utility": _json_value(row.get("utility")),
                "feasibility": _json_value(
                    row.get("feasibility", row.get("feasibility_status"))
                ),
                "result_data": _json_value(row),
            }
        )
    return normalized


def _baseline_result(result: ExperimentalDecisionResult) -> Any:
    outcome = _baseline_outcome(result)
    return outcome["result"] if outcome else None


def _counterfactual_result(result: ExperimentalDecisionResult) -> Any:
    for outcome in result.tool_outcomes:
        if outcome.tool_name == _COUNTERFACTUAL_TOOL:
            return outcome.result
    return None


def _explanation(
    goal: dict[str, Any],
    result: ExperimentalDecisionResult,
    decision_status: str,
    scenarios: list[dict[str, Any]],
) -> list[str]:
    lines = list(result.explanation)
    lines.append(
        f"Decision status: {decision_status} (Stage 3 termination: {result.termination_status})."
    )
    if goal["target_soh"] is None:
        lines.append("Target attainment is unavailable because no target SOH was supplied.")
    else:
        lines.append(f"Goal status: {result.goal_status or 'unavailable'}.")

    baseline = next(
        (row for row in scenarios if row["scenario_name"] == "No maintenance"), None
    )
    if baseline is None:
        lines.append("Baseline scenario evidence is unavailable.")
    else:
        lines.append(
            "Baseline projected SOH: "
            f"{float(baseline['projected_soh']):.17g}."
        )
        for row in scenarios:
            if row is baseline:
                continue
            lines.append(
                f"{row['scenario_name']} projected SOH: "
                f"{float(row['projected_soh']):.17g}."
            )

    ranking = result.utility_ranking
    if isinstance(ranking, dict):
        for group in ranking.get("ranked_groups", []):
            if isinstance(group, list) and len(group) > 1:
                lines.append("Utility tie preserved between: " + ", ".join(group) + ".")
    for candidate, assessment in result.intervention_feasibility.items():
        lines.append(
            f"{candidate} model-based feasibility: {assessment['status']}; "
            "this is not physical safety validation or proof of maintenance effectiveness."
        )
        for reason in assessment.get("reasons", []):
            if isinstance(reason, dict) and reason.get("explanation"):
                lines.append(f"{candidate} feasibility reason: {reason['explanation']}")
    if result.final_recommendation:
        lines.append(
            "Final model-based recommendation: "
            + str(result.final_recommendation.get("candidate") or "none")
            + ". "
            + str(result.final_recommendation.get("reason", ""))
        )

    if decision_status == "incomplete":
        lines.append("The decision attempt is incomplete; recorded results and errors are preserved.")
    elif decision_status == "failed":
        lines.append("The decision attempt failed before a complete assessment was available.")

    for outcome in result.tool_outcomes:
        if outcome.status != "success":
            lines.append(f"Tool {outcome.tool_name} status: {outcome.status}.")
    for error in result.errors:
        if isinstance(error, dict):
            code = error.get("code")
            message = error.get("message")
            if code or message:
                lines.append("Recorded error: " + ": ".join(str(v) for v in (code, message) if v) + ".")
    return lines


def freeze_decision_payload(
    *,
    goal: GoalSpec,
    result: ExperimentalDecisionResult,
    decision_started_at: datetime,
    planned_tools: Optional[tuple[str, ...]],
    plan_evidence_available: bool,
) -> FrozenDecisionPayload:
    """Construct and freeze the entire persistence payload exactly once."""
    if not isinstance(result, ExperimentalDecisionResult):
        raise ValueError("Decision result has an unsupported type.")
    if plan_evidence_available != (planned_tools is not None):
        raise ValueError("Plan evidence availability does not match the recorded plan.")

    goal_data = serialize_goal_spec(goal)
    decision_status = map_decision_status(result)
    tools = _tool_outcome_rows(result, planned_tools)
    scenarios = _scenario_rows(result)
    feasibility = _json_value(result.intervention_feasibility) or None
    if feasibility is None and isinstance(result.utility_ranking, dict):
        # Preserve serialization of historical callers that predate the
        # separate feasibility assessment field.
        feasibility = _json_value(result.utility_ranking.get("feasibility_status"))
    explanation = _explanation(goal_data, result, decision_status, scenarios)
    payload = {
        "decision_id": result.decision_id,
        "battery_id": result.battery_id,
        "created_at_utc": _utc_timestamp(decision_started_at),
        "goal_spec": goal_data,
        "goal_fields": goal_data,
        "result": _json_value(result),
        "snapshot_metadata": _json_value(result.snapshot_metadata),
        "baseline_result": _json_value(_baseline_result(result)),
        "counterfactual_result": _json_value(_counterfactual_result(result)),
        "utility_ranking": _json_value(result.utility_ranking),
        "feasibility": feasibility,
        "planned_tools": list(planned_tools) if planned_tools is not None else None,
        "plan_evidence_available": plan_evidence_available,
        "executed_tools": [row for row in tools if row["executed"]],
        "tool_outcomes": tools,
        "scenarios": scenarios,
        "final_decision": {
            "selected_action": result.selected_action,
            "model_based_recommendation": _json_value(result.final_recommendation),
            "policy_comparison": _json_value(result.policy_comparison),
        },
        "termination_status": result.termination_status,
        "decision_status": decision_status,
        "explanation": explanation,
        "failure_details": {
            "decision_errors": _json_value(result.errors),
            "tool_errors": [
                row["error_details"]
                for row in tools
                if row["error_details"] is not None
            ],
        },
        "record_version": RECORD_VERSION,
    }
    digest_bytes = canonical_digest_bytes(payload)
    digest = hashlib.sha256(digest_bytes).hexdigest()
    persisted_payload = {**payload, "payload_digest": digest}
    database_json = json.dumps(
        persisted_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return FrozenDecisionPayload(
        decision_id=result.decision_id,
        database_json=database_json,
        canonical_digest_bytes=digest_bytes,
        payload_digest=digest,
    )
