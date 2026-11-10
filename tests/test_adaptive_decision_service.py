from types import SimpleNamespace

import pytest

from backend.adaptive_decision_service import AdaptiveDecisionService
from backend.adaptive_evaluation_store import AdaptiveEvaluationStore
from digital_twin.goal_spec import GoalSpec


class Manager:
    def __init__(self, count=1, soh=0.9, index=10):
        self.count, self.soh, self.index = count, soh, index

    def get_state(self):
        return {
            "prediction_count": self.count,
            "last_observation_index": self.index,
            "twin_state": {"soh": self.soh},
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
    run = lambda: (calls.append(manager.count) or decision(manager.count))
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


def test_hold_then_reassess_using_actual_decision_watermark(tmp_path):
    service, manager = make_service(tmp_path, gap=3), Manager()
    calls = []

    def run():
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
                                run_decision=lambda: decision(manager.count))

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
                                run_decision=lambda: decision(manager.count))

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
                                run_decision=lambda: decision(manager.count))

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

    def crash():
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
    def crash():
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
        run_decision=lambda: (calls.append(2) or decision(1)),
    )
    assert result["evaluation_status"] == "indeterminate"
    assert calls == [1]


def test_event_watermark_must_match_registered_twin(tmp_path):
    service, manager = make_service(tmp_path), Manager()
    with pytest.raises(ValueError):
        service.evaluate(battery_id="b", goal=GoalSpec("g", 4),
                         event_watermark={"prediction_count": 0, "version": 0, "observation_index": 9},
                         twin_registry=Registry(manager), run_decision=lambda: decision(1))
