from concurrent.futures import ThreadPoolExecutor
from threading import Event
from types import SimpleNamespace

import pytest

from backend.adaptive_decision_service import AdaptiveDecisionService
from backend.adaptive_evaluation_store import AdaptiveEvaluationStore
from digital_twin.goal_spec import GoalSpec
from backend import agent_api
from backend.decision_history_store import DecisionHistoryStore
from backend.twin_registry import TwinRegistry
from digital_twin import twin_manager as twin_manager_module


class Manager:
    def __init__(self, count=1, soh=0.9, index=10):
        self.count, self.soh, self.index = count, soh, index

    def get_state(self):
        return {
            "prediction_count": self.count,
            "last_observation_index": self.index,
            "twin_state": {"soh": self.soh},
        }

    def get_snapshot(self):
        state = self.get_state()
        return {
            "battery_id": "b",
            "version": self.count,
            "state": state,
            "history": {
                "battery_id": "b",
                "state_source": "cnn_prediction",
                "prediction_history": [{} for _ in range(self.count)],
            },
            "_manager_identity": id(self),
        }


class Registry:
    def __init__(self, manager):
        self.manager = manager

    def get(self, battery_id):
        return self.manager


def event(manager):
    return {"prediction_count": manager.count, "version": manager.count,
            "observation_index": manager.index}


def decision(count):
    return SimpleNamespace(
        decision_id=f"decision-{count}",
        snapshot_metadata={"snapshot_version": count, "prediction_count": count,
                           "observation_index": count + 9},
    ), "saved", 200


def make_service(tmp_path, gap=3):
    return AdaptiveDecisionService(
        AdaptiveEvaluationStore(tmp_path / "adaptive.db"),
        minimum_gap=gap, epsilon_soh=0.01, policy_version="adaptive-test-v1",
    )


def test_first_event_reassesses_once_and_reuses_duplicate(tmp_path):
    service, manager = make_service(tmp_path), Manager()
    calls = []
    run = lambda _snapshot: (calls.append(manager.count) or decision(manager.count))
    first = service.evaluate(battery_id="b", goal=GoalSpec("g", 4),
                             event_watermark=event(manager), twin_registry=Registry(manager),
                             run_decision=run)
    duplicate = service.evaluate(battery_id="b", goal=GoalSpec("g", 4),
                                 event_watermark=event(manager), twin_registry=Registry(manager),
                                 run_decision=run)
    assert first["evaluation_status"] == "reassessed"
    assert first["decision_snapshot_watermark"]["prediction_count"] == 1
    assert duplicate["decision_id"] == "decision-1"
    assert calls == [1]



def test_event_snapshot_is_used_when_twin_advances_before_stage3(tmp_path, monkeypatch):
    class ConstantPredictor:
        def predict(self, _features):
            return 0.9

    monkeypatch.setattr(
        twin_manager_module, "SOHPredictor",
        lambda checkpoint_path=None: ConstantPredictor(),
    )
    registry = TwinRegistry()
    manager = registry.initialize("concurrent-snapshot-test")
    for index in range(3):
        manager.process_observation([0.5] * 67, observation_index=index)

    event_snapshot = manager.get_snapshot()
    event_watermark = {
        "prediction_count": event_snapshot["state"]["prediction_count"],
        "version": event_snapshot["version"],
        "observation_index": event_snapshot["state"]["last_observation_index"],
    }
    goal = GoalSpec("snapshot-race", 25, assessment_scope="baseline_only")
    service = make_service(tmp_path)
    monkeypatch.setattr(agent_api, "twin_registry", registry)
    monkeypatch.setattr(
        agent_api, "_history_store",
        DecisionHistoryStore(tmp_path / "stage4-history.db"),
    )

    callback_entered = Event()
    continue_callback = Event()
    original_run = agent_api._run_and_persist_decision
    callback_snapshots = []

    def pause_before_stage3(battery, requested_goal, captured_snapshot=None):
        callback_snapshots.append(captured_snapshot)
        callback_entered.set()
        if not continue_callback.wait(timeout=5):
            raise TimeoutError("Timed out waiting to resume Stage 3 callback.")
        return original_run(
            battery, requested_goal, captured_snapshot=captured_snapshot
        )

    monkeypatch.setattr(agent_api, "_run_and_persist_decision", pause_before_stage3)

    def evaluate_event():
        return service.evaluate(
            battery_id="concurrent-snapshot-test",
            goal=goal,
            event_watermark=event_watermark,
            twin_registry=registry,
            run_decision=lambda captured: agent_api._run_and_persist_decision(
                "concurrent-snapshot-test", goal, captured_snapshot=captured
            ),
        )

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(evaluate_event)
            assert callback_entered.wait(timeout=5)
            manager.process_observation([0.5] * 67, observation_index=3)
            assert manager.get_snapshot()["state"]["prediction_count"] == (
                event_watermark["prediction_count"] + 1
            )
            continue_callback.set()
            outcome = future.result(timeout=10)

        assert outcome["evaluation_status"] == "reassessed"
        assert callback_snapshots == [event_snapshot]
        assert outcome["event_watermark"] == event_watermark
        assert outcome["decision_snapshot_watermark"] == event_watermark
        assert outcome["decision_result"].snapshot_metadata["prediction_count"] == (
            event_watermark["prediction_count"]
        )
        assert outcome["decision_result"].snapshot_metadata["version"] == event_watermark["version"]
        assert manager.get_snapshot()["state"]["prediction_count"] == (
            event_watermark["prediction_count"] + 1
        )

        stored = agent_api._history_store.get_decision(outcome["decision_id"])
        assert stored is not None
        assert stored["snapshot_metadata"]["prediction_count"] == event_watermark["prediction_count"]
        assert stored["snapshot_metadata"]["version"] == event_watermark["version"]
    finally:
        continue_callback.set()
        service.store.close()

