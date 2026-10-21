
import numpy as np
import pandas as pd
import pytest

from digital_twin.sequential_replay import replay_battery


def test_replay_evaluates_predictions_and_updates_twin(tmp_path, monkeypatch):
    workbook = tmp_path / "battery.xlsx"

    # Three observations with 67 features and capacity labels.
    data = {
        f"feature_{i}": [float(i), float(i + 1), float(i + 2)]
        for i in range(67)
    }
    data["label"] = [1.9, 1.8, 1.7]

    frame = pd.DataFrame(data)
    frame.to_excel(workbook, sheet_name="Battery1", index=False)

    class FakePredictor:
        def __init__(self, checkpoint_path=None):
            pass

        def predict(self, features):
            import torch
            return torch.tensor([0.94, 0.89, 0.84])

    monkeypatch.setattr(
        "digital_twin.sequential_replay.SOHPredictor",
        FakePredictor,
    )

    result = replay_battery(
        workbook_path=workbook,
        sheet_name="Battery1",
        battery_id="test-battery",
    )

    assert result["observation_count"] == 3
    assert result["mae"] == pytest.approx(
        np.mean([0.01, 0.01, 0.01])
    )
    assert result["final_twin_state"]["soh"] == pytest.approx(0.85)
    assert [
        item["observation_index"] for item in result["observations"]
    ] == [0, 1, 2]
    assert result["observation_order_is_verified_physical_cycle_order"] is False


def test_replay_rejects_wrong_feature_count(tmp_path):
    workbook = tmp_path / "wrong_features.xlsx"

    data = {
        f"feature_{i}": [0.5, 0.6, 0.7]
        for i in range(66)
    }
    data["label"] = [1.9, 1.8, 1.7]

    pd.DataFrame(data).to_excel(
        workbook,
        sheet_name="Battery1",
        index=False,
    )

    with pytest.raises(ValueError, match="Expected 67 feature columns"):
        replay_battery(
            workbook_path=workbook,
            sheet_name="Battery1",
            battery_id="test-battery",
        )
