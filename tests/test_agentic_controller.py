from digital_twin.agentic_controller import run_agentic_maintenance_loop


def test_controller_selects_best_scenario_below_threshold():
    result = run_agentic_maintenance_loop(
        battery_id="test-battery",
        current_soh=0.75,
        cycle_count=0,
        trend_per_sample=-0.002,
    )

    assert result["selected_scenario"] == "Maintenance B"
    assert result["recommendation"]["status"] == "below_threshold"
    assert result["recommendation"]["projected_soh"] == 0.75
    assert result["selected_action"] == "Battery Health Diagnostics"
    assert result["controller_type"] == "deterministic_rule_based"


def test_controller_returns_all_simulation_scenarios():
    result = run_agentic_maintenance_loop(
        battery_id="test-battery",
        current_soh=0.75,
        cycle_count=0,
        trend_per_sample=-0.002,
    )

    names = [
        scenario["scenario"]
        for scenario in result["simulation_outcomes"]
    ]

    assert names == [
        "No maintenance",
        "Maintenance A",
        "Maintenance B",
    ]
    assert result["maintenance_effects_validated"] is False
import pytest


def test_controller_rejects_invalid_soh():
    with pytest.raises(ValueError):
        run_agentic_maintenance_loop(
            battery_id="test-battery",
            current_soh=1.5,
            cycle_count=0,
            trend_per_sample=-0.002,
        )


def test_controller_rejects_negative_cycle_count():
    with pytest.raises(ValueError):
        run_agentic_maintenance_loop(
            battery_id="test-battery",
            current_soh=0.75,
            cycle_count=-1,
            trend_per_sample=-0.002,
        )
def test_controller_recommendation_matches_selected_scenario():
    result = run_agentic_maintenance_loop(
        battery_id="test-battery",
        current_soh=0.75,
        cycle_count=0,
        trend_per_sample=-0.002,
    )

    outcomes = result["simulation_outcomes"]
    selected_name = result["selected_scenario"]

    selected_outcome = next(
        item for item in outcomes
        if item["scenario"] == selected_name
    )

    assert (
        result["recommendation"]["recommended_scenario"]
        == selected_name
    )
    assert (
        result["recommendation"]["projected_soh"]
        == selected_outcome["projected_soh"]
    )
    assert result["selected_action"] == (
        result["recommendation"]["recommended_action"]
    )