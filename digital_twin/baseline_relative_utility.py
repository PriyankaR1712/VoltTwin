"""Baseline-relative utility for validated counterfactual scenarios."""

from dataclasses import dataclass
from typing import Mapping, Optional

from digital_twin.goal_spec import GoalSpec
from digital_twin.planner_config import DEFAULT_PLANNER_CONFIG, PlannerConfig
from digital_twin.scenario_validation import ValidatedScenarioSet


@dataclass(frozen=True)
class UtilityRanking:
    formula_version: str
    utilities: Mapping[str, float]
    ranked_groups: tuple[tuple[str, ...], ...]
    target_attainment: Mapping[str, Optional[bool]]


def calculate_baseline_relative_utility(
    scenarios: ValidatedScenarioSet,
    goal: GoalSpec,
    config: PlannerConfig = DEFAULT_PLANNER_CONFIG,
) -> UtilityRanking:
    """Score Maintenance A/B only; target attainment remains a separate field."""
    baseline_soh = float(scenarios.baseline["projected_soh"])
    utilities = {
        name: 100.0 * (float(row["projected_soh"]) - baseline_soh)
        for name, row in scenarios.interventions.items()
    }
    ordered = sorted(utilities, key=lambda name: utilities[name], reverse=True)
    groups: list[list[str]] = []
    for name in ordered:
        if not groups or utilities[name] != utilities[groups[-1][0]]:
            groups.append([name])
        else:
            groups[-1].append(name)
    target_attainment = {
        name: goal.target_attainment(float(row["projected_soh"]))
        for name, row in scenarios.scenarios.items()
    }
    return UtilityRanking(
        formula_version=config.utility_formula_version,
        utilities=utilities,
        ranked_groups=tuple(tuple(group) for group in groups),
        target_attainment=target_attainment,
    )
