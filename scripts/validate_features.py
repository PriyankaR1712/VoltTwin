"""Recompute candidate XJTU charge features and compare them with workbook values.

The candidate formulas are deliberately not presented as the original feature
implementation. See reports/feature_formula_validation.md for provenance and
limitations.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.io import loadmat


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "reference" / "SOHbenchmark" / "data" / "XJTU"
GROUPS = ("CC", "dV", "CV", "dI", "Charge")
FORMULA_STATUS = (
    "Original formula implementation not located; candidate approximation only."
)
STAT_GRID_SIZE = 257
LABEL_MATCH_TOLERANCE = 1e-6


@dataclass(frozen=True)
class FeatureDescription:
    name: str
    group: str
    signal: str
    segment: str
    candidate_formula: str
    evidence: str
    source_notes: str
    unit: str


@dataclass(frozen=True)
class CycleInterval:
    start: float
    end: float
    point_start: float | None
    point_end: float | None


@dataclass
class Observation:
    expected: float
    candidate: float
    native: float | None
    point_boundary: float | None
    left_integral: float | None
    right_integral: float | None
    sample_std: float | None
    adjusted_skew: float | None
    fisher_kurtosis: float | None
    battery: str
    workbook_row: int
    raw_cycle: int


def describe_feature(name: str) -> FeatureDescription:
    group = next(
        (candidate for candidate in GROUPS if name.startswith(candidate + "_")),
        None,
    )
    if group is None:
        raise ValueError(f"Unrecognized feature name: {name}")

    suffix = name[len(group) + 1 :]
    segment = {
        "CC": "initial constant-current charge candidate",
        "dV": "candidate CC voltage window: 3.9-4.0 V",
        "CV": "candidate constant-voltage charge candidate",
        "dI": "candidate CV current window: 1.0-0.9 A",
        "Charge": "complete charge record",
    }[group]
    source_notes = {
        "CC": (
            "temp_preprocessing_source/XJTUBatteryClass.py::get_CC_value "
            "documents a current/voltage CC selector, but not this workbook feature formula."
        ),
        "dV": (
            "No local source defines this feature interval; the 3.9-4.0 V window "
            "is inferred from the workbook values and derivative name."
        ),
        "CV": (
            "temp_preprocessing_source/XJTUBatteryClass.py::get_CV_value "
            "documents voltage >=4.199 V selection, but not this workbook feature formula."
        ),
        "dI": (
            "No local source defines this feature interval; the 1.0-0.9 A window "
            "is inferred from the workbook values and derivative name."
        ),
        "Charge": (
            "The local benchmark loader reads prepared workbook values; no local "
            "source defines the complete-charge feature equations."
        ),
    }[group]

    if suffix == "energy":
        signal = "voltage and current"
        formula = "Trapezoidal integral of V(t)*I(t) over the candidate interval; minutes converted to hours."
        evidence = "Standard physical candidate; not located as the workbook's original implementation."
        unit = "Wh"
    elif suffix == "Q":
        signal = "current and time"
        formula = "Trapezoidal integral of I(t) over the candidate interval; minutes converted to hours."
        evidence = "Standard physical candidate; not located as the workbook's original implementation."
        unit = "Ah"
    elif suffix == "t_mean":
        signal = "elapsed time"
        formula = "Arithmetic mean of local elapsed time on a 257-point uniform-time linear interpolation grid."
        evidence = "Candidate uses segment-local time and explicit linear interpolation."
        unit = "min"
    elif suffix in ("CCCT", "CVCT"):
        signal = "time"
        formula = "End time minus start time of the candidate interval."
        evidence = "The label suggests a phase duration; exact original boundaries were not located."
        unit = "min"
    elif suffix in ("dV_devide_dt", "dI_devide_dt"):
        signal = "voltage and time" if suffix.startswith("dV") else "current and time"
        formula = "Endpoint signal difference divided by candidate interval duration."
        evidence = "Derivative interval and boundary values are candidate interpretations inferred from names and values."
        unit = "V/min" if suffix.startswith("dV") else "A/min"
    elif suffix == "entropy":
        signal = {
            "CC": "voltage (proxy channel)",
            "dV": "voltage (proxy channel)",
            "CV": "current (proxy channel)",
            "dI": "current (proxy channel)",
            "Charge": "current (proxy channel)",
        }[group]
        formula = "Shannon entropy (nats) of a 16-bin equal-width histogram of the proxy channel on the interpolated interval."
        evidence = "Estimator and signal are unknown; this histogram is only a reproducible diagnostic proxy."
        source_notes += " No local source identifies the entropy signal, estimator, bins, or logarithm base."
        unit = "nats"
    else:
        signal_code, statistic = suffix.split("_", maxsplit=1)
        signal = {
            "V": "voltage",
            "C": "current",
            "T": "temperature",
        }[signal_code]
        if statistic == "mean":
            formula = f"Arithmetic mean of {signal} on a 257-point uniform-time linear interpolation grid."
            evidence = "Candidate descriptive statistic; signal and estimator conventions are not sourced."
        elif statistic == "std":
            formula = f"Population standard deviation (ddof=0) of {signal} on the interpolated interval."
            evidence = "Population convention is a candidate; the original convention is not sourced."
        elif statistic == "skewness":
            formula = f"Biased third standardized central moment of {signal} (m3/m2**1.5)."
            evidence = "Biased moment convention is a candidate; the original convention is not sourced."
        elif statistic == "kurtosis":
            formula = f"Pearson fourth standardized central moment of {signal} (m4/m2**2; normal reference is 3)."
            evidence = "Pearson/bias convention is a candidate; the original convention is not sourced."
        else:
            raise ValueError(f"Unrecognized feature suffix: {name}")

        unit = {
            "mean": {"V": "V", "C": "A", "T": "degC"},
            "std": {"V": "V", "C": "A", "T": "degC"},
            "skewness": {"V": "dimensionless", "C": "dimensionless", "T": "dimensionless"},
            "kurtosis": {"V": "dimensionless", "C": "dimensionless", "T": "dimensionless"},
        }[statistic][signal_code]

    return FeatureDescription(
        name=name,
        group=group,
        signal=signal,
        segment=segment,
        candidate_formula=formula,
        evidence=evidence,
        source_notes=source_notes,
        unit=unit,
    )


def _interpolate_time(t: np.ndarray, signal: np.ndarray, threshold: float, left: int, right: int) -> float:
    y0 = float(signal[left])
    y1 = float(signal[right])
    if y0 == y1:
        return float(t[right])
    fraction = (threshold - y0) / (y1 - y0)
    return float(t[left] + fraction * (t[right] - t[left]))


def _crossing_time(
    t: np.ndarray,
    signal: np.ndarray,
    threshold: float,
    start: float,
    end: float,
    direction: str,
) -> float | None:
    selected = np.flatnonzero((t >= start) & (t <= end))
    if not len(selected):
        return None

    first = int(selected[0])
    if direction == "rising" and signal[first] >= threshold:
        return max(start, float(t[first]))
    if direction == "falling" and signal[first] <= threshold:
        return max(start, float(t[first]))

    for right in range(first + 1, len(t)):
        if t[right] > end:
            break
        left = right - 1
        if direction == "rising" and signal[left] < threshold <= signal[right]:
            return _interpolate_time(t, signal, threshold, left, right)
        if direction == "falling" and signal[left] > threshold >= signal[right]:
            return _interpolate_time(t, signal, threshold, left, right)
    return None


def _point_interval(t: np.ndarray, start: float, end: float) -> tuple[float | None, float | None]:
    indices = np.flatnonzero((t >= start) & (t <= end))
    if not len(indices):
        return None, None
    return float(t[indices[0]]), float(t[indices[-1]])


def _make_interval(t: np.ndarray, start: float, end: float) -> CycleInterval | None:
    if not (math.isfinite(start) and math.isfinite(end)) or end <= start:
        return None
    point_start, point_end = _point_interval(t, start, end)
    return CycleInterval(start, end, point_start, point_end)


def _phase_intervals(
    t: np.ndarray,
    voltage: np.ndarray,
    current: np.ndarray,
) -> dict[str, CycleInterval | None]:
    plateau = float(np.percentile(current, 95))
    current_threshold = 0.975 * plateau

    cc_indices = np.flatnonzero(
        (current >= current_threshold) & (voltage <= 4.199)
    )
    cc = None
    cc_start = float(t[0])
    cc_end = float(t[0])
    cc_start_idx: int | None = None
    cc_end_idx: int | None = None
    if len(cc_indices):
        cc_start_idx = int(cc_indices[0])
        cc_end_idx = int(cc_indices[-1])
        cc_start = float(t[cc_start_idx])
        cc_end = float(t[cc_end_idx])
        if cc_start_idx > 0:
            left = cc_start_idx - 1
            boundaries = []
            if voltage[left] < 4.199 <= voltage[cc_start_idx]:
                boundaries.append(
                    _interpolate_time(t, voltage, 4.199, left, cc_start_idx)
                )
            if current[left] < current_threshold <= current[cc_start_idx]:
                boundaries.append(
                    _interpolate_time(
                        t, current, current_threshold, left, cc_start_idx
                    )
                )
            if boundaries:
                cc_start = max(boundaries)
        if cc_end_idx < len(t) - 1:
            right = cc_end_idx + 1
            boundaries = []
            if voltage[cc_end_idx] <= 4.199 < voltage[right]:
                boundaries.append(
                    _interpolate_time(t, voltage, 4.199, cc_end_idx, right)
                )
            if current[cc_end_idx] >= current_threshold > current[right]:
                boundaries.append(
                    _interpolate_time(
                        t, current, current_threshold, cc_end_idx, right
                    )
                )
            if boundaries:
                cc_end = min(boundaries)
        cc = _make_interval(t, cc_start, cc_end)

    cv_start = _crossing_time(
        t, voltage, 4.199, float(t[0]), float(t[-1]), "rising"
    )
    cv = (
        _make_interval(t, cv_start, float(t[-1]))
        if cv_start is not None
        else None
    )

    dv_start = (
        _crossing_time(t, voltage, 3.9, cc.start, cc.end, "rising")
        if cc is not None
        else None
    )
    if (
        dv_start is None
        and cc is not None
        and cc_start_idx is not None
        and voltage[cc_start_idx] >= 3.9
    ):
        dv_start = cc.start
    dv_end = (
        _crossing_time(t, voltage, 4.0, dv_start, cc.end, "rising")
        if dv_start is not None and cc is not None
        else None
    )
    if (
        dv_end is None
        and dv_start is not None
        and cc is not None
        and cc_end_idx is not None
        and voltage[cc_end_idx] <= 4.0
    ):
        dv_end = cc.end
    dv = (
        _make_interval(t, dv_start, dv_end)
        if dv_start is not None and dv_end is not None
        else None
    )

    di_start = (
        _crossing_time(t, current, 1.0, cv.start, cv.end, "falling")
        if cv is not None
        else None
    )
    di_end = (
        _crossing_time(t, current, 0.9, di_start, cv.end, "falling")
        if di_start is not None and cv is not None
        else None
    )
    di = (
        _make_interval(t, di_start, di_end)
        if di_start is not None and di_end is not None
        else None
    )

    return {
        "CC": cc,
        "dV": dv,
        "CV": cv,
        "dI": di,
        "Charge": _make_interval(t, float(t[0]), float(t[-1])),
    }


def _interval_arrays(
    t: np.ndarray,
    signals: dict[str, np.ndarray],
    interval: CycleInterval,
    dense: bool,
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    if dense:
        sample_t = np.linspace(interval.start, interval.end, STAT_GRID_SIZE)
    else:
        inside = t[(t > interval.start) & (t < interval.end)]
        sample_t = np.unique(
            np.concatenate(
                ([interval.start], inside, [interval.end])
            )
        )
    sample_signals = {
        name: np.interp(sample_t, t, values)
        for name, values in signals.items()
    }
    return sample_t, sample_signals


def _moments(values: np.ndarray) -> tuple[float, float, float, float]:
    mean = float(np.mean(values))
    centered = values - mean
    second = float(np.mean(centered**2))
    std = math.sqrt(max(second, 0.0))
    if second <= np.finfo(float).eps:
        return mean, std, 0.0, 0.0
    third = float(np.mean(centered**3))
    fourth = float(np.mean(centered**4))
    return mean, std, third / (second**1.5), fourth / (second**2)


def _histogram_entropy(values: np.ndarray) -> float:
    counts, _ = np.histogram(values, bins=16)
    probabilities = counts[counts > 0].astype(np.float64)
    probabilities /= probabilities.sum()
    return float(-np.sum(probabilities * np.log(probabilities)))


def _integral(t: np.ndarray, values: np.ndarray) -> float:
    if len(t) < 2:
        return float("nan")
    return float(np.sum((values[:-1] + values[1:]) * 0.5 * np.diff(t)))


def _left_integral(t: np.ndarray, values: np.ndarray) -> float:
    if len(t) < 2:
        return float("nan")
    return float(np.sum(values[:-1] * np.diff(t)))


def _right_integral(t: np.ndarray, values: np.ndarray) -> float:
    if len(t) < 2:
        return float("nan")
    return float(np.sum(values[1:] * np.diff(t)))


def _values_for_interval(
    group: str,
    interval: CycleInterval | None,
    t: np.ndarray,
    signals: dict[str, np.ndarray],
) -> tuple[
    dict[str, float],
    dict[str, float],
    dict[str, float],
    dict[str, float],
    dict[str, float],
    dict[str, float],
]:
    if interval is None or interval.end <= interval.start:
        return {}, {}, {}, {}, {}, {}

    dense_t, dense = _interval_arrays(t, signals, interval, dense=True)
    native_t, native = _interval_arrays(t, signals, interval, dense=False)
    point_result: dict[str, float] = {}
    if (
        interval.point_start is not None
        and interval.point_end is not None
        and interval.point_end > interval.point_start
    ):
        point_interval = CycleInterval(
            interval.point_start,
            interval.point_end,
            interval.point_start,
            interval.point_end,
        )
        point_t, point = _interval_arrays(t, signals, point_interval, dense=False)
    else:
        point_t, point = np.array([], dtype=float), {}

    voltage_native = native["voltage"]
    current_native = native["current"]
    energy_native = current_native * voltage_native
    q_native = current_native
    left_energy = _left_integral(native_t, energy_native) / 60.0
    right_energy = _right_integral(native_t, energy_native) / 60.0
    left_q = _left_integral(native_t, q_native) / 60.0
    right_q = _right_integral(native_t, q_native) / 60.0

    dense_stats = {
        key: _moments(values)
        for key, values in dense.items()
    }
    native_stats = {
        key: _moments(values)
        for key, values in native.items()
    }
    point_stats = {
        key: _moments(values)
        for key, values in point.items()
    }
    alternative_stats: dict[str, float] = {}

    dense_primary = dense["voltage"] if group in ("CC", "dV") else dense["current"]
    native_primary = native["voltage"] if group in ("CC", "dV") else native["current"]
    point_primary = point.get(
        "voltage" if group in ("CC", "dV") else "current",
        np.array([], dtype=float),
    )

    dV_dt = (
        float((dense["voltage"][-1] - dense["voltage"][0]) / (interval.end - interval.start))
        if group == "dV"
        else float("nan")
    )
    dI_dt = (
        float((dense["current"][-1] - dense["current"][0]) / (interval.end - interval.start))
        if group == "dI"
        else float("nan")
    )

    dense_result: dict[str, float] = {
        f"{group}_energy": _integral(native_t, energy_native) / 60.0,
        f"{group}_Q": _integral(native_t, q_native) / 60.0,
        f"{group}_t_mean": float(np.mean(dense_t - interval.start)),
        f"{group}_entropy": _histogram_entropy(dense_primary),
    }
    native_result: dict[str, float] = {
        f"{group}_energy": dense_result[f"{group}_energy"],
        f"{group}_Q": dense_result[f"{group}_Q"],
        f"{group}_t_mean": float(np.mean(native_t - interval.start)),
        f"{group}_entropy": _histogram_entropy(native_primary),
    }
    left_result: dict[str, float] = {
        f"{group}_energy": left_energy,
        f"{group}_Q": left_q,
    }
    right_result: dict[str, float] = {
        f"{group}_energy": right_energy,
        f"{group}_Q": right_q,
    }

    if group in ("CC", "CV"):
        duration_name = "CC_CCCT" if group == "CC" else "CV_CVCT"
        dense_result[duration_name] = interval.end - interval.start
        native_result[duration_name] = interval.end - interval.start
    elif group == "dV":
        dense_result["dV_dV_devide_dt"] = dV_dt
        native_result["dV_dV_devide_dt"] = dV_dt
    elif group == "dI":
        dense_result["dI_dI_devide_dt"] = dI_dt
        native_result["dI_dI_devide_dt"] = dI_dt

    for channel, suffix in (
        ("voltage", "V"),
        ("current", "C"),
        ("temperature", "T"),
    ):
        mean, std, skewness, pearson_kurtosis = dense_stats[channel]
        native_mean, native_std, native_skewness, native_kurtosis = native_stats[channel]
        dense_result[f"{group}_{suffix}_mean"] = mean
        dense_result[f"{group}_{suffix}_std"] = std
        dense_result[f"{group}_{suffix}_skewness"] = skewness
        dense_result[f"{group}_{suffix}_kurtosis"] = pearson_kurtosis
        native_result[f"{group}_{suffix}_mean"] = native_mean
        native_result[f"{group}_{suffix}_std"] = native_std
        native_result[f"{group}_{suffix}_skewness"] = native_skewness
        native_result[f"{group}_{suffix}_kurtosis"] = native_kurtosis
        alternative_stats[f"{group}_{suffix}_std"] = float(
            std * math.sqrt(len(dense[channel]) / (len(dense[channel]) - 1))
        )
        alternative_stats[f"{group}_{suffix}_skewness"] = (
            skewness
            * math.sqrt(len(dense[channel]) * (len(dense[channel]) - 1))
            / (len(dense[channel]) - 2)
        )
        n = len(dense[channel])
        alternative_stats[f"{group}_{suffix}_kurtosis"] = (
            (n - 1)
            / ((n - 2) * (n - 3))
            * ((n + 1) * (pearson_kurtosis - 3.0) + 6.0)
        )

    if len(point_t) >= 2:
        point_result.update(
            {
                f"{group}_energy": _integral(point_t, point["voltage"] * point["current"]) / 60.0,
                f"{group}_Q": _integral(point_t, point["current"]) / 60.0,
                f"{group}_t_mean": float(np.mean(point_t - point_t[0])),
                f"{group}_entropy": _histogram_entropy(point_primary),
            }
        )
        if group in ("CC", "CV"):
            duration_name = "CC_CCCT" if group == "CC" else "CV_CVCT"
            point_result[duration_name] = float(point_t[-1] - point_t[0])
        elif group == "dV":
            point_result["dV_dV_devide_dt"] = float(
                (point["voltage"][-1] - point["voltage"][0])
                / (point_t[-1] - point_t[0])
            )
        elif group == "dI":
            point_result["dI_dI_devide_dt"] = float(
                (point["current"][-1] - point["current"][0])
                / (point_t[-1] - point_t[0])
            )
        for channel, suffix in (
            ("voltage", "V"),
            ("current", "C"),
            ("temperature", "T"),
        ):
            mean, std, skewness, pearson_kurtosis = point_stats[channel]
            point_result[f"{group}_{suffix}_mean"] = mean
            point_result[f"{group}_{suffix}_std"] = std
            point_result[f"{group}_{suffix}_skewness"] = skewness
            point_result[f"{group}_{suffix}_kurtosis"] = pearson_kurtosis

    return (
        dense_result,
        native_result,
        point_result,
        left_result,
        right_result,
        alternative_stats,
    )


def calculate_cycle_candidates(
    cycle: Any,
    feature_names: list[str],
) -> tuple[
    dict[str, float],
    dict[str, float],
    dict[str, float],
    dict[str, float],
    dict[str, float],
    dict[str, float],
]:
    required = ("relative_time_min", "voltage_V", "current_A", "temperature_C")
    arrays: dict[str, np.ndarray] = {}
    for field in required:
        value = getattr(cycle, field, None)
        if value is None:
            raise ValueError(f"Raw cycle has no {field!r} field.")
        arrays[field] = np.asarray(value, dtype=np.float64).reshape(-1)
    lengths = {len(values) for values in arrays.values()}
    if len(lengths) != 1 or not lengths or next(iter(lengths)) < 2:
        raise ValueError("Raw cycle channels do not have matching lengths >= 2.")
    if any(not np.isfinite(values).all() for values in arrays.values()):
        raise ValueError("Raw cycle contains non-finite channel values.")

    t = arrays["relative_time_min"]
    if np.any(np.diff(t) <= 0):
        raise ValueError("Raw relative_time_min must be strictly increasing.")
    signals = {
        "voltage": arrays["voltage_V"],
        "current": arrays["current_A"],
        "temperature": arrays["temperature_C"],
    }
    intervals = _phase_intervals(t, signals["voltage"], signals["current"])

    main_values: dict[str, float] = {}
    native_values: dict[str, float] = {}
    point_values: dict[str, float] = {}
    left_values: dict[str, float] = {}
    right_values: dict[str, float] = {}
    alternatives: dict[str, float] = {}
    for group in GROUPS:
        dense, native, point, left, right, stat_alternatives = _values_for_interval(
            group, intervals[group], t, signals
        )
        main_values.update(dense)
        native_values.update(native)
        point_values.update(point)
        left_values.update(left)
        right_values.update(right)
        alternatives.update(stat_alternatives)

    return (
        {name: main_values.get(name, float("nan")) for name in feature_names},
        {name: native_values.get(name, float("nan")) for name in feature_names},
        {name: point_values.get(name, float("nan")) for name in feature_names},
        {name: left_values.get(name, float("nan")) for name in feature_names},
        {name: right_values.get(name, float("nan")) for name in feature_names},
        alternatives,
    )


def _capacity_value(cycle: Any) -> float:
    value = getattr(cycle, "capacity", None)
    if value is None:
        raise ValueError("Raw cycle has no scalar 'capacity' for row alignment.")
    array = np.asarray(value, dtype=np.float64).reshape(-1)
    if not len(array) or not np.isfinite(array[0]):
        raise ValueError("Raw cycle capacity is missing or non-finite.")
    return float(array[0])


def _monotone_capacity_alignment(
    cycles: list[Any],
    labels: np.ndarray,
) -> tuple[list[tuple[int, int]], list[int]]:
    capacities = np.asarray([_capacity_value(cycle) for cycle in cycles])
    pairs: list[tuple[int, int]] = []
    unmatched: list[int] = []
    cursor = -1
    for row_index, label in enumerate(labels):
        candidates = np.flatnonzero(
            np.abs(capacities[cursor + 1 :] - label) <= LABEL_MATCH_TOLERANCE
        )
        if len(candidates):
            cycle_index = cursor + 1 + int(candidates[0])
            pairs.append((cycle_index, row_index))
            cursor = cycle_index
        else:
            unmatched.append(row_index)
    return pairs, unmatched


def align_profile_rows(
    cycles: list[Any],
    frame: pd.DataFrame,
) -> tuple[list[tuple[int, int]], list[int], str, list[float]]:
    if "label" not in frame.columns:
        raise ValueError("Feature workbook sheet has no 'label' column.")
    labels = frame["label"].to_numpy(dtype=np.float64)
    if not np.isfinite(labels).all():
        raise ValueError("Feature workbook contains non-finite labels.")

    if len(cycles) == len(frame):
        pairs = [(index, index) for index in range(len(frame))]
        differences = [
            abs(_capacity_value(cycles[index]) - float(labels[index]))
            for index in range(len(frame))
        ]
        return pairs, [], "cycle-order positional (equal row counts)", differences
    if len(cycles) < len(frame):
        raise ValueError(
            f"Raw cycle count {len(cycles)} is less than workbook rows {len(frame)}; "
            "a non-destructive alignment cannot be inferred."
        )

    pairs, unmatched = _monotone_capacity_alignment(cycles, labels)
    differences = [
        abs(_capacity_value(cycles[cycle_index]) - float(labels[row_index]))
        for cycle_index, row_index in pairs
    ]
    return (
        pairs,
        unmatched,
        f"monotone exact-capacity match (tolerance {LABEL_MATCH_TOLERANCE:g})",
        differences,
    )


def _load_batch(batch: int) -> tuple[list[Any], dict[str, pd.DataFrame]]:
    mat_path = DATA_ROOT / "charge" / f"batch-{batch}.mat"
    xlsx_path = DATA_ROOT / "handcraft_features" / f"batch-{batch}_features.xlsx"
    if not mat_path.is_file():
        raise FileNotFoundError(f"Raw charge file not found: {mat_path}")
    if not xlsx_path.is_file():
        raise FileNotFoundError(f"Feature workbook not found: {xlsx_path}")

    loaded = loadmat(mat_path, squeeze_me=True, struct_as_record=False)
    if "battery" not in loaded:
        raise ValueError(f"{mat_path} has no 'battery' array.")
    batteries = list(np.atleast_1d(loaded["battery"]))
    sheets = pd.read_excel(xlsx_path, sheet_name=None)
    return batteries, sheets


def _metrics(observations: list[Observation]) -> dict[str, float | int | None]:
    valid = [
        observation
        for observation in observations
        if math.isfinite(observation.expected)
        and math.isfinite(observation.candidate)
    ]
    if not valid:
        return {
            "valid_pairs": 0,
            "profiles": 0,
            "max_error_profile": None,
            "max_error_workbook_row": None,
            "max_error_raw_cycle": None,
            "mean_abs_reference": None,
            "mae": None,
            "rmse": None,
            "max_abs_error": None,
            "relative_error_pct": None,
            "native_mae": None,
            "point_boundary_mae": None,
            "left_integral_mae": None,
            "right_integral_mae": None,
            "sample_std_mae": None,
            "adjusted_skew_mae": None,
            "fisher_kurtosis_mae": None,
        }

    expected = np.asarray([item.expected for item in valid], dtype=np.float64)
    candidate = np.asarray([item.candidate for item in valid], dtype=np.float64)
    error = candidate - expected

    def variant_mae(field: str) -> float | None:
        pairs = [
            (item.expected, getattr(item, field))
            for item in valid
            if getattr(item, field) is not None
            and math.isfinite(float(getattr(item, field)))
        ]
        if not pairs:
            return None
        return float(
            np.mean(
                np.abs(
                    np.asarray([pred for _, pred in pairs])
                    - np.asarray([actual for actual, _ in pairs])
                )
            )
        )

    mean_abs_reference = float(np.mean(np.abs(expected)))
    relative_error = (
        float(np.mean(np.abs(error)) / mean_abs_reference * 100.0)
        if mean_abs_reference > 0
        else None
    )
    max_error_index = int(np.argmax(np.abs(error)))
    max_error_observation = valid[max_error_index]
    return {
        "valid_pairs": len(valid),
        "profiles": len({item.battery for item in valid}),
        "max_error_profile": max_error_observation.battery,
        "max_error_workbook_row": max_error_observation.workbook_row,
        "max_error_raw_cycle": max_error_observation.raw_cycle,
        "mean_abs_reference": mean_abs_reference,
        "mae": float(np.mean(np.abs(error))),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "max_abs_error": float(np.max(np.abs(error))),
        "relative_error_pct": relative_error,
        "native_mae": variant_mae("native"),
        "point_boundary_mae": variant_mae("point_boundary"),
        "left_integral_mae": variant_mae("left_integral"),
        "right_integral_mae": variant_mae("right_integral"),
        "sample_std_mae": variant_mae("sample_std"),
        "adjusted_skew_mae": variant_mae("adjusted_skew"),
        "fisher_kurtosis_mae": variant_mae("fisher_kurtosis"),
    }


def _observation(
    expected: float,
    candidate: float,
    native: float | None,
    point_boundary: float | None,
    left_integral: float | None,
    right_integral: float | None,
    alternative: float | None,
    feature_name: str,
    battery: str,
    workbook_row: int,
    raw_cycle: int,
) -> Observation:
    is_std = feature_name.endswith("_std")
    is_skew = feature_name.endswith("_skewness")
    is_kurtosis = feature_name.endswith("_kurtosis")
    return Observation(
        expected=expected,
        candidate=candidate,
        native=native,
        point_boundary=point_boundary,
        left_integral=left_integral,
        right_integral=right_integral,
        sample_std=alternative if is_std else None,
        adjusted_skew=alternative if is_skew else None,
        fisher_kurtosis=alternative if is_kurtosis else None,
        battery=battery,
        workbook_row=workbook_row,
        raw_cycle=raw_cycle,
    )

def validate_batches(
    batches: list[int],
    battery_ids: set[int] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[int, dict[str, Any]]]:
    observations: dict[str, dict[str, list[Observation]]] = {
        "overall": defaultdict(list)
    }
    batch_observations: dict[int, dict[str, list[Observation]]] = {}
    diagnostics: dict[int, dict[str, Any]] = {}
    feature_names: list[str] | None = None

    for batch in batches:
        raw_batteries, sheets = _load_batch(batch)
        sheet_items = list(sheets.items())
        if len(raw_batteries) != len(sheet_items):
            raise ValueError(
                f"Batch {batch}: raw profile count {len(raw_batteries)} does not "
                f"match workbook sheet count {len(sheet_items)}."
            )
        if not sheet_items:
            raise ValueError(f"Batch {batch} workbook has no sheets.")

        current_features = [
            column for column in sheet_items[0][1].columns if column != "label"
        ]
        if len(current_features) != 67 or len(set(current_features)) != 67:
            raise ValueError(
                f"Batch {batch} first sheet must contain 67 unique features and a label."
            )
        if feature_names is None:
            feature_names = current_features
        elif current_features != feature_names:
            raise ValueError(f"Batch {batch} feature order differs from batch 1.")

        batch_observations[batch] = defaultdict(list)
        profile_diagnostics: list[dict[str, Any]] = []
        batch_aligned_rows = 0
        batch_unmatched_rows = 0
        batch_alignment_errors: list[float] = []

        for battery_number, ((sheet_name, frame), raw_battery) in enumerate(
            zip(sheet_items, raw_batteries), start=1
        ):
            if battery_ids is not None and battery_number not in battery_ids:
                continue
            cycles = list(np.atleast_1d(raw_battery.cycles))
            frame_features = [
                column for column in frame.columns if column != "label"
            ]
            if frame_features != feature_names:
                raise ValueError(
                    f"Batch {batch} {sheet_name}: feature columns/order differ."
                )
            pairs, unmatched, method, label_differences = align_profile_rows(
                cycles, frame
            )
            profile_name = f"batch-{batch}/{sheet_name}"
            batch_aligned_rows += len(pairs)
            batch_unmatched_rows += len(unmatched)
            batch_alignment_errors.extend(label_differences)
            profile_diagnostics.append(
                {
                    "profile": profile_name,
                    "raw_cycles": len(cycles),
                    "workbook_rows": len(frame),
                    "paired_rows": len(pairs),
                    "unmatched_workbook_rows": len(unmatched),
                    "alignment_method": method,
                    "mean_abs_label_difference": (
                        float(np.mean(label_differences))
                        if label_differences
                        else None
                    ),
                    "max_abs_label_difference": (
                        float(np.max(label_differences))
                        if label_differences
                        else None
                    ),
                }
            )

            for cycle_index, row_index in pairs:
                raw_cycle = cycles[cycle_index]
                (
                    main,
                    native,
                    point,
                    left_integral,
                    right_integral,
                    alternatives,
                ) = calculate_cycle_candidates(
                    raw_cycle, feature_names
                )
                row = frame.iloc[row_index]
                for feature_name in feature_names:
                    actual = float(row[feature_name])
                    candidate = float(main[feature_name])
                    if not math.isfinite(candidate):
                        continue
                    point_candidate = point.get(feature_name)
                    alt_candidate = alternatives.get(feature_name)
                    item = _observation(
                        expected=actual,
                        candidate=candidate,
                        native=native.get(feature_name),
                        point_boundary=point_candidate,
                        left_integral=left_integral.get(feature_name),
                        right_integral=right_integral.get(feature_name),
                        alternative=alt_candidate,
                        feature_name=feature_name,
                        battery=profile_name,
                        workbook_row=row_index + 1,
                        raw_cycle=cycle_index + 1,
                    )
                    batch_observations[batch][feature_name].append(item)
                    observations["overall"][feature_name].append(item)

        diagnostics[batch] = {
            "raw_profiles": len(raw_batteries),
            "workbook_profiles": len(sheet_items),
            "paired_rows": batch_aligned_rows,
            "unmatched_workbook_rows": batch_unmatched_rows,
            "mean_abs_label_difference": (
                float(np.mean(batch_alignment_errors))
                if batch_alignment_errors
                else None
            ),
            "max_abs_label_difference": (
                float(np.max(batch_alignment_errors))
                if batch_alignment_errors
                else None
            ),
            "profiles": profile_diagnostics,
        }

    if feature_names is None:
        raise ValueError("No batches were selected.")

    result_rows: list[dict[str, Any]] = []
    scopes: list[tuple[str, dict[str, list[Observation]], int | None]] = [
        ("overall", observations["overall"], None)
    ]
    scopes.extend(
        (f"batch-{batch}", batch_observations[batch], batch)
        for batch in batches
    )
    total_aligned = sum(item["paired_rows"] for item in diagnostics.values())
    total_unmatched = sum(
        item["unmatched_workbook_rows"] for item in diagnostics.values()
    )
    profile_diagnostics = [
        profile
        for data in diagnostics.values()
        for profile in data["profiles"]
    ]
    weighted_label_error = (
        sum(
            (profile["mean_abs_label_difference"] or 0.0)
            * profile["paired_rows"]
            for profile in profile_diagnostics
        )
        / total_aligned
        if total_aligned
        else None
    )

    for scope, scoped_observations, batch_number in scopes:
        for feature_name in feature_names:
            description = describe_feature(feature_name)
            items = scoped_observations.get(feature_name, [])
            metrics = _metrics(items)
            row_count = (
                total_aligned
                if batch_number is None
                else diagnostics[batch_number]["paired_rows"]
            )
            result_rows.append(
                {
                    "scope": scope,
                    "batch": batch_number,
                    "feature_id": feature_name,
                    "feature_name": feature_name,
                    "group": description.group,
                    "signal": description.signal,
                    "segment": description.segment,
                    "unit": description.unit,
                    "candidate_formula": description.candidate_formula,
                    "formula_status": FORMULA_STATUS,
                    "evidence": description.evidence,
                    "source_notes": description.source_notes,
                    "aligned_cycle_rows": row_count,
                    "unaligned_workbook_rows": (
                        total_unmatched
                        if batch_number is None
                        else diagnostics[batch_number]["unmatched_workbook_rows"]
                    ),
                    "alignment_method": (
                        "positional for equal-length batches; monotone capacity-label "
                        "matching for batch 6"
                        if batch_number is None
                        else (
                            "cycle-order positional (equal row counts)"
                            if diagnostics[batch_number]["unmatched_workbook_rows"] == 0
                            else "monotone exact-capacity match; unmatched rows excluded"
                        )
                    ),
                    "mean_abs_label_alignment_difference": (
                        weighted_label_error
                        if batch_number is None
                        else diagnostics[batch_number]["mean_abs_label_difference"]
                    ),
                    "valid_pairs": metrics["valid_pairs"],
                    "profiles": metrics["profiles"],
                    "max_error_profile": metrics["max_error_profile"],
                    "max_error_workbook_row": metrics["max_error_workbook_row"],
                    "max_error_raw_cycle": metrics["max_error_raw_cycle"],
                    "skipped_pairs": (
                        row_count - int(metrics["valid_pairs"] or 0)
                    ),
                    "mean_abs_reference": metrics["mean_abs_reference"],
                    "mae": metrics["mae"],
                    "rmse": metrics["rmse"],
                    "max_abs_error": metrics["max_abs_error"],
                    "relative_error_pct": metrics["relative_error_pct"],
                    "native_sampling_mae": metrics["native_mae"],
                    "point_boundary_mae": metrics["point_boundary_mae"],
                    "left_integral_mae": metrics["left_integral_mae"],
                    "right_integral_mae": metrics["right_integral_mae"],
                    "sample_std_mae": metrics["sample_std_mae"],
                    "adjusted_skew_mae": metrics["adjusted_skew_mae"],
                    "fisher_kurtosis_mae": metrics["fisher_kurtosis_mae"],
                }
            )
    return result_rows, feature_names, diagnostics


def write_results(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("Refusing to write an empty validation CSV.")
    fieldnames = list(rows[0].keys())
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_diagnostics(diagnostics: dict[int, dict[str, Any]]) -> None:
    for batch, data in diagnostics.items():
        print(
            f"batch-{batch}: profiles={data['workbook_profiles']} "
            f"paired_cycles={data['paired_rows']} "
            f"unmatched_workbook_rows={data['unmatched_workbook_rows']} "
            f"mean_abs_label_difference={data['mean_abs_label_difference']} "
            f"max_abs_label_difference={data['max_abs_label_difference']}"
        )
        for profile in data["profiles"]:
            if profile["unmatched_workbook_rows"]:
                print(
                    f"  {profile['profile']}: unmatched="
                    f"{profile['unmatched_workbook_rows']} "
                    f"alignment={profile['alignment_method']}"
                )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=int, required=True, choices=range(1, 7))
    parser.add_argument(
        "--battery-id",
        type=int,
        help="Optional 1-based workbook sheet/profile number; by default use the full batch.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional CSV output path. By default metrics are printed only.",
    )
    args = parser.parse_args()

    battery_ids = {args.battery_id} if args.battery_id is not None else None
    if args.battery_id is not None and args.battery_id < 1:
        parser.error("--battery-id must be >= 1.")
    rows, _, diagnostics = validate_batches([args.batch], battery_ids)
    print_diagnostics(diagnostics)
    if args.output is not None:
        write_results(rows, args.output)
        print(f"Wrote {len(rows)} rows to {args.output}")
        return
    overview = [
        row
        for row in rows
        if row["scope"] == f"batch-{args.batch}"
    ]
    for row in overview:
        print(
            f"{row['feature_name']}: MAE={row['mae']} RMSE={row['rmse']} "
            f"max={row['max_abs_error']} relative_error_pct={row['relative_error_pct']} "
            f"valid={row['valid_pairs']}"
        )


if __name__ == "__main__":
    main()
