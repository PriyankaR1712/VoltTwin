from copy import deepcopy

import pytest
import torch

from backend.twin_registry import TwinRegistry
from digital_twin import twin_manager as twin_manager_module
from digital_twin.counterfactual_service import simulate_registered_twin


class ConstantPredictor:
    def predict(self, features):
        return torch.tensor([0.92], dtype=torch.float32)


@pytest.fixture
def registered_manager(monkeypatch):
    monkeypatch.setattr(
        twin_manager_module,
        "SOHPredictor",
        lambda checkpoint_path=None: ConstantPredictor(),
    )
    registry = TwinRegistry()
    manager = registry.initialize("counterfactual-test")
    for index in range(3):
        manager.process_observation([0.5] * 67, observation_index=index + 4)
    return registry, manager


def test_registered_counterfactual_does_not_mutate_twin_or_histories(
    registered_manager,
):
    registry, manager = registered_manager
    before = manager.get_snapshot()
    twin_state = deepcopy(manager.twin.get_state())
    predictions = deepcopy(manager.twin.prediction_history)
    observations = deepcopy(manager.twin.observation_history)
    observation_index = manager.last_observation_index
    prediction_count = len(predictions)
    provenance = before["state"]["state_source"]

    result = simulate_registered_twin(
        registry,
        "counterfactual-test",
        additional_cycles=125,
    )

    after = manager.get_snapshot()
    assert [scenario["scenario"] for scenario in result["scenarios"]] == [
        "No maintenance",
        "Maintenance A",
        "Maintenance B",
    ]
    assert result["snapshot_version"] == before["version"]
    assert manager.twin.get_state() == twin_state
    assert manager.twin.prediction_history == predictions
    assert manager.twin.observation_history == observations
    assert manager.last_observation_index == observation_index
    assert after["state"]["prediction_count"] == prediction_count
    assert after["state"]["state_source"] == provenance
    assert after["history"] == before["history"]
