
from unittest.mock import patch

from backend.main import (
    AdaptiveMaintenanceInput,
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
            AdaptiveMaintenanceInput(
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

def test_adaptive_maintenance_returns_controller_results():
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

    with patch(
        "backend.main.replay_battery",
        return_value=fake_replay,
    ):
        result = adaptive_maintenance(
            AdaptiveMaintenanceInput(
                sheet_name="Sheet1",
                battery_id="XJTU-Battery-1",
            )
        )

    assert result["controller_type"] == "deterministic_rule_based"
    assert result["maintenance_effects_validated"] is False
    assert result["selected_scenario"] == result["recommendation"][
        "recommended_scenario"
    ]
    assert result["selected_action"] == result["recommendation"][
        "recommended_action"
    ]
    assert len(result["interventions"]) == 3
    assert len(result["scenarios"]) == 3
