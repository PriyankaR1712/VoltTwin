from __future__ import annotations

import unittest

import numpy as np

from scripts.member4_xjtu.original_verification.report import (
    FeaturePairs,
    _correlation,
    summarize_pairs,
)


class OriginalVerificationMetricTests(unittest.TestCase):
    def test_candidate_metrics_include_errors_and_correlations(self) -> None:
        pairs = FeaturePairs()
        for actual, candidate in ((1.0, 2.0), (2.0, 4.0), (3.0, 6.0)):
            pairs.add(actual, candidate)

        result = summarize_pairs(pairs)

        self.assertEqual(result["aligned_pairs"], 3)
        self.assertEqual(result["valid_pairs"], 3)
        self.assertEqual(result["mae"], 2.0)
        self.assertAlmostEqual(result["rmse"], np.sqrt(14 / 3))
        self.assertAlmostEqual(result["pearson_r"], 1.0)
        self.assertAlmostEqual(result["spearman_rho"], 1.0)
        self.assertAlmostEqual(result["relative_error_pct"], 100.0)

    def test_invalid_values_are_counted_separately_and_excluded(self) -> None:
        pairs = FeaturePairs()
        pairs.add(None, 1.0)
        pairs.add(2.0, None)
        pairs.add(3.0, 4.0)

        result = summarize_pairs(pairs)

        self.assertEqual(result["aligned_pairs"], 3)
        self.assertEqual(result["valid_pairs"], 1)
        self.assertEqual(result["workbook_invalid"], 1)
        self.assertEqual(result["candidate_invalid"], 1)
        self.assertIsNone(result["pearson_r"])
        self.assertIsNone(result["spearman_rho"])

    def test_relative_error_is_unavailable_for_zero_reference_scale(self) -> None:
        pairs = FeaturePairs()
        pairs.add(0.0, 1.0)
        pairs.add(0.0, 2.0)

        result = summarize_pairs(pairs)

        self.assertEqual(result["mae"], 1.5)
        self.assertIsNone(result["relative_error_pct"])

    def test_correlations_are_undefined_for_constant_series(self) -> None:
        pearson, spearman = _correlation(
            np.asarray([1.0, 1.0, 1.0]),
            np.asarray([2.0, 3.0, 4.0]),
        )

        self.assertIsNone(pearson)
        self.assertIsNone(spearman)


if __name__ == "__main__":
    unittest.main()
