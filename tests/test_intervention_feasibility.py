from digital_twin.intervention_feasibility import (
    RULE_ID,
    RULE_VERSION,
    assess_intervention_feasibility,
    recommend_highest_utility_feasible,
)


def documented_definition(*, effect="require", expected="recorded"):
    return {
        "definition_id": "hypothetical-scenario",
        "definition_version": "test-v1",
        "documentation_ref": "test-only abstract scenario documentation",
        "rules": [{
            "rule_id": "test-record-rule",
            "evidence_key": "abstract_record",
            "expected_value": expected,
            "effect": effect,
            "accepted_sources": ["test_fixture"],
            "documentation_ref": "test-only abstract eligibility rule",
            "explanation": "The abstract test rule was not satisfied.",
        }],
    }


def evidence(value):
    return {
        "abstract_record": {
            "value": value,
            "provenance": {"source": "test_fixture", "verification": "fixture"},
        }
    }


def test_undocumented_maintenance_scenarios_remain_unknown():
    for name in ("Maintenance A", "Maintenance B"):
        result = assess_intervention_feasibility(name, None, {})
        assert result["status"] == "unknown"
        assert result["rule_id"] == RULE_ID
        assert result["rule_version"] == RULE_VERSION
        assert result["missing_evidence"] == [
            "documented_intervention_definition",
            "documented_eligibility_requirements",
        ]
        assert result["evidence_used"] == []
        assert result["is_physical_safety_validation"] is False
        assert result["proves_maintenance_effectiveness"] is False


def test_documented_abstract_requirement_can_be_model_feasible():
    result = assess_intervention_feasibility(
        "Hypothetical candidate", documented_definition(), evidence("recorded")
    )
    assert result["status"] == "feasible"
    assert result["evidence_used"][0]["provenance"]["source"] == "test_fixture"
    assert result["missing_evidence"] == []


def test_documented_abstract_requirement_can_be_model_infeasible():
    result = assess_intervention_feasibility(
        "Hypothetical candidate", documented_definition(), evidence("absent")
    )
    assert result["status"] == "infeasible"
    assert result["reasons"][0]["code"] == "documented_rule_not_satisfied"


def test_missing_or_unaccepted_evidence_is_unknown():
    result = assess_intervention_feasibility(
        "Hypothetical candidate", documented_definition(), {}
    )
    assert result["status"] == "unknown"
    assert result["missing_evidence"] == ["abstract_record"]


def test_only_unique_highest_utility_feasible_candidate_is_recommended():
    eligible = assess_intervention_feasibility(
        "Hypothetical candidate", documented_definition(), evidence("recorded")
    )
    result = recommend_highest_utility_feasible(
        {"Hypothetical candidate": 1.0, "Unknown candidate": 5.0},
        {"Hypothetical candidate": eligible, "Unknown candidate": {"status": "unknown"}},
    )
    assert result["status"] == "recommended"
    assert result["candidate"] == "Hypothetical candidate"
    assert result["is_physical_safety_validation"] is False
    assert result["proves_maintenance_effectiveness"] is False


def test_tied_or_empty_feasible_set_produces_no_recommendation():
    feasible = assess_intervention_feasibility(
        "Hypothetical candidate", documented_definition(), evidence("recorded")
    )
    tied = recommend_highest_utility_feasible(
        {"A": 1.0, "B": 1.0}, {"A": feasible, "B": feasible}
    )
    empty = recommend_highest_utility_feasible({"A": 1.0}, {"A": {"status": "infeasible"}})
    assert tied["status"] == empty["status"] == "no_recommendation"
    assert tied["candidate"] is empty["candidate"] is None
