import copy

import pytest
import torch
from fastapi.testclient import TestClient

from backend.main import app
from backend.twin_registry import twin_registry
from digital_twin.counterfactual_service import (
    CounterfactualStateUnavailable,
    assess_registered_baseline,
    simulate_registered_twin,
)
from digital_twin.twin_manager import TwinManager
from digital_twin.scenario_validation import validate_counterfactual_response


class FakePredictor:
    def __init__(self, predictions):
        self.predictions = iter(predictions)

    def predict(self, features):
        return torch.tensor([next(self.predictions)], dtype=torch.float32)


class FakeRegistry:
    def __init__(self, managers):
        self.managers = managers

    def get(self, battery_id):
        if battery_id not in self.managers:
            raise KeyError(battery_id)
        return self.managers[battery_id]


def make_manager(predictions=(0.94, 0.91)):
    manager = TwinManager(
        battery_id="counterfactual-test",
        initial_soh=1.0,
        predictor=FakePredictor(predictions),
    )
    for index in range(len(predictions)):
        manager.process_observation([0.5] * 67, observation_index=index + 3)
    return manager


def test_service_uses_latest_prediction_and_shared_snapshot():
    manager = make_manager()
    registry = FakeRegistry({"counterfactual-test": manager})

    result = simulate_registered_twin(
        registry,
        "counterfactual-test",
        additional_cycles=100,
    )

    assert result["snapshot_soh"] == pytest.approx(0.91)
    assert result["snapshot_soh_percent"] == pytest.approx(91.0)
    assert result["state_source"] == "cnn_prediction"
    assert result["latest_observation_index"] == 4
    assert result["prediction_count"] == 2
    assert [item["scenario"] for item in result["scenarios"]] == [
        "No maintenance",
        "Maintenance A",
        "Maintenance B",
    ]
    assert all(
        item["initial_soh"] == pytest.approx(0.91)
        for item in result["scenarios"]
    )


def test_service_does_not_mutate_registered_twin_or_histories():
    manager = make_manager()
    registry = FakeRegistry({"counterfactual-test": manager})
    state_before = manager.twin.get_state()
    prediction_history_before = copy.deepcopy(manager.twin.prediction_history)
    observation_history_before = copy.deepcopy(manager.twin.observation_history)
    last_observation_index_before = manager.last_observation_index

    simulate_registered_twin(
        registry,
        "counterfactual-test",
        additional_cycles=250,
    )

    assert manager.twin.get_state() == state_before
    assert manager.twin.prediction_history == prediction_history_before
    assert manager.twin.observation_history == observation_history_before
    assert manager.last_observation_index == last_observation_index_before


def test_service_uses_supplied_snapshot_after_manager_advances():
    manager = TwinManager(
        battery_id="counterfactual-test",
        initial_soh=1.0,
        predictor=FakePredictor([0.94, 0.91, 0.88]),
    )
    registry = FakeRegistry({"counterfactual-test": manager})
    manager.process_observation([0.5] * 67, observation_index=3)
    manager.process_observation([0.5] * 67, observation_index=4)
    captured = manager.get_snapshot()
    manager.process_observation([0.5] * 67, observation_index=5)

    result = simulate_registered_twin(
        registry,
        "counterfactual-test",
        additional_cycles=100,
        state_snapshot=captured,
    )

    assert result["snapshot_version"] == captured["version"]
    assert result["snapshot_soh"] == pytest.approx(0.91)
    assert result["latest_observation_index"] == 4
    assert result["prediction_count"] == 2
    assert all(
        scenario["initial_soh"] == pytest.approx(0.91)
        for scenario in result["scenarios"]
    )
    assert manager.twin.state.soh == pytest.approx(0.88)
    assert manager.last_observation_index == 5


def test_service_rejects_snapshot_for_another_manager():
    manager = make_manager()
    other_manager = make_manager()
    registry = FakeRegistry({"counterfactual-test": manager})

    with pytest.raises(ValueError, match="does not belong"):
        simulate_registered_twin(
            registry,
            "counterfactual-test",
            additional_cycles=100,
            state_snapshot=other_manager.get_snapshot(),
        )


