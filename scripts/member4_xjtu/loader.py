from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.io import loadmat

from .models import CycleTrace

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = (
    REPOSITORY_ROOT / "reference" / "SOHbenchmark" / "data" / "XJTU"
)


def _as_items(value: Any) -> list[Any]:
    return list(np.atleast_1d(value))


def _array_field(raw_cycle: Any, name: str) -> np.ndarray:
    value = getattr(raw_cycle, name, None)
    if value is None:
        raise ValueError(f"Raw MAT cycle is missing {name!r}.")
    return np.asarray(value, dtype=np.float64).reshape(-1)


def _capacity_label(raw_cycle: Any) -> float:
    value = getattr(raw_cycle, "capacity", None)
    if value is None:
        raise ValueError("Raw MAT cycle is missing scalar 'capacity'.")
    values = np.asarray(value, dtype=np.float64).reshape(-1)
    if not len(values) or not np.isfinite(values[0]):
        raise ValueError("Raw MAT cycle capacity is missing or non-finite.")
    return float(values[0])


def load_batch(
    batch: int, data_root: Path = DEFAULT_DATA_ROOT
) -> tuple[list[list[CycleTrace]], dict[str, pd.DataFrame]]:
    if batch not in range(1, 7):
        raise ValueError("XJTU batch must be between 1 and 6.")
    mat_path = data_root / "charge" / f"batch-{batch}.mat"
    workbook_path = (
        data_root / "handcraft_features" / f"batch-{batch}_features.xlsx"
    )
    if not mat_path.is_file():
        raise FileNotFoundError(f"Raw charge file not found: {mat_path}")
    if not workbook_path.is_file():
        raise FileNotFoundError(f"Feature workbook not found: {workbook_path}")

    mat_data = loadmat(mat_path, squeeze_me=True, struct_as_record=False)
    if "battery" not in mat_data:
        raise ValueError(f"{mat_path} has no 'battery' array.")
    batteries = _as_items(mat_data["battery"])
    sheets = pd.read_excel(workbook_path, sheet_name=None)
    if len(batteries) != len(sheets):
        raise ValueError(
            f"Batch {batch}: raw profile count {len(batteries)} does not "
            f"match workbook sheet count {len(sheets)}."
        )

    profiles: list[list[CycleTrace]] = []
    for profile_index, battery in enumerate(batteries, start=1):
        raw_cycles = _as_items(battery.cycles)
        profile = []
        for cycle_index, raw_cycle in enumerate(raw_cycles, start=1):
            trace = CycleTrace(
                batch=batch,
                profile=f"Sheet{profile_index}",
                cycle_index=cycle_index,
                time_min=_array_field(raw_cycle, "relative_time_min"),
                voltage_v=_array_field(raw_cycle, "voltage_V"),
                current_a=_array_field(raw_cycle, "current_A"),
                temperature_c=_array_field(raw_cycle, "temperature_C"),
                capacity_label=_capacity_label(raw_cycle),
            )
            trace.validate()
            profile.append(trace)
        profiles.append(profile)

    for sheet_name, frame in sheets.items():
        missing = {"label"} - set(frame.columns)
        if missing:
            raise ValueError(f"{sheet_name} is missing required workbook columns: {missing}")
    return profiles, sheets