def test_hold_then_reassess_using_actual_decision_watermark(tmp_path):
    service, manager = make_service(tmp_path, gap=3), Manager()
    calls = []

    def run(_snapshot):
        calls.append(manager.count)
        # Deliberately return an actual decision snapshot behind event intake.
        return SimpleNamespace(decision_id=f"d{manager.count}", snapshot_metadata={
            "snapshot_version": manager.count - 1,
            "prediction_count": manager.count - 1,
            "observation_index": manager.index - 1,
        }), "saved", 200

    service.evaluate(battery_id="b", goal=GoalSpec("g", 4), event_watermark=event(manager),
                      twin_registry=Registry(manager), run_decision=run)
    manager.count, manager.index = 2, 11
    held = service.evaluate(battery_id="b", goal=GoalSpec("g", 4), event_watermark=event(manager),
                            twin_registry=Registry(manager), run_decision=run)
    assert held["evaluation_status"] == "held"
    assert held["decision_snapshot_watermark"]["prediction_count"] == 0
    manager.count, manager.index = 4, 13
    reassessed = service.evaluate(battery_id="b", goal=GoalSpec("g", 4), event_watermark=event(manager),
                                  twin_registry=Registry(manager), run_decision=run)
    assert reassessed["evaluation_status"] == "reassessed"
    assert calls == [1, 4]


def test_decision_reference_survives_one_and_multiple_holds(tmp_path):
    service, manager = make_service(tmp_path, gap=3), Manager()
    goal, registry = GoalSpec("g", 4), Registry(manager)

    def assess():
        return service.evaluate(battery_id="b", goal=goal, event_watermark=event(manager),
                                twin_registry=registry,
                                run_decision=lambda _snapshot: decision(manager.count))

    assess()  # D1 at watermark 1
    manager.count, manager.index = 2, 11
    assert assess()["evaluation_status"] == "held"
    assert service.store.get_latest("b", service._generation(manager))["decision_id"] is None
    manager.count, manager.index = 3, 12
    assert assess()["evaluation_status"] == "held"
    assert service.store.get_latest("b", service._generation(manager))["decision_id"] is None
    manager.count, manager.index = 4, 13
    assess()
    latest = service.store.get_latest("b", service._generation(manager))
    assert latest["prior_decision_id"] == "decision-1"


def test_decision_reference_survives_single_hold(tmp_path):
    service, manager = make_service(tmp_path, gap=3), Manager()
    goal, registry = GoalSpec("g", 4), Registry(manager)

    def assess():
        return service.evaluate(battery_id="b", goal=goal, event_watermark=event(manager),
                                twin_registry=registry,
                                run_decision=lambda _snapshot: decision(manager.count))

    assess()
    manager.count, manager.index = 2, 11
    assert assess()["evaluation_status"] == "held"
    manager.count, manager.index = 4, 13
    assert assess()["evaluation_status"] == "reassessed"
    latest = service.store.get_latest("b", service._generation(manager))
    assert latest["prior_decision_id"] == "decision-1"


