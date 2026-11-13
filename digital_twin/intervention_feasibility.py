"""Deterministic feasibility checks against documented abstract rules.

This framework evaluates model-based eligibility only. It does not validate
physical battery safety or prove that a simulated intervention is effective.
"""

from __future__ import annotations

from typing import Any, Mapping


RULE_ID = "documented_intervention_eligibility"
RULE_VERSION = "v1"
MODEL_BASED_LABEL = "model_based_not_physical_safety_or_effectiveness_validation"

# Intentionally empty: the project defines no service procedure or eligibility
# rules for its hypothetical Maintenance A/B recovery scenarios.
DOCUMENTED_INTERVENTION_RULES: dict[str, dict[str, Any]] = {}


def assess_intervention_feasibility(
    candidate: str,
    definition: Mapping[str, Any] | None,
    evidence: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Evaluate exact-value requirements/exclusions in a documented contract.

    Each rule must declare a rule ID, evidence key, expected value, effect
    (``require`` or ``exclude``), accepted evidence sources, and documentation
    reference. Evidence sources and constraints are supplied by documented
    definitions; this module invents no battery-specific thresholds.
    """
    evidence_available = []
    evidence_provenance = []
    for key, record in evidence.items():
        if not isinstance(record, Mapping) or "value" not in record:
            continue
        provenance = record.get("provenance")
        provenance = dict(provenance) if isinstance(provenance, Mapping) else None
        evidence_available.append({
            "evidence_key": key,
            "value": record["value"],
            "provenance": provenance,
        })
        if provenance is not None:
            evidence_provenance.append({"evidence_key": key, **provenance})
    result = {
        "status": "unknown",
        "rule_id": RULE_ID,
        "rule_version": RULE_VERSION,
        "candidate": candidate,
        "definition_id": None,
        "definition_version": None,
        "reasons": [],
        "evidence_used": [],
        "evidence_available": evidence_available,
        "evidence_provenance": evidence_provenance,
        "missing_evidence": [],
        "explanation": "Model-based eligibility only; not physical safety validation or proof of maintenance effectiveness.",
        "assessment_label": MODEL_BASED_LABEL,
        "is_physical_safety_validation": False,
        "proves_maintenance_effectiveness": False,
    }
    if not isinstance(definition, Mapping):
        result["reasons"].append({
            "code": "intervention_definition_undocumented",
            "explanation": f"{candidate} has no documented intervention definition.",
        })
        result["missing_evidence"] = [
            "documented_intervention_definition",
            "documented_eligibility_requirements",
        ]
        result["explanation"] = (
            f"{candidate} remains unknown because its intervention definition "
            "and eligibility requirements are undocumented."
        )
        return result

    definition_id = definition.get("definition_id")
    definition_version = definition.get("definition_version")
    documentation_ref = definition.get("documentation_ref")
    rules = definition.get("rules")
    result["definition_id"] = definition_id
    result["definition_version"] = definition_version
    if not all(isinstance(value, str) and value.strip() for value in (
        definition_id, definition_version, documentation_ref
    )) or not isinstance(rules, list) or not rules:
        result["reasons"].append({
            "code": "eligibility_requirements_undocumented",
            "explanation": f"{candidate} has no complete, sourced eligibility rule set.",
        })
        result["missing_evidence"] = ["complete_sourced_eligibility_rules"]
        result["explanation"] = (
            f"{candidate} remains unknown because its eligibility rules are "
            "missing or incomplete."
        )
        return result

    missing: list[str] = []
    failed: list[dict[str, str]] = []
    invalid_rules: list[str] = []
    used: list[dict[str, Any]] = []
    for rule in rules:
        if not isinstance(rule, Mapping):
            invalid_rules.append("rule_not_an_object")
            continue
        rule_id = rule.get("rule_id")
        key = rule.get("evidence_key")
        expected = rule.get("expected_value")
        effect = rule.get("effect")
        accepted = rule.get("accepted_sources")
        source_ref = rule.get("documentation_ref")
        if (
            not isinstance(rule_id, str) or not rule_id.strip()
            or not isinstance(key, str) or not key.strip()
            or not isinstance(effect, str) or effect not in {"require", "exclude"}
            or "expected_value" not in rule
            or not isinstance(accepted, list) or not accepted
            or any(not isinstance(item, str) or not item.strip() for item in accepted)
            or not isinstance(source_ref, str) or not source_ref.strip()
        ):
            invalid_rules.append(str(rule_id or "unnamed_rule"))
            continue

        record = evidence.get(key)
        if not isinstance(record, Mapping) or "value" not in record:
            missing.append(key)
            continue
        source = record.get("provenance")
        if not isinstance(source, Mapping) or source.get("source") not in accepted:
            missing.append(key)
            continue
        used.append({
            "evidence_key": key,
            "value": record["value"],
            "provenance": dict(source),
            "rule_id": rule_id,
            "documentation_ref": source_ref,
        })
        matched = record["value"] == expected
        violated = (effect == "require" and not matched) or (
            effect == "exclude" and matched
        )
        if violated:
            failed.append({
                "code": "documented_rule_not_satisfied",
                "rule_id": rule_id,
                "explanation": str(rule.get("explanation") or f"Documented rule {rule_id} was not satisfied."),
            })

    result["evidence_used"] = used
    result["missing_evidence"] = sorted(set(missing))
    if invalid_rules:
        result["reasons"].append({
            "code": "eligibility_rule_invalid",
            "explanation": "One or more eligibility rules are incomplete or malformed.",
        })
    result["reasons"].extend(failed)
    if failed:
        result["status"] = "infeasible"
        result["explanation"] = "At least one documented eligibility rule is not satisfied; this is a model-based result only."
    elif missing or invalid_rules:
        result["status"] = "unknown"
        if missing:
            result["reasons"].append({
                "code": "required_evidence_missing_or_unaccepted",
                "explanation": "Required evidence is absent or its provenance is not accepted by the documented rule.",
            })
        result["explanation"] = "Feasibility is unknown because required evidence or valid documented rules are missing."
    else:
        result["status"] = "feasible"
        result["reasons"].append({
            "code": "all_documented_rules_satisfied",
            "explanation": "All supplied, documented model eligibility rules passed.",
        })
        result["explanation"] = "All documented model eligibility rules passed; this is not physical safety validation or proof of effectiveness."
    return result


def recommend_highest_utility_feasible(
    utilities: Mapping[str, float], feasibility: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Recommend only a unique highest-utility candidate marked feasible."""
    eligible = [
        (name, utility)
        for name, utility in utilities.items()
        if _passed_documented_rules(feasibility.get(name))
    ]
    base = {
        "recommendation_type": "model_based_candidate_recommendation",
        "is_physical_safety_validation": False,
        "proves_maintenance_effectiveness": False,
    }
    if not eligible:
        return {
            **base, "status": "no_recommendation", "candidate": None,
            "reason": "No candidate passed all documented eligibility rules.",
        }
    highest = max(value for _, value in eligible)
    winners = [name for name, value in eligible if value == highest]
    if len(winners) != 1:
        return {
            **base, "status": "no_recommendation", "candidate": None,
            "reason": "The highest-utility feasible candidates are tied.",
            "tied_candidates": sorted(winners),
        }
    return {
        **base, "status": "recommended", "candidate": winners[0],
        "reason": "This candidate uniquely ranks highest by simulated utility among candidates passing all documented model eligibility rules.",
        "utility": highest,
    }


def _passed_documented_rules(assessment: Mapping[str, Any] | None) -> bool:
    if not isinstance(assessment, Mapping):
        return False
    return (
        assessment.get("status") == "feasible"
        and assessment.get("rule_id") == RULE_ID
        and assessment.get("rule_version") == RULE_VERSION
        and isinstance(assessment.get("definition_id"), str)
        and bool(assessment.get("definition_id", "").strip())
        and isinstance(assessment.get("definition_version"), str)
        and bool(assessment.get("definition_version", "").strip())
        and assessment.get("missing_evidence") == []
        and any(
            isinstance(reason, Mapping)
            and reason.get("code") == "all_documented_rules_satisfied"
            for reason in assessment.get("reasons", [])
        )
    )
