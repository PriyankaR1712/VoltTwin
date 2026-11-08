from typing import Optional
import math

from digital_twin.battery_twin import BatteryState, BatteryTwin
from digital_twin.counterfactual import (
    MaintenanceScenario,
    compare_scenarios,
)
from digital_twin.degradation_estimator import DegradationEstimator
from digital_twin.rul_estimator import RULEstimator
from digital_twin.maintenance_agent import recommend_maintenance
from digital_twin.historical_degradation import analyze_soh_history

def _validate_inputs(
    battery_id: str,
    current_soh: float,
    cycle_count: int,
    minimum_acceptable_soh: float,
    observed_soh_history: Optional[list] = None,
    diagnostic_evidence: Optional[dict] = None,
) -> None:
    """Validate inputs before the agent starts planning."""

    if not isinstance(battery_id, str) or not battery_id.strip():
        raise ValueError("Battery ID cannot be empty.")

    if (
        isinstance(current_soh, bool)
        or not isinstance(current_soh, (int, float))
        or not math.isfinite(current_soh)
        or not 0.0 <= current_soh <= 1.0
    ):
        raise ValueError("Current SOH must be between 0 and 1.")

    if (
        isinstance(cycle_count, bool)
        or not isinstance(cycle_count, int)
        or cycle_count < 0
    ):
        raise ValueError("Cycle count must be a non-negative integer.")

    if (
        isinstance(minimum_acceptable_soh, bool)
        or not isinstance(minimum_acceptable_soh, (int, float))
        or not math.isfinite(minimum_acceptable_soh)
        or not 0.0 < minimum_acceptable_soh < 1.0
    ):
        raise ValueError(
            "Minimum acceptable SOH must be between 0 and 1."
        )

    if observed_soh_history is not None:
        if not isinstance(observed_soh_history, list):
            raise ValueError("SOH history must be a list.")

        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or not 0.0 <= value <= 1.0
            for value in observed_soh_history
        ):
            raise ValueError("SOH history must contain valid SOH values.")

    if diagnostic_evidence is not None and not isinstance(
        diagnostic_evidence, dict
    ):
        raise ValueError("Diagnostic evidence must be a dictionary.")

def _build_analysis_plan(
    current_soh: float,
    minimum_acceptable_soh: float,
    observed_soh_history: Optional[list] = None,
    diagnostic_evidence: Optional[dict] = None,
) -> list:
    """
    Dynamically select analysis tools based on battery condition
    and available evidence.
    """

    evidence = diagnostic_evidence or {}
    plan = ["battery_state_observation"]

    # Historical analysis requires at least 3 observations.
    if observed_soh_history and len(observed_soh_history) >= 3:
        plan.append("historical_degradation_analysis")
        plan.append("degradation_trend_estimation")
        plan.append("rul_estimation")

    # Check whether the battery needs deeper investigation.
    low_soh = current_soh < minimum_acceptable_soh

    fault_evidence = any([
        evidence.get("thermal_alert", False),
        bool(evidence.get("bms_fault_codes", [])),
        evidence.get("cell_voltage_imbalance", False),
        evidence.get("charging_anomaly", False),
        evidence.get("confirmed_fault", False),
    ])

    declining_trend = False

    if observed_soh_history and len(observed_soh_history) >= 3:
        trend = DegradationEstimator().estimate(
            observed_soh_history
        )
        declining_trend = trend["trend_per_sample"] < 0

    if low_soh or fault_evidence or declining_trend:
        plan.append("counterfactual_simulation")
    else:
        plan.append("baseline_battery_assessment")

    plan.append("maintenance_recommendation")

    return plan

