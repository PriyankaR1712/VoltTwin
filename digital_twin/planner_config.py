"""Versioned constants for the experimental goal-directed planner."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PlannerConfig:
    """Configuration values that affect planner validation and scoring."""

    config_version: str = "goal_planner_v1"
    scenario_soh_rounding_tolerance: float = 0.0001
    baseline_delta_consistency_tolerance: float = 0.0001
    recovery_assumption_tolerance: float = 0.000000001
    expected_recovery_assumptions: tuple[float, float, float] = (
        0.0,
        0.005,
        0.01,
    )
    maximum_planning_iterations: int = 3
    maximum_service_tool_invocations: int = 3
    maximum_counterfactual_invocations: int = 1
    expected_scenario_count: int = 3
    utility_formula_version: str = "baseline_relative_v1"


DEFAULT_PLANNER_CONFIG = PlannerConfig()
