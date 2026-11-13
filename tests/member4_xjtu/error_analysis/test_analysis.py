from __future__ import annotations

import unittest

import numpy as np

from scripts.member4_xjtu.error_analysis.analysis import (
    COHORT_CAPACITY,
    COHORT_POSITIONAL,
    ErrorAccumulator,
    PairedSensitivityAccumulator,
    _alignment_class,
    _metrics,
    _paired_sensitivity_metrics,
    _segment_variant,
    _variant_features,
    _variant_specs,
)
from scripts.member4_xjtu.models import CycleTrace, PhaseSegment, TimeInterval
from scripts.member4_xjtu.segments import SegmentationPolicy, segment_cycle
from scripts.member4_xjtu.extractor import extract_cycle
from scripts.member4_xjtu.feature_definitions import FEATURE_NAMES


def _cycle() -> CycleTrace:
    time = np.arange(12, dtype=np.float64)
    voltage = np.asarray(
        [3.50, 3.60, 3.70, 3.80, 3.90, 3.95, 4.00, 4.08, 4.199, 4.199, 4.199, 4.199]
    )
    current = np.asarray([4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 4.0, 3.0, 2.0, 1.5, 1.0, 0.9])
    temperature = np.asarray([24.0, 24.2, 24.4, 24.7, 25.0, 25.4, 25.9, 26.3, 26.8, 27.1, 27.5, 28.0])
    return CycleTrace(
        batch=1,
        profile="Sheet1",
        cycle_index=1,
        time_min=time,
        voltage_v=voltage,
        current_a=current,
        temperature_c=temperature,
        capacity_label=1.9,
    )


class ErrorAnalysisTests(unittest.TestCase):
    def test_alignment_cohorts_remain_explicitly_unverified(self) -> None:
        self.assertEqual(
            _alignment_class("positional_unverified_equal_counts"),
            COHORT_POSITIONAL,
        )
        self.assertEqual(
            _alignment_class("unique_monotone_capacity_diagnostic"),
            COHORT_CAPACITY,
        )
        with self.assertRaises(ValueError):
            _alignment_class("unknown_alignment")

    def test_metrics_exclude_near_zero_references_from_mape(self) -> None:
        accumulator = ErrorAccumulator()
        accumulator.add(0.0, 2.0)
        accumulator.add(100.0, 110.0)
        accumulator.add(200.0, 220.0)

        result = _metrics(accumulator)

        self.assertEqual(result["valid_observations"], 3)
        self.assertEqual(result["mape_observations"], 2)
        self.assertEqual(result["mape_excluded_near_zero"], 1)
        self.assertAlmostEqual(result["mape_pct"], 10.0)
        self.assertAlmostEqual(result["mean_signed_error"], 32.0 / 3.0)
        self.assertAlmostEqual(result["median_absolute_error"], 10.0)

    def test_candidate_variant_matches_baseline_on_fixed_segment(self) -> None:
        cycle = _cycle()
        segments = segment_cycle(cycle, SegmentationPolicy())
        baseline, _ = extract_cycle(cycle, SegmentationPolicy())

        for group, segment in segments.items():
            candidate = _segment_variant(cycle, group, segment)
            for name, value in candidate.items():
                if name in FEATURE_NAMES and value is not None:
                    self.assertAlmostEqual(value, baseline[name], places=10, msg=name)

    def test_time_unit_sensitivity_is_a_declared_diagnostic(self) -> None:
        cycle = _cycle()
        segment = PhaseSegment(
            "Charge",
            (TimeInterval(0.0, 11.0),),
            "test",
            "test",
            "test",
            np.ones(len(cycle.time_min), dtype=bool),
        )
        baseline = _segment_variant(cycle, "Charge", segment)
        seconds = _segment_variant(
            cycle, "Charge", segment, time_unit="seconds"
        )

        self.assertAlmostEqual(seconds["Charge_t_mean"], baseline["Charge_t_mean"] * 60)
        self.assertAlmostEqual(seconds["Charge_Q"], baseline["Charge_Q"] / 60)

    def test_sensitivity_delta_uses_common_valid_observations(self) -> None:
        accumulator = PairedSensitivityAccumulator()
        accumulator.add(10.0, 9.0, 8.0)
        accumulator.add(20.0, None, 18.0)

        baseline, variant = _paired_sensitivity_metrics(accumulator)

        self.assertEqual(baseline["valid_observations"], 1)
        self.assertEqual(variant["valid_observations"], 1)
        self.assertEqual(baseline["invalid_candidate"], 1)
        self.assertAlmostEqual(baseline["mae"], 1.0)
        self.assertAlmostEqual(variant["mae"], 2.0)

    def test_sensitivity_specs_are_fixed_and_entropy_labeled_diagnostic(self) -> None:
        specs = _variant_specs()
        names = {spec["variant"] for spec in specs}
        self.assertIn("author_documented_cc_selector", names)
        self.assertIn("left_rectangle_integrals", names)
        entropy = [spec for spec in specs if spec["axis"] == "entropy proxy"]
        self.assertTrue(entropy)
        self.assertTrue(all("proxy" in spec["evidence_class"] for spec in entropy))
        self.assertEqual(
            _variant_features("entropy_bits"),
            {name for name in FEATURE_NAMES if name.endswith("_entropy")},
        )


if __name__ == "__main__":
    unittest.main()
