from __future__ import annotations

import unittest

from scripts.member4_xjtu.cycle_identity.identity_investigation import (
    _identifier_columns,
    capacity_label_agreement,
)


class CapacityLabelAgreementTests(unittest.TestCase):
    def test_equal_counts_report_tolerance_counts_without_identity_claim(self) -> None:
        result = capacity_label_agreement(
            [1.0, 1.1, 1.2],
            [1.0, 1.1004, 1.202],
            tolerances=(1e-6, 5e-4, 1e-3),
        )

        self.assertTrue(result["counts_equal"])
        self.assertEqual(result["compared_pairs"], 3)
        self.assertEqual(result["matches_within_1e-06"], 1)
        self.assertEqual(result["matches_within_0.0005"], 2)
        self.assertEqual(result["matches_within_0.001"], 2)
        self.assertAlmostEqual(result["max_abs_label_delta"], 0.002)
        self.assertNotIn("identity_verified", result)

    def test_unequal_counts_do_not_create_positional_pairs(self) -> None:
        result = capacity_label_agreement([1.0, 1.1, 1.2], [1.0, 1.1])

        self.assertFalse(result["counts_equal"])
        self.assertEqual(result["compared_pairs"], 0)
        self.assertIsNone(result["mean_abs_label_delta"])
        self.assertIsNone(result["matches_within_1e-06"])

    def test_non_finite_capacity_values_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            capacity_label_agreement([1.0, float("nan")], [1.0, 1.1])

    def test_elapsed_time_is_not_mistaken_for_an_absolute_timestamp(self) -> None:
        self.assertEqual(
            _identifier_columns(
                ["relative_time_min", "cycle_index", "system_time", "CC_t_mean"]
            ),
            ["cycle_index", "system_time"],
        )


if __name__ == "__main__":
    unittest.main()
