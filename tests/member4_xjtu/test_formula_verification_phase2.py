from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from scripts.member4_xjtu.feature_definitions import FEATURE_NAMES


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "member4"
PHASE2_CSV = REPORT_DIR / "formula_verification_phase2.csv"
PHASE2_SUMMARY = REPORT_DIR / "formula_verification_phase2_summary.json"


def test_phase2_formula_report_has_one_row_per_feature_and_required_fields() -> None:
    with PHASE2_CSV.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))

    assert tuple(row["feature"] for row in rows) == FEATURE_NAMES
    assert set(rows[0]) == {
        "feature",
        "group",
        "original_formula",
        "evidence_status",
        "source_url",
        "source_file",
        "source_page",
        "source_section",
        "implementation_formula",
        "equivalence",
        "discrepancy",
        "notes",
    }
    assert all(row["implementation_formula"] for row in rows)
    assert all(row["source_url"] and row["source_file"] for row in rows)
    assert all(not row["original_formula"] for row in rows)
    assert Counter(row["evidence_status"] for row in rows) == {
        "CANDIDATE_UNVERIFIED": 31,
        "RELATED_METHOD_ONLY": 32,
        "ORIGINAL_FORMULA_UNKNOWN": 4,
    }


def test_phase2_summary_keeps_original_provenance_counts_distinct() -> None:
    summary = json.loads(PHASE2_SUMMARY.read_text(encoding="utf-8"))
    assert summary["feature_count"] == 67
    assert summary["original_formulas_recovered"] == 0
    assert summary["phase2_evidence_status_counts"] == {
        "SOURCE_VERIFIED": 0,
        "PARTIALLY_VERIFIED": 0,
        "RELATED_METHOD_ONLY": 32,
        "CANDIDATE_UNVERIFIED": 31,
        "ORIGINAL_FORMULA_UNKNOWN": 4,
    }
    assert summary["original_formula_provenance_counts"] == {
        "SOURCE_VERIFIED": 0,
        "PARTIALLY_VERIFIED": 0,
        "CANDIDATE_UNVERIFIED": 63,
        "ORIGINAL_FORMULA_UNKNOWN": 4,
    }
