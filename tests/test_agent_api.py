import pytest
import torch
from fastapi.testclient import TestClient

from backend.main import app
from backend.twin_registry import twin_registry
from digital_twin import twin_manager as twin_manager_module
from digital_twin import goal_directed_orchestrator as planner


class SequencePredictor:
    def __init__(self):
        self.values = iter((0.95, 0.92, 0.89))
        self.last_value = 0.89

    def predict(self, features):
        try:
            self.last_value = next(self.values)
        except StopIteration:
            pass
        return torch.tensor([self.last_value], dtype=torch.float32)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        twin_manager_module,
        "SOHPredictor",
        lambda checkpoint_path=None: SequencePredictor(),
    )
    twin_registry._twins.clear()
    with TestClient(app) as test_client:
        yield test_client
    twin_registry._twins.clear()


def _initialize_with_observations(client, battery_id, count):
    response = client.post(f"/twin/{battery_id}/initialize", json={})
    assert response.status_code == 200
    for index in range(count):
        response = client.post(
            f"/twin/{battery_id}/observation",
            json={"features": [0.5] * 67, "observation_index": index},
        )
        assert response.status_code == 200


def _request(battery_id, goal):
    return {"battery_id": battery_id, "goal": goal}


def test_decision_api_returns_baseline_only_result(client):
    battery_id = "agent-baseline-api"
    _initialize_with_observations(client, battery_id, 1)

    response = client.post(
        "/api/agent/decide",
        json=_request(
            battery_id,
            {"goal_id": "baseline-check", "horizon_cycles": 25, "assessment_scope": "baseline_only"},
        ),
    )

    assert response.status_code == 200
    result = response.json()
    assert result["battery_id"] == battery_id
    assert result["assessment_path"] == "baseline_only"
    assert result["candidate_evaluations"][0]["scenario"] == "No maintenance"
    assert result["utility_ranking"] is None
    assert result["policy_comparison"]["status"] == "not_applicable_baseline_only"
    assert result["snapshot_metadata"]["prediction_count"] == 1


def test_decision_api_counterfactual_uses_one_snapshot_and_does_not_mutate_twin(client, monkeypatch):
    battery_id = "agent-counterfactual-api"
    _initialize_with_observations(client, battery_id, 3)
    manager = twin_registry.get(battery_id)
    before = manager.get_snapshot()
    snapshot_calls = 0
    original_get_snapshot = manager.get_snapshot

    def counted_get_snapshot():
        nonlocal snapshot_calls
        snapshot_calls += 1
        return original_get_snapshot()

    monkeypatch.setattr(manager, "get_snapshot", counted_get_snapshot)
    response = client.post(
        "/api/agent/decide",
        json=_request(
            battery_id,
            {
                "goal_id": "compare-scenarios",
                "horizon_cycles": 75,
                "assessment_scope": "counterfactual_comparison",
                "target_soh": 0.9,
            },
        ),
    )

    assert response.status_code == 200
    result = response.json()
    assert snapshot_calls == 1
    after = manager.get_snapshot()
    assert result["assessment_path"] == "counterfactual_comparison"
    assert result["snapshot_metadata"]["snapshot_version"] == before["version"]
    assert result["snapshot_metadata"]["observation_index"] == before["state"]["last_observation_index"]
    assert result["snapshot_metadata"]["prediction_count"] == before["state"]["prediction_count"]
    assert {row["scenario"] for row in result["candidate_evaluations"]} == {
        "No maintenance", "Maintenance A", "Maintenance B"
    }
    assert all(
        row["initial_soh"] == pytest.approx(before["state"]["twin_state"]["soh"])
        for row in result["candidate_evaluations"]
    )
    assert result["utility_ranking"]["feasibility_status"] == "unknown"
    assert result["utility_ranking"]["selected_candidate"] is None
    assert all(
        row["feasibility_status"] in {"unknown", "not_applicable_baseline_comparator"}
        for row in result["candidate_evaluations"]
    )
    assert after == before


def test_decision_api_unknown_battery_returns_404(client):
    response = client.post(
        "/api/agent/decide",
        json=_request("missing-agent-battery", {"goal_id": "g", "horizon_cycles": 10}),
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "goal",
    [
        {"goal_id": "bad-horizon", "horizon_cycles": True},
        {"goal_id": "bad-scope", "horizon_cycles": 10, "assessment_scope": "unsupported"},
        {"goal_id": "bad-evidence", "horizon_cycles": 10, "diagnostic_evidence": {"invented": True}},
        {"goal_id": "extra-field", "horizon_cycles": 10, "starting_soh": 0.9},
    ],
)
def test_decision_api_rejects_invalid_goal_with_422(client, goal):
    response = client.post(
        "/api/agent/decide",
        json=_request("any-battery", goal),
    )

    assert response.status_code == 422


def test_decision_api_requires_registered_cnn_prediction(client):
    battery_id = "agent-no-prediction"
    assert client.post(f"/twin/{battery_id}/initialize", json={}).status_code == 200

    response = client.post(
        "/api/agent/decide",
        json=_request(battery_id, {"goal_id": "baseline", "horizon_cycles": 10}),
    )

    assert response.status_code == 409
    assert response.json()["termination_status"] == "invalid_snapshot"


def test_decision_api_maps_counterfactual_service_failure_to_500(client, monkeypatch):
    battery_id = "agent-service-failure"
    _initialize_with_observations(client, battery_id, 1)

    def fail_simulation(**kwargs):
        raise RuntimeError("simulation unavailable")

    monkeypatch.setattr(planner, "simulate_registered_twin", fail_simulation)
    response = client.post(
        "/api/agent/decide",
        json=_request(
            battery_id,
            {"goal_id": "compare", "horizon_cycles": 10, "assessment_scope": "counterfactual_comparison"},
        ),
    )

    assert response.status_code == 500
    result = response.json()
    assert result["termination_status"] == "service_failure"
    assert result["errors"][0]["code"] == "counterfactual_simulation_failed"


def test_decision_api_route_is_in_openapi(client):
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/api/agent/decide"]["post"]
    assert operation["requestBody"]
    assert operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/ExperimentalDecisionResult"
    )
