from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .models import CycleTrace, PhaseSegment, TimeInterval


@dataclass(frozen=True)
class SegmentationPolicy:
    cc_method: str = "adaptive_candidate"
    cc_voltage_cutoff_v: float = 4.199
    cc_current_fixed_a: float = 3.9
    adaptive_current_fraction: float = 0.975
    cv_voltage_threshold_v: float = 4.199
    dv_voltage_range_v: tuple[float, float] = (3.9, 4.0)
    di_current_range_a: tuple[float, float] = (1.0, 0.9)

    def __post_init__(self) -> None:
        if self.cc_method not in ("adaptive_candidate", "author_documented"):
            raise ValueError(
                "cc_method must be 'adaptive_candidate' or 'author_documented'."
            )
        if not 0 < self.adaptive_current_fraction <= 1:
            raise ValueError("adaptive_current_fraction must be in (0, 1].")
        if self.dv_voltage_range_v[1] <= self.dv_voltage_range_v[0]:
            raise ValueError("dV voltage range must be increasing.")
        if self.di_current_range_a[1] >= self.di_current_range_a[0]:
            raise ValueError("dI current range must be decreasing.")


def _crossing_time(
    time: np.ndarray,
    signal: np.ndarray,
    threshold: float,
    start: float,
    end: float,
    direction: str,
) -> float | None:
    indices = np.flatnonzero((time >= start) & (time <= end))
    if not len(indices):
        return None
    first = int(indices[0])
    if direction == "rising" and signal[first] >= threshold:
        return max(start, float(time[first]))
    if direction == "falling" and signal[first] <= threshold:
        return max(start, float(time[first]))
    for right in range(first + 1, len(time)):
        if time[right] > end:
            break
        left = right - 1
        crossed = (
            signal[left] < threshold <= signal[right]
            if direction == "rising"
            else signal[left] > threshold >= signal[right]
        )
        if crossed:
            y0, y1 = float(signal[left]), float(signal[right])
            if y0 == y1:
                return float(time[right])
            fraction = (threshold - y0) / (y1 - y0)
            return float(time[left] + fraction * (time[right] - time[left]))
    return None


def _mask_runs(mask: np.ndarray) -> list[tuple[int, int]]:
    indices = np.flatnonzero(mask)
    if not len(indices):
        return []
    breaks = np.flatnonzero(np.diff(indices) > 1) + 1
    return [
        (int(run[0]), int(run[-1]))
        for run in np.split(indices, breaks)
        if len(run)
    ]


def _mask_intervals(
    cycle: CycleTrace,
    mask: np.ndarray,
    *,
    current_threshold: float | None = None,
    voltage_cutoff: float | None = None,
) -> tuple[TimeInterval, ...]:
    intervals: list[TimeInterval] = []
    time = cycle.time_min
    for first, last in _mask_runs(mask):
        start = float(time[first])
        end = float(time[last])
        if first > 0:
            left = first - 1
            start_crossings: list[float] = []
            if (
                current_threshold is not None
                and cycle.current_a[left] < current_threshold <= cycle.current_a[first]
            ):
                crossing = _crossing_time(
                    time, cycle.current_a, current_threshold, float(time[left]), start, "rising"
                )
                if crossing is not None:
                    start_crossings.append(crossing)
            if (
                voltage_cutoff is not None
                and cycle.voltage_v[left] < voltage_cutoff <= cycle.voltage_v[first]
            ):
                crossing = _crossing_time(
                    time, cycle.voltage_v, voltage_cutoff, float(time[left]), start, "rising"
                )
                if crossing is not None:
                    start_crossings.append(crossing)
            if start_crossings:
                start = max(start_crossings)
        if last < len(time) - 1:
            right = last + 1
            end_crossings: list[float] = []
            if (
                current_threshold is not None
                and cycle.current_a[last] >= current_threshold > cycle.current_a[right]
            ):
                crossing = _crossing_time(
                    time, cycle.current_a, current_threshold, end, float(time[right]), "falling"
                )
                if crossing is not None:
                    end_crossings.append(crossing)
            if (
                voltage_cutoff is not None
                and cycle.voltage_v[last] <= voltage_cutoff < cycle.voltage_v[right]
            ):
                crossing = _crossing_time(
                    time, cycle.voltage_v, voltage_cutoff, end, float(time[right]), "rising"
                )
                if crossing is not None:
                    end_crossings.append(crossing)
            if end_crossings:
                end = min(end_crossings)
        if end > start:
            intervals.append(TimeInterval(start, end))
    return tuple(intervals)


