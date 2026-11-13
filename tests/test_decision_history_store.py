import sqlite3
from datetime import datetime, timezone

import pytest

from backend.decision_history_serializer import freeze_decision_payload
from backend.decision_history_store import DecisionHistoryStore, decode_cursor, encode_cursor
from digital_twin.decision_models import ExperimentalDecisionResult, ToolExecutionOutcome
from digital_twin.goal_spec import GoalSpec


def payload(decision_id="d1", created_at=None, *, battery_id="battery-1", goal_id="g"):
    result = ExperimentalDecisionResult(
        decision_id=decision_id,
        battery_id=battery_id,
        assessment_path="baseline_only",
        termination_status="completed",
        goal_status="target_unavailable",
        selected_action="no_intervention_selected",
        candidate_evaluations=[
            {
                "scenario": "No maintenance",
                "projected_soh": 0.88,
                "utility": None,
                "feasibility_status": "not_applicable_baseline_comparator",
            }
        ],
        policy_comparison={"status": "not_applicable_baseline_only"},
        snapshot_metadata={"version": 2},
        tool_outcomes=[
            ToolExecutionOutcome(
                "registered_twin_snapshot", "success", 1,
                result={"battery_id": battery_id, "version": 2},
            ),
            ToolExecutionOutcome(
                "baseline_assessment", "success", 2,
                result={
                    "scenario": "No maintenance",
                    "snapshot_version": 2,
                    "projected_soh": 0.88,
                },
            ),
        ],
    )
    return freeze_decision_payload(
        goal=GoalSpec(goal_id, 10),
        result=result,
        decision_started_at=created_at or datetime(2026, 1, 1, tzinfo=timezone.utc),
        planned_tools=("registered_twin_snapshot", "baseline_assessment"),
        plan_evidence_available=True,
    )


@pytest.fixture
def store(tmp_path):
    return DecisionHistoryStore(tmp_path / "decision_history.db")


def test_schema_initializes_with_foreign_keys_indexes_and_version(store):
    with sqlite3.connect(store.database_path) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 0
        # Foreign-key enforcement is enabled on each store-owned connection.
    with store._connect() as connection:
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        names = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
    assert {"decision_records", "decision_tool_outcomes", "decision_scenarios"} <= names


def test_save_and_identical_payload_retry_return_saved_then_already_saved(store):
    item = payload()
    assert store.save(item) == "saved"
    assert store.save(item) == "already_saved"
    record = store.get_decision("d1")
    assert record["decision_id"] == "d1"
    assert record["decision_status"] == "completed"
    assert record["termination_status"] == "completed"
    assert len(record["tool_outcomes"]) == 2
    assert len(record["scenarios"]) == 1
    assert isinstance(record["scenarios"][0]["projected_soh"], float)


def test_persisted_records_match_agent_api_response_models(store):
    from backend.agent_api import DecisionDetailResponse, DecisionListResponse

    store.save(payload())
    detail = store.get_decision("d1")
    listing = store.list_decisions("battery-1")
    assert DecisionDetailResponse.model_validate(detail).decision_id == "d1"
    assert DecisionListResponse.model_validate(listing).items[0].goal_id == "g"