def _execute_analysis_plan(
    plan: list,
    battery_id: str,
    current_soh: float,
    cycle_count: int,
    minimum_acceptable_soh: float,
    observed_soh_history: Optional[list] = None,
    diagnostic_evidence: Optional[dict] = None,
    additional_cycles: int = 100,
) -> dict:
    """Execute only the analysis tools selected by the agent."""

    results = {
        "executed_tools": [],
        "tool_results": {},
    }

    history = observed_soh_history or []
    evidence = diagnostic_evidence or {}

    # Tool 1: Observe the current battery state.
    if "battery_state_observation" in plan:
        twin = BatteryTwin(
            state=BatteryState(
                battery_id=battery_id,
                soh=current_soh,
                cycle_count=cycle_count,
            )
        )

        results["tool_results"]["battery_state"] = twin.get_state()
        results["executed_tools"].append(
            "battery_state_observation"
        )

    # Tool 2: Analyze historical degradation.
    if "historical_degradation_analysis" in plan:
        historical_result = analyze_soh_history(
            [value * 2.0 for value in history]
        )

        results["tool_results"]["historical_degradation"] = (
            historical_result
        )
        results["executed_tools"].append(
            "historical_degradation_analysis"
        )

    # Tool 3: Estimate the recent degradation trend.
    if "degradation_trend_estimation" in plan:
        trend_result = DegradationEstimator().estimate(history)

        results["tool_results"]["degradation_trend"] = trend_result
        results["executed_tools"].append(
            "degradation_trend_estimation"
        )

    # Tool 4: Estimate remaining useful life.
    if "rul_estimation" in plan:
        rul_result = RULEstimator(
            eol_threshold=minimum_acceptable_soh
        ).estimate(history)

        results["tool_results"]["rul_estimate"] = rul_result
        results["executed_tools"].append("rul_estimation")

    # Tool 5: Run counterfactual maintenance simulations.
    if "counterfactual_simulation" in plan:
        twin = BatteryTwin(
            state=BatteryState(
                battery_id=battery_id,
                soh=current_soh,
                cycle_count=cycle_count,
            )
        )

        scenarios = [
            MaintenanceScenario(
                name="No maintenance",
                additional_cycles=additional_cycles,
                recovery_assumption=0.0,
            ),
            MaintenanceScenario(
                name="Maintenance A",
                additional_cycles=additional_cycles,
                recovery_assumption=0.005,
            ),
            MaintenanceScenario(
                name="Maintenance B",
                additional_cycles=additional_cycles,
                recovery_assumption=0.01,
            ),
        ]

        scenario_results = compare_scenarios(twin, scenarios)

        results["tool_results"]["scenario_results"] = (
            scenario_results
        )
        results["executed_tools"].append(
            "counterfactual_simulation"
        )

    # Tool 6: Run a baseline assessment when deeper simulation
    # is not required.
    if "baseline_battery_assessment" in plan:
        twin = BatteryTwin(
            state=BatteryState(
                battery_id=battery_id,
                soh=current_soh,
                cycle_count=cycle_count,
            )
        )

        baseline = twin.simulate(additional_cycles)

        scenario_results = [
            {
                "scenario": "No maintenance",
                "projected_soh": baseline["projected_soh"],
            }
        ]

        results["tool_results"]["scenario_results"] = (
            scenario_results
        )
        results["executed_tools"].append(
            "baseline_battery_assessment"
        )

    # Tool 7: Generate the maintenance recommendation.
    if "maintenance_recommendation" in plan:
        trend_result = results["tool_results"].get(
            "degradation_trend", {}
        )

        recommendation = recommend_maintenance(
            scenario_results=results["tool_results"][
                "scenario_results"
            ],
            minimum_acceptable_soh=minimum_acceptable_soh,
            current_soh=current_soh,
            trend_per_sample=trend_result.get(
                "trend_per_sample"
            ),
            diagnostic_evidence=evidence,
        )

        results["tool_results"]["recommendation"] = recommendation
        results["executed_tools"].append(
            "maintenance_recommendation"
        )

    return results

def run_agent_orchestrator(
    battery_id: str,
    current_soh: float,
    cycle_count: int,
    minimum_acceptable_soh: float = 0.80,
    observed_soh_history: Optional[list] = None,
    diagnostic_evidence: Optional[dict] = None,
    additional_cycles: int = 100,
) -> dict:
    """
    Run the complete tool-using agent workflow.

    The agent validates inputs, dynamically selects analysis tools,
    executes the selected tools, and produces a maintenance decision.
    """

    # Step 1: Validate inputs.
    _validate_inputs(
        battery_id=battery_id,
        current_soh=current_soh,
        cycle_count=cycle_count,
        minimum_acceptable_soh=minimum_acceptable_soh,
        observed_soh_history=observed_soh_history,
        diagnostic_evidence=diagnostic_evidence,
    )

    # Step 2: Create the analysis plan.
    plan = _build_analysis_plan(
        current_soh=current_soh,
        minimum_acceptable_soh=minimum_acceptable_soh,
        observed_soh_history=observed_soh_history,
        diagnostic_evidence=diagnostic_evidence,
    )

    # Step 3: Execute the selected tools.
    execution = _execute_analysis_plan(
        plan=plan,
        battery_id=battery_id,
        current_soh=current_soh,
        cycle_count=cycle_count,
        minimum_acceptable_soh=minimum_acceptable_soh,
        observed_soh_history=observed_soh_history,
        diagnostic_evidence=diagnostic_evidence,
        additional_cycles=additional_cycles,
    )

    # Step 4: Return the agent's complete decision trace.
    return {
        "battery_id": battery_id,
        "agent_type": "adaptive_tool_using_agent",
        "planning_method": "condition_based_tool_selection",
        "analysis_plan": plan,
        "executed_tools": execution["executed_tools"],
        "tool_results": execution["tool_results"],
        "recommended_action": execution["tool_results"][
            "recommendation"
        ]["recommended_action"],
        "recommended_scenario": execution["tool_results"][
            "recommendation"
        ]["recommended_scenario"],
        "decision_status": execution["tool_results"][
            "recommendation"
        ]["status"],
        "is_agentic_workflow": True,
        "is_llm_based": False,
    }