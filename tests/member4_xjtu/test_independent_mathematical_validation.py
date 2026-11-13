from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import pytest

from scripts.member4_xjtu.extractor import extract_cycle
from scripts.member4_xjtu.feature_definitions import FEATURE_NAMES, GROUPS
from scripts.member4_xjtu.models import CycleTrace, TimeInterval
from scripts.member4_xjtu.segments import segment_cycle


def cc_to_cv_cycle(time_scale: float = 1.0) -> CycleTrace:
    time = np.linspace(0.0, 12.7, 128) * time_scale
    voltage = np.concatenate((np.linspace(3.5, 4.2, 86), np.full(42, 4.2)))
    current = np.full(128, 4.0)
    current[90:] = np.linspace(3.8, 0.1, 38)
    return CycleTrace(
        batch=1,
        profile="synthetic",
        cycle_index=1,
        time_min=time,
        voltage_v=voltage,
        current_a=current,
        temperature_c=25.0 + 0.1 * (time / time_scale),
        capacity_label=1.8,
    )


def independent_expected_values(
    cycle: CycleTrace, segments: dict[str, object]
) -> dict[str, float]:
    expected: dict[str, float] = {}
    channels = {
        "V": cycle.voltage_v,
        "C": cycle.current_a,
        "T": cycle.temperature_c,
    }

    for group in GROUPS:
        intervals = segments[group].intervals
        native_times: list[np.ndarray] = []
        dense_times: list[np.ndarray] = []
        dense_signals = {suffix: [] for suffix in channels}
        native_signals = {suffix: [] for suffix in channels}
        for interval in intervals:
            interior = cycle.time_min[
                (cycle.time_min > interval.start_min)
                & (cycle.time_min < interval.end_min)
            ]
            native_time = np.unique(
                np.concatenate(([interval.start_min], interior, [interval.end_min]))
            )
            grid = np.linspace(interval.start_min, interval.end_min, 257)
            native_times.append(native_time)
            dense_times.append(grid)
            for suffix, source in channels.items():
                native_signals[suffix].append(
                    np.interp(native_time, cycle.time_min, source)
                )
                dense_signals[suffix].append(
                    np.interp(grid, cycle.time_min, source)
                )

        if not intervals or any(len(times) < 2 for times in native_times):
            continue

        def integrate(times: np.ndarray, values: np.ndarray) -> float:
            return float(
                sum(
                    (times[i + 1] - times[i])
                    * (values[i + 1] + values[i])
                    / 2
                    for i in range(len(times) - 1)
                )
            )

        energy = 0.0
        charge = 0.0
        for times, voltage, current in zip(
            native_times, native_signals["V"], native_signals["C"]
        ):
            energy += integrate(times, voltage * current) / 60
            charge += integrate(times, current) / 60
        expected[f"{group}_energy"] = energy
        expected[f"{group}_Q"] = charge

        elapsed = np.concatenate(
            [grid - grid[0] for grid in dense_times]
        )
        expected[f"{group}_t_mean"] = float(np.mean(elapsed))

        for suffix, parts in dense_signals.items():
            values = np.concatenate(parts)
            mean = float(np.mean(values))
            centered = values - mean
            variance = float(np.mean(centered**2))
            standard_deviation = math.sqrt(variance)
            expected[f"{group}_{suffix}_mean"] = mean
            expected[f"{group}_{suffix}_std"] = standard_deviation
            if variance <= np.finfo(float).eps:
                skewness = 0.0
                kurtosis = 0.0
            else:
                skewness = float(np.mean(centered**3) / variance**1.5)
                kurtosis = float(np.mean(centered**4) / variance**2)
            expected[f"{group}_{suffix}_skewness"] = skewness
            expected[f"{group}_{suffix}_kurtosis"] = kurtosis

        if group in ("CC", "CV"):
            expected[f"{group}_{'CCCT' if group == 'CC' else 'CVCT'}"] = sum(
                interval.end_min - interval.start_min for interval in intervals
            )
        if group in ("CC", "dV"):
            signal = dense_signals["V"]
            values = np.concatenate(signal)
            counts, _ = np.histogram(values, bins=16)
            probabilities = counts[counts > 0] / counts.sum()
            expected[f"{group}_entropy"] = float(
                -sum(float(p) * math.log(float(p)) for p in probabilities)
            )
        elif group in ("CV", "dI"):
            values = np.concatenate(dense_signals["C"])
            counts, _ = np.histogram(values, bins=16)
            probabilities = counts[counts > 0] / counts.sum()
            expected[f"{group}_entropy"] = float(
                -sum(float(p) * math.log(float(p)) for p in probabilities)
            )

        if group == "dV":
            interval = intervals[0]
            start = float(np.interp(interval.start_min, cycle.time_min, cycle.voltage_v))
            end = float(np.interp(interval.end_min, cycle.time_min, cycle.voltage_v))
            expected["dV_dV_devide_dt"] = (
                end - start
            ) / (interval.end_min - interval.start_min)
        if group == "dI":
            interval = intervals[0]
            start = float(np.interp(interval.start_min, cycle.time_min, cycle.current_a))
            end = float(np.interp(interval.end_min, cycle.time_min, cycle.current_a))
            expected["dI_dI_devide_dt"] = (
                end - start
            ) / (interval.end_min - interval.start_min)

    return {name: value for name, value in expected.items() if name in FEATURE_NAMES}