def test_model_feasibility_round_trips_without_schema_change(store):
    assessment = {
        "status": "unknown",
        "rule_id": "documented_intervention_eligibility",
        "rule_version": "v1",
        "reasons": [{"code": "intervention_definition_undocumented"}],
        "evidence_used": [],
        "evidence_provenance": [],
        "missing_evidence": ["documented_intervention_definition"],
        "assessment_label": "model_based_not_physical_safety_or_effectiveness_validation",
        "is_physical_safety_validation": False,
        "proves_maintenance_effectiveness": False,
    }
    result = ExperimentalDecisionResult(
        decision_id="feasibility-round-trip",
        battery_id="battery-1",
        assessment_path="counterfactual_comparison",
        termination_status="completed",
        goal_status="target_unavailable",
        candidate_evaluations=[
            {"scenario": "No maintenance", "projected_soh": 0.89,
             "feasibility_status": "not_applicable_baseline_comparator"},
            {"scenario": "Maintenance A", "projected_soh": 0.90,
             "utility": 1.0, "feasibility_status": "unknown", "feasibility": assessment},
        ],
        utility_ranking={"utilities": {"Maintenance A": 1.0}, "ranked_groups": [["Maintenance A"]]},
        intervention_feasibility={"Maintenance A": assessment},
        final_recommendation={"status": "no_recommendation", "candidate": None,
                              "reason": "No candidate passed documented rules."},
        policy_comparison={"status": "available", "policy_recommended_scenario": "Maintenance A"},
        snapshot_metadata={"version": 2},
        tool_outcomes=[
            ToolExecutionOutcome("registered_twin_snapshot", "success", 1,
                                 result={"battery_id": "battery-1", "version": 2}),
            ToolExecutionOutcome("baseline_assessment", "success", 2,
                                 result={"scenario": "No maintenance", "snapshot_version": 2,
                                         "projected_soh": 0.89}),
            ToolExecutionOutcome("counterfactual_simulation", "success", 3,
                                 result={"scenarios": [
                                     {"scenario": "No maintenance", "projected_soh": 0.89},
                                     {"scenario": "Maintenance A", "projected_soh": 0.90},
                                 ]}),
        ],
    )
    frozen = freeze_decision_payload(
        goal=GoalSpec("g", 10, assessment_scope="counterfactual_comparison"),
        result=result,
        decision_started_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        planned_tools=("registered_twin_snapshot", "baseline_assessment",
                       "counterfactual_simulation", "maintenance_policy"),
        plan_evidence_available=True,
    )
    assert store.save(frozen) == "saved"
    record = store.get_decision("feasibility-round-trip")
    assert record["feasibility"]["Maintenance A"] == assessment
    scenario = next(row for row in record["scenarios"] if row["scenario_name"] == "Maintenance A")
    assert scenario["feasibility"] == assessment
    assert scenario["result_data"]["feasibility"]["missing_evidence"] == [
        "documented_intervention_definition"
    ]
    assert record["final_decision"]["model_based_recommendation"]["status"] == "no_recommendation"


def test_same_id_with_different_frozen_content_is_conflict(store):
    assert store.save(payload(goal_id="original")) == "saved"
    assert store.save(payload(goal_id="changed")) == "idempotency_conflict"
    assert store.get_decision("d1")["goal_spec"]["goal_id"] == "original"


def test_child_failure_rolls_back_parent_and_all_children(store, monkeypatch):
    def fail_scenarios(_connection, _rows):
        raise RuntimeError("injected child insert failure")

    monkeypatch.setattr(store, "_insert_scenario_rows", fail_scenarios)
    with pytest.raises(RuntimeError, match="injected"):
        store.save(payload())
    assert store.get_decision("d1") is None


def test_transient_lock_retry_reuses_same_prepared_payload(store, monkeypatch):
    prepared_objects = []
    original = store._write_transaction

    def fail_once(prepared):
        prepared_objects.append(prepared)
        if len(prepared_objects) == 1:
            raise sqlite3.OperationalError("database is locked")
        return original(prepared)

    monkeypatch.setattr(store, "_write_transaction", fail_once)
    monkeypatch.setattr("backend.decision_history_store.time.sleep", lambda _delay: None)
    frozen = payload()
    assert store.save(frozen) == "saved"
    assert len(prepared_objects) == 2
    assert prepared_objects[0] is prepared_objects[1]
    assert prepared_objects[0].database_json is frozen.database_json
    assert prepared_objects[0].payload_digest == frozen.payload_digest


def test_history_paginates_by_descending_composite_cursor_with_timestamp_ties(store):
    timestamp = datetime(2026, 2, 3, 4, 5, tzinfo=timezone.utc)
    for decision_id in ("d1", "d2", "d3"):
        assert store.save(payload(decision_id, timestamp)) == "saved"

    first = store.list_decisions("battery-1", limit=2)
    assert [item["decision_id"] for item in first["items"]] == ["d3", "d2"]
    assert first["has_more"] is True
    second = store.list_decisions("battery-1", limit=2, cursor=first["next_cursor"])
    assert [item["decision_id"] for item in second["items"]] == ["d1"]
    assert second["has_more"] is False
    assert second["next_cursor"] is None


def test_empty_history_missing_detail_and_invalid_pagination(store):
    assert store.list_decisions("unknown") == {
        "items": [],
        "next_cursor": None,
        "has_more": False,
    }
    assert store.get_decision("missing") is None
    with pytest.raises(ValueError, match="limit"):
        store.list_decisions("battery-1", limit=True)
    with pytest.raises(ValueError, match="cursor"):
        store.list_decisions("battery-1", cursor="not a cursor!")
    with pytest.raises(ValueError, match="cursor"):
        decode_cursor(encode_cursor("not-a-timestamp", "d1"))
