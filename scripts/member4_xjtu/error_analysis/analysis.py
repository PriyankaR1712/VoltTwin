from __future__ import annotations

import argparse
import csv
import gzip
import math
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import rankdata

from scripts.member4_xjtu.extractor import (
    _interval_arrays,
    extract_cycle,
)
from scripts.member4_xjtu.feature_definitions import (
    FEATURE_NAMES,
    GROUPS,
    feature_definitions,
)
from scripts.member4_xjtu.loader import DEFAULT_DATA_ROOT, load_batch
from scripts.member4_xjtu.models import CycleTrace, PhaseSegment, TimeInterval
from scripts.member4_xjtu.segments import SegmentationPolicy
from scripts.member4_xjtu.validation import _profile_pairs


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = ROOT / "reports" / "member4_feature_error_analysis"
DEFAULT_REPORT = ROOT / "reports" / "member4_feature_error_analysis.md"
COHORT_POSITIONAL = "positional_unverified"
COHORT_CAPACITY = "capacity_match_diagnostic"
COHORTS = (COHORT_POSITIONAL, COHORT_CAPACITY)
MAPE_FLOOR_FRACTION = 0.01
MAPE_ABSOLUTE_FLOOR = 1e-12
CYCLE_ERROR_HEADER = [
    "alignment_cohort",
    "alignment_method",
    "batch",
    "profile",
    "workbook_row",
    "raw_cycle_index",
    "feature",
    "benchmark_value",
    "candidate_value",
    "signed_error_candidate_minus_benchmark",
    "absolute_error",
    "candidate_formula_status",
]


@dataclass
class ErrorAccumulator:
    reference_abs: list[float] = field(default_factory=list)
    signed_errors: list[float] = field(default_factory=list)
    candidate_values: list[float] = field(default_factory=list)
    reference_values: list[float] = field(default_factory=list)
    invalid_candidates: int = 0
    invalid_benchmark: int = 0
    aligned: int = 0

    def add(self, reference: Any, candidate: Any) -> None:
        self.aligned += 1
        ref = finite_float(reference)
        cand = finite_float(candidate)
        if ref is None:
            self.invalid_benchmark += 1
        if cand is None:
            self.invalid_candidates += 1
        if ref is None or cand is None:
            return
        self.reference_abs.append(abs(ref))
        self.signed_errors.append(cand - ref)
        self.reference_values.append(ref)
        self.candidate_values.append(cand)


@dataclass
class PairedSensitivityAccumulator:
    references: list[float] = field(default_factory=list)
    baselines: list[float] = field(default_factory=list)
    variants: list[float] = field(default_factory=list)
    aligned: int = 0
    invalid_benchmark: int = 0
    invalid_baseline: int = 0
    invalid_variant: int = 0

    def add(self, reference: Any, baseline: Any, variant: Any) -> None:
        self.aligned += 1
        ref = finite_float(reference)
        base = finite_float(baseline)
        changed = finite_float(variant)
        self.invalid_benchmark += int(ref is None)
        self.invalid_baseline += int(base is None)
        self.invalid_variant += int(changed is None)
        if ref is None or base is None or changed is None:
            return
        self.references.append(ref)
        self.baselines.append(base)
        self.variants.append(changed)


def finite_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def _new_accumulators() -> dict[str, ErrorAccumulator]:
    return {name: ErrorAccumulator() for name in FEATURE_NAMES}


def _metrics(accumulator: ErrorAccumulator) -> dict[str, Any]:
    errors = np.asarray(accumulator.signed_errors, dtype=np.float64)
    reference = np.asarray(accumulator.reference_values, dtype=np.float64)
    candidate = np.asarray(accumulator.candidate_values, dtype=np.float64)
    absolute = np.abs(errors)
    valid = len(errors)
    if not valid:
        return {
            "aligned_observations": accumulator.aligned,
            "valid_observations": 0,
            "invalid_benchmark": accumulator.invalid_benchmark,
            "invalid_candidate": accumulator.invalid_candidates,
            "mape_observations": 0,
            "mape_excluded_near_zero": 0,
            **{
                key: None
                for key in (
                    "mae",
                    "rmse",
                    "mean_signed_error",
                    "median_absolute_error",
                    "max_absolute_error",
                    "error_min",
                    "error_q05",
                    "error_q25",
                    "error_median",
                    "error_q75",
                    "error_q95",
                    "error_max",
                    "mape_pct",
                    "mean_abs_reference",
                    "pearson_r",
                    "spearman_rho",
                )
            },
        }
    reference_scale = float(np.mean(np.abs(reference)))
    median_reference_abs = float(np.median(np.abs(reference)))
    mape_floor = max(
        MAPE_ABSOLUTE_FLOOR, MAPE_FLOOR_FRACTION * median_reference_abs
    )
    mape_mask = np.abs(reference) > mape_floor
    mape = (
        float(np.mean(absolute[mape_mask] / np.abs(reference[mape_mask])) * 100.0)
        if np.any(mape_mask)
        else None
    )
    pearson: float | None = None
    spearman: float | None = None
    if valid > 1 and np.ptp(reference) > 0 and np.ptp(candidate) > 0:
        pearson = float(np.corrcoef(reference, candidate)[0, 1])
        reference_ranks = rankdata(reference, method="average")
        candidate_ranks = rankdata(candidate, method="average")
        if np.ptp(reference_ranks) > 0 and np.ptp(candidate_ranks) > 0:
            spearman = float(np.corrcoef(reference_ranks, candidate_ranks)[0, 1])
    quantiles = np.quantile(errors, [0.05, 0.25, 0.5, 0.75, 0.95])
    return {
        "aligned_observations": accumulator.aligned,
        "valid_observations": valid,
        "invalid_benchmark": accumulator.invalid_benchmark,
        "invalid_candidate": accumulator.invalid_candidates,
        "mape_observations": int(np.count_nonzero(mape_mask)),
        "mape_excluded_near_zero": int(valid - np.count_nonzero(mape_mask)),
        "mape_reference_floor": mape_floor,
        "mae": float(np.mean(absolute)),
        "rmse": float(np.sqrt(np.mean(errors**2))),
        "mean_signed_error": float(np.mean(errors)),
        "median_absolute_error": float(np.median(absolute)),
        "max_absolute_error": float(np.max(absolute)),
        "error_min": float(np.min(errors)),
        "error_q05": float(quantiles[0]),
        "error_q25": float(quantiles[1]),
        "error_median": float(quantiles[2]),
        "error_q75": float(quantiles[3]),
        "error_q95": float(quantiles[4]),
        "error_max": float(np.max(errors)),
        "mape_pct": mape,
        "mean_abs_reference": reference_scale,
        "relative_mae_pct": (
            float(np.mean(absolute) / reference_scale * 100.0)
            if reference_scale > 0
            else None
        ),
        "pearson_r": pearson,
        "spearman_rho": spearman,
    }


def _paired_sensitivity_metrics(
    accumulator: PairedSensitivityAccumulator,
) -> tuple[dict[str, Any], dict[str, Any]]:
    baseline = ErrorAccumulator(
        reference_values=list(accumulator.references),
        candidate_values=list(accumulator.baselines),
        reference_abs=[abs(value) for value in accumulator.references],
        signed_errors=[
            candidate - reference
            for reference, candidate in zip(
                accumulator.references, accumulator.baselines
            )
        ],
        aligned=accumulator.aligned,
        invalid_benchmark=accumulator.invalid_benchmark,
        invalid_candidates=accumulator.invalid_baseline,
    )
    variant = ErrorAccumulator(
        reference_values=list(accumulator.references),
        candidate_values=list(accumulator.variants),
        reference_abs=[abs(value) for value in accumulator.references],
        signed_errors=[
            candidate - reference
            for reference, candidate in zip(
                accumulator.references, accumulator.variants
            )
        ],
        aligned=accumulator.aligned,
        invalid_benchmark=accumulator.invalid_benchmark,
        invalid_candidates=accumulator.invalid_variant,
    )
    return _metrics(baseline), _metrics(variant)


