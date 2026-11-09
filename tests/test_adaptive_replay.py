from backend.adaptive_replay import compare_reassessment_policies, sweep_development_thresholds
from digital_twin.goal_spec import GoalSpec


def test_replay_is_repeatable_and_compares_all_three_policies():
    events = [
        {"watermark": {"prediction_count": count, "version": count,
                        "observation_index": count + 10},
         "predicted_soh": soh}
        for count, soh in [(1, 0.91), (2, 0.905), (3, 0.89), (4, 0.87), (5, 0.86)]
    ]
    goal = GoalSpec("replay-goal", 100, target_soh=0.90)
    first = compare_reassessment_policies(events, goal, minimum_gap=3, epsilon_soh=0.005)
    second = compare_reassessment_policies(events, goal, minimum_gap=3, epsilon_soh=0.005)
    assert first == second
    assert first["policies"]["held"]["invocations"] == 1
    assert first["policies"]["periodic"]["invocations"] == 2
    assert first["policies"]["adaptive"]["invocations"] >= 2
    assert first["policies"]["held"]["freshness"]["replay_event"]["max_predictions"] == 4
    assert first["policies"]["adaptive"]["crossing_detection_delay"]["max_delay_predictions"] == 0
    assert first["policies"]["adaptive"]["freshness"]["actual_decision_snapshot"]["available"] is False
    assert first["evaluation_kind"] == "trigger_policy_only_no_stage3_execution"


def test_development_threshold_sweep_is_repeatable_and_reports_tradeoffs():
    events = [
        {"watermark": {"prediction_count": i, "version": i, "observation_index": i},
         "predicted_soh": value}
        for i, value in [(1, .92), (2, .91), (3, .89), (4, .88)]
    ]
    args = dict(battery_sequences={"dev-1": events, "dev-2": events},
                goal=GoalSpec("tune", 10, target_soh=.90),
                minimum_gaps=[2, 4], epsilon_values=[0.0, .01])
    first = sweep_development_thresholds(**args)
    second = sweep_development_thresholds(**args)
    assert first == second
    assert len(first) == 4
    assert all(row["development_batteries"] == ["dev-1", "dev-2"] for row in first)
    assert all(row["matched_periodic_gap"] >= 1 for row in first)
    assert all(row["invocations"]["adaptive"] >= 0 for row in first)
    assert all(row["freshness"]["periodic"]["replay_event"]["mean_predictions"] is not None for row in first)
    assert all(row["actual_decision_snapshot_freshness"] == "unavailable_without_stage3_integration_trace" for row in first)
    assert all(row["decision_quality_claim"] is False for row in first)


def test_crossing_delays_include_right_censored_periodic_and_held_cases():
    events = [
        {"watermark": {"prediction_count": i, "version": i, "observation_index": i},
         "predicted_soh": value}
        for i, value in [(1, .92), (2, .92), (3, .87)]
    ]
    report = compare_reassessment_policies(
        events, GoalSpec("censor", 10, target_soh=.90), minimum_gap=10,
        epsilon_soh=.005, periodic_gap=10,
    )
    assert report["policies"]["adaptive"]["crossing_detection_delay"]["max_delay_predictions"] == 0
    assert report["policies"]["periodic"]["crossing_detection_delay"]["censored"] == 1
    assert report["policies"]["held"]["crossing_detection_delay"]["censored"] == 1


def test_snapshot_freshness_uses_supplied_actual_decision_watermarks():
    events = [
        {"watermark": {"prediction_count": i, "version": i, "observation_index": i},
         "predicted_soh": .91}
        for i in range(1, 5)
    ]
    actual = {"held": [events[0]["watermark"], None, None, None],
              "periodic": [events[0]["watermark"], None, None, events[3]["watermark"]],
              "adaptive": [events[0]["watermark"], None, None, None]}
    report = compare_reassessment_policies(
        events, GoalSpec("snapshot", 10), minimum_gap=2, epsilon_soh=.01,
        periodic_gap=3, actual_snapshot_watermarks=actual,
    )
    periodic = report["policies"]["periodic"]["freshness"]["actual_decision_snapshot"]
    assert periodic["available"] is True
    assert periodic["max_predictions"] == 2


def test_adaptive_invocation_reasons_count_goal_and_policy_changes():
    original = GoalSpec("g1", 10, target_soh=.9)
    changed = GoalSpec("g2", 10, target_soh=.88)
    events = [
        {"watermark": {"prediction_count": 1, "version": 1, "observation_index": 1},
         "predicted_soh": .91, "goal": original, "policy_version": "v1"},
        {"watermark": {"prediction_count": 2, "version": 2, "observation_index": 2},
         "predicted_soh": .91, "goal": changed, "policy_version": "v1"},
        {"watermark": {"prediction_count": 3, "version": 3, "observation_index": 3},
         "predicted_soh": .91, "goal": changed, "policy_version": "v2"},
    ]
    report = compare_reassessment_policies(
        events, original, minimum_gap=10, epsilon_soh=.01,
    )
    assert report["adaptive_invocations_by_reason"] == {
        "first_assessment": 1,
        "goal_changed": 1,
        "policy_configuration_changed": 1,
    }
