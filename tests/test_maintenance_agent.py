
import pytest

from digital_twin.maintenance_agent import recommend_maintenance


@pytest.fixture
def scenarios():
    return [
        {"scenario": "No maintenance", "projected_soh": 0.85},
        {"scenario": "Maintenance A", "projected_soh": 0.86},
        {"scenario": "Maintenance B", "projected_soh": 0.87},
    ]


def test_stable_battery_prefers_baseline(scenarios):
    result = recommend_maintenance(
        scenarios,
        current_soh=0.90,
        trend_per_sample=-0.0001,
    )

    assert result["recommended_scenario"] == "No maintenance"
    assert result["status"] == "acceptable_under_assumptions"


def test_declining_battery_prefers_maintenance(scenarios):
    result = recommend_maintenance(
        scenarios,
        current_soh=0.90,
        trend_per_sample=-0.002,
    )

    assert result["recommended_scenario"] == "Maintenance B"
    assert result["status"] == "maintenance_preferred_by_condition"


def test_below_threshold_battery_prefers_maintenance(scenarios):
    result = recommend_maintenance(
        scenarios,
        minimum_acceptable_soh=0.80,
        current_soh=0.75,
        trend_per_sample=-0.0005,
    )

    assert result["recommended_scenario"] == "Maintenance B"
    assert result["status"] == "maintenance_preferred_by_condition"


def test_no_scenario_meets_threshold():
    results = [
        {"scenario": "No maintenance", "projected_soh": 0.70},
        {"scenario": "Maintenance A", "projected_soh": 0.74},
    ]

    result = recommend_maintenance(
        results,
        minimum_acceptable_soh=0.80,
        current_soh=0.75,
        trend_per_sample=-0.002,
    )

    assert result["recommended_scenario"] == "Maintenance A"
    assert result["status"] == "below_threshold"


def test_invalid_current_soh_is_rejected(scenarios):
    with pytest.raises(ValueError):
        recommend_maintenance(scenarios, current_soh=1.2)


def test_invalid_trend_is_rejected(scenarios):
    with pytest.raises(ValueError):
        recommend_maintenance(scenarios, trend_per_sample=float("nan"))
