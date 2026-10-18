
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent

DATA_FILE = (
    ROOT
    / "reference"
    / "SOHbenchmark"
    / "data"
    / "XJTU"
    / "handcraft_features"
    / "batch-1_features.xlsx"
)

MAX_CAPACITY = 2.0
TRAIN_FRACTIONS = [0.50, 0.60, 0.70]
RECENT_WINDOWS = [25, 50, 100]


def fit_linear_trend(
    values: np.ndarray,
    indices: np.ndarray,
) -> tuple[float, float]:
    """Fit SOH = intercept + slope * observation index."""
    slope, intercept = np.polyfit(indices, values, 1)
    return float(slope), float(intercept)


def calculate_metrics(
    actual: np.ndarray,
    predicted: np.ndarray,
) -> dict:
    errors = predicted - actual

    return {
        "mae_percentage_points": float(
            np.mean(np.abs(errors)) * 100
        ),
        "rmse_percentage_points": float(
            np.sqrt(np.mean(errors**2)) * 100
        ),
    }


def evaluate_split(
    soh: np.ndarray,
    battery_name: str,
    train_fraction: float,
) -> list[dict]:
    split = int(len(soh) * train_fraction)

    train = soh[:split]
    actual = soh[split:]

    train_indices = np.arange(split, dtype=float)
    test_indices = np.arange(split, len(soh), dtype=float)

    rows = []

    # Baseline: hold the last observed SOH constant.
    baseline_prediction = np.full(len(actual), train[-1])

    rows.append({
        "battery": battery_name,
        "train_fraction": train_fraction,
        "method": "Last-SOH baseline",
        "window": None,
        **calculate_metrics(actual, baseline_prediction),
    })

    # Full-history linear trend.
    slope, intercept = fit_linear_trend(train, train_indices)
    prediction = np.clip(
        intercept + slope * test_indices, 0.0, 1.0
    )

    rows.append({
        "battery": battery_name,
        "train_fraction": train_fraction,
        "method": "Full-history linear trend",
        "window": None,
        **calculate_metrics(actual, prediction),
    })

    # Recent-window trends.
    for window in RECENT_WINDOWS:
        if window > len(train):
            continue

        recent_values = train[-window:]
        recent_indices = train_indices[-window:]

        recent_slope, recent_intercept = fit_linear_trend(
            recent_values,
            recent_indices,
        )

        prediction = np.clip(
            recent_intercept + recent_slope * test_indices,
            0.0,
            1.0,
        )

        rows.append({
            "battery": battery_name,
            "train_fraction": train_fraction,
            "method": "Recent-window linear trend",
            "window": window,
            **calculate_metrics(actual, prediction),
        })

    return rows


def main() -> None:
    if not DATA_FILE.is_file():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    sheets = pd.read_excel(DATA_FILE, sheet_name=None)
    all_results = []

    for battery_name, frame in sheets.items():
        if "label" not in frame.columns:
            raise ValueError(
                f"{battery_name} has no 'label' column."
            )

        soh = (
            frame["label"].to_numpy(dtype=np.float64)
            / MAX_CAPACITY
        )

        if not np.isfinite(soh).all():
            raise ValueError(
                f"{battery_name} contains invalid labels."
            )

        if np.any((soh < 0) | (soh > 1)):
            raise ValueError(
                f"{battery_name} has SOH outside [0, 1]."
            )

        for fraction in TRAIN_FRACTIONS:
            all_results.extend(
                evaluate_split(soh, battery_name, fraction)
            )

    results = pd.DataFrame(all_results)

    print("CHRONOLOGICAL VALIDATION")
    print("Training fractions:", TRAIN_FRACTIONS)
    print("Recent windows:", RECENT_WINDOWS)
    print("Errors are in SOH percentage points; lower is better.\n")

    summary = (
        results.groupby(["method", "window"], dropna=False)
        .agg(
            mean_mae=("mae_percentage_points", "mean"),
            mean_rmse=("rmse_percentage_points", "mean"),
            battery_split_cases=("battery", "count"),
        )
        .reset_index()
        .sort_values("mean_mae")
    )

    print(summary.round(4).to_string(index=False))

    output_path = ROOT / "results" / "degradation_validation.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_path, index=False)

    print(f"\nDetailed results saved to: {output_path}")


if __name__ == "__main__":
    main()