def test_service_rejects_snapshot_for_another_battery():
    manager = make_manager()
    registry = FakeRegistry({"counterfactual-test": manager})
    snapshot = manager.get_snapshot()
    snapshot["battery_id"] = "different-battery"

    with pytest.raises(ValueError, match="belongs to another battery"):
        simulate_registered_twin(
            registry,
            "counterfactual-test",
            additional_cycles=100,
            state_snapshot=snapshot,
        )


@pytest.mark.parametrize(
    "mutate_snapshot",
    [
        lambda snapshot: snapshot["state"].update(state_source="manual"),
        lambda snapshot: snapshot["history"].update(state_source="manual"),
        lambda snapshot: snapshot["state"].update(prediction_count=99),
    ],
)
def test_service_rejects_inconsistent_snapshot(mutate_snapshot):
    manager = make_manager()
    registry = FakeRegistry({"counterfactual-test": manager})
    snapshot = manager.get_snapshot()
    mutate_snapshot(snapshot)

    with pytest.raises(ValueError):
        simulate_registered_twin(
            registry,
            "counterfactual-test",
            additional_cycles=100,
            state_snapshot=snapshot,
        )


def test_baseline_assessment_uses_snapshot_and_does_not_mutate_manager():
    manager = make_manager()
    registry = FakeRegistry({"counterfactual-test": manager})
    snapshot = manager.get_snapshot()
    before = manager.get_snapshot()

    result = assess_registered_baseline(
        registry,
        "counterfactual-test",
        additional_cycles=100,
        state_snapshot=snapshot,
    )

    assert result["scenario"] == "No maintenance"
    assert result["snapshot_version"] == snapshot["version"]
    assert result["initial_soh"] == pytest.approx(snapshot["state"]["twin_state"]["soh"])
    assert result["recovery_assumption"] == 0.0
    assert result["difference_vs_baseline"] == 0.0
    assert manager.get_snapshot() == before


def test_baseline_assessment_matches_counterfactual_baseline_from_same_snapshot():
    manager = make_manager()
    registry = FakeRegistry({"counterfactual-test": manager})
    snapshot = manager.get_snapshot()

    baseline = assess_registered_baseline(
        registry,
        "counterfactual-test",
        additional_cycles=100,
        state_snapshot=snapshot,
    )
    comparison = simulate_registered_twin(
        registry,
        "counterfactual-test",
        additional_cycles=100,
        state_snapshot=snapshot,
    )
    no_maintenance = next(
        scenario
        for scenario in comparison["scenarios"]
        if scenario["scenario"] == "No maintenance"
    )

    assert baseline["initial_soh"] == pytest.approx(no_maintenance["initial_soh"])
    assert baseline["projected_soh"] == pytest.approx(no_maintenance["projected_soh"])
    assert baseline["projected_soh_percent"] == pytest.approx(
        no_maintenance["projected_soh_percent"]
    )
    assert baseline["additional_cycles"] == no_maintenance["additional_cycles"]
    assert baseline["snapshot_version"] == comparison["snapshot_version"] == snapshot["version"]
    assert comparison["battery_id"] == snapshot["battery_id"]
    assert comparison["snapshot_soh"] == pytest.approx(baseline["initial_soh"])
    assert comparison["state_source"] == snapshot["state"]["state_source"]
    assert comparison["latest_observation_index"] == snapshot["state"][
        "last_observation_index"
    ]
    assert comparison["prediction_count"] == snapshot["state"]["prediction_count"]


def test_service_without_snapshot_captures_registered_manager_snapshot():
    manager = make_manager()
    registry = FakeRegistry({"counterfactual-test": manager})

    result = simulate_registered_twin(
        registry,
        "counterfactual-test",
        additional_cycles=100,
    )

    assert result["snapshot_version"] == manager.get_snapshot()["version"]
    assert result["snapshot_soh"] == pytest.approx(0.91)


