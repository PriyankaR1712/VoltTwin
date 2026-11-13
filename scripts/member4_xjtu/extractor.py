from __future__ import annotations

import math

import numpy as np

from .feature_definitions import CHANNELS, FEATURE_NAMES, GROUPS
from .models import CycleTrace, PhaseSegment, TimeInterval
from .segments import SegmentationPolicy, segment_cycle

STAT_GRID_SIZE = 257


def _interval_arrays(
    cycle: CycleTrace, interval: TimeInterval, dense: bool
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    if dense:
        sample_time = np.linspace(interval.start_min, interval.end_min, STAT_GRID_SIZE)
    else:
        interior = cycle.time_min[
            (cycle.time_min > interval.start_min) & (cycle.time_min < interval.end_min)
        ]
        sample_time = np.unique(
            np.concatenate(
                ([interval.start_min], interior, [interval.end_min])
            )
        )
    signals = {
        "voltage": np.interp(sample_time, cycle.time_min, cycle.voltage_v),
        "current": np.interp(sample_time, cycle.time_min, cycle.current_a),
        "temperature": np.interp(sample_time, cycle.time_min, cycle.temperature_c),
    }
    return sample_time, signals


def _moments(values: np.ndarray) -> dict[str, float | int]:
    mean = float(np.mean(values))
    centered = values - mean
    second = float(np.mean(centered**2))
    if second <= np.finfo(float).eps:
        return {
            "sample_count": int(len(values)),
            "mean": mean,
            "variance": 0.0,
            "standard_deviation": 0.0,
            "third_central_moment": 0.0,
            "fourth_central_moment": 0.0,
            "skewness": 0.0,
            "pearson_kurtosis": 0.0,
        }
    third = float(np.mean(centered**3))
    fourth = float(np.mean(centered**4))
    return {
        "sample_count": int(len(values)),
        "mean": mean,
        "variance": second,
        "standard_deviation": math.sqrt(second),
        "third_central_moment": third,
        "fourth_central_moment": fourth,
        "skewness": float(third / second**1.5),
        "pearson_kurtosis": float(fourth / second**2),
    }


def _entropy_proxy(values: np.ndarray) -> tuple[float, dict[str, object]]:
    counts, bin_edges = np.histogram(values, bins=16)
    probabilities = counts[counts > 0].astype(np.float64)
    probabilities /= probabilities.sum()
    contributions = -probabilities * np.log(probabilities)
    entropy = float(np.sum(contributions))
    nonzero_bin_indices = np.flatnonzero(counts)
    return entropy, {
        "sample_count": int(len(values)),
        "bin_count": 16,
        "bin_edges": bin_edges.tolist(),
        "nonzero_bin_indices": nonzero_bin_indices.tolist(),
        "nonzero_bin_counts": counts[counts > 0].tolist(),
        "nonzero_bin_probabilities": probabilities.tolist(),
        "entropy_contributions": contributions.tolist(),
        "entropy_nats": entropy,
    }


def _trapezoid_details(
    times: np.ndarray,
    values: np.ndarray,
) -> dict[str, object]:
    delta_time = np.diff(times)
    panels = delta_time * (values[:-1] + values[1:]) / 2
    return {
        "sample_count": int(len(times)),
        "panel_count": int(len(panels)),
        "start_time_min": float(times[0]),
        "end_time_min": float(times[-1]),
        "duration_min": float(times[-1] - times[0]),
        "first_value": float(values[0]),
        "last_value": float(values[-1]),
        "minimum_delta_time_min": float(np.min(delta_time)),
        "maximum_delta_time_min": float(np.max(delta_time)),
        "nonuniform_delta_time_count": int(
            np.count_nonzero(
                ~np.isclose(delta_time, np.median(delta_time), rtol=1e-6, atol=1e-9)
            )
        ),
        "trapezoid_sum_before_hour_conversion": float(np.sum(panels)),
        "hour_conversion_divisor": 60.0,
        "trapezoid_panels": [
            {
                "panel_index": int(index + 1),
                "start_time_min": float(times[index]),
                "end_time_min": float(times[index + 1]),
                "delta_time_min": float(delta_time[index]),
                "start_value": float(values[index]),
                "end_value": float(values[index + 1]),
                "panel_integral": float(panels[index]),
            }
            for index in range(len(panels))
        ],
    }


def _features_for_segment(
    cycle: CycleTrace,
    group: str,
    segment: PhaseSegment,
    calculation_details: dict[str, dict[str, object]] | None = None,
) -> dict[str, float | None]:
    if not segment.intervals:
        return {}
    native_parts = [
        _interval_arrays(cycle, interval, dense=False)
        for interval in segment.intervals
    ]
    dense_parts = [
        _interval_arrays(cycle, interval, dense=True)
        for interval in segment.intervals
    ]
    if any(len(times) < 2 for times, _ in native_parts):
        return {}

    energy_parts = [
        _trapezoid_details(
            times, signals["voltage"] * signals["current"]
        )
        for times, signals in native_parts
    ]
    charge_parts = [
        _trapezoid_details(times, signals["current"])
        for times, signals in native_parts
    ]
    energy = sum(
        float(part["trapezoid_sum_before_hour_conversion"])
        / float(part["hour_conversion_divisor"])
        for part in energy_parts
    )
    charge = sum(
        float(part["trapezoid_sum_before_hour_conversion"])
        / float(part["hour_conversion_divisor"])
        for part in charge_parts
    )
    elapsed = np.concatenate(
        [times - times[0] for times, _ in dense_parts]
    )
    all_dense = {
        name: np.concatenate([signals[name] for _, signals in dense_parts])
        for name in ("voltage", "current", "temperature")
    }
    values: dict[str, float | None] = {
        f"{group}_energy": energy,
        f"{group}_Q": charge,
        f"{group}_t_mean": float(np.mean(elapsed)),
    }
    moments_by_channel: dict[str, dict[str, float | int]] = {}
    for suffix, channel in CHANNELS[group]:
        moments = _moments(all_dense[channel])
        moments_by_channel[suffix] = moments
        values[f"{group}_{suffix}_mean"] = float(moments["mean"])
        values[f"{group}_{suffix}_std"] = float(moments["standard_deviation"])
        values[f"{group}_{suffix}_skewness"] = float(moments["skewness"])
        values[f"{group}_{suffix}_kurtosis"] = float(moments["pearson_kurtosis"])

    duration = sum(interval.end_min - interval.start_min for interval in segment.intervals)
    special_details: dict[str, dict[str, object]] = {}
    if group == "CC":
        values["CC_CCCT"] = duration if not segment.is_disjoint else None
        entropy, entropy_details = _entropy_proxy(all_dense["voltage"])
        values["CC_entropy"] = entropy
        special_details["CC_entropy"] = entropy_details
        special_details["CC_CCCT"] = {
            "interval_durations_min": [
                float(interval.end_min - interval.start_min)
                for interval in segment.intervals
            ],
            "combined_duration_min": float(duration),
            "is_disjoint": segment.is_disjoint,
        }
    elif group == "dV":
        values["dV_dV_devide_dt"] = (
            float(
                (
                    np.interp(segment.intervals[0].end_min, cycle.time_min, cycle.voltage_v)
                    - np.interp(segment.intervals[0].start_min, cycle.time_min, cycle.voltage_v)
                )
                / duration
            )
            if not segment.is_disjoint
            else None
        )
        entropy, entropy_details = _entropy_proxy(all_dense["voltage"])
        values["dV_entropy"] = entropy
        special_details["dV_entropy"] = entropy_details
        interval = segment.intervals[0]
        start_value = float(np.interp(interval.start_min, cycle.time_min, cycle.voltage_v))
        end_value = float(np.interp(interval.end_min, cycle.time_min, cycle.voltage_v))
        special_details["dV_dV_devide_dt"] = {
            "start_time_min": float(interval.start_min),
            "end_time_min": float(interval.end_min),
            "start_voltage_v": start_value,
            "end_voltage_v": end_value,
            "delta_voltage_v": end_value - start_value,
            "duration_min": float(duration),
            "candidate_rate_v_per_min": values["dV_dV_devide_dt"],
        }
    elif group == "CV":
        values["CV_CVCT"] = duration if not segment.is_disjoint else None
        entropy, entropy_details = _entropy_proxy(all_dense["current"])
        values["CV_entropy"] = entropy
        special_details["CV_entropy"] = entropy_details
        special_details["CV_CVCT"] = {
            "interval_durations_min": [
                float(interval.end_min - interval.start_min)
                for interval in segment.intervals
            ],
            "combined_duration_min": float(duration),
            "is_disjoint": segment.is_disjoint,
        }
    elif group == "dI":
        values["dI_dI_devide_dt"] = (
            float(
                (
                    np.interp(segment.intervals[0].end_min, cycle.time_min, cycle.current_a)
                    - np.interp(segment.intervals[0].start_min, cycle.time_min, cycle.current_a)
                )
                / duration
            )
            if not segment.is_disjoint
            else None
        )
        entropy, entropy_details = _entropy_proxy(all_dense["current"])
        values["dI_entropy"] = entropy
        special_details["dI_entropy"] = entropy_details
        interval = segment.intervals[0]
        start_value = float(np.interp(interval.start_min, cycle.time_min, cycle.current_a))
        end_value = float(np.interp(interval.end_min, cycle.time_min, cycle.current_a))
        special_details["dI_dI_devide_dt"] = {
            "start_time_min": float(interval.start_min),
            "end_time_min": float(interval.end_min),
            "start_current_a": start_value,
            "end_current_a": end_value,
            "delta_current_a": end_value - start_value,
            "duration_min": float(duration),
            "candidate_rate_a_per_min": values["dI_dI_devide_dt"],
        }

    if calculation_details is not None:
        interval_details = [
            {
                "start_time_min": float(interval.start_min),
                "end_time_min": float(interval.end_min),
                "duration_min": float(interval.end_min - interval.start_min),
                "raw_sample_count": int(
                    np.count_nonzero(
                        (cycle.time_min >= interval.start_min)
                        & (cycle.time_min <= interval.end_min)
                    )
                ),
            }
            for interval in segment.intervals
        ]
        delta_time = np.diff(cycle.time_min)
        grid_details = {
            "point_count_per_interval": STAT_GRID_SIZE,
            "intervals": [
                {
                    "start_time_min": float(times[0]),
                    "end_time_min": float(times[-1]),
                    "elapsed_time_first_min": float(times[0] - times[0]),
                    "elapsed_time_last_min": float(times[-1] - times[0]),
                    "mean_elapsed_time_min": float(np.mean(times - times[0])),
                }
                for times, _ in dense_parts
            ],
            "combined_mean_elapsed_time_min": float(np.mean(elapsed)),
            "combined_sample_count": int(len(elapsed)),
        }
        energy_total_before_conversion = sum(
            float(part["trapezoid_sum_before_hour_conversion"])
            for part in energy_parts
        )
        charge_total_before_conversion = sum(
            float(part["trapezoid_sum_before_hour_conversion"])
            for part in charge_parts
        )
        group_context: dict[str, object] = {
            "group": group,
            "intervals": interval_details,
            "segment_sample_count": int(np.count_nonzero(segment.selected_mask)),
            "statistical_grid": grid_details,
            "statistical_moments_by_channel": moments_by_channel,
            "input_sampling": {
                "raw_sample_count": int(len(cycle.time_min)),
                "minimum_delta_time_min": float(np.min(delta_time)),
                "maximum_delta_time_min": float(np.max(delta_time)),
                "median_delta_time_min": float(np.median(delta_time)),
                "nonuniform_delta_time_count": int(
                    np.count_nonzero(
                        ~np.isclose(delta_time, np.median(delta_time), rtol=1e-6, atol=1e-9)
                    )
                ),
            },
        }
        for name, result, parts, total_before_conversion in (
            (
                f"{group}_energy",
                energy,
                energy_parts,
                energy_total_before_conversion,
            ),
            (
                f"{group}_Q",
                charge,
                charge_parts,
                charge_total_before_conversion,
            ),
        ):
            calculation_details[name] = {
                **group_context,
                "operation": "trapezoidal_time_integration",
                "integrand": "voltage × current" if name.endswith("_energy") else "current",
                "integration_by_interval": parts,
                "trapezoid_sum_before_hour_conversion": total_before_conversion,
                "hour_conversion_divisor": 60.0,
                "candidate_result": result,
            }
        calculation_details[f"{group}_t_mean"] = {
            **group_context,
            "operation": "arithmetic_mean_of_elapsed_time",
            "grid": grid_details,
            "candidate_result": values[f"{group}_t_mean"],
        }
        for suffix, moments in moments_by_channel.items():
            for statistic, statistic_key in (
                ("mean", "mean"),
                ("std", "standard_deviation"),
                ("skewness", "skewness"),
                ("kurtosis", "pearson_kurtosis"),
            ):
                name = f"{group}_{suffix}_{statistic}"
                calculation_details[name] = {
                    **group_context,
                    "operation": statistic,
                    "channel": suffix,
                    "moments": moments,
                    "candidate_result": float(moments[statistic_key]),
                }
        for name, details in special_details.items():
            if name.endswith("_entropy"):
                operation = "entropy"
            elif name.endswith(("_CCCT", "_CVCT")):
                operation = "sum_of_interval_durations"
            else:
                operation = "candidate_endpoint_rate"
            calculation_details[name] = {
                **group_context,
                "operation": operation,
                **details,
                "candidate_result": values[name],
            }
    return values


def extract_cycle_with_details(
    cycle: CycleTrace,
    policy: SegmentationPolicy = SegmentationPolicy(),
) -> tuple[
    dict[str, float | None],
    dict[str, PhaseSegment],
    dict[str, dict[str, object]],
]:
    cycle.validate()
    segments = segment_cycle(cycle, policy)
    values: dict[str, float | None] = {}
    calculation_details: dict[str, dict[str, object]] = {}
    for group in GROUPS:
        values.update(
            _features_for_segment(
                cycle, group, segments[group], calculation_details
            )
        )
    return (
        {name: values.get(name) for name in FEATURE_NAMES},
        segments,
        calculation_details,
    )


def extract_cycle(
    cycle: CycleTrace,
    policy: SegmentationPolicy = SegmentationPolicy(),
) -> tuple[dict[str, float | None], dict[str, PhaseSegment]]:
    values, segments, _ = extract_cycle_with_details(cycle, policy)
    return values, segments
