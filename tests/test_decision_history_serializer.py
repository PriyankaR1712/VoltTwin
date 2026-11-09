import json
from datetime import datetime, timezone

import pytest

from digital_twin.decision_models import ExperimentalDecisionResult, ToolExecutionOutcome
from digital_twin.goal_spec import GoalSpec

from backend.decision_history_serializer import (
    canonical_digest_bytes,
    freeze_decision_payload,
    map_decision_status,
)


BASELINE = {
    "scenario": "No maintenance",
    "snapshot_version": 3,
    "initial_soh": 0.9,
    "projected_soh": 0.89,
    "additional_cycles": 10,
    "recovery_assumption": 0.0,
    "difference_vs_baseline": 0.0,
}


def result_for(termination="completed", *, baseline=True, candidates=None, ranking=None):
    outcomes = [
        ToolExecutionOutcome(
            "registered_twin_snapshot",
            "success",
            1,
            result={"battery_id": "battery-1", "version": 3},
        )
    ]
    if baseline:
        outcomes.append(
            ToolExecutionOutcome(
                "baseline_assessment",
                "success",
                2,
                result=dict(BASELINE),
            )
        )
    comparison = ranking is not None or any(
        isinstance(candidate, dict)
        and candidate.get("scenario") in {"Maintenance A", "Maintenance B"}
        for candidate in (candidates or [])
    )
    return ExperimentalDecisionResult(
        decision_id="decision-1",
        battery_id="battery-1",
        assessment_path=(
            "counterfactual_comparison" if comparison else "baseline_only"
        ),
        termination_status=termination,
        goal_status="goal_unmet" if termination == "goal_unmet" else "target_unavailable",
        selected_action="no_intervention_selected",
        candidate_evaluations=candidates or [],
        utility_ranking=ranking,
        policy_comparison={
            "status": "unavailable" if comparison else "not_applicable_baseline_only"
        },
        explanation=["Stage 3 explanation."],
        snapshot_metadata={"version": 3, "current_soh": 0.9},
        errors=[] if termination in {"completed", "goal_unmet", "tie"} else [
            {"code": "stage_error", "message": "Recorded failure."}
        ],
        tool_outcomes=outcomes,
    )


@pytest.mark.parametrize(
    ("termination", "has_baseline", "expected"),
    [
        ("completed", False, "completed"),
        ("goal_unmet", False, "completed"),
        ("tie", False, "completed"),
        ("completed_with_policy_error", False, "incomplete"),
        ("service_failure", True, "incomplete"),
        ("service_failure", False, "failed"),
        ("invalid_service_result", True, "incomplete"),
        ("invalid_service_result", False, "failed"),
        ("invalid_scenario_evidence", True, "incomplete"),
        ("invalid_scenario_evidence", False, "failed"),
        ("invalid_goal", True, "failed"),
        ("invalid_snapshot", True, "failed"),
        ("future_termination", True, "failed"),
    ],
)
def test_status_mapping_uses_termination_and_validated_baseline_evidence(
    termination, has_baseline, expected
):
    assert map_decision_status(result_for(termination, baseline=has_baseline)) == expected


def test_baseline_with_invalid_result_does_not_count_as_validated_evidence():
    result = result_for("service_failure")
    baseline = result.tool_outcomes[-1]
    baseline.status = "invalid_result"
    baseline.result = None
    assert map_decision_status(result) == "failed"


def test_planned_but_unexecuted_tools_are_recorded_without_fabricated_evidence():
    result = result_for("service_failure")
    frozen = freeze_decision_payload(
        goal=GoalSpec("g", 10),
        result=result,
        decision_started_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
        planned_tools=(
            "registered_twin_snapshot",
            "baseline_assessment",
            "counterfactual_simulation",
            "maintenance_policy",
        ),
        plan_evidence_available=True,
    )
    payload = json.loads(frozen.database_json)
    tools = payload["tool_outcomes"]
    assert tools[0]["executed"] is True
    assert tools[1]["executed"] is True
    assert [row["tool_name"] for row in payload["executed_tools"]] == [
        "registered_twin_snapshot",
        "baseline_assessment",
    ]
    assert tools[2] == {
        "tool_name": "counterfactual_simulation",
        "planned": True,
        "executed": False,
        "execution_order": 3,
        "status": "not_executed",
        "validated_arguments": None,
        "result_summary": None,
        "error_details": None,
    }


def test_incomplete_utility_failure_preserves_validated_scenario_rows():
    result = result_for("invalid_service_result")
    result.assessment_path = "counterfactual_comparison"
    scenarios = [
        {"scenario": "No maintenance", "projected_soh": 0.89},
        {"scenario": "Maintenance A", "projected_soh": 0.895},
        {"scenario": "Maintenance B", "projected_soh": 0.90},
    ]
    result.tool_outcomes.append(
        ToolExecutionOutcome(
            "counterfactual_simulation",
            "success",
            3,
            result={"scenarios": scenarios},
        )
    )
    frozen = freeze_decision_payload(
        goal=GoalSpec("g", 10, assessment_scope="counterfactual_comparison"),
        result=result,
        decision_started_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
        planned_tools=(
            "registered_twin_snapshot",
            "baseline_assessment",
            "counterfactual_simulation",
            "maintenance_policy",
        ),
        plan_evidence_available=True,
    )
    persisted = json.loads(frozen.database_json)
    assert [row["scenario_name"] for row in persisted["scenarios"]] == [
        "No maintenance",
        "Maintenance A",
        "Maintenance B",
    ]
    assert persisted["scenarios"][1]["utility"] is None
    assert persisted["scenarios"][1]["feasibility"] is None