def _phase(
    name: str,
    cycle: CycleTrace,
    intervals: tuple[TimeInterval, ...],
    method: str,
    evidence: str,
    note: str,
) -> PhaseSegment:
    mask = np.zeros(len(cycle.time_min), dtype=bool)
    for interval in intervals:
        mask |= (cycle.time_min >= interval.start_min) & (
            cycle.time_min <= interval.end_min
        )
    return PhaseSegment(name, intervals, method, evidence, note, mask)


def _threshold_window(
    cycle: CycleTrace,
    base: PhaseSegment,
    signal: np.ndarray,
    start_threshold: float,
    end_threshold: float,
    direction: str,
    method: str,
    evidence: str,
) -> PhaseSegment:
    if len(base.intervals) != 1:
        return _phase(
            base.name + "_window",
            cycle,
            (),
            method,
            evidence,
            "Window not formed: the parent phase is missing or disjoint.",
        )
    parent = base.intervals[0]
    start = _crossing_time(
        cycle.time_min, signal, start_threshold, parent.start_min, parent.end_min, direction
    )
    if start is None:
        return _phase(
            base.name + "_window",
            cycle,
            (),
            method,
            evidence,
            f"Window not formed: start threshold {start_threshold:g} was not crossed.",
        )
    end = _crossing_time(
        cycle.time_min, signal, end_threshold, start, parent.end_min, direction
    )
    if end is None or end <= start:
        return _phase(
            base.name + "_window",
            cycle,
            (),
            method,
            evidence,
            f"Window not formed: end threshold {end_threshold:g} was not crossed.",
        )
    return _phase(
        base.name + "_window",
        cycle,
        (TimeInterval(start, end),),
        method,
        evidence,
        "Candidate threshold window; original workbook boundaries were not located.",
    )


def segment_cycle(
    cycle: CycleTrace,
    policy: SegmentationPolicy = SegmentationPolicy(),
) -> dict[str, PhaseSegment]:
    cycle.validate()
    if policy.cc_method == "author_documented":
        current_threshold = policy.cc_current_fixed_a
        cc_method = "author_documented_helper_selector"
        cc_evidence = (
            "XJTUBatteryClass.get_CC_value documents current >= 3.9 A intersected "
            "with voltage <= 4.199 V; this is not workbook formula evidence."
        )
    else:
        current_threshold = policy.adaptive_current_fraction * float(
            np.percentile(cycle.current_a, 95)
        )
        cc_method = "adaptive_candidate"
        cc_evidence = (
            "Adaptive current plateau candidate; not an author-documented workbook rule."
        )
    cc_mask = (
        (cycle.current_a >= current_threshold)
        & (cycle.voltage_v <= policy.cc_voltage_cutoff_v)
    )
    cc_intervals = _mask_intervals(
        cycle,
        cc_mask,
        current_threshold=current_threshold,
        voltage_cutoff=policy.cc_voltage_cutoff_v,
    )
    cc = _phase(
        "CC",
        cycle,
        cc_intervals,
        cc_method,
        cc_evidence,
        "Multiple selected runs remain separate; no gap is silently bridged.",
    )

    cv_start = _crossing_time(
        cycle.time_min,
        cycle.voltage_v,
        policy.cv_voltage_threshold_v,
        float(cycle.time_min[0]),
        float(cycle.time_min[-1]),
        "rising",
    )
    cv_intervals = (
        (TimeInterval(cv_start, float(cycle.time_min[-1])),)
        if cv_start is not None and cycle.time_min[-1] > cv_start
        else ()
    )
    cv = _phase(
        "CV",
        cycle,
        cv_intervals,
        "voltage_threshold_candidate",
        (
            "XJTUBatteryClass.get_CV_value documents voltage >= 4.199 V; "
            "the selected cutoff-to-record-end interval is a candidate interpretation."
        ),
        "Exact original workbook cutoff and endpoint convention were not located.",
    )

    dv = _threshold_window(
        cycle,
        cc,
        cycle.voltage_v,
        policy.dv_voltage_range_v[0],
        policy.dv_voltage_range_v[1],
        "rising",
        "candidate_voltage_window",
        "The 3.9-4.0 V window is inferred, not source-defined.",
    )
    di = _threshold_window(
        cycle,
        cv,
        cycle.current_a,
        policy.di_current_range_a[0],
        policy.di_current_range_a[1],
        "falling",
        "candidate_current_window",
        "The 1.0-0.9 A window is inferred, not source-defined.",
    )
    charge = _phase(
        "Charge",
        cycle,
        (TimeInterval(float(cycle.time_min[0]), float(cycle.time_min[-1])),),
        "complete_stored_trace",
        "The MAT file is the benchmark's prepared charge trace; original workbook boundaries are unknown.",
        "Uses the full stored trace and does not infer a different physical charge endpoint.",
    )
    return {"CC": cc, "dV": dv, "CV": cv, "dI": di, "Charge": charge}
