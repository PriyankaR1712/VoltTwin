"""Allowlisted planner tools with strict arguments and safe outcomes."""

import math
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Callable, Mapping

from digital_twin.counterfactual_service import (
    assess_registered_baseline,
    simulate_registered_twin,
)
from digital_twin.maintenance_agent import recommend_maintenance
from digital_twin.goal_spec import validate_diagnostic_evidence
from digital_twin.twin_manager import TwinManager
from digital_twin.decision_models import ToolExecutionOutcome


def _capture_snapshot(twin_registry, battery_id):
    manager = twin_registry.get(battery_id)
    snapshot = manager.get_snapshot()
    if isinstance(snapshot, dict) and snapshot.get("_manager_identity") != id(manager):
        raise ValueError("Captured snapshot manager identity is inconsistent.")
    return snapshot


def _run_baseline(**arguments):
    return assess_registered_baseline(**arguments)


def _run_counterfactual(**arguments):
    return simulate_registered_twin(**arguments)


def _run_policy(**arguments):
    return recommend_maintenance(**arguments)


@dataclass(frozen=True)
class PlannerTool:
    name: str
    purpose: str
    preconditions: str
    expected_output: str
    function: Callable
    required_arguments: frozenset[str]
    allowed_arguments: frozenset[str]


_TOOLS = {
    "registered_twin_snapshot": PlannerTool(
        name="registered_twin_snapshot",
        purpose="Capture state, histories, provenance, and version atomically.",
        preconditions="A registered TwinManager is available.",
        expected_output="A versioned atomic snapshot dictionary.",
        function=_capture_snapshot,
        required_arguments=frozenset({"twin_registry", "battery_id"}),
        allowed_arguments=frozenset({"twin_registry", "battery_id"}),
    ),
    "baseline_assessment": PlannerTool(
        name="baseline_assessment",
        purpose="Assess the no-maintenance projection from a captured snapshot.",
        preconditions="A valid CNN-provenance snapshot and strict integer horizon.",
        expected_output="One No maintenance scenario and snapshot version.",
        function=_run_baseline,
        required_arguments=frozenset({"twin_registry", "battery_id", "additional_cycles", "state_snapshot"}),
        allowed_arguments=frozenset({"twin_registry", "battery_id", "additional_cycles", "state_snapshot"}),
    ),
    "counterfactual_simulation": PlannerTool(
        name="counterfactual_simulation",
        purpose="Simulate the registered twin's three existing scenarios.",
        preconditions="A valid CNN-provenance snapshot and strict integer horizon.",
        expected_output="No maintenance, Maintenance A, and Maintenance B scenarios.",
        function=_run_counterfactual,
        required_arguments=frozenset({"twin_registry", "battery_id", "additional_cycles", "state_snapshot"}),
        allowed_arguments=frozenset({"twin_registry", "battery_id", "additional_cycles", "state_snapshot"}),
    ),
    "maintenance_policy": PlannerTool(
        name="maintenance_policy",
        purpose="Apply the existing deterministic maintenance recommendation policy.",
        preconditions="At least one validated scenario result.",
        expected_output="The existing policy recommendation and evidence fields.",
        function=_run_policy,
        required_arguments=frozenset({"scenario_results"}),
        allowed_arguments=frozenset({"scenario_results", "minimum_acceptable_soh", "current_soh", "trend_per_sample", "diagnostic_evidence"}),
    ),
}

PLANNER_TOOLS: Mapping[str, PlannerTool] = MappingProxyType(_TOOLS)


def get_planner_tool(name: str) -> PlannerTool:
    if not isinstance(name, str):
        raise ValueError("Tool is not allowed for the planner.")
    try:
        return PLANNER_TOOLS[name]
    except KeyError as exc:
        raise ValueError(f"Tool is not allowed for the planner: {name}") from exc


def _safe_arguments(arguments: dict[str, Any]) -> dict[str, Any]:
    """Keep histories and live service objects out of decision records."""
    safe = {}
    for key, value in arguments.items():
        if key in {"twin_registry", "manager"}:
            continue
        if key == "state_snapshot" and isinstance(value, dict):
            safe[key] = {
                "battery_id": value.get("battery_id"),
                "version": value.get("version"),
            }
        elif key == "scenario_results" and isinstance(value, list):
            safe[key] = [row.get("scenario") for row in value if isinstance(row, dict)]
        else:
            safe[key] = value
    return safe