def _segment_variant(
    cycle: CycleTrace,
    group: str,
    segment: PhaseSegment,
    *,
    statistic_sampling: str = "uniform_time",
    point_boundaries: bool = False,
    integration: str = "trapezoid",
    statistic_convention: str = "population_biased_pearson",
    entropy_bins: int = 16,
    entropy_log_base: str = "e",
    entropy_normalized: bool = False,
    derivative: str = "endpoint",
    time_unit: str = "minutes",
    selected_features: set[str] | None = None,
) -> dict[str, float | None]:
    selected = selected_features or {
        feature for feature in FEATURE_NAMES if feature.startswith(group + "_")
    }
    if not segment.intervals:
        return {}
    intervals: list[TimeInterval] = []
    for interval in segment.intervals:
        if point_boundaries:
            included = cycle.time_min[
                (cycle.time_min >= interval.start_min)
                & (cycle.time_min <= interval.end_min)
            ]
            if len(included) < 2:
                continue
            intervals.append(TimeInterval(float(included[0]), float(included[-1])))
        else:
            intervals.append(interval)
    if not intervals:
        return {}

    needs_dense = any(
        name.endswith(("_t_mean", "_mean", "_std", "_skewness", "_kurtosis", "_entropy"))
        for name in selected
    ) and statistic_sampling == "uniform_time"
    arrays = [
        _interval_arrays(cycle, interval, dense=needs_dense)
        for interval in intervals
    ]
    if any(len(times) < 2 for times, _ in arrays):
        return {}
    signal_names = ("voltage", "current", "temperature")
    signals = {
        name: np.concatenate([channels[name] for _, channels in arrays])
        for name in signal_names
    }
    times = [time for time, _ in arrays]
    elapsed = np.concatenate([time - time[0] for time in times])
    if time_unit == "seconds":
        elapsed = elapsed * 60.0
    values: dict[str, float | None] = {}
    if f"{group}_t_mean" in selected:
        values[f"{group}_t_mean"] = float(np.mean(elapsed))

    def integrate(samples: list[tuple[np.ndarray, np.ndarray]]) -> float:
        total = 0.0
        for sample_time, sample_values in samples:
            dt = np.diff(sample_time)
            if integration == "left_rectangle":
                total += float(np.sum(sample_values[:-1] * dt))
            elif integration == "right_rectangle":
                total += float(np.sum(sample_values[1:] * dt))
            else:
                total += float(
                    np.sum(dt * (sample_values[:-1] + sample_values[1:]) / 2.0)
                )
        return total

    requested_integrals = {
        name for name in (f"{group}_energy", f"{group}_Q") if name in selected
    }
    if requested_integrals:
        integration_times = [
            _interval_arrays(cycle, interval, dense=False) for interval in intervals
        ]
        conversion = 3600.0 if time_unit == "seconds" else 60.0
        if f"{group}_energy" in requested_integrals:
            v_times = [
                (time, channels["voltage"] * channels["current"])
                for time, channels in integration_times
            ]
            values[f"{group}_energy"] = integrate(v_times) / conversion
        if f"{group}_Q" in requested_integrals:
            i_times = [
                (time, channels["current"])
                for time, channels in integration_times
            ]
            values[f"{group}_Q"] = integrate(i_times) / conversion

    for suffix, signal in zip(("V", "C", "T"), signal_names):
        names = {
            f"{group}_{suffix}_mean",
            f"{group}_{suffix}_std",
            f"{group}_{suffix}_skewness",
            f"{group}_{suffix}_kurtosis",
        } & selected
        if not names:
            continue
        series = signals[signal]
        mean = float(np.mean(series))
        centered = series - mean
        m2 = float(np.mean(centered**2))
        std = float(np.std(series, ddof=1)) if statistic_convention == "sample" and len(series) > 1 else math.sqrt(max(m2, 0.0))
        if m2 <= np.finfo(float).eps:
            skewness = kurtosis = 0.0
        else:
            m3 = float(np.mean(centered**3))
            m4 = float(np.mean(centered**4))
            skewness = m3 / (m2**1.5)
            kurtosis = m4 / (m2**2)
            if statistic_convention == "adjusted_skewness" and len(series) > 2:
                n = len(series)
                skewness *= math.sqrt(n * (n - 1)) / (n - 2)
            elif statistic_convention == "fisher_excess" and len(series) > 3:
                n = len(series)
                kurtosis = (n - 1) / ((n - 2) * (n - 3)) * (
                    (n + 1) * (kurtosis - 3.0) + 6.0
                )
        if f"{group}_{suffix}_mean" in names:
            values[f"{group}_{suffix}_mean"] = mean
        if f"{group}_{suffix}_std" in names:
            values[f"{group}_{suffix}_std"] = std
        if f"{group}_{suffix}_skewness" in names:
            values[f"{group}_{suffix}_skewness"] = float(skewness)
        if f"{group}_{suffix}_kurtosis" in names:
            values[f"{group}_{suffix}_kurtosis"] = float(kurtosis)

    duration = sum(interval.end_min - interval.start_min for interval in intervals)
    if time_unit == "seconds":
        duration *= 60.0
    if group == "CC":
        values["CC_CCCT"] = duration if len(intervals) == 1 else None
        entropy_signal = signals["voltage"]
    elif group == "CV":
        values["CV_CVCT"] = duration if len(intervals) == 1 else None
        entropy_signal = signals["current"]
    elif group == "dV":
        entropy_signal = signals["voltage"]
        if len(intervals) == 1:
            interval = intervals[0]
            start = float(np.interp(interval.start_min, cycle.time_min, cycle.voltage_v))
            end = float(np.interp(interval.end_min, cycle.time_min, cycle.voltage_v))
            if derivative == "least_squares":
                raw_mask = (cycle.time_min >= interval.start_min) & (cycle.time_min <= interval.end_min)
                x = cycle.time_min[raw_mask]
                y = cycle.voltage_v[raw_mask]
                slope = float(np.polyfit(x, y, 1)[0]) if len(x) >= 2 else math.nan
            else:
                slope = (end - start) / (interval.end_min - interval.start_min)
            values["dV_dV_devide_dt"] = slope / (60.0 if time_unit == "seconds" else 1.0)
    elif group == "dI":
        entropy_signal = signals["current"]
        if len(intervals) == 1:
            interval = intervals[0]
            start = float(np.interp(interval.start_min, cycle.time_min, cycle.current_a))
            end = float(np.interp(interval.end_min, cycle.time_min, cycle.current_a))
            if derivative == "least_squares":
                raw_mask = (cycle.time_min >= interval.start_min) & (cycle.time_min <= interval.end_min)
                x = cycle.time_min[raw_mask]
                y = cycle.current_a[raw_mask]
                slope = float(np.polyfit(x, y, 1)[0]) if len(x) >= 2 else math.nan
            else:
                slope = (end - start) / (interval.end_min - interval.start_min)
            values["dI_dI_devide_dt"] = slope / (60.0 if time_unit == "seconds" else 1.0)
    else:
        entropy_signal = signals["current"]

    derivative_name = {
        "dV": "dV_dV_devide_dt",
        "dI": "dI_dI_devide_dt",
    }.get(group)
    if derivative_name in selected and len(intervals) == 1:
        interval = intervals[0]
        if group == "dV":
            raw_signal = cycle.voltage_v
        else:
            raw_signal = cycle.current_a
        start = float(np.interp(interval.start_min, cycle.time_min, raw_signal))
        end = float(np.interp(interval.end_min, cycle.time_min, raw_signal))
        if derivative == "least_squares":
            raw_mask = (
                (cycle.time_min >= interval.start_min)
                & (cycle.time_min <= interval.end_min)
            )
            x = cycle.time_min[raw_mask]
            y = raw_signal[raw_mask]
            slope = float(np.polyfit(x, y, 1)[0]) if len(x) >= 2 else math.nan
        else:
            slope = (end - start) / (interval.end_min - interval.start_min)
        values[derivative_name] = slope / (60.0 if time_unit == "seconds" else 1.0)

    entropy_name = f"{group}_entropy"
    if entropy_name in selected and group in ("CC", "dV", "CV", "dI"):
        counts, _ = np.histogram(entropy_signal, bins=entropy_bins)
        probabilities = counts[counts > 0].astype(np.float64)
        probabilities /= probabilities.sum()
        if entropy_log_base == "2":
            entropy = float(-np.sum(probabilities * np.log2(probabilities)))
        else:
            entropy = float(-np.sum(probabilities * np.log(probabilities)))
        if entropy_normalized and entropy_bins > 1:
            entropy /= math.log(entropy_bins) if entropy_log_base == "e" else math.log2(entropy_bins)
        values[entropy_name] = entropy
    return values


