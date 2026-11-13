import asyncio
import json

from backend import agent_api
from backend.decision_history_store import DecisionHistoryStore
from backend.twin_registry import TwinRegistry
from digital_twin import twin_manager as twin_manager_module
from backend.adaptive_decision_service import AdaptiveDecisionService
from backend.adaptive_evaluation_store import AdaptiveEvaluationStore
from backend.main import app
from digital_twin.decision_models import ExperimentalDecisionResult
from digital_twin.goal_spec import GoalSpec


class Manager:
    def __init__(self):
        self.count = 1
        self.index = 10

    def get_state(self):
        return {"prediction_count": self.count, "last_observation_index": self.index,
                "twin_state": {"soh": 0.9}}

    def get_snapshot(self):
        return {
            "battery_id": "b",
            "version": self.count,
            "state": self.get_state(),
            "history": {"battery_id": "b", "state_source": "cnn_prediction",
                        "prediction_history": [{} for _ in range(self.count)]},
            "_manager_identity": id(self),
        }


async def _asgi_post(path, body):
    messages = []
    sent = False
    async def receive():
        nonlocal sent
        if not sent:
            sent = True
            return {"type": "http.request", "body": json.dumps(body).encode(), "more_body": False}
        return {"type": "http.disconnect"}
    async def send(message):
        messages.append(message)
    await app({
        "type": "http", "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1", "method": "POST", "scheme": "http",
        "path": path, "raw_path": path.encode(), "query_string": b"",
        "headers": [(b"host", b"testserver"), (b"content-type", b"application/json")],
        "client": ("test", 123), "server": ("testserver", 80), "root_path": "",
    }, receive, send)
    start = next(message for message in messages if message["type"] == "http.response.start")
    payload = b"".join(message.get("body", b"") for message in messages if message["type"] == "http.response.body")
    return start["status"], dict(start["headers"]), json.loads(payload) if payload else None


def test_adaptive_http_route_reuses_same_event_without_rerunning_stage3(monkeypatch, tmp_path):
    manager = Manager()
    monkeypatch.setattr(agent_api.twin_registry, "get", lambda _battery: manager)
    service = AdaptiveDecisionService(
        AdaptiveEvaluationStore(tmp_path / "adaptive.db"), minimum_gap=3,
        epsilon_soh=0.01, policy_version="dev-policy-1",
    )
    monkeypatch.setattr(agent_api, "_adaptive_service", service)
    calls = []
    def run(_battery, _goal, captured_snapshot=None):
        calls.append(1)
        return ExperimentalDecisionResult(
            decision_id="d1", battery_id="b", assessment_path="baseline_only",
            termination_status="completed", goal_status="target_unavailable",
            selected_action="no_intervention_selected",
            policy_comparison={"status": "not_applicable_baseline_only"},
            snapshot_metadata={"snapshot_version": 1, "prediction_count": 1,
                               "observation_index": 10},
        ), "saved", 200
    monkeypatch.setattr(agent_api, "_run_and_persist_decision", run)
    request = {
        "battery_id": "b",
        "goal": {"goal_id": "g", "horizon_cycles": 2},
        "event_watermark": {"prediction_count": 1, "version": 1, "observation_index": 10},
    }
    first = asyncio.run(_asgi_post("/api/agent/adaptive-decide", request))
    duplicate = asyncio.run(_asgi_post("/api/agent/adaptive-decide", request))
    assert first[0] == duplicate[0] == 200
    assert first[1][b"x-decision-persistence-status"] == b"saved"
    assert first[2]["evaluation_status"] == "reassessed"
    assert first[2]["decision_snapshot_watermark"]["prediction_count"] == 1
    assert duplicate[2]["decision_id"] == "d1"
    assert calls == [1]


def test_adaptive_route_rejects_invalid_watermark_with_422(monkeypatch):
    status, _, _ = asyncio.run(_asgi_post("/api/agent/adaptive-decide", {
        "battery_id": "b", "goal": {"goal_id": "g", "horizon_cycles": 1},
        "event_watermark": {"prediction_count": True, "version": 1, "observation_index": 2},
    }))
    assert status == 422


