from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class CycleTrace:
    batch: int
    profile: str
    cycle_index: int
    time_min: np.ndarray
    voltage_v: np.ndarray
    current_a: np.ndarray
    temperature_c: np.ndarray
    capacity_label: float

    def validate(self) -> None:
        arrays = (
            self.time_min,
            self.voltage_v,
            self.current_a,
            self.temperature_c,
        )
        lengths = {len(array) for array in arrays}
        if len(lengths) != 1 or not lengths or next(iter(lengths)) < 2:
            raise ValueError("Cycle channels must have matching lengths of at least two.")
        if any(not np.isfinite(array).all() for array in arrays):
            raise ValueError("Cycle channels contain non-finite values.")
        if np.any(np.diff(self.time_min) <= 0):
            raise ValueError("Cycle time must be strictly increasing.")
        if not np.isfinite(self.capacity_label):
            raise ValueError("Cycle capacity label must be finite.")


@dataclass(frozen=True)
class TimeInterval:
    start_min: float
    end_min: float

    def __post_init__(self) -> None:
        if not (
            np.isfinite(self.start_min)
            and np.isfinite(self.end_min)
            and self.end_min > self.start_min
        ):
            raise ValueError("Interval boundaries must be finite and increasing.")


@dataclass(frozen=True)
class PhaseSegment:
    name: str
    intervals: tuple[TimeInterval, ...]
    selection_method: str
    evidence: str
    note: str
    selected_mask: np.ndarray

    @property
    def is_disjoint(self) -> bool:
        return len(self.intervals) > 1
