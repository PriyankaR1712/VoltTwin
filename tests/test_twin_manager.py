
from threading import Event, Thread

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


def test_snapshot_version_tracks_successful_observations():
    manager = create_manager([0.95, 0.93])

    assert manager.get_snapshot()["version"] == 0
    manager.process_observation(np.ones(67), observation_index=0)
    assert manager.get_snapshot()["version"] == 1
    manager.process_observation(np.ones(67), observation_index=1)
    snapshot = manager.get_snapshot()

    assert snapshot["version"] == 2
    assert snapshot["state"]["prediction_count"] == 2
    assert snapshot["state"]["last_observation_index"] == 1
    assert len(snapshot["history"]["prediction_history"]) == 2


def test_snapshot_and_history_are_deep_copy_isolated():
    manager = create_manager([0.95])
    manager.process_observation(np.ones(67), observation_index=0)

    snapshot = manager.get_snapshot()
    snapshot["state"]["twin_state"]["soh"] = 0.1
    snapshot["history"]["prediction_history"][0]["predicted_soh"] = 0.1
    snapshot["simulation_assumptions"]["degradation_per_cycle"] = 0.9

    history = manager.get_history()
    history["prediction_history"][0]["predicted_soh"] = 0.2

    fresh = manager.get_snapshot()
    assert fresh["state"]["twin_state"]["soh"] == pytest.approx(0.95)
    assert fresh["history"]["prediction_history"][0]["predicted_soh"] == pytest.approx(0.95)
    assert fresh["simulation_assumptions"]["degradation_per_cycle"] == pytest.approx(0.0001)


def test_concurrent_duplicate_observation_is_applied_once():
    manager = create_manager([0.95])
    start = Event()
    outcomes = []

    def submit_observation():
        start.wait()
        try:
            outcomes.append(manager.process_observation(np.ones(67), observation_index=0))
        except ValueError as exc:
            outcomes.append(exc)

    workers = [Thread(target=submit_observation) for _ in range(2)]
    for worker in workers:
        worker.start()
    start.set()
    for worker in workers:
        worker.join(timeout=5)

    assert all(not worker.is_alive() for worker in workers)
    assert sum(isinstance(outcome, dict) for outcome in outcomes) == 1
    assert sum(isinstance(outcome, ValueError) for outcome in outcomes) == 1
    snapshot = manager.get_snapshot()
    assert snapshot["version"] == 1
    assert snapshot["state"]["prediction_count"] == 1
    assert snapshot["state"]["last_observation_index"] == 0


def test_snapshot_waits_for_observation_and_captures_consistent_state():
    inference_started = Event()
    release_inference = Event()
    snapshot_started = Event()
    snapshot_finished = Event()

    class BlockingPredictor:
        def predict(self, features):
            inference_started.set()
            assert release_inference.wait(timeout=5)
            return torch.tensor([0.92], dtype=torch.float32)

    manager = TwinManager(battery_id="snapshot-battery", predictor=BlockingPredictor())
    observation_worker = Thread(
        target=lambda: manager.process_observation(np.ones(67), observation_index=4)
    )
    observation_worker.start()
    assert inference_started.wait(timeout=5)

    captured = []

    def capture_snapshot():
        snapshot_started.set()
        captured.append(manager.get_snapshot())
        snapshot_finished.set()

    snapshot_worker = Thread(target=capture_snapshot)
    snapshot_worker.start()
    assert snapshot_started.wait(timeout=5)
    assert not snapshot_finished.wait(timeout=0.05)

    release_inference.set()
    observation_worker.join(timeout=5)
    snapshot_worker.join(timeout=5)

    assert not observation_worker.is_alive()
    assert not snapshot_worker.is_alive()
    snapshot = captured[0]
    assert snapshot["version"] == 1
    assert snapshot["state"]["last_observation_index"] == 4
    assert snapshot["state"]["prediction_count"] == 1
    assert snapshot["state"]["twin_state"]["soh"] == pytest.approx(0.92)
    assert len(snapshot["history"]["prediction_history"]) == 1