def _argument_error(name: str, arguments: object, tool: PlannerTool) -> str | None:
    if not isinstance(arguments, dict):
        return "Tool arguments must be supplied as a dictionary."
    unexpected = set(arguments) - tool.allowed_arguments
    missing = tool.required_arguments - set(arguments)
    if unexpected:
        return f"Unexpected arguments for {name}: {sorted(unexpected)}."
    if missing:
        return f"Missing required arguments for {name}: {sorted(missing)}."
    if name in {"baseline_assessment", "counterfactual_simulation"}:
        if not isinstance(arguments.get("battery_id"), str) or not arguments["battery_id"].strip():
            return "battery_id must be a non-empty string."
        horizon = arguments.get("additional_cycles")
        if type(horizon) is not int or not 0 <= horizon <= 100000:
            return "additional_cycles must be an integer between 0 and 100000."
        if not isinstance(arguments.get("state_snapshot"), dict):
            return "state_snapshot must be a dictionary."
        snapshot_error = _snapshot_argument_error(
            arguments["state_snapshot"], arguments["battery_id"]
        )
        if snapshot_error:
            return snapshot_error
    if name == "registered_twin_snapshot":
        if not isinstance(arguments.get("battery_id"), str) or not arguments["battery_id"].strip():
            return "battery_id must be a non-empty string."
        if not callable(getattr(arguments.get("twin_registry"), "get", None)):
            return "A registered twin registry is unavailable."
    if name == "maintenance_policy":
        rows = arguments.get("scenario_results")
        if not isinstance(rows, list) or not rows or any(not isinstance(row, dict) for row in rows):
            return "scenario_results must be a non-empty list of dictionaries."
        threshold = arguments.get("minimum_acceptable_soh", 0.80)
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or not math.isfinite(threshold) or not 0.0 < threshold < 1.0:
            return "minimum_acceptable_soh must be a number between 0 and 1."
        current = arguments.get("current_soh")
        if current is not None and (isinstance(current, bool) or not isinstance(current, (int, float)) or not math.isfinite(current) or not 0.0 <= current <= 1.0):
            return "current_soh must be a number between 0 and 1."
        trend = arguments.get("trend_per_sample")
        if trend is not None and (isinstance(trend, bool) or not isinstance(trend, (int, float)) or not math.isfinite(trend)):
            return "trend_per_sample must be a number or null."
        evidence = arguments.get("diagnostic_evidence", {})
        try:
            validate_diagnostic_evidence(evidence)
        except (TypeError, ValueError) as exc:
            return str(exc)
    return None


def _snapshot_argument_error(snapshot: dict[str, Any], battery_id: str) -> str | None:
    """Reject structurally malformed snapshots before availability checks."""
    if snapshot.get("battery_id") != battery_id:
        return "state_snapshot battery identity is inconsistent."
    if type(snapshot.get("version")) is not int or snapshot["version"] < 0:
        return "state_snapshot version must be a non-negative integer."
    manager_identity = snapshot.get("_manager_identity")
    if type(manager_identity) is not int or manager_identity < 1:
        return "state_snapshot manager identity is invalid."
    state = snapshot.get("state")
    history = snapshot.get("history")
    if not isinstance(state, dict) or not isinstance(history, dict):
        return "state_snapshot must include state and history dictionaries."
    if (
        state.get("battery_id") != battery_id
        or history.get("battery_id") != battery_id
        or state.get("state_source") != "cnn_prediction"
        or history.get("state_source") != "cnn_prediction"
    ):
        return "state_snapshot identity or CNN provenance is invalid."
    count = state.get("prediction_count")
    if type(count) is not int or count < 0:
        return "state_snapshot prediction_count must be a non-negative integer."
    predictions = history.get("prediction_history")
    if not isinstance(predictions, list) or len(predictions) != count:
        return "state_snapshot prediction history does not match prediction_count."
    return None


def _available(name: str, arguments: dict[str, Any]) -> str | None:
    if name == "registered_twin_snapshot":
        try:
            arguments["twin_registry"].get(arguments["battery_id"])
        except Exception:
            return "No registered twin is available for this battery."
    if name in {"baseline_assessment", "counterfactual_simulation"}:
        registry = arguments["twin_registry"]
        snapshot = arguments["state_snapshot"]
        try:
            manager = registry.get(arguments["battery_id"])
        except Exception:
            return "No registered twin is available for this battery."
        if snapshot.get("_manager_identity") != id(manager):
            return "The captured snapshot is not available for this registered twin."
        if snapshot.get("battery_id") != arguments["battery_id"]:
            return "The captured snapshot belongs to a different battery."
        state = snapshot.get("state")
        history = snapshot.get("history")
        if (
            not isinstance(state, dict)
            or not isinstance(history, dict)
            or state.get("state_source") != "cnn_prediction"
            or history.get("state_source") != "cnn_prediction"
        ):
            return "A complete CNN-provenance snapshot is required."
        if state["prediction_count"] == 0:
            return "A CNN prediction is required before assessment."
    return None


def execute_planner_tool(name: str, arguments: dict[str, Any], execution_order: int) -> ToolExecutionOutcome:
    """Validate and execute one allowlisted tool, returning no stack traces."""
    base_name = name if isinstance(name, str) and name else "<invalid>"
    if type(execution_order) is not int or execution_order < 1:
        execution_order = 1
    try:
        tool = get_planner_tool(name)
    except ValueError:
        return ToolExecutionOutcome(base_name, "unknown_tool", execution_order, error={"code": "unknown_tool", "message": "Tool is not allowed for the planner."})
    try:
        argument_error = _argument_error(name, arguments, tool)
    except Exception:
        argument_error = "Tool arguments are malformed."
    if argument_error:
        return ToolExecutionOutcome(name, "invalid_arguments", execution_order, error={"code": "invalid_arguments", "message": argument_error})
    try:
        availability_error = _available(name, arguments)
    except Exception:
        return ToolExecutionOutcome(
            name,
            "invalid_arguments",
            execution_order,
            validated_arguments=_safe_arguments(arguments),
            error={"code": "invalid_arguments", "message": "Tool arguments are malformed."},
        )
    if availability_error:
        return ToolExecutionOutcome(name, "unavailable", execution_order, validated_arguments=_safe_arguments(arguments), error={"code": "tool_unavailable", "message": availability_error})
    try:
        result = tool.function(**arguments)
    except Exception:
        return ToolExecutionOutcome(name, "execution_failure", execution_order, validated_arguments=_safe_arguments(arguments), error={"code": "tool_execution_failed", "message": "Tool execution failed."})
    return ToolExecutionOutcome(name, "success", execution_order, validated_arguments=_safe_arguments(arguments), result=result)
