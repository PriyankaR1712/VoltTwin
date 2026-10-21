
from unittest.mock import patch

from backend.main import (
    SequentialReplayInput,
    adaptive_maintenance,
)


def test_adaptive_maintenance_connects_replay_trend_and_scenarios():
    fake_replay = {
        "battery_id": "XJTU-Battery-1",
        "sheet_name": "Sheet1",
        "observation_count": 4,
        "mae": 0.01,
        "mae_percentage_points": 1.0,
        "rmse": 0.012,
        "rmse_percentage_points": 1.2,
        "observations": [
            {"actual_soh": 0.83},
            {"actual_soh": 0.82},
            {"actual_soh": 0.81},
            {"actual_soh": 0.79},
        ],
        "final_twin_state": {
            "battery_id": "XJTU-Battery-1",
            "soh": 0.79,
            "soh_percent": 79.0,
            "cycle_count": 0,
        },
        "evaluation_type": "sequential_observation_replay",
        "observation_order_is_verified_physical_cycle_order": False,
    }

    with patch("backend.main.replay_battery", return_value=fake_replay):
        result = adaptive_maintenance(
            SequentialReplayInput(
                sheet_name="Sheet1",
                battery_id="XJTU-Battery-1",
            )
        )

    assert result["battery"]["soh"] == 0.79
    assert result["degradation_trend"]["latest_observed_soh"] == 0.79
    assert len(result["scenarios"]) == 3
    assert result["recommendation"]["recommended_scenario"] == "Maintenance B"
    assert result["recommendation"]["status"] == "below_threshold"
    assert result["recommendation"]["is_rule_based"] is True
