import math
"""Orchestrate the VoltTwin agent–Digital Twin decision loop."""

from digital_twin.battery_twin import (
    BatteryState,
    BatteryTwin,
    SimulationAssumptions,
)
from digital_twin.counterfactual import (
    MaintenanceScenario,
    compare_scenarios,
)
from digital_twin.maintenance_agent import recommend_maintenance


def run_agentic_maintenance_loop(
    battery_id: str,
    current_soh: float,
    cycle_count: int,
    trend_per_sample: float,
    additional_cycles: int = 100,
    minimum_acceptable_soh: float = 0.80,
    diagnostic_evidence: dict | None = None,
) -> dict:
    """Observe state, propose interventions, simulate, and select an action.

    Scenario recovery values are illustrative assumptions, not validated
    maintenance effects. This is a deterministic, rule-based controller.
    """
    if not isinstance(battery_id, str) or not battery_id.strip():
        raise ValueError("Battery ID cannot be empty.")

    if (
        isinstance(current_soh, bool)
        or not isinstance(current_soh, (int, float))
        or not math.isfinite(current_soh)
        or not 0.0 <= current_soh <= 1.0
    ):
        raise ValueError("Current SOH must be finite and between 0 and 1.")

    if (
        not isinstance(cycle_count, int)
        or isinstance(cycle_count, bool)
        or cycle_count < 0
    ):
        raise ValueError("Cycle count must be a non-negative integer.")

    if (
        isinstance(trend_per_sample, bool)
        or not isinstance(trend_per_sample, (int, float))
        or not math.isfinite(trend_per_sample)
    ):
        raise ValueError("Trend must be a finite number.")

    if (
        not isinstance(additional_cycles, int)
        or isinstance(additional_cycles, bool)
        or additional_cycles < 0
    ):
        raise ValueError("Additional cycles must be a non-negative integer.")

    if (
        isinstance(minimum_acceptable_soh, bool)
        or not isinstance(minimum_acceptable_soh, (int, float))
        or not math.isfinite(minimum_acceptable_soh)
        or not 0.0 <= minimum_acceptable_soh <= 1.0
    ):
        raise ValueError(
            "Minimum acceptable SOH must be finite and between 0 and 1."
        )

    if diagnostic_evidence is not None and not isinstance(
        diagnostic_evidence, dict
    ):
        raise ValueError("Diagnostic evidence must be a dictionary.")

    # 1. Observe the estimated battery state.
    twin = BatteryTwin(
        state=BatteryState(
            battery_id=battery_id,
            soh=current_soh,
            cycle_count=cycle_count,
        ),
        assumptions=SimulationAssumptions(
            degradation_per_cycle=0.0001,
        ),
    )
    observed_state = twin.get_state()

    # 2. Generate candidate interventions for what-if evaluation.
    interventions = [
        {
            "name": "No maintenance",
            "recovery_assumption": 0.0,
            "description": "Continue operation without a simulated intervention.",
        },
        {
            "name": "Maintenance A",
            "recovery_assumption": 0.005,
            "description": "Evaluate a hypothetical maintenance intervention A.",
        },
        {
            "name": "Maintenance B",
            "recovery_assumption": 0.01,
            "description": "Evaluate a hypothetical maintenance intervention B.",
        },
    ]

    # 3. Pass each candidate through the Digital Twin simulator.
    scenarios = [
        MaintenanceScenario(
            name=item["name"],
            additional_cycles=additional_cycles,
            recovery_assumption=item["recovery_assumption"],
        )
        for item in interventions
    ]
    outcomes = compare_scenarios(twin, scenarios)

    # 4. Return simulated outcomes to the decision policy.
    recommendation = recommend_maintenance(
        scenario_results=outcomes,
        minimum_acceptable_soh=minimum_acceptable_soh,
        current_soh=current_soh,
        trend_per_sample=trend_per_sample,
        diagnostic_evidence=diagnostic_evidence or {},
    )

    # 5. Return the decision and an auditable record of the loop.
    return {
        "observed_battery_state": observed_state,
        "intervention_proposals": interventions,
        "simulation_outcomes": outcomes,
        "selected_scenario": recommendation["recommended_scenario"],
        "selected_action": recommendation["recommended_action"],
        "recommendation": recommendation,
        "controller_type": "deterministic_rule_based",
        "is_simulation_based": True,
        "maintenance_effects_validated": False,
        "notice": (
            "Interventions are candidate scenarios. Recovery values are "
            "illustrative assumptions, not validated maintenance effects. "
            "The selected action is a rule-based recommendation requiring "
            "appropriate evidence and qualified assessment."
        ),
    }

