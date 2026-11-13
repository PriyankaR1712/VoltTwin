import pytest
import torch
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient

from backend.main import app
from backend import agent_api
from backend.decision_history_store import DecisionHistoryStore
from backend.twin_registry import twin_registry
from digital_twin import twin_manager as twin_manager_module
from digital_twin import goal_directed_orchestrator as planner
from digital_twin import planner_tool_registry as planner_tools


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
def client(monkeypatch, tmp_path):
    monkeypatch.setattr(
        twin_manager_module,
        "SOHPredictor",
        lambda checkpoint_path=None: SequencePredictor(),
    )
    monkeypatch.setattr(
        agent_api,
        "_history_store",
        DecisionHistoryStore(tmp_path / "test-decision-history.db"),
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
    assert response.headers["X-Decision-Persistence-Status"] == "saved"


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
    assert set(result["intervention_feasibility"]) == {"Maintenance A", "Maintenance B"}
    assert all(
        result["intervention_feasibility"][name]["status"] == "unknown"
        for name in ("Maintenance A", "Maintenance B")
    )
    assert result["final_recommendation"]["status"] == "no_recommendation"
    assert result["final_recommendation"]["candidate"] is None
    assert "feasibility_status" not in result["utility_ranking"]
    assert result["intervention_feasibility"]["Maintenance A"]["rule_id"] == (
        "documented_intervention_eligibility"
    )
    assert result["intervention_feasibility"]["Maintenance B"]["assessment_label"] == (
        "model_based_not_physical_safety_or_effectiveness_validation"
    )
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

    monkeypatch.setattr(planner_tools, "simulate_registered_twin", fail_simulation)
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


def test_persistence_failure_preserves_decision_body_status_and_single_execution(
    client, monkeypatch
):
    battery_id = "agent-persistence-failure"
    _initialize_with_observations(client, battery_id, 1)
    calls = []
    original_orchestrator = agent_api.run_goal_directed_orchestrator

    def counted_orchestrator(**kwargs):
        result = original_orchestrator(**kwargs)
        calls.append(result)
        return result

    def fail_persistence(_payload):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(agent_api, "run_goal_directed_orchestrator", counted_orchestrator)
    monkeypatch.setattr(agent_api._history_store, "save", fail_persistence)
    response = client.post(
        "/api/agent/decide",
        json=_request(
            battery_id,
            {"goal_id": "baseline", "horizon_cycles": 10, "assessment_scope": "baseline_only"},
        ),
    )

    assert len(calls) == 1
    assert response.status_code == 200
    assert response.json() == jsonable_encoder(calls[0])
    assert response.headers["X-Decision-Persistence-Status"] == "failed"


def test_plan_recorder_failure_is_persisted_as_unavailable_without_changing_decision(
    client, monkeypatch
):
    battery_id = "agent-plan-recorder-failure"
    _initialize_with_observations(client, battery_id, 1)

    def fail_recording(_state, _plan):
        raise RuntimeError("in-memory recorder unavailable")

    monkeypatch.setattr(agent_api, "_record_plan_in_memory", fail_recording)
    response = client.post(
        "/api/agent/decide",
        json=_request(
            battery_id,
            {"goal_id": "baseline", "horizon_cycles": 10, "assessment_scope": "baseline_only"},
        ),
    )

    assert response.status_code == 200
    assert response.json()["termination_status"] == "completed"
    record = agent_api._history_store.get_decision(response.json()["decision_id"])
    assert record["plan_evidence_available"] is False
    assert record["planned_tools"] is None
    assert all(tool["planned"] is None for tool in record["tool_outcomes"])


def test_decision_history_routes_return_summary_and_full_record(client):
    battery_id = "agent-history-api"
    _initialize_with_observations(client, battery_id, 1)
    decision = client.post(
        "/api/agent/decide",
        json=_request(battery_id, {"goal_id": "history-goal", "horizon_cycles": 10}),
    )
    decision_id = decision.json()["decision_id"]
    twin_registry._twins.pop(battery_id)

    history = client.get(f"/api/agent/batteries/{battery_id}/decisions?limit=1")
    detail = client.get(f"/api/agent/decisions/{decision_id}")

    assert history.status_code == 200
    summary = history.json()["items"][0]
    assert summary["decision_id"] == decision_id
    assert summary["battery_id"] == battery_id
    assert summary["created_at"]
    assert summary["decision_status"] == "completed"
    assert summary["termination_status"] == "completed"
    assert summary["goal_id"] == "history-goal"
    assert history.json()["has_more"] is False
    assert detail.status_code == 200
    assert detail.json()["goal_spec"]["goal_id"] == "history-goal"
    assert detail.json()["tool_outcomes"][0]["tool_name"] == "registered_twin_snapshot"
    assert len(detail.json()["scenarios"]) == 1


def test_decision_history_routes_validate_cursor_and_missing_detail(client):
    bad_cursor = client.get(
        "/api/agent/batteries/battery/decisions?cursor=not%20a%20cursor"
    )
    missing = client.get("/api/agent/decisions/not-found")
    assert bad_cursor.status_code == 422
    assert missing.status_code == 404


def test_baseline_failure_is_persisted_as_failed_without_losing_stage3_status(
    client, monkeypatch
):
    battery_id = "agent-baseline-failure-status"
    _initialize_with_observations(client, battery_id, 1)

    def fail_baseline(**_kwargs):
        raise RuntimeError("baseline unavailable")

    monkeypatch.setattr(planner.planner_tool_registry, "assess_registered_baseline", fail_baseline)
    response = client.post(
        "/api/agent/decide",
        json=_request(
            battery_id,
            {"goal_id": "baseline-failure", "horizon_cycles": 10, "assessment_scope": "baseline_only"},
        ),
    )
    record = agent_api._history_store.get_decision(response.json()["decision_id"])
    assert response.status_code == 500
    assert record["decision_status"] == "failed"
    assert record["termination_status"] == "service_failure"


def test_counterfactual_failure_after_baseline_is_persisted_as_incomplete(
    client, monkeypatch
):
    battery_id = "agent-counterfactual-failure-status"
    _initialize_with_observations(client, battery_id, 1)

    def fail_counterfactual(**_kwargs):
        raise RuntimeError("counterfactual unavailable")

    monkeypatch.setattr(planner.planner_tool_registry, "simulate_registered_twin", fail_counterfactual)
    response = client.post(
        "/api/agent/decide",
        json=_request(
            battery_id,
            {
                "goal_id": "comparison-failure",
                "horizon_cycles": 10,
                "assessment_scope": "counterfactual_comparison",
            },
        ),
    )
    record = agent_api._history_store.get_decision(response.json()["decision_id"])
    assert response.status_code == 500
    assert record["decision_status"] == "incomplete"
    assert record["termination_status"] == "service_failure"
    cf_tool = next(
        tool for tool in record["tool_outcomes"]
        if tool["tool_name"] == "counterfactual_simulation"
    )
    assert cf_tool["status"] == "execution_failure"
    assert cf_tool["planned"] is True
    assert cf_tool["executed"] is True
    assert cf_tool["error_details"] is not None
    assert cf_tool["result_summary"] is None
    assert cf_tool["execution_order"] == 3
    assert cf_tool["validated_arguments"] is not None
    assert any(
        tool["tool_name"] == "maintenance_policy"
        and tool["status"] == "not_executed"
        and tool["planned"] is True
        and tool["executed"] is False
        and tool["validated_arguments"] is None
        and tool["result_summary"] is None
        and tool["error_details"] is None
        for tool in record["tool_outcomes"]
    )
