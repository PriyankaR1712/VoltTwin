
import pytest

from digital_twin.agent_orchestrator import run_agent_orchestrator


def test_agent_builds_plan_for_declining_battery():
    result = run_agent_orchestrator(
        battery_id="Test-Battery-1",
        current_soh=0.79,
        cycle_count=0,
        observed_soh_history=[0.83, 0.82, 0.81, 0.79],
    )

    assert result["is_agentic_workflow"] is True
    assert result["analysis_plan"] == [
        "battery_state_observation",
        "historical_degradation_analysis",
        "degradation_trend_estimation",
        "rul_estimation",
        "counterfactual_simulation",
        "maintenance_recommendation",
    ]

    assert result["executed_tools"] == result["analysis_plan"]
    assert result["recommended_action"] == "Battery Health Diagnostics"
    assert result["decision_status"] == "below_threshold"


def test_agent_skips_counterfactual_for_stable_battery():
    result = run_agent_orchestrator(
        battery_id="Stable-Battery",
        current_soh=0.95,
        cycle_count=0,
        observed_soh_history=[0.94, 0.945, 0.95, 0.95],
    )

    assert "baseline_battery_assessment" in result["analysis_plan"]
    assert "counterfactual_simulation" not in result["analysis_plan"]
    assert "maintenance_recommendation" in result["analysis_plan"]


def test_agent_rejects_invalid_soh():
    with pytest.raises(ValueError):
        run_agent_orchestrator(
            battery_id="Test-Battery",
            current_soh=1.5,
            cycle_count=0,
        )


def test_agent_rejects_empty_battery_id():
    with pytest.raises(ValueError):
        run_agent_orchestrator(
            battery_id="",
            current_soh=0.90,
            cycle_count=0,
        )
