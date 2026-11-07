
import numpy as np
import pytest
import torch

from digital_twin.twin_manager import TwinManager


class FakePredictor:
    """Deterministic CNN replacement for unit testing."""

    def __init__(self, predictions):
        self.predictions = iter(predictions)

    def predict(self, features):
        return torch.tensor(
            [next(self.predictions)],
            dtype=torch.float32,
        )


def create_manager(predictions):
    return TwinManager(
        battery_id="test-battery",
        initial_soh=1.0,
        predictor=FakePredictor(predictions),
    )


def test_manager_processes_first_observation():
    manager = create_manager([0.95])

    result = manager.process_observation(
        np.ones(67),
        observation_index=0,
    )

    assert result["prediction"]["predicted_soh"] == pytest.approx(0.95)
    assert result["twin_state"]["soh"] == pytest.approx(0.95)
    assert result["prediction_count"] == 1
    assert result["degradation"]["status"] == "insufficient_observations"
    assert result["rul"]["status"] == "insufficient_observations"


def test_manager_updates_prediction_history():
    manager = create_manager([0.95, 0.93])

    manager.process_observation(np.ones(67), 0)
    manager.process_observation(np.ones(67), 1)

    assert len(manager.twin.prediction_history) == 2
    assert len(manager.twin.observation_history) == 0
    assert manager.twin.state.soh == pytest.approx(0.93)


def test_manager_estimates_degradation_and_rul():
    manager = create_manager([0.95, 0.93, 0.91])

    for index in range(3):
        result = manager.process_observation(
            np.ones(67),
            observation_index=index,
        )

    assert result["degradation"]["observation_count"] == 3
    assert result["degradation"]["trend_per_sample"] == pytest.approx(-0.02)
    assert result["rul"]["status"] == "estimated"
    assert result["rul"]["rul_observations"] == 6


def test_manager_get_state_returns_latest_state():
    manager = create_manager([0.95, 0.93, 0.91])

    for index in range(3):
        manager.process_observation(np.ones(67), index)

    state = manager.get_state()

    assert state["battery_id"] == "test-battery"
    assert state["twin_state"]["soh"] == pytest.approx(0.91)
    assert state["prediction_count"] == 3
    assert state["state_source"] == "cnn_prediction"


@pytest.mark.parametrize(
    "features",
    [
        np.ones(66),
        np.ones(68),
        np.full(67, np.nan),
        np.full(67, np.inf),
    ],
)
def test_manager_rejects_invalid_features(features):
    manager = create_manager([0.95])

    with pytest.raises(ValueError):
        manager.process_observation(features, 0)

    assert len(manager.twin.prediction_history) == 0


@pytest.mark.parametrize("invalid_index", [-1, 1.5, True])
def test_manager_rejects_invalid_observation_index(invalid_index):
    manager = create_manager([0.95])

    with pytest.raises(ValueError):
        manager.process_observation(
            np.ones(67),
            observation_index=invalid_index,
        )


def test_manager_rejects_duplicate_or_out_of_order_indices():
    manager = create_manager([0.95, 0.93])

    manager.process_observation(np.ones(67), 2)

    with pytest.raises(ValueError):
        manager.process_observation(np.ones(67), 2)

    with pytest.raises(ValueError):
        manager.process_observation(np.ones(67), 1)

    assert len(manager.twin.prediction_history) == 1


def test_manager_rejects_invalid_cnn_prediction():
    manager = create_manager([1.2])

    with pytest.raises(ValueError, match="outside the valid SOH range"):
        manager.process_observation(np.ones(67), 0)

    assert len(manager.twin.prediction_history) == 0
def test_manager_returns_prediction_history():
    manager = create_manager([0.95, 0.93])

    manager.process_observation(np.ones(67), 0)
    manager.process_observation(np.ones(67), 1)

    history = manager.get_history()

    assert history["battery_id"] == "test-battery"
    assert history["observation_count"] == 2
    assert len(history["prediction_history"]) == 2
    assert history["prediction_history"][0]["predicted_soh"] == pytest.approx(0.95)
    assert history["prediction_history"][1]["predicted_soh"] == pytest.approx(0.93)
    assert history["observation_history"] == []