def test_new_decision_replaces_prior_reference_after_holds(tmp_path):
    service, manager = make_service(tmp_path, gap=3), Manager()
    goal, registry = GoalSpec("g", 4), Registry(manager)

    def assess():
        return service.evaluate(battery_id="b", goal=goal, event_watermark=event(manager),
                                twin_registry=registry,
                                run_decision=lambda _snapshot: decision(manager.count))

    assess()
    manager.count, manager.index = 2, 11
    assess()
    manager.count, manager.index = 4, 13
    assess()  # D2
    manager.count, manager.index = 5, 14
    assert assess()["evaluation_status"] == "held"
    manager.count, manager.index = 7, 16
    assess()  # next assessment must refer to D2
    latest = service.store.get_latest("b", service._generation(manager))
    assert latest["prior_decision_id"] == "decision-4"


def test_no_previous_decision_reference_is_invented(tmp_path):
    service = make_service(tmp_path)
    generation = "generation-with-only-holds"
    for index in range(2):
        event_id, existing = service.store.reserve(
            event_key=f"held-{index}", battery_id="b", generation_id=generation,
            goal_fingerprint="goal", goal_spec={"goal_id": "g"},
            event_watermark={"prediction_count": index, "version": index,
                             "observation_index": index},
            predicted_soh=None, minimum_gap=3, epsilon_soh=.01,
            policy_version="v1", prior_decision_id=None,
        )
        assert existing is None
        service.store.finish(event_id, status="held", reasons=["not_ready"])
    assert service.store.get_latest_decision_id("b", generation) is None
    assert service.store.get_latest("b", generation)["prior_decision_id"] is None


def test_failed_callback_is_indeterminate_and_never_retried(tmp_path):
    service, manager = make_service(tmp_path), Manager()
    calls = []

    def crash(_snapshot):
        calls.append(1)
        raise RuntimeError("crash after possible Stage 3 execution")

    with pytest.raises(RuntimeError):
        service.evaluate(battery_id="b", goal=GoalSpec("g", 4), event_watermark=event(manager),
                         twin_registry=Registry(manager), run_decision=crash)
    result = service.evaluate(battery_id="b", goal=GoalSpec("g", 4), event_watermark=event(manager),
                              twin_registry=Registry(manager), run_decision=crash)
    assert result["evaluation_status"] == "indeterminate"
    assert calls == [1]


def test_indeterminate_event_is_not_retried_after_service_and_generation_restart(tmp_path):
    path = tmp_path / "adaptive.db"
    manager = Manager()
    registry = Registry(manager)
    calls = []
    first_service = AdaptiveDecisionService(
        AdaptiveEvaluationStore(path), minimum_gap=3, epsilon_soh=.01,
        policy_version="policy-v1",
    )
    def crash(_snapshot):
        calls.append(1)
        raise RuntimeError("simulated process interruption")
    with pytest.raises(RuntimeError):
        first_service.evaluate(battery_id="b", goal=GoalSpec("g", 4),
                               event_watermark=event(manager), twin_registry=registry,
                               run_decision=crash)

    # A new evaluator process and re-registered Twin get a new generation,
    # but the unresolved battery/goal/watermark tuple remains blocked.
    restarted_manager = Manager()
    restarted_service = AdaptiveDecisionService(
        AdaptiveEvaluationStore(path), minimum_gap=3, epsilon_soh=.01,
        policy_version="policy-v1",
    )
    result = restarted_service.evaluate(
        battery_id="b", goal=GoalSpec("g", 4), event_watermark=event(restarted_manager),
        twin_registry=Registry(restarted_manager),
        run_decision=lambda _snapshot: (calls.append(2) or decision(1)),
    )
    assert result["evaluation_status"] == "indeterminate"
    assert calls == [1]


def test_event_watermark_must_match_registered_twin(tmp_path):
    service, manager = make_service(tmp_path), Manager()
    with pytest.raises(ValueError):
        service.evaluate(battery_id="b", goal=GoalSpec("g", 4),
                         event_watermark={"prediction_count": 0, "version": 0, "observation_index": 9},
                         twin_registry=Registry(manager), run_decision=lambda _snapshot: decision(1))