def test_all_67_candidate_outputs_match_independent_equations() -> None:
    cycle = cc_to_cv_cycle()
    actual, segments = extract_cycle(cycle)
    expected = independent_expected_values(cycle, segments)

    assert tuple(actual) == FEATURE_NAMES
    assert len(expected) == 67
    assert all(value is not None and np.isfinite(value) for value in actual.values())
    for name in FEATURE_NAMES:
        assert actual[name] == pytest.approx(expected[name], rel=1e-11, abs=1e-12), name


def test_constant_current_and_constant_voltage_cases() -> None:
    time = np.array([0.0, 1.0, 2.0, 3.0])
    constant_current = CycleTrace(
        batch=1,
        profile="synthetic-cc",
        cycle_index=1,
        time_min=time,
        voltage_v=np.array([3.5, 3.7, 3.9, 4.1]),
        current_a=np.full(4, 4.0),
        temperature_c=np.full(4, 25.0),
        capacity_label=1.8,
    )
    cc_values, cc_segments = extract_cycle(constant_current)
    assert cc_segments["CC"].intervals
    assert not cc_segments["CV"].intervals
    assert cc_values["CC_Q"] == pytest.approx(4 * 3 / 60)
    assert cc_values["CC_T_std"] == 0.0
    assert cc_values["CC_T_skewness"] == 0.0
    assert cc_values["CC_T_kurtosis"] == 0.0
    assert cc_values["CV_energy"] is None

    constant_voltage = CycleTrace(
        batch=1,
        profile="synthetic-cv",
        cycle_index=1,
        time_min=time,
        voltage_v=np.full(4, 4.2),
        current_a=np.array([4.0, 2.0, 0.8, 0.5]),
        temperature_c=np.full(4, 25.0),
        capacity_label=1.8,
    )
    cv_values, cv_segments = extract_cycle(constant_voltage)
    assert not cv_segments["CC"].intervals
    assert cv_segments["CV"].intervals
    assert cv_segments["dI"].intervals
    expected_charge = (4.0 + 2.0) / 2 + (2.0 + 0.8) / 2 + (0.8 + 0.5) / 2
    assert cv_values["CV_Q"] == pytest.approx(expected_charge / 60)
    assert cv_values["CV_energy"] == pytest.approx(4.2 * expected_charge / 60)
    assert cv_values["CV_T_std"] == 0.0
    assert cv_values["CC_energy"] is None


def test_constant_signals_have_zero_moments_and_zero_proxy_entropy() -> None:
    cycle = CycleTrace(
        batch=1,
        profile="constant",
        cycle_index=1,
        time_min=np.array([0.0, 1.0, 2.0]),
        voltage_v=np.full(3, 3.8),
        current_a=np.full(3, 4.0),
        temperature_c=np.full(3, 25.0),
        capacity_label=1.8,
    )
    values, _ = extract_cycle(cycle)
    for name in (
        "CC_V_std",
        "CC_T_std",
        "CC_V_skewness",
        "CC_T_skewness",
        "CC_V_kurtosis",
        "CC_T_kurtosis",
    ):
        assert values[name] == 0.0
    assert values["CC_entropy"] == 0.0


def test_capacity_label_does_not_change_feature_calculations() -> None:
    cycle = cc_to_cv_cycle()
    changed_label = replace(cycle, capacity_label=1.2)
    original_values, _ = extract_cycle(cycle)
    changed_values, _ = extract_cycle(changed_label)
    assert changed_values == original_values


def test_increasing_duration_scales_integrals_duration_and_rates() -> None:
    short = cc_to_cv_cycle(time_scale=1.0)
    long = cc_to_cv_cycle(time_scale=2.0)
    short_values, _ = extract_cycle(short)
    long_values, _ = extract_cycle(long)

    for name in FEATURE_NAMES:
        if name.endswith(("_energy", "_Q", "_t_mean", "_CCCT", "_CVCT")):
            if short_values[name] is not None:
                assert long_values[name] == pytest.approx(2 * short_values[name])
        elif name.endswith("_devide_dt"):
            if short_values[name] is not None:
                assert long_values[name] == pytest.approx(short_values[name] / 2)
        elif short_values[name] is not None:
            assert long_values[name] == pytest.approx(short_values[name])