def test_unavailable_plan_evidence_is_null_not_an_empty_plan():
    result = result_for()
    frozen = freeze_decision_payload(
        goal=GoalSpec("g", 10),
        result=result,
        decision_started_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
        planned_tools=None,
        plan_evidence_available=False,
    )
    payload = json.loads(frozen.database_json)
    assert payload["planned_tools"] is None
    assert payload["plan_evidence_available"] is False
    assert all(row["planned"] is None for row in payload["executed_tools"])


def test_frozen_payload_preserves_goal_result_nulls_and_numeric_json_values():
    result = result_for(
        candidates=[
            {
                "scenario": "No maintenance",
                "projected_soh": 0.89,
                "utility": None,
                "feasibility_status": "not_applicable_baseline_comparator",
            }
        ],
        ranking={
            "utilities": {"Maintenance A": 0.5},
            "ranked_groups": [["Maintenance A", "Maintenance B"]],
            "feasibility_status": "unknown",
        },
    )
    result.selected_action = None
    frozen = freeze_decision_payload(
        goal=GoalSpec("g", 10, target_soh=0.95),
        result=result,
        decision_started_at=datetime(2026, 1, 2, 3, tzinfo=timezone.utc),
        planned_tools=("registered_twin_snapshot", "baseline_assessment"),
        plan_evidence_available=True,
    )
    payload = json.loads(frozen.database_json)
    assert payload["goal_spec"]["target_soh"] == 0.95
    assert payload["goal_spec"]["diagnostic_evidence"] is None
    assert payload["result"]["selected_action"] is None
    assert payload["scenarios"][0]["utility"] is None
    assert payload["feasibility"] == "unknown"
    assert isinstance(payload["utility_ranking"]["utilities"]["Maintenance A"], float)
    assert payload["created_at_utc"] == "2026-01-02T03:00:00.000000Z"
    assert frozen.payload_digest == __import__("hashlib").sha256(
        frozen.canonical_digest_bytes
    ).hexdigest()
    assert isinstance(frozen.database_json, bytes)
    assert isinstance(frozen.canonical_digest_bytes, bytes)


def test_canonical_digest_is_stable_and_type_aware():
    left = {"z": None, "a": [True, 1, 1.0, "1", {"b": 2, "a": 3}]}
    right = {"a": [True, 1, 1.0, "1", {"a": 3, "b": 2}], "z": None}
    assert canonical_digest_bytes(left) == canonical_digest_bytes(right)
    assert len({
        canonical_digest_bytes({"value": True}),
        canonical_digest_bytes({"value": 1}),
        canonical_digest_bytes({"value": 1.0}),
        canonical_digest_bytes({"value": "1"}),
        canonical_digest_bytes({"value": None}),
    }) == 5


def test_frozen_payload_bytes_do_not_follow_later_goal_or_result_mutations():
    evidence = {"confirmed_fault": False}
    goal = GoalSpec("immutable-goal", 20, diagnostic_evidence=evidence)
    result = result_for()
    frozen = freeze_decision_payload(
        goal=goal,
        result=result,
        decision_started_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
        planned_tools=("registered_twin_snapshot", "baseline_assessment"),
        plan_evidence_available=True,
    )
    database_json = frozen.database_json
    canonical = frozen.canonical_digest_bytes
    digest = frozen.payload_digest

    evidence["confirmed_fault"] = True
    result.snapshot_metadata["version"] = 99
    result.tool_outcomes[0].result["version"] = 99

    assert frozen.database_json is database_json
    assert frozen.canonical_digest_bytes is canonical
    assert frozen.payload_digest == digest
    payload = json.loads(frozen.database_json)
    assert payload["goal_spec"]["diagnostic_evidence"] == {"confirmed_fault": False}
    assert payload["snapshot_metadata"]["version"] == 3
    assert payload["result"]["tool_outcomes"][0]["result"]["version"] == 3


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_canonical_digest_rejects_non_finite_float(value):
    with pytest.raises(ValueError, match="non-finite"):
        canonical_digest_bytes({"value": value})


def test_explanation_preserves_ties_and_unknown_feasibility():
    result = result_for(
        "tie",
        candidates=[
            {"scenario": "No maintenance", "projected_soh": 0.89, "utility": None},
            {"scenario": "Maintenance A", "projected_soh": 0.90, "utility": 1.0},
            {"scenario": "Maintenance B", "projected_soh": 0.90, "utility": 1.0},
        ],
        ranking={
            "ranked_groups": [["Maintenance A", "Maintenance B"]],
            "feasibility_status": "unknown",
        },
    )
    payload = freeze_decision_payload(
        goal=GoalSpec("g", 10),
        result=result,
        decision_started_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
        planned_tools=("registered_twin_snapshot", "baseline_assessment"),
        plan_evidence_available=True,
    )
    explanation = json.loads(payload.database_json)["explanation"]
    assert "Utility tie preserved between: Maintenance A, Maintenance B." in explanation
    assert "Intervention feasibility is unknown; no physical feasibility was established." in explanation
    assert not any("safe" in line.lower() or "recommended" in line.lower() for line in explanation)
