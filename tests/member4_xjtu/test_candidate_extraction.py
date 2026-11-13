from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from scripts.member4_xjtu.extractor import extract_cycle, extract_cycle_with_details
from scripts.member4_xjtu.feature_definitions import FEATURE_NAMES, feature_definitions
from scripts.member4_xjtu.models import CycleTrace
from scripts.member4_xjtu.segments import SegmentationPolicy, segment_cycle
from scripts.member4_xjtu.validation import _profile_pairs


def synthetic_cycle() -> CycleTrace:
    time = np.linspace(0.0, 12.7, 128)
    voltage = np.concatenate(
        (np.linspace(3.5, 4.2, 86), np.full(42, 4.2))
    )
    current = np.full(128, 4.0)
    current[90:] = np.linspace(3.8, 0.1, 38)
    temperature = 25.0 + 0.1 * time
    return CycleTrace(
        batch=1,
        profile="synthetic",
        cycle_index=1,
        time_min=time,
        voltage_v=voltage,
        current_a=current,
        temperature_c=temperature,
        capacity_label=1.8,
    )


class CandidateExtractionTests(unittest.TestCase):
    def test_feature_schema_is_67_unique_names(self) -> None:
        definitions = feature_definitions()
        self.assertEqual(len(FEATURE_NAMES), 67)
        self.assertEqual(len({definition.name for definition in definitions}), 67)
        self.assertEqual(
            sum(definition.evidence_class == "unknown_original_definition" for definition in definitions),
            4,
        )

    def test_candidate_segments_and_values_are_explicit(self) -> None:
        cycle = synthetic_cycle()
        segments = segment_cycle(cycle, SegmentationPolicy())
        self.assertTrue(segments["CC"].intervals)
        self.assertTrue(segments["CV"].intervals)
        self.assertTrue(segments["dV"].intervals)
        self.assertTrue(segments["dI"].intervals)
        values, _ = extract_cycle(cycle)
        detailed_values, detailed_segments, details = extract_cycle_with_details(cycle)
        self.assertEqual(set(values), set(FEATURE_NAMES))
        self.assertEqual(values, detailed_values)
        self.assertEqual(set(segments), set(detailed_segments))
        for group in segments:
            np.testing.assert_array_equal(
                segments[group].selected_mask,
                detailed_segments[group].selected_mask,
            )
            self.assertEqual(segments[group].intervals, detailed_segments[group].intervals)
        self.assertEqual(
            details["CC_CCCT"]["operation"], "sum_of_interval_durations"
        )
        self.assertEqual(details["dV_dV_devide_dt"]["operation"], "candidate_endpoint_rate")
        self.assertEqual(details["CV_CVCT"]["operation"], "sum_of_interval_durations")
        self.assertEqual(details["dI_dI_devide_dt"]["operation"], "candidate_endpoint_rate")
        for name in ("CC_entropy", "dV_entropy", "CV_entropy", "dI_entropy"):
            self.assertEqual(details[name]["operation"], "entropy")
            self.assertEqual(
                len(details[name]["nonzero_bin_indices"]),
                len(details[name]["nonzero_bin_counts"]),
            )
        self.assertTrue(np.isfinite(values["CC_energy"]))
        self.assertTrue(np.isfinite(values["Charge_Q"]))
        self.assertEqual(
            feature_definitions()[-1].formula_status,
            "Original formula implementation not located; candidate approximation only.",
        )

    def test_missing_candidate_window_is_not_fabricated(self) -> None:
        cycle = synthetic_cycle()
        voltage = np.linspace(3.5, 3.8, 128)
        no_cv = CycleTrace(
            batch=1,
            profile="synthetic",
            cycle_index=1,
            time_min=cycle.time_min,
            voltage_v=voltage,
            current_a=cycle.current_a,
            temperature_c=cycle.temperature_c,
            capacity_label=cycle.capacity_label,
        )
        values, segments = extract_cycle(no_cv)
        self.assertFalse(segments["CV"].intervals)
        self.assertIsNone(values["CV_energy"])
        self.assertIsNone(values["dI_dI_devide_dt"])

    def test_integration_uses_irregular_timestamps(self) -> None:
        cycle = CycleTrace(
            batch=1,
            profile="synthetic",
            cycle_index=1,
            time_min=np.array([0.0, 1.0, 3.0]),
            voltage_v=np.array([4.0, 4.0, 4.0]),
            current_a=np.array([2.0, 2.0, 2.0]),
            temperature_c=np.array([25.0, 25.0, 25.0]),
            capacity_label=1.8,
        )
        values, _ = extract_cycle(cycle)
        self.assertAlmostEqual(values["Charge_Q"], 0.1)
        self.assertAlmostEqual(values["Charge_energy"], 0.4)

    def test_duplicate_capacity_matches_are_left_unmatched(self) -> None:
        base = synthetic_cycle()
        cycles = [
            CycleTrace(
                batch=1,
                profile="synthetic",
                cycle_index=index,
                time_min=base.time_min,
                voltage_v=base.voltage_v,
                current_a=base.current_a,
                temperature_c=base.temperature_c,
                capacity_label=1.8,
            )
            for index in (1, 2)
        ]
        pairs, method, unmatched, ambiguous = _profile_pairs(
            cycles, pd.DataFrame({"label": [1.8]})
        )
        self.assertEqual(pairs, [])
        self.assertEqual(method, "unique_monotone_capacity_diagnostic")
        self.assertEqual(unmatched, [0])
        self.assertEqual(ambiguous, [0])

    def test_author_documented_cc_rule_is_distinct_from_adaptive_candidate(self) -> None:
        cycle = synthetic_cycle()
        adaptive = segment_cycle(cycle, SegmentationPolicy(cc_method="adaptive_candidate"))
        documented = segment_cycle(cycle, SegmentationPolicy(cc_method="author_documented"))
        self.assertEqual(adaptive["CC"].selection_method, "adaptive_candidate")
        self.assertEqual(
            documented["CC"].selection_method, "author_documented_helper_selector"
        )
        self.assertIn("not workbook formula evidence", documented["CC"].evidence)


if __name__ == "__main__":
    unittest.main()
