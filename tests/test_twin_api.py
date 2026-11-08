
import pytest
import torch
from fastapi.testclient import TestClient

from backend.main import app
from backend.twin_registry import twin_registry


class FakePredictor:
    def predict(self, features):
        return torch.tensor([0.95], dtype=torch.float32)


@pytest.fixture
def client(monkeypatch):
    from digital_twin import twin_manager

    monkeypatch.setattr(
        twin_manager,
        "SOHPredictor",
        lambda checkpoint_path=None: FakePredictor(),
    )

    # Keep tests isolated from previously initialized batteries.
    twin_registry._twins.clear()

    with TestClient(app) as test_client:
        yield test_client

    twin_registry._twins.clear()


def test_complete_twin_api_flow(client):
    battery_id = "api-test-battery"

    # 1. Initialize the Digital Twin.
    response = client.post(
        f"/twin/{battery_id}/initialize",
        json={"initial_soh": 1.0},
    )

    assert response.status_code == 200
    assert response.json()["battery_id"] == battery_id

    # 2. Process one observation.
    response = client.post(
        f"/twin/{battery_id}/observation",
        json={
            "features": [0.5] * 67,
            "observation_index": 0,
        },
    )

    assert response.status_code == 200
    assert response.json()["prediction"]["predicted_soh"] == pytest.approx(0.95)
    assert response.json()["twin_state"]["soh"] == pytest.approx(0.95)

    # 3. Retrieve current state.
    response = client.get(
        f"/twin/{battery_id}/state"
    )

    assert response.status_code == 200
    assert response.json()["twin_state"]["soh"] == pytest.approx(0.95)
    assert response.json()["prediction_count"] == 1

    # 4. Retrieve prediction history.
    response = client.get(
        f"/twin/{battery_id}/history"
    )

    assert response.status_code == 200
    assert response.json()["observation_count"] == 1
    assert len(response.json()["prediction_history"]) == 1


def test_duplicate_twin_initialization_returns_409(client):
    battery_id = "duplicate-test"

    client.post(
        f"/twin/{battery_id}/initialize",
        json={"initial_soh": 0.95},
    )

    response = client.post(
        f"/twin/{battery_id}/initialize",
        json={"initial_soh": 0.90},
    )

    assert response.status_code == 409


def test_unknown_battery_returns_404(client):
    response = client.get(
        "/twin/unknown-battery/state"
    )

    assert response.status_code == 404


def test_observation_before_initialization_returns_404(client):
    response = client.post(
        "/twin/not-initialized/observation",
        json={
            "features": [0.5] * 67,
            "observation_index": 0,
        },
    )

    assert response.status_code == 404


def test_invalid_feature_count_returns_422(client):
    battery_id = "invalid-features-test"

    client.post(
        f"/twin/{battery_id}/initialize",
        json={"initial_soh": 1.0},
    )

    response = client.post(
        f"/twin/{battery_id}/observation",
        json={
            "features": [0.5] * 66,
            "observation_index": 0,
        },
    )

    assert response.status_code == 422