def test_irregular_sampling_and_hour_conversion_have_expected_integrals() -> None:
    cycle = CycleTrace(
        batch=1,
        profile="irregular",
        cycle_index=1,
        time_min=np.array([0.0, 1.0, 3.0]),
        voltage_v=np.array([3.0, 3.5, 4.5]),
        current_a=np.array([2.0, 3.0, 5.0]),
        temperature_c=np.array([20.0, 21.0, 23.0]),
        capacity_label=1.8,
    )
    values, _ = extract_cycle(cycle)
    assert values["Charge_Q"] == pytest.approx(10.5 / 60)
    assert values["Charge_energy"] == pytest.approx(41.25 / 60)


def test_very_short_and_zero_duration_intervals_are_not_silently_extrapolated() -> None:
    short = CycleTrace(
        batch=1,
        profile="short",
        cycle_index=1,
        time_min=np.array([0.0, 1e-8]),
        voltage_v=np.array([3.7, 3.8]),
        current_a=np.array([4.0, 4.0]),
        temperature_c=np.array([25.0, 25.0]),
        capacity_label=1.8,
    )
    values, segments = extract_cycle(short)
    assert segments["CC"].intervals
    assert values["Charge_Q"] == pytest.approx(4 * 1e-8 / 60)
    assert values["Charge_energy"] == pytest.approx(4 * 3.75 * 1e-8 / 60)
    assert np.isfinite(values["Charge_V_mean"])

    with pytest.raises(ValueError, match="finite and increasing"):
        TimeInterval(1.0, 1.0)


def test_cc_interval_start_uses_interpolated_current_threshold_crossing() -> None:
    cycle = CycleTrace(
        batch=1,
        profile="cc-start-crossing",
        cycle_index=1,
        time_min=np.array([0.0, 1.0, 2.0]),
        voltage_v=np.array([3.7, 3.8, 3.9]),
        current_a=np.array([3.8, 4.0, 4.0]),
        temperature_c=np.full(3, 25.0),
        capacity_label=1.8,
    )
    cc = segment_cycle(cycle)["CC"]
    assert len(cc.intervals) == 1
    assert cc.intervals[0].start_min == pytest.approx(0.5)
    assert cc.intervals[0].end_min == pytest.approx(2.0)


def test_cc_interval_end_preserves_positive_duration_to_voltage_crossing() -> None:
    cycle = CycleTrace(
        batch=1,
        profile="cc-voltage-cutoff",
        cycle_index=1,
        time_min=np.array([0.0, 1.0, 2.0]),
        voltage_v=np.array([4.1, 4.2, 4.3]),
        current_a=np.full(3, 4.0),
        temperature_c=np.full(3, 25.0),
        capacity_label=1.8,
    )
    cc = segment_cycle(cycle)["CC"]
    assert len(cc.intervals) == 1
    assert cc.intervals[0].start_min == pytest.approx(0.0)
    assert cc.intervals[0].end_min == pytest.approx(0.99)


@pytest.mark.parametrize(
    ("field", "replacement", "message"),
    [
        (
            "voltage_v",
            np.concatenate((np.array([3.5, np.nan, 3.9]), np.full(125, 4.0))),
            "non-finite",
        ),
        (
            "current_a",
            np.concatenate((np.array([4.0, np.inf, 4.0]), np.full(125, 4.0))),
            "non-finite",
        ),
        ("temperature_c", np.full(127, 25.0), "matching lengths"),
        ("time_min", np.array([0.0]), "matching lengths"),
        (
            "time_min",
            np.concatenate((np.array([0.0, 1.0, 1.0]), np.arange(2.0, 127.0))),
            "strictly increasing",
        ),
    ],
)
def test_invalid_or_missing_signal_samples_are_rejected(
    field: str, replacement: np.ndarray, message: str
) -> None:
    cycle = cc_to_cv_cycle()
    cycle = replace(cycle, **{field: replacement})
    with pytest.raises(ValueError, match=message):
        cycle.validate()


def test_short_trace_keeps_charge_values_and_marks_unavailable_phase_features() -> None:
    cycle = CycleTrace(
        batch=1,
        profile="two-points",
        cycle_index=1,
        time_min=np.array([0.0, 1.0]),
        voltage_v=np.array([3.7, 3.8]),
        current_a=np.array([4.0, 4.0]),
        temperature_c=np.array([25.0, 25.0]),
        capacity_label=1.8,
    )
    values, segments = extract_cycle(cycle)
    assert set(values) == set(FEATURE_NAMES)
    assert segments["Charge"].intervals
    assert values["Charge_Q"] == pytest.approx(4 / 60)
    assert values["CV_Q"] is None
    assert values["dI_dI_devide_dt"] is None