@pytest.fixture
def client(monkeypatch):
    from digital_twin import twin_manager

    monkeypatch.setattr(
        twin_manager,
        "SOHPredictor",
        lambda checkpoint_path=None: FakePredictor([0.94]),
    )
    twin_registry._twins.clear()
    with TestClient(app) as test_client:
        yield test_client
    twin_registry._twins.clear()


def test_counterfactual_api_uses_registered_prediction_without_mutation(client):
    battery_id = "counterfactual-api-test"
    assert client.post(
        f"/twin/{battery_id}/initialize",
        json={"initial_soh": 1.0},
    ).status_code == 200
    observation = client.post(
        f"/twin/{battery_id}/observation",
        json={"features": [0.5] * 67, "observation_index": 7},
    )
    assert observation.status_code == 200

    state_before = client.get(f"/twin/{battery_id}/state").json()
    history_before = client.get(f"/twin/{battery_id}/history").json()
    response = client.post(
        f"/twin/{battery_id}/counterfactual",
        json={"additional_cycles": 125},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["battery_id"] == battery_id
    assert result["snapshot_soh"] == pytest.approx(0.94)
    assert result["snapshot_soh_percent"] == pytest.approx(94.0)
    assert result["state_source"] == "cnn_prediction"
    assert result["latest_observation_index"] == 7
    assert result["prediction_count"] == 1
    assert result["is_simulation"] is True
    assert result["is_physically_validated"] is False
    assert "illustrative" in result["notice"]
    assert all(
        scenario["initial_soh"] == pytest.approx(0.94)
        for scenario in result["scenarios"]
    )

    assert client.get(f"/twin/{battery_id}/state").json() == state_before
    assert client.get(f"/twin/{battery_id}/history").json() == history_before


def test_counterfactual_api_returns_404_for_unknown_battery(client):
    response = client.post(
        "/twin/not-registered/counterfactual",
        json={"additional_cycles": 100},
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "additional_cycles",
    [-1, 100001, 1.5, True, False],
)
def test_counterfactual_api_rejects_invalid_horizon(client, additional_cycles):
    response = client.post(
        "/twin/horizon-test/counterfactual",
        json={"additional_cycles": additional_cycles},
    )

    assert response.status_code == 422


def test_counterfactual_api_rejects_manual_starting_soh(client):
    response = client.post(
        "/twin/horizon-test/counterfactual",
        json={"additional_cycles": 100, "soh": 0.8},
    )

    assert response.status_code == 422


def test_counterfactual_api_requires_a_cnn_prediction(client):
    battery_id = "not-yet-predicted"
    assert client.post(
        f"/twin/{battery_id}/initialize",
        json={"initial_soh": 1.0},
    ).status_code == 200

    response = client.post(
        f"/twin/{battery_id}/counterfactual",
        json={"additional_cycles": 100},
    )

    assert response.status_code == 409

def test_real_counterfactual_response_validates_against_captured_snapshot():
    manager = make_manager()
    registry = FakeRegistry({"counterfactual-test": manager})
    snapshot = manager.get_snapshot()
    state_before = copy.deepcopy(snapshot["state"])
    history_before = copy.deepcopy(snapshot["history"])
    observation_index_before = manager.last_observation_index

    response = simulate_registered_twin(
        registry,
        "counterfactual-test",
        additional_cycles=125,
        state_snapshot=snapshot,
    )
    validated = validate_counterfactual_response(
        response,
        captured_snapshot=snapshot,
        requested_horizon=125,
    )

    after = manager.get_snapshot()
    assert set(validated.scenarios) == {
        "No maintenance",
        "Maintenance A",
        "Maintenance B",
    }
    assert validated.snapshot_version == snapshot["version"]
    assert response["snapshot_version"] == snapshot["version"]
    assert after["state"] == state_before
    assert after["history"] == history_before
    assert manager.last_observation_index == observation_index_before