def _variant_specs() -> list[dict[str, Any]]:
    return [
        {
            "variant": "author_documented_cc_selector",
            "axis": "phase segmentation",
            "settings": {"policy": "cc_method=author_documented; all other defaults"},
            "evidence_class": "author-helper selector; not workbook provenance",
            "description": "Recompute all features under the existing fixed 3.9 A CC helper selector.",
        },
        {
            "variant": "native_sample_statistics",
            "axis": "sampling/statistics",
            "settings": {"statistic_sampling": "native timestamps"},
            "evidence_class": "candidate convention comparison",
            "description": "Use stored timestamps and samples for descriptive statistics rather than a 257-point uniform-time grid.",
        },
        {
            "variant": "observed_point_boundaries",
            "axis": "boundary inclusion",
            "settings": {"point_boundaries": True},
            "evidence_class": "candidate convention comparison",
            "description": "Replace interpolated threshold endpoints with first/last recorded samples inside each selected interval.",
        },
        {
            "variant": "left_rectangle_integrals",
            "axis": "integration",
            "settings": {"integration": "left_rectangle"},
            "evidence_class": "numerical convention comparison",
            "description": "Use left rectangles for V*I and I integrals on the same native timestamps and boundaries.",
        },
        {
            "variant": "right_rectangle_integrals",
            "axis": "integration",
            "settings": {"integration": "right_rectangle"},
            "evidence_class": "numerical convention comparison",
            "description": "Use right rectangles for V*I and I integrals on the same native timestamps and boundaries.",
        },
        {
            "variant": "sample_standard_deviation",
            "axis": "statistical convention",
            "settings": {"statistic_convention": "sample"},
            "evidence_class": "statistical convention comparison",
            "description": "Use ddof=1 standard deviation; other candidate calculations stay at baseline.",
        },
        {
            "variant": "adjusted_skewness",
            "axis": "statistical convention",
            "settings": {"statistic_convention": "adjusted_skewness"},
            "evidence_class": "statistical convention comparison",
            "description": "Apply the common finite-sample skewness adjustment; other candidate calculations stay at baseline.",
        },
        {
            "variant": "fisher_excess_kurtosis",
            "axis": "statistical convention",
            "settings": {"statistic_convention": "fisher_excess"},
            "evidence_class": "statistical convention comparison",
            "description": "Use bias-corrected Fisher/excess kurtosis; other candidate calculations stay at baseline.",
        },
        {
            "variant": "least_squares_derivative",
            "axis": "derivative estimator",
            "settings": {"derivative": "least_squares"},
            "evidence_class": "numerical convention comparison",
            "description": "Replace endpoint secant rate by a linear least-squares slope over recorded samples in the same derivative window.",
        },
        {
            "variant": "entropy_8_bins",
            "axis": "entropy proxy",
            "settings": {"entropy_bins": 8},
            "evidence_class": "diagnostic proxy variant; original entropy unknown",
            "description": "Recompute the Shannon histogram proxy with 8 equal-width bins.",
        },
        {
            "variant": "entropy_32_bins",
            "axis": "entropy proxy",
            "settings": {"entropy_bins": 32},
            "evidence_class": "diagnostic proxy variant; original entropy unknown",
            "description": "Recompute the Shannon histogram proxy with 32 equal-width bins.",
        },
        {
            "variant": "entropy_bits",
            "axis": "entropy proxy",
            "settings": {"entropy_log_base": "2"},
            "evidence_class": "diagnostic proxy variant; original entropy unknown",
            "description": "Express the same 16-bin entropy proxy using log base 2.",
        },
        {
            "variant": "entropy_normalized",
            "axis": "entropy proxy",
            "settings": {"entropy_normalized": True},
            "evidence_class": "diagnostic proxy variant; original entropy unknown",
            "description": "Divide 16-bin nats entropy by ln(16); this is a normalized diagnostic, not a proposed original formula.",
        },
        {
            "variant": "time_seconds_interpretation",
            "axis": "unit interpretation",
            "settings": {"time_unit": "seconds"},
            "evidence_class": "unit-scale diagnostic",
            "description": "Re-express time-dependent candidates as if stored minute values were seconds; this is a factor-of-60 diagnostic, not an accepted unit change.",
        },
    ]


def _variant_arguments(name: str) -> dict[str, Any]:
    return {
        "native_sample_statistics": {"statistic_sampling": "native"},
        "observed_point_boundaries": {"point_boundaries": True},
        "left_rectangle_integrals": {"integration": "left_rectangle"},
        "right_rectangle_integrals": {"integration": "right_rectangle"},
        "sample_standard_deviation": {"statistic_convention": "sample"},
        "adjusted_skewness": {"statistic_convention": "adjusted_skewness"},
        "fisher_excess_kurtosis": {"statistic_convention": "fisher_excess"},
        "least_squares_derivative": {"derivative": "least_squares"},
        "entropy_8_bins": {"entropy_bins": 8},
        "entropy_32_bins": {"entropy_bins": 32},
        "entropy_bits": {"entropy_log_base": "2"},
        "entropy_normalized": {"entropy_normalized": True},
        "time_seconds_interpretation": {"time_unit": "seconds"},
    }.get(name, {})


def _variant_features(name: str) -> set[str]:
    if name == "author_documented_cc_selector":
        return {
            feature for feature in FEATURE_NAMES
            if feature.startswith(("CC_", "dV_"))
        }
    if name in ("left_rectangle_integrals", "right_rectangle_integrals"):
        suffixes = ("_energy", "_Q")
    elif name == "sample_standard_deviation":
        suffixes = ("_std",)
    elif name == "adjusted_skewness":
        suffixes = ("_skewness",)
    elif name == "fisher_excess_kurtosis":
        suffixes = ("_kurtosis",)
    elif name == "least_squares_derivative":
        return {"dV_dV_devide_dt", "dI_dI_devide_dt"}
    elif name in ("entropy_8_bins", "entropy_32_bins", "entropy_bits", "entropy_normalized"):
        return {feature for feature in FEATURE_NAMES if feature.endswith("_entropy")}
    elif name == "time_seconds_interpretation":
        suffixes = ("_energy", "_Q", "_t_mean", "_CCCT", "_CVCT", "_devide_dt")
    else:
        suffixes = ("_t_mean", "_mean", "_std", "_skewness", "_kurtosis")
    return {
        feature for feature in FEATURE_NAMES
        if feature.endswith(suffixes)
    }


def _alignment_class(method: str) -> str:
    if method == "positional_unverified_equal_counts":
        return COHORT_POSITIONAL
    if method == "unique_monotone_capacity_diagnostic":
        return COHORT_CAPACITY
    raise ValueError(f"Unknown alignment method: {method}")


def _cycle_bin(cycle_index: int, raw_cycle_count: int) -> str:
    decile = min(9, max(0, int((cycle_index - 1) * 10 / raw_cycle_count)))
    return f"D{decile + 1:02d}"


def _sampling_summary(batch: int, profile: str, cycles: list[CycleTrace]) -> dict[str, Any]:
    delta = [np.diff(cycle.time_min) for cycle in cycles]
    all_delta = np.concatenate(delta) if delta else np.asarray([], dtype=np.float64)
    deviations = [
        float(np.max(np.abs(values - np.median(values))) / abs(np.median(values)))
        for values in delta
    ]
    return {
        "batch": batch,
        "profile": profile,
        "raw_cycles": len(cycles),
        "samples_per_cycle_min": min((len(cycle.time_min) for cycle in cycles), default=None),
        "samples_per_cycle_max": max((len(cycle.time_min) for cycle in cycles), default=None),
        "median_delta_time_min": float(np.median(all_delta)) if len(all_delta) else None,
        "minimum_delta_time_min": float(np.min(all_delta)) if len(all_delta) else None,
        "maximum_delta_time_min": float(np.max(all_delta)) if len(all_delta) else None,
        "nonuniform_cycles": sum(
            not np.allclose(values, np.median(values), rtol=1e-6, atol=1e-9)
            for values in delta
        ),
        "maximum_relative_step_deviation": max(deviations, default=None),
    }


def _write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False, float_format="%.12g")


def _save_plots(feature_rows: list[dict[str, Any]], profile_rows: list[dict[str, Any]], output_dir: Path) -> list[str]:
    paths: list[str] = []
    features = [
        row for row in feature_rows
        if row["alignment_cohort"] == COHORT_POSITIONAL and row["scope"] == "overall"
        and row["relative_mae_pct"] is not None
    ]
    ranked = sorted(features, key=lambda row: row["relative_mae_pct"], reverse=True)[:20]
    if ranked:
        figure, axis = plt.subplots(figsize=(12, 8))
        labels = [row["feature"] for row in reversed(ranked)]
        values = [row["relative_mae_pct"] for row in reversed(ranked)]
        axis.barh(labels, values, color="#b65353")
        axis.set_xlabel("Relative MAE (% of mean absolute benchmark value)")
        axis.set_title("Largest relative candidate errors — unverified positional cohort")
        axis.grid(axis="x", alpha=0.25)
        figure.tight_layout()
        path = output_dir / "top_relative_errors.png"
        figure.savefig(path, dpi=160)
        plt.close(figure)
        paths.append(path.name)

    worst_features = [row["feature"] for row in ranked[:12]]
    profiles = [
        row for row in profile_rows
        if row["alignment_cohort"] == COHORT_POSITIONAL
        and row["feature"] in worst_features
        and row["relative_mae_pct"] is not None
    ]
    if profiles:
        frame = pd.DataFrame(profiles)
        pivot = frame.pivot(index="feature", columns=["batch", "profile"], values="relative_mae_pct")
        pivot = pivot.reindex(worst_features).dropna(how="all")
        if not pivot.empty:
            figure, axis = plt.subplots(
                figsize=(max(12, pivot.shape[1] * 0.28), max(5, pivot.shape[0] * 0.55))
            )
            image = axis.imshow(pivot.to_numpy(), aspect="auto", interpolation="nearest", cmap="magma")
            axis.set_yticks(range(len(pivot.index)), labels=pivot.index)
            axis.set_xlabel("Profile (batch / sheet)")
            axis.set_title("Profile concentration of relative candidate error (diagnostic alignment)")
            axis.set_xticks(
                range(len(pivot.columns)),
                labels=[f"{batch}/{profile}" for batch, profile in pivot.columns],
                rotation=90,
                fontsize=6,
            )
            figure.colorbar(image, ax=axis, label="Relative MAE (%)")
            figure.tight_layout()
            path = output_dir / "profile_error_heatmap.png"
            figure.savefig(path, dpi=160)
            plt.close(figure)
            paths.append(path.name)
    return paths


