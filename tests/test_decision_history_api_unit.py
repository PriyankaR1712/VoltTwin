import json
from datetime import datetime, timezone

import pytest

from backend import agent_api
from backend.decision_history_store import DecisionHistoryStore
from digital_twin.decision_models import ExperimentalDecisionResult, ToolExecutionOutcome


class RegisteredTwin:
    def get(self, battery_id):
        return object()


def decision_result(termination="completed"):
    return ExperimentalDecisionResult(
        decision_id="api-decision-1",
        battery_id="battery-api",
        assessment_path="baseline_only",
        termination_status=termination,
        goal_status="target_unavailable",
        selected_action="no_intervention_selected",
        candidate_evaluations=[
            {
                "scenario": "No maintenance",
                "projected_soh": 0.9,
                "utility": None,
            }
        ],
        policy_comparison={"status": "not_applicable_baseline_only"},
        snapshot_metadata={"version": 1},
        errors=[] if termination == "completed" else [
            {"code": "service_error", "message": "baseline failed"}
        ],
        tool_outcomes=[
            ToolExecutionOutcome(
                "registered_twin_snapshot",
                "success",
                1,
                result={"battery_id": "battery-api", "version": 1},
            ),
            ToolExecutionOutcome(
                "baseline_assessment",
                "success" if termination == "completed" else "execution_failure",
                2,
                result={"scenario": "No maintenance", "projected_soh": 0.9}
                if termination == "completed" else None,
                error=None if termination == "completed" else {
                    "code": "tool_execution_failed", "message": "Tool execution failed."
                },
            ),
        ],
    )


@pytest.fixture
def api_setup(monkeypatch, tmp_path):
    store = DecisionHistoryStore(tmp_path / "api-history.db")
    monkeypatch.setattr(agent_api, "_history_store", store)
    monkeypatch.setattr(agent_api, "twin_registry", RegisteredTwin())
    calls = []

    def run_once(**kwargs):
        calls.append(kwargs)
        try:
            kwargs["plan_recorder"](("registered_twin_snapshot", "baseline_assessment"))
        except Exception:
            pass
        return decision_result()

    monkeypatch.setattr(agent_api, "run_goal_directed_orchestrator", run_once)
    request = agent_api.AgentDecisionRequest.model_validate(
        {
            "battery_id": "battery-api",
            "goal": {"goal_id": "goal-api", "horizon_cycles": 12},
        }
    )
    return store, calls, request


def test_decide_persists_once_and_returns_original_result_with_status_header(api_setup):
    store, calls, request = api_setup

    response = agent_api.decide(request)

    assert len(calls) == 1
    assert calls[0]["goal"] == request.goal
    assert response.status_code == 200
    body = json.loads(response.body)
    assert body["decision_id"] == "api-decision-1"
    assert body["termination_status"] == "completed"
    assert response.headers["X-Decision-Persistence-Status"] == "saved"
    record = store.get_decision("api-decision-1")
    assert record["goal_spec"]["goal_id"] == "goal-api"
    assert record["planned_tools"] == [
        "registered_twin_snapshot",
        "baseline_assessment",
    ]


def test_decide_persistence_failure_does_not_mutate_failed_stage3_response(
    api_setup, monkeypatch
):
    _store, calls, request = api_setup

    def fail_save(_payload):
        raise RuntimeError("private database failure")

    monkeypatch.setattr(agent_api._history_store, "save", fail_save)

    def failed_run(**kwargs):
        calls.append(kwargs)
        kwargs["plan_recorder"](("registered_twin_snapshot", "baseline_assessment"))
        return decision_result("service_failure")

    monkeypatch.setattr(agent_api, "run_goal_directed_orchestrator", failed_run)
    response = agent_api.decide(request)

    assert len(calls) == 1
    assert response.status_code == 500
    body = json.loads(response.body)
    assert body["termination_status"] == "service_failure"
    assert body["errors"][0]["code"] == "service_error"
    assert response.headers["X-Decision-Persistence-Status"] == "failed"


def test_payload_construction_failure_isolated_from_stage3_result(api_setup, monkeypatch):
    _store, calls, request = api_setup

    def fail_payload(**_kwargs):
        raise ValueError("payload serializer failed")

    monkeypatch.setattr(agent_api, "freeze_decision_payload", fail_payload)
    response = agent_api.decide(request)

    assert len(calls) == 1
    assert response.status_code == 200
    body = json.loads(response.body)
    assert body["decision_id"] == "api-decision-1"
    assert body["termination_status"] == "completed"
    assert response.headers["X-Decision-Persistence-Status"] == "failed"


def test_plan_recorder_failure_persists_plan_as_unavailable(api_setup, monkeypatch):
    store, calls, request = api_setup

    def fail_recording(_state, _plan):
        raise RuntimeError("recorder failed")

    monkeypatch.setattr(agent_api, "_record_plan_in_memory", fail_recording)
    response = agent_api.decide(request)

    assert len(calls) == 1
    assert response.status_code == 200
    record = store.get_decision("api-decision-1")
    assert record["plan_evidence_available"] is False
    assert record["planned_tools"] is None
    assert all(row["planned"] is None for row in record["tool_outcomes"])


def test_history_handlers_return_empty_and_detail_records(api_setup):
    store, _calls, _request = api_setup
    assert agent_api.list_battery_decisions("no-history", limit=20, cursor=None)["items"] == []
    store.save(
        agent_api.freeze_decision_payload(
            goal=agent_api.GoalSpec("goal-api", 12),
            result=decision_result(),
            decision_started_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            planned_tools=("registered_twin_snapshot", "baseline_assessment"),
            plan_evidence_available=True,
        )
    )
    summary = agent_api.list_battery_decisions("battery-api", limit=20, cursor=None)
    detail = agent_api.get_decision("api-decision-1")
    assert summary["items"][0]["goal_id"] == "goal-api"
    assert detail["decision_id"] == "api-decision-1"
    assert len(detail["tool_outcomes"]) == 2
    assert len(detail["scenarios"]) == 1


def test_history_handlers_hide_database_errors_and_reject_bad_cursors(
    api_setup, monkeypatch
):
    store, _calls, _request = api_setup
    with pytest.raises(agent_api.HTTPException) as invalid_cursor:
        agent_api.list_battery_decisions(
            "battery-api", limit=20, cursor="not-valid!"
        )
    assert invalid_cursor.value.status_code == 422

    def fail_query(*_args, **_kwargs):
        raise RuntimeError("private SQL detail")

    monkeypatch.setattr(store, "list_decisions", fail_query)
    with pytest.raises(agent_api.HTTPException) as database_error:
        agent_api.list_battery_decisions("battery-api", limit=20, cursor=None)
    assert database_error.value.status_code == 500
    assert database_error.value.detail == "Decision history is unavailable."