def test_adaptive_route_fails_closed_without_frozen_policy_config(monkeypatch):
    monkeypatch.setattr(agent_api, "_adaptive_service", None)
    for key in (
        "VOLTTWIN_ADAPTIVE_MINIMUM_GAP",
        "VOLTTWIN_ADAPTIVE_EPSILON_SOH",
        "VOLTTWIN_ADAPTIVE_POLICY_VERSION",
    ):
        monkeypatch.delenv(key, raising=False)
    status, _, body = asyncio.run(_asgi_post("/api/agent/adaptive-decide", {
        "battery_id": "b", "goal": {"goal_id": "g", "horizon_cycles": 1},
        "event_watermark": {"prediction_count": 1, "version": 1, "observation_index": 10},
    }))
    assert status == 503
    assert body["detail"] == "Adaptive evaluation is unavailable or indeterminate."


def test_configured_application_startup_acquires_adaptive_worker_lease(monkeypatch, tmp_path):
    from backend.main import app_lifespan

    monkeypatch.setattr(agent_api, "_adaptive_service", None)
    monkeypatch.setenv("VOLTTWIN_ADAPTIVE_DB_PATH", str(tmp_path / "startup.db"))
    monkeypatch.setenv("VOLTTWIN_ADAPTIVE_MINIMUM_GAP", "3")
    monkeypatch.setenv("VOLTTWIN_ADAPTIVE_EPSILON_SOH", "0.01")
    monkeypatch.setenv("VOLTTWIN_ADAPTIVE_POLICY_VERSION", "startup-test")

    async def enter_lifespan():
        async with app_lifespan(app):
            assert agent_api._adaptive_service is not None
            assert agent_api._adaptive_service.store.database_path == tmp_path / "startup.db"

    asyncio.run(enter_lifespan())
    agent_api._adaptive_service.store.close()
    monkeypatch.setattr(agent_api, "_adaptive_service", None)



def test_ordinary_decide_captures_registered_snapshot_without_override(
    monkeypatch, tmp_path
):
    class ConstantPredictor:
        def predict(self, _features):
            return 0.91

    monkeypatch.setattr(
        twin_manager_module, "SOHPredictor",
        lambda checkpoint_path=None: ConstantPredictor(),
    )
    registry = TwinRegistry()
    manager = registry.initialize("ordinary-decide-snapshot")
    manager.process_observation([0.5] * 67, observation_index=0)
    monkeypatch.setattr(agent_api, "twin_registry", registry)
    history = DecisionHistoryStore(tmp_path / "ordinary-decision-history.db")
    monkeypatch.setattr(agent_api, "_history_store", history)

    status, headers, body = asyncio.run(_asgi_post("/api/agent/decide", {
        "battery_id": "ordinary-decide-snapshot",
        "goal": {"goal_id": "ordinary", "horizon_cycles": 2,
                 "assessment_scope": "baseline_only"},
    }))

    assert status == 200
    assert headers[b"x-decision-persistence-status"] == b"saved"
    assert body["snapshot_metadata"]["prediction_count"] == 1
    assert body["snapshot_metadata"]["version"] == 1
    stored = history.get_decision(body["decision_id"])
    assert stored["snapshot_metadata"]["prediction_count"] == 1
    assert stored["snapshot_metadata"]["version"] == 1

def test_existing_decide_contract_keeps_body_status_and_persistence_header(monkeypatch):
    result = ExperimentalDecisionResult(
        decision_id="preserved-id", battery_id="b", assessment_path="baseline_only",
        termination_status="invalid_snapshot", selected_action="no_intervention_selected",
        policy_comparison={"status": "not_applicable_baseline_only"},
    )
    calls = []
    def run(_battery, _goal, captured_snapshot=None):
        calls.append(1)
        return result, "failed", 409
    monkeypatch.setattr(agent_api, "_run_and_persist_decision", run)
    status, headers, body = asyncio.run(_asgi_post("/api/agent/decide", {
        "battery_id": "b", "goal": {"goal_id": "g", "horizon_cycles": 1},
    }))
    assert status == 409
    assert headers[b"x-decision-persistence-status"] == b"failed"
    assert body["decision_id"] == "preserved-id"
    assert body["termination_status"] == "invalid_snapshot"
    assert calls == [1]
