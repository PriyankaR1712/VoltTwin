"""Agent orchestration over the registered, CNN-driven Digital Twin."""

import math

from backend.twin_registry import twin_registry as shared_twin_registry
from digital_twin.counterfactual_service import simulate_registered_twin
from digital_twin.maintenance_agent import recommend_maintenance


def _validate_additional_cycles(value: object) -> int:
    """Validate the supported simulation horizon without coercion."""
    if type(value) is not int or not 0 <= value <= 100000:
        raise ValueError(
            "Additional cycles must be an integer between 0 and 100000."
        )
    return value


def run_agent_orchestrator(
    battery_id: str,
    additional_cycles: int = 100,
    minimum_acceptable_soh: float = 0.80,
    diagnostic_evidence: dict | None = None,
    twin_registry=None,
) -> dict:
    """Analyze the registered twin using its current CNN prediction state."""
    _validate_additional_cycles(additional_cycles)

    if not isinstance(battery_id, str) or not battery_id.strip():
        raise ValueError("Battery ID cannot be empty.")
    if (
        isinstance(minimum_acceptable_soh, bool)
        or not isinstance(minimum_acceptable_soh, (int, float))
        or not math.isfinite(minimum_acceptable_soh)
        or not 0.0 < minimum_acceptable_soh < 1.0
    ):
        raise ValueError("Minimum acceptable SOH must be between 0 and 1.")
    if diagnostic_evidence is not None and not isinstance(
        diagnostic_evidence, dict
    ):
        raise ValueError("Diagnostic evidence must be a dictionary.")

    registry = (
        shared_twin_registry if twin_registry is None else twin_registry
    )
    manager = registry.get(battery_id)
    state = manager.get_state()
    history = manager.get_history()

    prediction_count = state.get("prediction_count")
    if (
        not isinstance(prediction_count, int)
        or isinstance(prediction_count, bool)
        or prediction_count < 1
    ):
        raise ValueError(
            f"Battery '{battery_id}' has no CNN prediction yet. "
            "Process an observation before running the agent."
        )
    if state.get("state_source") != "cnn_prediction":
        raise ValueError("Registered battery state is not CNN-prediction sourced.")

    prediction_history = history.get("prediction_history")
    if not isinstance(prediction_history, list) or not prediction_history:
        raise ValueError(
            "Registered battery has no CNN prediction history available."
        )
    if history.get("state_source") != "cnn_prediction":
        raise ValueError(
            "Registered battery history is not CNN-prediction sourced."
        )
    if len(prediction_history) != prediction_count:
        raise ValueError(
            "Registered battery prediction history does not match its state count."
        )

    twin_state = state.get("twin_state")
    if (
        not isinstance(twin_state, dict)
        or twin_state.get("battery_id") != battery_id
        or state.get("battery_id") != battery_id
    ):
        raise ValueError("Registered battery state is missing or inconsistent.")

    current_soh = twin_state.get("soh")
    if (
        isinstance(current_soh, bool)
        or not isinstance(current_soh, (int, float))
        or not math.isfinite(current_soh)
        or not 0.0 <= current_soh <= 1.0
    ):
        raise ValueError("Registered battery state has an invalid SOH value.")

    # Prediction history remains explicitly distinct from measured observations.
    # Reuse TwinManager results; unavailable values are surfaced as unavailable.
    manager_degradation = state.get("degradation")
    manager_rul = state.get("rul")
    degradation = manager_degradation
    if degradation is None:
        degradation = {
            "status": "unavailable",
            "reason": "TwinManager has not produced a degradation estimate.",
        }
    rul = manager_rul
    if rul is None:
        rul = {
            "status": "unavailable",
            "rul_observations": None,
            "unit": state.get("rul_unit", "observations"),
            "is_physically_validated": False,
            "reason": "TwinManager has not produced an RUL estimate.",
        }

    trend_per_sample = (
        manager_degradation.get("trend_per_sample")
        if isinstance(manager_degradation, dict)
        else None
    )
    declining = (
        isinstance(trend_per_sample, (int, float))
        and not isinstance(trend_per_sample, bool)
        and math.isfinite(trend_per_sample)
        and trend_per_sample < 0
    )
    evidence = diagnostic_evidence or {}
    fault_evidence = any(
        (
            evidence.get("thermal_alert", False),
            bool(evidence.get("bms_fault_codes", [])),
            evidence.get("cell_voltage_imbalance", False),
            evidence.get("charging_anomaly", False),
            evidence.get("confirmed_fault", False),
        )
    )
    needs_counterfactual = (
        current_soh < minimum_acceptable_soh or declining or fault_evidence
    )

    # Delegate all scenario execution to the shared registered-twin service.
    simulation = simulate_registered_twin(
        twin_registry=registry,
        battery_id=battery_id,
        additional_cycles=additional_cycles,
    )
    if simulation.get("state_source") != "cnn_prediction":
        raise ValueError("Counterfactual result lost CNN prediction provenance.")

    if needs_counterfactual:
        plan_tool = "counterfactual_simulation"
        scenario_results = simulation["scenarios"]
    else:
        plan_tool = "baseline_battery_assessment"
        scenario_results = [
            item
            for item in simulation["scenarios"]
            if item["scenario"] == "No maintenance"
        ]
        if not scenario_results:
            raise ValueError(
                "Counterfactual service returned no baseline scenario."
            )

    recommendation = recommend_maintenance(
        scenario_results=scenario_results,
        minimum_acceptable_soh=minimum_acceptable_soh,
        current_soh=current_soh,
        trend_per_sample=trend_per_sample,
        diagnostic_evidence=evidence,
    )

    observation_index = state.get("last_observation_index")
    analysis_plan = [
        "battery_state_observation",
        "prediction_history_context",
    ]
    executed_tools = list(analysis_plan)
    if isinstance(manager_degradation, dict):
        analysis_plan.append("degradation_result_reuse")
        executed_tools.append("degradation_result_reuse")
    if isinstance(manager_rul, dict):
        analysis_plan.append("rul_result_reuse")
        executed_tools.append("rul_result_reuse")
    analysis_plan.extend([plan_tool, "maintenance_recommendation"])
    executed_tools.extend([plan_tool, "maintenance_recommendation"])

    tool_results = {
        "battery_state": twin_state,
        "state_source": simulation["state_source"],
        "observation_index": observation_index,
        "prediction_count": prediction_count,
        "prediction_history": prediction_history,
        "history_state_source": history["state_source"],
        "degradation": degradation,
        "rul_estimate": rul,
        "scenario_results": scenario_results,
        "recommendation": recommendation,
    }

    return {
        "battery_id": battery_id,
        "agent_type": "adaptive_tool_using_agent",
        "planning_method": "condition_based_tool_selection",
        "analysis_plan": analysis_plan,
        "executed_tools": executed_tools,
        "tool_results": tool_results,
        "recommended_action": recommendation["recommended_action"],
        "recommended_scenario": recommendation["recommended_scenario"],
        "decision_status": recommendation["status"],
        "state_source": simulation["state_source"],
        "observation_index": observation_index,
        "prediction_count": prediction_count,
        "is_agentic_workflow": True,
        "is_llm_based": False,
    }
