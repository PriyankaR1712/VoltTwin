
from pathlib import Path

import numpy as np
import pandas as pd


def analyze_soh_history(
    labels,
    max_capacity: float = 2.0,
) -> dict:
    """
    Analyze observed SOH labels in their recorded order.

    The trend is expressed per sample, not per physical cycle,
    because the input does not establish verified cycle numbers.

    This is descriptive historical analysis, not a future forecast.
    """
    values = np.asarray(labels, dtype=np.float64)

    if values.ndim != 1:
        raise ValueError("Labels must be a one-dimensional sequence.")

    if len(values) < 3:
        raise ValueError("At least 3 observations are required.")

    if not np.isfinite(values).all():
        raise ValueError("Labels contain NaN or infinite values.")

    if not np.isfinite(max_capacity) or max_capacity <= 0:
        raise ValueError("Maximum capacity must be positive and finite.")

    soh = values / max_capacity

    if np.any(soh < 0) or np.any(soh > 1):
        raise ValueError("Converted SOH values must be between 0 and 1.")

    sample_indices = np.arange(len(soh), dtype=np.float64)

    # Least-squares linear trend across the observed sequence.
    slope, intercept = np.polyfit(sample_indices, soh, 1)

    fitted = slope * sample_indices + intercept
    residuals = soh - fitted

    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((soh - np.mean(soh)) ** 2))

    r_squared = (
        1.0 - ss_res / ss_tot
        if ss_tot > 0
        else None
    )

    return {
        "observation_count": int(len(soh)),
        "first_observed_soh": round(float(soh[0]), 6),
        "last_observed_soh": round(float(soh[-1]), 6),
        "minimum_observed_soh": round(float(np.min(soh)), 6),
        "maximum_observed_soh": round(float(np.max(soh)), 6),
        "net_change_percentage_points": round(
            float((soh[-1] - soh[0]) * 100), 4
        ),
        "linear_trend_percentage_points_per_sample": round(
            float(slope * 100), 6
        ),
        "linear_trend_r_squared": (
            round(r_squared, 6) if r_squared is not None else None
        ),
        "trend_unit": "percentage_points_per_sample",
        "is_historical_analysis": True,
        "is_future_forecast": False,
    }


def analyze_xjtu_workbook(workbook_path: str | Path) -> dict:
    """
    Analyze the observed SOH labels in every sheet of an XJTU
    handcrafted-feature workbook.

    Does not modify the workbook or train a model.
    """
    path = Path(workbook_path)

    if not path.is_file():
        raise FileNotFoundError(f"Workbook not found: {path}")

    sheets = pd.read_excel(path, sheet_name=None)

    if not sheets:
        raise ValueError("Workbook contains no sheets.")

    results = {}

    for sheet_name, frame in sheets.items():
        if "label" not in frame.columns:
            raise ValueError(
                f"Sheet '{sheet_name}' does not contain a 'label' column."
            )

        results[sheet_name] = analyze_soh_history(frame["label"].to_numpy())

    return {
        "dataset_file": path.name,
        "sheet_count": len(results),
        "analysis_type": "observed_historical_trend",
        "sheets": results,
    }
