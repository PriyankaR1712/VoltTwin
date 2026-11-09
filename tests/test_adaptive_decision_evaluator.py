import pytest

from backend.adaptive_decision_evaluator import choose_trigger, goal_fingerprint, validate_watermark
from digital_twin.goal_spec import GoalSpec


def wm(count, index=None):
    return {"prediction_count": count, "version": count, "observation_index": index}


def test_goal_fingerprint_is_stable_and_covers_diagnostic_evidence():
    a = GoalSpec("g", 5, target_soh=0.9, diagnostic_evidence={"thermal_alert": True})
    b = GoalSpec("g", 5, target_soh=0.9, diagnostic_evidence={"thermal_alert": True})
    c = GoalSpec("g", 5, target_soh=0.9, diagnostic_evidence={"thermal_alert": False})
    assert goal_fingerprint(a) == goal_fingerprint(b)
    assert goal_fingerprint(a)[0] != goal_fingerprint(c)[0]


def test_watermark_rejects_boolean_and_inconsistent_values():
    with pytest.raises(ValueError):
        validate_watermark({"prediction_count": True, "version": True, "observation_index": 1})
    with pytest.raises(ValueError):
        validate_watermark({"prediction_count": 2, "version": 1, "observation_index": 1})


def test_first_assessment_and_minimum_gap():
    goal = GoalSpec("g", 3)
    first = choose_trigger(
        current={"watermark": wm(2, 4), "predicted_soh": 0.9}, previous=None,
        goal=goal, minimum_gap=3, epsilon_soh=0.01,
    )
    assert first["action"] == "reassess"
    previous = {
        "watermark": wm(2, 4), "goal_fingerprint": "same",
        "decision_snapshot_watermark": wm(2, 4), "latched_side": None,
    }
    held = choose_trigger(
        current={"watermark": wm(3, 5), "predicted_soh": 0.9, "goal_fingerprint": "same"},
        previous=previous, goal=goal, minimum_gap=3, epsilon_soh=0.01,
    )
    assert held["status"] == "held"
    due = choose_trigger(
        current={"watermark": wm(5, 7), "predicted_soh": 0.9, "goal_fingerprint": "same"},
        previous=previous, goal=goal, minimum_gap=3, epsilon_soh=0.01,
    )
    assert due["reasons"] == ["minimum_observation_gap"]


def test_hysteresis_crossing_duplicate_and_out_of_order():
    goal = GoalSpec("g", 3, target_soh=0.8)
    previous = {
        "watermark": wm(4, 4), "goal_fingerprint": "same",
        "decision_snapshot_watermark": wm(4, 4), "latched_side": "above",
    }
    crossing = choose_trigger(
        current={"watermark": wm(5, 5), "predicted_soh": 0.79, "goal_fingerprint": "same"},
        previous=previous, goal=goal, minimum_gap=10, epsilon_soh=0.005,
    )
    assert crossing["reasons"] == ["target_band_crossing"]
    duplicate = choose_trigger(
        current={"watermark": wm(4, 4), "goal_fingerprint": "same"}, previous=previous,
        goal=goal, minimum_gap=10, epsilon_soh=0.005,
    )
    assert duplicate["status"] == "duplicate"
    stale = choose_trigger(
        current={"watermark": wm(3, 3), "goal_fingerprint": "same"}, previous=previous,
        goal=goal, minimum_gap=10, epsilon_soh=0.005,
    )
    assert stale["status"] == "stale_event"


def test_unknown_target_evidence_does_not_trigger_crossing():
    goal = GoalSpec("g", 3)
    previous = {"watermark": wm(4, 4), "goal_fingerprint": "same",
                "decision_snapshot_watermark": wm(4, 4), "latched_side": None}
    result = choose_trigger(
        current={"watermark": wm(5, 5), "predicted_soh": None, "goal_fingerprint": "same"},
        previous=previous, goal=goal, minimum_gap=3, epsilon_soh=0.01,
    )
    assert result["status"] == "held"
    assert result["reasons"] == ["minimum_gap_not_met"]


def test_goal_change_triggers_even_when_observation_watermark_is_unchanged():
    goal = GoalSpec("g2", 3)
    result = choose_trigger(
        current={"watermark": wm(4, 4), "predicted_soh": 0.9, "goal_fingerprint": "new"},
        previous={"watermark": wm(4, 4), "goal_fingerprint": "old",
                  "decision_snapshot_watermark": wm(4, 4), "latched_side": None},
        goal=goal, minimum_gap=10, epsilon_soh=0.01,
    )
    assert result["reasons"] == ["goal_changed"]


def test_policy_version_change_triggers_reassessment():
    result = choose_trigger(
        current={"watermark": wm(4, 4), "predicted_soh": 0.9, "goal_fingerprint": "same",
                 "policy_version": "v2", "minimum_gap": 4, "epsilon_soh": 0.01},
        previous={"watermark": wm(3, 3), "goal_fingerprint": "same",
                  "decision_snapshot_watermark": wm(3, 3), "latched_side": None,
                  "policy_version": "v1", "minimum_gap": 4, "epsilon_soh": 0.01},
        goal=GoalSpec("g", 3), minimum_gap=10, epsilon_soh=0.01,
    )
    assert result["reasons"] == ["policy_configuration_changed"]