def _root_cause_rows(
    feature_rows: list[dict[str, Any]],
    batch_rows: list[dict[str, Any]],
    profile_rows: list[dict[str, Any]],
    alignment_rows: list[dict[str, Any]],
    sensitivity_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    positional = [
        row for row in feature_rows
        if row["scope"] == "overall" and row["alignment_cohort"] == COHORT_POSITIONAL
    ]
    top = sorted(
        (row for row in positional if row["relative_mae_pct"] is not None),
        key=lambda row: row["relative_mae_pct"],
        reverse=True,
    )
    summaries = [row for row in alignment_rows if row.get("alignment_summary")]
    positional_count = sum(row["matched_pairs"] for row in summaries if row["alignment_cohort"] == COHORT_POSITIONAL)
    capacity_count = sum(row["matched_pairs"] for row in summaries if row["alignment_cohort"] == COHORT_CAPACITY)
    ambiguity = sum(row["ambiguous_workbook_rows"] for row in summaries)
    unmatched = sum(row["unmatched_workbook_rows"] for row in summaries)
    invalid = sum(row["invalid_candidate"] for row in positional)
    sensitivity_by_variant: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in sensitivity_rows:
        sensitivity_by_variant[row["variant"]].append(row)
    entropy_rows = [row for row in positional if row["feature"].endswith("_entropy")]
    temperature_shape = [row for row in positional if "_T_skewness" in row["feature"] or "_T_kurtosis" in row["feature"]]
    cc_docs = [
        row for row in sensitivity_by_variant.get("author_documented_cc_selector", [])
        if row["feature"].startswith(("CC_", "dV_"))
    ]
    return [
        {
            "finding_id": "alignment_identity",
            "classification": "Confirmed observation",
            "suspected_cause": "Cycle identity uncertainty",
            "affected_features": "All 67; affects interpretation of every candidate-vs-workbook residual",
            "evidence": (
                f"{positional_count:,} equal-count pairs are positional and unverified; "
                f"{capacity_count:,} batch-6 matches are capacity-label diagnostics; "
                f"{ambiguity:,} workbook rows are ambiguous (subset of "
                f"{unmatched:,} unmatched workbook rows)."
            ),
            "mechanism": "A wrong cycle-to-row pairing can create apparent feature error or hide real error.",
            "confidence": "High for uncertainty; no cycle identity ground truth is available.",
            "cannot_establish": "Which residuals are caused by row identity rather than formula/segment differences.",
        },
        {
            "finding_id": "candidate_phase_rules",
            "classification": "Evidence-supported explanation",
            "suspected_cause": "Candidate phase boundary and segmentation conventions",
            "affected_features": "CC and dV families directly; CV and dI boundary-dependent features",
            "evidence": (
                f"The code uses an adaptive CC plateau, CV first 4.199 V crossing, "
                f"dV 3.9–4.0 V, and dI 1.0–0.9 A. The author helper only documents a "
                f"fixed 3.9 A CC selector and V≥4.199 V CV selector; it does not connect "
                f"those rules to workbook generation. {len(cc_docs)} feature sensitivity rows "
                "compare the fixed-CC selector against baseline."
            ),
            "mechanism": "Changing segment endpoints changes durations, integrals, elapsed-time statistics, and all within-segment statistics.",
            "confidence": "High that implementations differ in assumptions; low that this explains any specific workbook residual.",
            "cannot_establish": "Original workbook phase thresholds, disconnected-run handling, or boundary inclusion.",
        },
        {
            "finding_id": "entropy_proxy",
            "classification": "Confirmed observation",
            "suspected_cause": "Unknown original entropy definition versus diagnostic histogram proxy",
            "affected_features": ", ".join(row["feature"] for row in entropy_rows),
            "evidence": (
                f"All four entropy definitions remain unknown. The candidate uses a 16-bin "
                f"equal-width histogram with natural logarithms; {len(entropy_rows)} positional "
                "feature summaries retain that proxy label. Sensitivity outputs include 8/32 "
                "bins, bits, and normalized entropy as diagnostics only."
            ),
            "mechanism": "Signal choice, estimator, bin edges/count, and logarithm base directly determine entropy scale and value.",
            "confidence": "High that the candidate proxy is not source-verified; no attribution of the mismatch mechanism to any original formula.",
            "cannot_establish": "Whether Excel entropy uses histogram entropy, another entropy estimator, another signal, or another normalization.",
        },
        {
            "finding_id": "coarse_prepared_sampling",
            "classification": "Evidence-supported explanation",
            "suspected_cause": "Prepared-cycle sampling and preprocessing",
            "affected_features": "All phase-dependent features; strongest potential sensitivity for narrow dV/dI windows and derivatives",
            "evidence": "Prepared MAT traces have 128 samples per cycle and measured time intervals from about 0.092 to 1.185 minutes; the dataset release states 1 Hz acquisition. The transformation between these representations is undocumented.",
            "mechanism": "Sparse prepared points can make threshold crossings, endpoint slopes, integrals, and moments sensitive to interpolation and sampling convention.",
            "confidence": "High for observed representation mismatch; medium for likely sensitivity; low for attributing particular residuals.",
            "cannot_establish": "Whether workbook features were calculated from the original 1 Hz stream or from the prepared 128-point traces.",
        },
        {
            "finding_id": "statistics_conventions",
            "classification": "Plausible hypothesis",
            "suspected_cause": "Time weighting and statistical estimator conventions",
            "affected_features": "Mean/std/skewness/kurtosis and elapsed-time features across CC, dV, CV, dI, Charge",
            "evidence": (
                "Candidate moments use a 257-point uniform-time interpolation grid and population/biased Pearson moments. "
                "The sensitivity CSV reports native-sample and alternative statistical-convention errors for the same paired observations."
            ),
            "mechanism": "Equal weighting of interpolated times differs from equal weighting of recorded samples when intervals/segments differ; ddof, bias correction, and excess/Pearson conventions alter moments.",
            "confidence": "Medium as a general mechanism; feature-specific evidence is in the sensitivity output and does not identify workbook convention.",
            "cannot_establish": "The original sampling weights or statistical library/conventions.",
        },
        {
            "finding_id": "outlier_concentration",
            "classification": "Confirmed observation",
            "suspected_cause": "Concentration of residuals in feature/profile subsets",
            "affected_features": ", ".join(row["feature"] for row in top[:10]),
            "evidence": (
                f"Top positional relative-MAE feature is {top[0]['feature']} "
                f"({top[0]['relative_mae_pct']:.4g}%, n={top[0]['valid_observations']})"
                if top else "No valid feature residuals available."
            ),
            "mechanism": "Report profile, batch, and cycle-decile tables show whether aggregate errors are broadly distributed or concentrated.",
            "confidence": "High for descriptive concentration; low for causal interpretation.",
            "cannot_establish": "Whether clustering by a batch/profile characteristic is causal or an alignment artifact.",
        },
        {
            "finding_id": "invalid_candidate_segments",
            "classification": "Confirmed observation",
            "suspected_cause": "Candidate intervals unavailable or degenerate",
            "affected_features": "Features whose candidate segment cannot be formed (especially dV/dI and phase-duration features)",
            "evidence": f"Across 67 feature accumulators in the positional cohort there are {invalid:,} candidate-invalid feature observations.",
            "mechanism": "Missing threshold crossings or disjoint/missing intervals prevent feature calculation; these values are excluded rather than imputed.",
            "confidence": "High for candidate invalid count; not evidence that the benchmark row is invalid.",
            "cannot_establish": "Whether corresponding workbook features use different windows or an alternative fallback.",
        },
    ]


def _markdown_table(rows: Iterable[dict[str, Any]], columns: list[tuple[str, str]]) -> list[str]:
    output = [
        "| " + " | ".join(title for title, _ in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        cells = []
        for _, key in columns:
            value = row.get(key)
            if value is None or (isinstance(value, float) and not math.isfinite(value)):
                cells.append("—")
            elif isinstance(value, float):
                cells.append(f"{value:.5g}")
            else:
                cells.append(str(value).replace("|", "\\|").replace("\n", " "))
        output.append("| " + " | ".join(cells) + " |")
    return output


def _write_report(
    report_path: Path,
    feature_rows: list[dict[str, Any]],
    batch_rows: list[dict[str, Any]],
    profile_rows: list[dict[str, Any]],
    cycle_bin_rows: list[dict[str, Any]],
    alignment_rows: list[dict[str, Any]],
    root_rows: list[dict[str, Any]],
    sensitivity_rows: list[dict[str, Any]],
    plot_names: list[str],
    sampling_rows: list[dict[str, Any]],
    phase_rows: list[dict[str, Any]],
) -> None:
    positional = sorted(
        (
            row for row in feature_rows
            if row["scope"] == "overall"
            and row["alignment_cohort"] == COHORT_POSITIONAL
            and row["relative_mae_pct"] is not None
        ),
        key=lambda row: row["relative_mae_pct"],
    )
    high = list(reversed(positional))
    low_rows, high_rows = positional[:10], high[:10]
    groups: list[dict[str, Any]] = []
    for group in GROUPS:
        members = [
            row for row in positional
            if row["group"] == group
        ]
        groups.append(
            {
                "group": group,
                "features": len(members),
                "median_relative_mae_pct": (
                    float(np.median([row["relative_mae_pct"] for row in members]))
                    if members else None
                ),
                "median_relative_bias_pct": (
                    float(np.median([
                        row["mean_signed_error"] / row["mean_abs_reference"] * 100.0
                        for row in members
                        if row["mean_signed_error"] is not None
                        and row["mean_abs_reference"] not in (None, 0)
                    ]))
                    if any(
                        row["mean_signed_error"] is not None
                        and row["mean_abs_reference"] not in (None, 0)
                        for row in members
                    ) else None
                ),
                "valid_pairs_min": min((row["valid_observations"] for row in members), default=0),
                "valid_pairs_max": max((row["valid_observations"] for row in members), default=0),
            }
        )
    sensitivity_head = sorted(
        (
            row for row in sensitivity_rows
            if row["alignment_cohort"] == COHORT_POSITIONAL
            and row.get("delta_relative_mae_pct") is not None
        ),
        key=lambda row: abs(row["delta_relative_mae_pct"]),
        reverse=True,
    )[:20]
    alignment_summaries = [row for row in alignment_rows if row.get("alignment_summary")]
    alignment_totals = {
        cohort: sum(row["matched_pairs"] for row in alignment_summaries if row["alignment_cohort"] == cohort)
        for cohort in COHORTS
    }
    ambiguous = sum(row["ambiguous_workbook_rows"] for row in alignment_summaries)
    unmatched_workbook = sum(row["unmatched_workbook_rows"] for row in alignment_summaries)
    unmatched_raw = sum(row["unmatched_raw_cycles"] for row in alignment_summaries)
    invalid_overall = sum(
        row["invalid_candidate"]
        for row in feature_rows
        if row["scope"] == "overall" and row["alignment_cohort"] == COHORT_POSITIONAL
    )
    lines = [
        "# XJTU Feature Error Analysis and Root Cause Investigation",
        "",
        "## Executive summary",
        "",
        "This investigation compares the existing candidate extractor with workbook values. It does not identify or reproduce the original feature generator, and no candidate result is labeled as an original formula.",
        "",
        f"- Alignment inventory: **{alignment_totals[COHORT_POSITIONAL]:,} positional, unverified pairs**, **{alignment_totals[COHORT_CAPACITY]:,} capacity-match diagnostic pairs**, **0 identity-verified pairs**, **{ambiguous:,} ambiguous workbook rows** (included in {unmatched_workbook:,} unmatched workbook rows), and **{unmatched_raw:,} unmatched raw cycles**.",
        "- Positional and capacity-match results are kept in separate cohorts. Ambiguous and unmatched workbook rows are not scored. No cohort is described as verified cycle identity.",
        "- Feature-level rankings below use the positional cohort only as a diagnostic; its identity remains unverified. Batch-6 capacity matches are reported separately and are not pooled into the primary ranking.",
        f"- Candidate-invalid feature observations in the positional cohort: **{invalid_overall:,}** across the 67 feature summaries.",
        "- MAPE excludes benchmark values at or below 1% of that feature/cohort's median absolute benchmark value (or 1e-12, whichever is larger); both included and excluded counts are reported.",
        "- The four entropy columns remain unknown-original-formula features; every entropy sensitivity is explicitly a proxy diagnostic.",
        "",
        "## Methodology and reproducibility",
        "",
        "The runner loads each batch's raw prepared MAT cycles and Excel sheets, calls the existing `_profile_pairs` alignment helper unchanged, and evaluates the existing default `SegmentationPolicy()` and `extract_cycle()` candidate values. The workbook feature order is checked against all 67 known names. Candidate and benchmark non-finite values are counted separately and excluded from numeric metrics.",
        "",
        "For each feature and scope, signed error is candidate minus workbook. The report computes MAE, RMSE, mean signed bias, median/max absolute error, signed-error quantiles, MAPE with the near-zero exclusion above, relative MAE (`MAE / mean(abs(benchmark))`), and Pearson/Spearman correlations when defined. MAPE is the mean of per-observation absolute percentage errors over non-near-zero references; it is not the aggregate relative MAE.",
        "",
        "Scope tables use the same pairs, grouped as overall, batch, profile, and within-profile cycle deciles. The compressed cycle-wise diagnostic file contains one feature-level record per aligned pair; it preserves the alignment cohort and is not ground-truth cycle error.",
        "",
        "### Alignment limitations",
        "",
        *_markdown_table(
            alignment_summaries,
            [
                ("Batch", "batch"),
                ("Profile", "profile"),
                ("Alignment cohort", "alignment_cohort"),
                ("Method", "alignment_method"),
                ("Matched pairs", "matched_pairs"),
                ("Unmatched workbook rows", "unmatched_workbook_rows"),
                ("Ambiguous rows (subset)", "ambiguous_workbook_rows"),
                ("Unmatched raw cycles", "unmatched_raw_cycles"),
                ("Mean |label Δ|", "mean_abs_label_difference"),
                ("Max |label Δ|", "max_abs_label_difference"),
            ],
        ),
        "",
        "Equal-count pairs are positional and unverified; label equality/near-equality is only a diagnostic. In unequal-count profiles, unique monotone capacity matches are diagnostics, while ambiguous rows stay unmatched. The alignment implementation was not altered. The benchmark has no independent cycle identity field in the inspected workbooks, so reliable cycle identity cannot be asserted.",
        "",
        "## Prepared-MAT sampling and candidate phase coverage",
        "",
        "Sampling is recomputed from every loaded prepared MAT cycle, not inferred from the 1 Hz release statement. The per-profile details are in `sampling_audit.csv`. Constant spacing within a prepared cycle does not establish that the workbook was generated from these points or resolve the release-to-MAT preprocessing gap.",
        "",
        *_markdown_table(
            [
                {
                    "profile": "all profiles",
                    "raw_cycles": sum(row["raw_cycles"] for row in sampling_rows),
                    "samples_per_cycle_min": min((row["samples_per_cycle_min"] for row in sampling_rows if row["samples_per_cycle_min"] is not None), default=None),
                    "samples_per_cycle_max": max((row["samples_per_cycle_max"] for row in sampling_rows if row["samples_per_cycle_max"] is not None), default=None),
                    "median_delta_time_min": float(np.median([row["median_delta_time_min"] for row in sampling_rows if row["median_delta_time_min"] is not None])),
                    "minimum_delta_time_min": min((row["minimum_delta_time_min"] for row in sampling_rows if row["minimum_delta_time_min"] is not None), default=None),
                    "maximum_delta_time_min": max((row["maximum_delta_time_min"] for row in sampling_rows if row["maximum_delta_time_min"] is not None), default=None),
                    "nonuniform_cycles": sum(row["nonuniform_cycles"] for row in sampling_rows),
                    "maximum_relative_step_deviation": max((row["maximum_relative_step_deviation"] for row in sampling_rows if row["maximum_relative_step_deviation"] is not None), default=None),
                }
            ],
            [
                ("Scope", "profile"),
                ("Raw cycles", "raw_cycles"),
                ("Min samples/cycle", "samples_per_cycle_min"),
                ("Max samples/cycle", "samples_per_cycle_max"),
                ("Median Δt (min)", "median_delta_time_min"),
                ("Min Δt (min)", "minimum_delta_time_min"),
                ("Max Δt (min)", "maximum_delta_time_min"),
                ("Nonuniform cycles", "nonuniform_cycles"),
                ("Max relative Δt deviation", "maximum_relative_step_deviation"),
            ],
        ),
        "",
        "Candidate phase coverage is computed only for cycles admitted by the unchanged alignment helper; it documents candidate interval availability, not benchmark phase labels.",
        "",
        *_markdown_table(
            [
                {
                    "group": group,
                    "profiles": len({
                        (row["batch"], row["profile"])
                        for row in phase_rows
                        if row["alignment_cohort"] == COHORT_POSITIONAL and row["group"] == group
                    }),
                    "matched_cycles": sum(
                        row["matched_cycles"]
                        for row in phase_rows
                        if row["alignment_cohort"] == COHORT_POSITIONAL and row["group"] == group
                    ),
                    "missing_segments": sum(
                        row["missing_segment_cycles"]
                        for row in phase_rows
                        if row["alignment_cohort"] == COHORT_POSITIONAL and row["group"] == group
                    ),
                    "disjoint_segments": sum(
                        row["disjoint_segment_cycles"]
                        for row in phase_rows
                        if row["alignment_cohort"] == COHORT_POSITIONAL and row["group"] == group
                    ),
                    "median_selected_samples": float(np.median([
                        row["median_selected_sample_count"]
                        for row in phase_rows
                        if row["alignment_cohort"] == COHORT_POSITIONAL and row["group"] == group and row["median_selected_sample_count"] is not None
                    ])),
                    "median_duration_min": float(np.median([
                        row["median_interval_duration_min"]
                        for row in phase_rows
                        if row["alignment_cohort"] == COHORT_POSITIONAL and row["group"] == group and row["median_interval_duration_min"] is not None
                    ])),
                }
                for group in GROUPS
            ],
            [
                ("Group", "group"),
                ("Profiles", "profiles"),
                ("Matched cycles", "matched_cycles"),
                ("Missing segments", "missing_segments"),
                ("Disjoint segments", "disjoint_segments"),
                ("Median selected samples/profile", "median_selected_samples"),
                ("Median duration/profile (min)", "median_duration_min"),
            ],
        ),
        "",
        "## Overall feature-wise error statistics",
        "",
        "### Positional, unverified cohort (diagnostic only)",
        "",
        *_markdown_table(
            [row for row in sorted(feature_rows, key=lambda r: r["feature_order"]) if row["scope"] == "overall" and row["alignment_cohort"] == COHORT_POSITIONAL],
            [
                ("Feature", "feature"),
                ("Group", "group"),
                ("Valid", "valid_observations"),
                ("Invalid candidate", "invalid_candidate"),
                ("MAE", "mae"),
                ("RMSE", "rmse"),
                ("MAPE %", "mape_pct"),
                ("MAPE n", "mape_observations"),
                ("Bias", "mean_signed_error"),
                ("Median |err|", "median_absolute_error"),
                ("Max |err|", "max_absolute_error"),
                ("Error q05", "error_q05"),
                ("Error median", "error_median"),
                ("Error q95", "error_q95"),
                ("Relative MAE %", "relative_mae_pct"),
                ("Pearson r", "pearson_r"),
                ("Spearman ρ", "spearman_rho"),
            ],
        ),
        "",
        "### Highest relative MAE — diagnostic only",
        "",
        *_markdown_table(
            high_rows,
            [
                ("Feature", "feature"),
                ("Relative MAE %", "relative_mae_pct"),
                ("MAE", "mae"),
                ("RMSE", "rmse"),
                ("Bias", "mean_signed_error"),
                ("Valid n", "valid_observations"),
            ],
        ),
        "",
        "### Lowest relative MAE — diagnostic only",
        "",
        *_markdown_table(
            low_rows,
            [
                ("Feature", "feature"),
                ("Relative MAE %", "relative_mae_pct"),
                ("MAE", "mae"),
                ("RMSE", "rmse"),
                ("Bias", "mean_signed_error"),
                ("Valid n", "valid_observations"),
            ],
        ),
        "",
        "Low relative error is not formula verification; relative error is scale-normalized and cannot neutralize alignment uncertainty.",
        "",
        "## Feature-group findings",
        "",
        *_markdown_table(
            groups,
            [
                ("Group", "group"),
                ("Features", "features"),
                ("Median feature relative MAE %", "median_relative_mae_pct"),
                ("Median relative bias %", "median_relative_bias_pct"),
                ("Valid n min", "valid_pairs_min"),
                ("Valid n max", "valid_pairs_max"),
            ],
        ),
        "",
        "The group median relative MAE summarizes per-feature ratios; it does not pool unlike physical units. Individual features must be interpreted using their own units and near-zero policy.",
        "",
        "## Batch, profile, and cycle-range findings",
        "",
        "Machine-readable outputs contain the complete feature × batch, feature × profile, and feature × within-profile cycle-decile tables. They are split by positional versus capacity-diagnostic cohort. Profile/cycle clustering is descriptive, not causal.",
        "",
        "### Largest positional profile relative errors",
        "",
        *_markdown_table(
            sorted(
                (row for row in profile_rows if row["alignment_cohort"] == COHORT_POSITIONAL and row["relative_mae_pct"] is not None),
                key=lambda row: row["relative_mae_pct"],
                reverse=True,
            )[:20],
            [
                ("Batch", "batch"),
                ("Profile", "profile"),
                ("Feature", "feature"),
                ("Relative MAE %", "relative_mae_pct"),
                ("MAE", "mae"),
                ("Bias", "mean_signed_error"),
                ("Valid n", "valid_observations"),
            ],
        ),
        "",
        "### Cycle-decile errors for the 10 highest overall relative-MAE features",
        "",
        *_markdown_table(
            [
                row for row in cycle_bin_rows
                if row["alignment_cohort"] == COHORT_POSITIONAL
                and row["feature"] in {item["feature"] for item in high_rows}
            ][:60],
            [
                ("Batch", "batch"),
                ("Profile", "profile"),
                ("Cycle decile", "cycle_decile"),
                ("Feature", "feature"),
                ("MAE", "mae"),
                ("Bias", "mean_signed_error"),
                ("Valid n", "valid_observations"),
            ],
        ),
        "",
        "## Root-cause evidence table",
        "",
        *_markdown_table(
            root_rows,
            [
                ("ID", "finding_id"),
                ("Classification", "classification"),
                ("Suspected cause", "suspected_cause"),
                ("Affected features", "affected_features"),
                ("Evidence", "evidence"),
                ("Mechanism", "mechanism"),
                ("Confidence", "confidence"),
                ("Cannot establish", "cannot_establish"),
            ],
        ),
        "",
        "## Sensitivity experiments",
        "",
        "Every variant was declared before comparing its benchmark error and is reported, not selected. No threshold, offset, coefficient, or correction was fitted to workbook values. Segment-changing sensitivity rows use the same preserved alignment pairs. Results are differences in candidate MAE from the baseline candidate on the same cohort; they are not evidence of original-formula recovery.",
        "",
        *_markdown_table(
            sensitivity_head,
            [
                ("Cohort", "alignment_cohort"),
                ("Variant", "variant"),
                ("Feature", "feature"),
                ("Baseline MAE", "baseline_mae"),
                ("Variant MAE", "variant_mae"),
                ("Δ relative MAE (percentage points)", "delta_relative_mae_pct"),
                ("Δ MAE (feature units)", "delta_mae"),
                ("Valid n", "valid_observations"),
                ("Evidence class", "evidence_class"),
            ],
        ),
        "",
        "Fixed sensitivity variants include: documented fixed-current versus adaptive CC selector; native versus uniform-time statistics; observed-point versus interpolated endpoints; left/right rectangles versus trapezoids; sample standard deviation; adjusted skewness; Fisher/excess kurtosis; least-squares versus endpoint derivative; 8/32 bins, log2, and normalized entropy; and a factor-of-60 time-unit diagnostic. Entropy variants are proxy-only. The time-unit scenario is deliberately a diagnostic counterfactual, not an endorsed unit reinterpretation.",
        "",
        "No arbitrary dV/dI threshold perturbation was run: the original ranges are unknown and no defensible source-backed range is available. The only phase sensitivity uses the documented author helper selector as a distinct, clearly labeled option.",
        "",
        "## Confirmed observations, unresolved questions, and limitations",
        "",
        "- **Confirmed observation:** workbook-value differences exist under the current candidate definitions in each reported cohort; these are benchmark mismatches, not proof the extractor code is incorrect or that the workbook is correct.",
        "- **Confirmed observation:** the four entropy definitions are unknown and candidate entropy values are histogram proxies.",
        "- **Confirmed observation:** alignment is unverified; ambiguous and unmatched workbook rows are excluded, and all remaining comparisons are still diagnostic.",
        "- **Evidence-supported explanation:** the candidate uses explicit segmentation, interpolation, and moment conventions. The source does not establish that the workbook uses these conventions.",
        "- **Unresolved:** cycle identity for equal-count positional profiles; correctness of batch-6 capacity matches; original signal preprocessing and workbook formulas; whether the workbook was computed from 1 Hz source data or 128-point prepared MAT traces; source statistical weighting; exact phase thresholds; derivative and entropy definitions.",
        "- **Not investigated:** arbitrary threshold fitting, learned corrections, and any attempt to optimize candidate settings against workbook values.",
        "",
        "## Generated artifacts",
        "",
        "- `feature_error.csv`: overall feature summaries split by alignment cohort.",
        "- `batch_error.csv`, `profile_error.csv`, `cycle_decile_error.csv`: scoped summaries.",
        "- `cycle_wise_diagnostic_errors.csv.gz`: compressed long-form errors for all pairs retained by the existing alignment helper; every row carries its unverified/diagnostic cohort.",
        "- `cycle_wise_identity_verified_errors.csv`: header-only because no identity-verified matched observations exist.",
        "- `alignment_audit.csv`: matched, ambiguous, and unmatched row/cycle accounting.",
        "- `root_cause_evidence.csv` and `sensitivity_results.csv`: machine-readable evidence/hypotheses and controlled sensitivity results.",
        "- `sampling_audit.csv` and `phase_coverage.csv`: measured prepared-MAT sampling and candidate interval availability.",
        *[f"- `{name}`: visualization." for name in plot_names],
        "",
        "No prior report, candidate extractor, segmentation implementation, alignment behavior, API, UI, metadata, or model code was modified.",
        "",
    ]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def run_analysis(
    batches: Iterable[int] = range(1, 7),
    data_root: Path = DEFAULT_DATA_ROOT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    report_path: Path = DEFAULT_REPORT,
) -> dict[str, int]:
    batch_list = list(batches)
    output_dir.mkdir(parents=True, exist_ok=True)
    definitions = {definition.name: definition for definition in feature_definitions()}
    feature_order = {name: index + 1 for index, name in enumerate(FEATURE_NAMES)}

    feature_acc = {(cohort, name): ErrorAccumulator() for cohort in COHORTS for name in FEATURE_NAMES}
    batch_acc: dict[tuple[str, int, str], ErrorAccumulator] = {}
    profile_acc: dict[tuple[str, int, str, str], ErrorAccumulator] = {}
    cycle_bin_acc: dict[tuple[str, int, str, str, str], ErrorAccumulator] = {}
    alignment_rows: list[dict[str, Any]] = []
    pair_count = 0
    cycle_error_count = 0
    raw_cycle_count = 0
    workbook_row_count = 0
    ambiguous_count = 0
    unmatched_workbook_count = 0
    unmatched_raw_count = 0
    sensitivity_specs = _variant_specs()
    variant_features = {
        spec["variant"]: _variant_features(spec["variant"])
        for spec in sensitivity_specs
    }
    sensitivity_acc: dict[
        tuple[str, str, str], PairedSensitivityAccumulator
    ] = {}
    sampling_rows: list[dict[str, Any]] = []
    phase_acc: dict[tuple[str, int, str, str], dict[str, Any]] = {}

    cycle_csv_path = output_dir / "cycle_wise_diagnostic_errors.csv.gz"
    with gzip.open(cycle_csv_path, "wt", encoding="utf-8", newline="") as cycle_file:
        cycle_writer = csv.DictWriter(cycle_file, fieldnames=CYCLE_ERROR_HEADER)
        cycle_writer.writeheader()
        for batch in batch_list:
            profiles, sheets = load_batch(batch, data_root)
            for (sheet_name, frame), cycles in zip(sheets.items(), profiles):
                workbook_row_count += len(frame)
                raw_cycle_count += len(cycles)
                profile_key = sheet_name
                sampling_rows.append(_sampling_summary(batch, profile_key, cycles))
                if tuple(column for column in frame.columns if column != "label") != FEATURE_NAMES:
                    raise ValueError(f"Batch {batch}/{sheet_name}: workbook feature schema/order changed.")
                pairs, method, unmatched, ambiguous = _profile_pairs(cycles, frame)
                cohort = _alignment_class(method)
                used_cycles = {cycle_index for cycle_index, _ in pairs}
                ambiguous_set = set(ambiguous)
                unmatched_set = set(unmatched)
                for cycle_index, row_index in pairs:
                    cycle = cycles[cycle_index]
                    workbook_row = frame.iloc[row_index]
                    candidate_values, segments = extract_cycle(cycle, SegmentationPolicy())
                    pair_count += 1
                    cycle_decile = _cycle_bin(cycle.cycle_index, len(cycles))
                    for group, segment in segments.items():
                        phase_key = (cohort, batch, profile_key, group)
                        phase = phase_acc.setdefault(
                            phase_key,
                            {
                                "matched_cycles": 0,
                                "missing_segment_cycles": 0,
                                "disjoint_segment_cycles": 0,
                                "selected_sample_counts": [],
                                "durations_min": [],
                            },
                        )
                        phase["matched_cycles"] += 1
                        phase["missing_segment_cycles"] += int(not segment.intervals)
                        phase["disjoint_segment_cycles"] += int(segment.is_disjoint)
                        phase["selected_sample_counts"].append(
                            int(np.count_nonzero(segment.selected_mask))
                        )
                        phase["durations_min"].append(
                            float(sum(
                                interval.end_min - interval.start_min
                                for interval in segment.intervals
                            ))
                        )
                    variant_values: dict[str, dict[str, float | None]] = {}
                    for spec in sensitivity_specs:
                        name = spec["variant"]
                        if name == "author_documented_cc_selector":
                            alternate_policy = SegmentationPolicy(cc_method="author_documented")
                            alternate_values, _ = extract_cycle(cycle, alternate_policy)
                            variant_values[name] = {
                                feature: alternate_values.get(feature)
                                for feature in variant_features[name]
                            }
                        else:
                            arguments = _variant_arguments(name)
                            values: dict[str, float | None] = {}
                            selected = variant_features[name]
                            for group in GROUPS:
                                group_features = {
                                    feature for feature in selected
                                    if feature.startswith(group + "_")
                                }
                                if group_features:
                                    values.update(
                                        _segment_variant(
                                            cycle,
                                            group,
                                            segments[group],
                                            selected_features=group_features,
                                            **arguments,
                                        )
                                    )
                            variant_values[name] = values

                    for feature in FEATURE_NAMES:
                        reference = workbook_row[feature]
                        candidate = candidate_values.get(feature)
                        accumulator = feature_acc[(cohort, feature)]
                        accumulator.add(reference, candidate)
                        batch_key = (cohort, batch, feature)
                        profile_scope_key = (cohort, batch, profile_key, feature)
                        bin_key = (cohort, batch, profile_key, cycle_decile, feature)
                        batch_acc.setdefault(batch_key, ErrorAccumulator()).add(reference, candidate)
                        profile_acc.setdefault(profile_scope_key, ErrorAccumulator()).add(reference, candidate)
                        cycle_bin_acc.setdefault(bin_key, ErrorAccumulator()).add(reference, candidate)
                        ref_number, candidate_number = finite_float(reference), finite_float(candidate)
                        if ref_number is not None and candidate_number is not None:
                            error = candidate_number - ref_number
                            cycle_writer.writerow(
                                {
                                    "alignment_cohort": cohort,
                                    "alignment_method": method,
                                    "batch": batch,
                                    "profile": profile_key,
                                    "workbook_row": row_index + 1,
                                    "raw_cycle_index": cycle.cycle_index,
                                    "feature": feature,
                                    "benchmark_value": ref_number,
                                    "candidate_value": candidate_number,
                                    "signed_error_candidate_minus_benchmark": error,
                                    "absolute_error": abs(error),
                                    "candidate_formula_status": definitions[feature].formula_status,
                                }
                            )
                            cycle_error_count += 1
                        for spec in sensitivity_specs:
                            name = spec["variant"]
                            if feature not in variant_features[name]:
                                continue
                            variant_value = variant_values[name].get(feature)
                            sensitivity_acc.setdefault(
                                (cohort, name, feature),
                                PairedSensitivityAccumulator(),
                            ).add(
                                reference,
                                candidate,
                                variant_value,
                            )

                alignment_rows.append(
                    {
                        "alignment_summary": True,
                        "batch": batch,
                        "profile": profile_key,
                        "alignment_cohort": cohort,
                        "alignment_method": method,
                        "raw_cycles": len(cycles),
                        "workbook_rows": len(frame),
                        "matched_pairs": len(pairs),
                        "unmatched_workbook_rows": len(unmatched),
                        "ambiguous_workbook_rows": len(ambiguous),
                        "unmatched_raw_cycles": len(cycles) - len(used_cycles),
                        "mean_abs_label_difference": (
                            float(np.mean([
                                abs(cycles[cycle_index].capacity_label - float(frame.iloc[row_index]["label"]))
                                for cycle_index, row_index in pairs
                            ])) if pairs else None
                        ),
                        "max_abs_label_difference": (
                            float(np.max([
                                abs(cycles[cycle_index].capacity_label - float(frame.iloc[row_index]["label"]))
                                for cycle_index, row_index in pairs
                            ])) if pairs else None
                        ),
                    }
                )
                ambiguous_count += len(ambiguous)
                unmatched_workbook_count += len(unmatched)
                unmatched_raw_count += len(cycles) - len(used_cycles)
                for row_index in sorted(unmatched_set):
                    alignment_rows.append(
                        {
                            "alignment_summary": False,
                            "batch": batch,
                            "profile": profile_key,
                            "alignment_cohort": "ambiguous" if row_index in ambiguous_set else "unmatched_workbook",
                            "alignment_method": method,
                            "raw_cycles": len(cycles),
                            "workbook_rows": len(frame),
                            "matched_pairs": 0,
                            "unmatched_workbook_rows": 1,
                            "ambiguous_workbook_rows": int(row_index in ambiguous_set),
                            "unmatched_raw_cycles": 0,
                            "workbook_row": row_index + 1,
                            "raw_cycle_index": None,
                            "note": "Ambiguous row excluded" if row_index in ambiguous_set else "No unique monotone capacity match; excluded",
                        }
                    )
                for cycle_index, cycle in enumerate(cycles):
                    if cycle_index not in used_cycles:
                        alignment_rows.append(
                            {
                                "alignment_summary": False,
                                "batch": batch,
                                "profile": profile_key,
                                "alignment_cohort": "unmatched_raw_cycle",
                                "alignment_method": method,
                                "raw_cycles": len(cycles),
                                "workbook_rows": len(frame),
                                "matched_pairs": 0,
                                "unmatched_workbook_rows": 0,
                                "ambiguous_workbook_rows": 0,
                                "unmatched_raw_cycles": 1,
                                "workbook_row": None,
                                "raw_cycle_index": cycle.cycle_index,
                                "note": "Raw cycle not used by existing alignment helper",
                            }
                        )

    feature_rows: list[dict[str, Any]] = []
    for cohort in COHORTS:
        for feature in FEATURE_NAMES:
            metrics = _metrics(feature_acc[(cohort, feature)])
            definition = definitions[feature]
            feature_rows.append(
                {
                    "alignment_cohort": cohort,
                    "scope": "overall",
                    "feature_order": feature_order[feature],
                    "feature": feature,
                    "group": definition.group,
                    "unit": definition.unit,
                    "formula_status": definition.formula_status,
                    **metrics,
                }
            )
    batch_rows: list[dict[str, Any]] = []
    for (cohort, batch, feature), accumulator in batch_acc.items():
        definition = definitions[feature]
        batch_rows.append(
            {
                "alignment_cohort": cohort,
                "scope": f"batch-{batch}",
                "batch": batch,
                "feature_order": feature_order[feature],
                "feature": feature,
                "group": definition.group,
                "unit": definition.unit,
                **_metrics(accumulator),
            }
        )
    profile_rows: list[dict[str, Any]] = []
    for (cohort, batch, profile, feature), accumulator in profile_acc.items():
        definition = definitions[feature]
        profile_rows.append(
            {
                "alignment_cohort": cohort,
                "scope": "profile",
                "batch": batch,
                "profile": profile,
                "feature_order": feature_order[feature],
                "feature": feature,
                "group": definition.group,
                "unit": definition.unit,
                **_metrics(accumulator),
            }
        )
    cycle_bin_rows: list[dict[str, Any]] = []
    for (cohort, batch, profile, decile, feature), accumulator in cycle_bin_acc.items():
        definition = definitions[feature]
        cycle_bin_rows.append(
            {
                "alignment_cohort": cohort,
                "batch": batch,
                "profile": profile,
                "cycle_decile": decile,
                "feature_order": feature_order[feature],
                "feature": feature,
                "group": definition.group,
                "unit": definition.unit,
                **_metrics(accumulator),
            }
        )
    sensitivity_rows: list[dict[str, Any]] = []
    specs_by_name = {spec["variant"]: spec for spec in sensitivity_specs}
    for (cohort, variant, feature), accumulator in sensitivity_acc.items():
        baseline_metrics, variant_metrics = _paired_sensitivity_metrics(accumulator)
        spec = specs_by_name[variant]
        sensitivity_rows.append(
            {
                "alignment_cohort": cohort,
                "variant": variant,
                "axis": spec["axis"],
                "settings": str(spec["settings"]),
                "description": spec["description"],
                "evidence_class": spec["evidence_class"],
                "feature": feature,
                "group": definitions[feature].group,
                "unit": definitions[feature].unit,
                "baseline_mae": baseline_metrics["mae"],
                "variant_mae": variant_metrics["mae"],
                "delta_mae": (
                    variant_metrics["mae"] - baseline_metrics["mae"]
                    if variant_metrics["mae"] is not None and baseline_metrics["mae"] is not None
                    else None
                ),
                "delta_relative_mae_pct": (
                    variant_metrics["relative_mae_pct"]
                    - baseline_metrics["relative_mae_pct"]
                    if variant_metrics["relative_mae_pct"] is not None
                    and baseline_metrics["relative_mae_pct"] is not None
                    else None
                ),
                **{
                    key: variant_metrics[key]
                    for key in (
                        "valid_observations",
                        "invalid_candidate",
                        "mape_pct",
                        "mean_signed_error",
                        "relative_mae_pct",
                    )
                },
            }
        )
    phase_rows = []
    for (cohort, batch, profile, group), values in phase_acc.items():
        phase_rows.append(
            {
                "alignment_cohort": cohort,
                "batch": batch,
                "profile": profile,
                "group": group,
                "matched_cycles": values["matched_cycles"],
                "missing_segment_cycles": values["missing_segment_cycles"],
                "disjoint_segment_cycles": values["disjoint_segment_cycles"],
                "median_selected_sample_count": (
                    float(np.median(values["selected_sample_counts"]))
                    if values["selected_sample_counts"] else None
                ),
                "median_interval_duration_min": (
                    float(np.median(values["durations_min"]))
                    if values["durations_min"] else None
                ),
            }
        )
    root_rows = _root_cause_rows(
        feature_rows,
        batch_rows,
        profile_rows,
        alignment_rows,
        sensitivity_rows,
    )
    plot_names = _save_plots(feature_rows, profile_rows, output_dir)

    _write_rows(output_dir / "feature_error.csv", feature_rows)
    _write_rows(output_dir / "batch_error.csv", batch_rows)
    _write_rows(output_dir / "profile_error.csv", profile_rows)
    _write_rows(output_dir / "cycle_decile_error.csv", cycle_bin_rows)
    _write_rows(output_dir / "alignment_audit.csv", alignment_rows)
    _write_rows(output_dir / "root_cause_evidence.csv", root_rows)
    _write_rows(output_dir / "sensitivity_results.csv", sensitivity_rows)
    _write_rows(output_dir / "sampling_audit.csv", sampling_rows)
    _write_rows(output_dir / "phase_coverage.csv", phase_rows)
    pd.DataFrame(columns=CYCLE_ERROR_HEADER + ["identity_status"]).to_csv(
        output_dir / "cycle_wise_identity_verified_errors.csv", index=False
    )
    _write_report(
        report_path,
        feature_rows,
        batch_rows,
        profile_rows,
        cycle_bin_rows,
        alignment_rows,
        root_rows,
        sensitivity_rows,
        plot_names,
        sampling_rows,
        phase_rows,
    )
    return {
        "batches": len(batch_list),
        "profiles": len({(row["batch"], row["profile"]) for row in alignment_rows}),
        "raw_cycles": raw_cycle_count,
        "workbook_rows": workbook_row_count,
        "matched_pairs": pair_count,
        "ambiguous_rows": ambiguous_count,
        "unmatched_workbook_rows": unmatched_workbook_count,
        "unmatched_raw_cycles": unmatched_raw_count,
        "feature_rows": len(feature_rows),
        "batch_feature_rows": len(batch_rows),
        "profile_feature_rows": len(profile_rows),
        "cycle_decile_rows": len(cycle_bin_rows),
        "sensitivity_rows": len(sensitivity_rows),
        "sampling_profiles": len(sampling_rows),
        "phase_profile_rows": len(phase_rows),
        "cycle_error_rows": cycle_error_count,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run isolated XJTU candidate feature error analysis.")
    parser.add_argument("--batches", nargs="+", type=int, default=list(range(1, 7)))
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    counts = run_analysis(args.batches, args.data_root, args.output_dir, args.report)
    print("XJTU error analysis complete:")
    for key, value in counts.items():
        print(f"  {key}: {value}")
    print(f"  report: {args.report}")
    print(f"  artifacts: {args.output_dir}")


if __name__ == "__main__":
    main()
