from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.member4_xjtu.formula_recovery.recover import (
    ENTROPY_NAMES,
    STATUSES,
    feature_evidence_rows,
    generate_outputs,
)
from scripts.member4_xjtu.feature_definitions import FEATURE_NAMES


class FormulaRecoveryEvidenceTests(unittest.TestCase):
    def test_feature_ledger_covers_canonical_schema_without_verified_claims(self) -> None:
        rows = feature_evidence_rows()

        self.assertEqual(len(rows), 67)
        self.assertEqual(tuple(row["feature"] for row in rows), FEATURE_NAMES)
        self.assertEqual(
            {row["status"] for row in rows},
            {"Candidate/unverified", "Original formula unavailable"},
        )
        self.assertTrue(all(row["original_formula"].startswith("Not located") for row in rows))
        self.assertTrue(all(not row["source_equation_reference"] for row in rows))
        self.assertFalse(any(row["status"] == "Source verified" for row in rows))
        self.assertEqual(
            {row["feature"] for row in rows if row["status"] == "Original formula unavailable"},
            set(ENTROPY_NAMES),
        )

    def test_output_generation_writes_all_tables_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output_dir = root / "tables"
            report_path = root / "report.md"

            counts = generate_outputs(output_dir, report_path)

            self.assertEqual(counts["features"], 67)
            self.assertEqual(counts["entropy_features"], 4)
            self.assertTrue(report_path.is_file())
            self.assertIn("Candidate interpretation only", report_path.read_text(encoding="utf-8"))
            self.assertIn("No original source implementation", report_path.read_text(encoding="utf-8"))
            for name in (
                "feature_evidence.csv",
                "entropy_evidence.csv",
                "source_evidence.csv",
                "search_log.csv",
                "status_summary.json",
            ):
                self.assertTrue((output_dir / name).is_file(), name)

    def test_status_vocabulary_is_explicit(self) -> None:
        self.assertEqual(
            STATUSES,
            (
                "Source verified",
                "Partially verified",
                "Candidate/unverified",
                "Original formula unavailable",
            ),
        )


if __name__ == "__main__":
    unittest.main()
