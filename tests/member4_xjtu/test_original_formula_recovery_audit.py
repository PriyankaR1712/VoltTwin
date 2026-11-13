from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from backend.formula_explorer_api import get_formula_features
from scripts.member4_xjtu.feature_definitions import FEATURE_NAMES

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
AUDIT_CSV = REPOSITORY_ROOT / "reports" / "member4" / "original_formula_recovery.csv"
AUDIT_SUMMARY = (
    REPOSITORY_ROOT / "reports" / "member4" / "original_formula_recovery_summary.json"
)


def test_original_formula_audit_covers_all_features_without_overclaiming() -> None:
    with AUDIT_CSV.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    summary = json.loads(AUDIT_SUMMARY.read_text(encoding="utf-8"))

    assert tuple(row["feature_name"] for row in rows) == FEATURE_NAMES
    counts = Counter(row["verification_status"] for row in rows)
    assert counts == {
        "CANDIDATE_UNVERIFIED": 63,
        "ORIGINAL_FORMULA_UNKNOWN": 4,
    }
    assert all(not row["original_formula"] for row in rows)
    assert all(row["original_source_location"] for row in rows)
    assert summary["original_formulas_recovered"] == 0
    assert summary["status_counts"] == {
        "SOURCE_VERIFIED": 0,
        "PARTIALLY_VERIFIED": 0,
        "CANDIDATE_UNVERIFIED": 63,
        "ORIGINAL_FORMULA_UNKNOWN": 4,
    }


def test_formula_explorer_keeps_candidate_and_original_provenance_distinct() -> None:
    response = get_formula_features()

    assert response["count"] == len(FEATURE_NAMES) == 67
    assert response["source_verified_count"] == 0
    assert "not author-confirmed" in response["notice"]
    assert tuple(item["name"] for item in response["features"]) == FEATURE_NAMES
    assert all(
        item["original_benchmark_formula"]
        == "Unavailable — original formula not verified."
        for item in response["features"]
    )
    assert all(item["candidate_formula"] for item in response["features"])
    assert Counter(item["status"] for item in response["features"]) == {
        "candidate_unverified": 63,
        "original_formula_unknown": 4,
    }
