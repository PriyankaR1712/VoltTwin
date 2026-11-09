"""Allowlist metadata for existing planner tools; no tool is reimplemented."""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable, Mapping

from digital_twin.counterfactual_service import (
    assess_registered_baseline,
    simulate_registered_twin,
)
from digital_twin.maintenance_agent import recommend_maintenance
from digital_twin.twin_manager import TwinManager


@dataclass(frozen=True)
class PlannerTool:
    name: str
    purpose: str
    preconditions: str
    expected_output: str
    function: Callable


_TOOLS = {
    "registered_twin_snapshot": PlannerTool(
        name="registered_twin_snapshot",
        purpose="Capture state, histories, provenance, and version atomically.",
        preconditions="A registered TwinManager is available.",
        expected_output="A versioned atomic snapshot dictionary.",
        function=TwinManager.get_snapshot,
    ),
    "baseline_assessment": PlannerTool(
        name="baseline_assessment",
        purpose="Assess the no-maintenance projection from a captured snapshot.",
        preconditions="A valid CNN-provenance snapshot and strict integer horizon.",
        expected_output="One No maintenance scenario and snapshot version.",
        function=assess_registered_baseline,
    ),
    "counterfactual_simulation": PlannerTool(
        name="counterfactual_simulation",
        purpose="Simulate the registered twin's three existing scenarios.",
        preconditions="A valid CNN-provenance snapshot and strict integer horizon.",
        expected_output="No maintenance, Maintenance A, and Maintenance B scenarios.",
        function=simulate_registered_twin,
    ),
    "maintenance_policy": PlannerTool(
        name="maintenance_policy",
        purpose="Apply the existing deterministic maintenance recommendation policy.",
        preconditions="At least one validated scenario result.",
        expected_output="The existing policy recommendation and evidence fields.",
        function=recommend_maintenance,
    ),
}

PLANNER_TOOLS: Mapping[str, PlannerTool] = MappingProxyType(_TOOLS)


def get_planner_tool(name: str) -> PlannerTool:
    try:
        return PLANNER_TOOLS[name]
    except KeyError as exc:
        raise ValueError(f"Tool is not allowed for the planner: {name}") from exc
