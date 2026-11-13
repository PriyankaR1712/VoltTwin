from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .analysis_data import load_candidate_frame
from .feature_definitions import FEATURE_NAMES
from .loader import DEFAULT_DATA_ROOT

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
REPORT_ROOT = REPOSITORY_ROOT / "reports" / "member4"
DEFAULT_CSV = REPORT_ROOT / "aging_prediction_results.csv"
DEFAULT_SUMMARY = REPORT_ROOT / "aging_prediction_summary.json"
DEFAULT_REPORT = REPORT_ROOT / "leakage_safe_prediction.md"
N_SPLITS = 5
TARGET_COLUMN = "capacity_label"
GROUP_COLUMN = "cell_id"
EXCLUDED_FEATURE_SUFFIXES = ("_Q", "_energy")
EXCLUDED_NAMES = {
    "capacity",
    "capacity_label",
    "soh",
    "state_of_health",
    "cycle",
    "cycle_index",
    "cycle_id",
    "profile",
    "profile_id",
    "cell_id",
    "batch",
    "label",
    "target",
}


def select_predictor_columns(columns: Iterable[str]) -> list[str]:
    available = set(columns)
    selected = []
    for name in FEATURE_NAMES:
        normalized = name.casefold()
        if name not in available or normalized in EXCLUDED_NAMES:
            continue
        if normalized.endswith(tuple(suffix.casefold() for suffix in EXCLUDED_FEATURE_SUFFIXES)):
            continue
        if any(token in normalized for token in ("capacity", "soh", "cycle_id", "profile_id")):
            continue
        selected.append(name)
    if not selected:
        raise ValueError("No eligible candidate feature predictors are available.")
    return selected


def make_grouped_splits(
    groups: Iterable[str], n_splits: int = N_SPLITS
) -> list[tuple[np.ndarray, np.ndarray]]:
    group_values = np.asarray(list(groups), dtype=object)
    unique_groups, group_sizes = np.unique(group_values, return_counts=True)
    if n_splits < 2:
        raise ValueError("n_splits must be at least 2.")
    if len(unique_groups) < n_splits:
        raise ValueError(
            f"Need at least {n_splits} independent profiles; found {len(unique_groups)}."
        )
    fold_groups: list[list[str]] = [[] for _ in range(n_splits)]
    fold_sizes = np.zeros(n_splits, dtype=np.int64)
    order = sorted(
        range(len(unique_groups)),
        key=lambda index: (-int(group_sizes[index]), str(unique_groups[index])),
    )
    for index in order:
        fold = int(np.argmin(fold_sizes))
        fold_groups[fold].append(str(unique_groups[index]))
        fold_sizes[fold] += int(group_sizes[index])
    return [
        (
            np.flatnonzero(~np.isin(group_values, test_groups)),
            np.flatnonzero(np.isin(group_values, test_groups)),
        )
        for test_groups in fold_groups
    ]


def calculate_metrics(
    actual: Iterable[float], predicted: Iterable[float]
) -> dict[str, float | None]:
    y_true = np.asarray(list(actual), dtype=np.float64)
    y_pred = np.asarray(list(predicted), dtype=np.float64)
    if y_true.shape != y_pred.shape or y_true.ndim != 1 or not len(y_true):
        raise ValueError("Metric inputs must be non-empty 1D arrays of equal length.")
    if not np.isfinite(y_true).all() or not np.isfinite(y_pred).all():
        raise ValueError("Metric inputs must contain only finite values.")
    total_sum_squares = float(np.sum((y_true - np.mean(y_true)) ** 2))
    r2 = (
        float(1 - np.sum((y_true - y_pred) ** 2) / total_sum_squares)
        if len(y_true) > 1 and total_sum_squares > 0
        else None
    )
    return {
        "mae": float(np.mean(np.abs(y_true - y_pred))),
        "rmse": float(np.sqrt(np.mean((y_true - y_pred) ** 2))),
        "r2": r2,
    }


def _preprocess_fold(
    train: np.ndarray, test: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    train = np.asarray(train, dtype=np.float64).copy()
    test = np.asarray(test, dtype=np.float64).copy()
    medians = np.zeros(train.shape[1], dtype=np.float64)
    for column in range(train.shape[1]):
        finite = np.isfinite(train[:, column])
        medians[column] = float(np.median(train[finite, column])) if finite.any() else 0.0
        train[~finite, column] = medians[column]
        test[~np.isfinite(test[:, column]), column] = medians[column]
    means = train.mean(axis=0)
    scales = train.std(axis=0)
    scales[scales == 0] = 1.0
    return (train - means) / scales, (test - means) / scales


def _ridge_fold_predictions(
    train_features: np.ndarray,
    train_target: np.ndarray,
    test_features: np.ndarray,
    alpha: float = 1.0,
) -> np.ndarray:
    train_x, test_x = _preprocess_fold(train_features, test_features)
    train_design = np.column_stack((train_x, np.ones(len(train_x))))
    test_design = np.column_stack((test_x, np.ones(len(test_x))))
    penalty = np.eye(train_design.shape[1], dtype=np.float64) * alpha
    penalty[-1, -1] = 0.0
    coefficients = np.linalg.solve(
        train_design.T @ train_design + penalty,
        train_design.T @ train_target,
    )
    return test_design @ coefficients


def evaluate_capacity_prediction(
    frame: pd.DataFrame,
    n_splits: int = N_SPLITS,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    required = {TARGET_COLUMN, GROUP_COLUMN}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Prediction data is missing required columns: {sorted(missing)}")
    feature_columns = select_predictor_columns(frame.columns)
    target = pd.to_numeric(frame[TARGET_COLUMN], errors="coerce").to_numpy(dtype=np.float64)
    valid_target = np.isfinite(target)
    working = frame.loc[valid_target].reset_index(drop=True).copy()
    target = target[valid_target]
    groups = working[GROUP_COLUMN].astype(str).to_numpy()
    features = working.loc[:, feature_columns].apply(pd.to_numeric, errors="coerce")
    feature_values = features.to_numpy(dtype=np.float64)
    splits = make_grouped_splits(groups, n_splits=n_splits)
    records: list[dict[str, Any]] = []
    model_names = ("training_median_baseline", "ridge")
    out_of_fold = {
        name: np.full(len(working), np.nan, dtype=np.float64) for name in model_names
    }
    per_fold_cell_counts = []
    for fold_number, (train_indices, test_indices) in enumerate(splits, start=1):
        train_groups = set(groups[train_indices])
        test_groups = set(groups[test_indices])
        if train_groups & test_groups:
            raise RuntimeError("Grouped split placed a battery profile in train and test.")
        fold_cell_counts = {
            "fold": fold_number,
            "training_profiles": len(train_groups),
            "test_profiles": len(test_groups),
            "training_cycles": len(train_indices),
            "test_cycles": len(test_indices),
        }
        per_fold_cell_counts.append(fold_cell_counts)
        baseline_prediction = np.full(
            len(test_indices), float(np.median(target[train_indices])), dtype=np.float64
        )
        fold_predictions = {
            "training_median_baseline": baseline_prediction,
            "ridge": _ridge_fold_predictions(
                feature_values[train_indices],
                target[train_indices],
                feature_values[test_indices],
            ),
        }
        for model_name, predictions in fold_predictions.items():
            if not np.isfinite(predictions).all():
                raise RuntimeError(f"{model_name} produced non-finite predictions.")
            out_of_fold[model_name][test_indices] = predictions
            for cell_id in sorted(test_groups):
                cell_mask = groups[test_indices] == cell_id
                cell_indices = test_indices[cell_mask]
                metric_values = calculate_metrics(target[cell_indices], predictions[cell_mask])
                records.append(
                    {
                        "scope": "held_out_profile",
                        "fold": fold_number,
                        "held_out_cell": cell_id,
                        "model": model_name,
                        **fold_cell_counts,
                        **metric_values,
                    }
                )
            metrics = calculate_metrics(target[test_indices], predictions)
            records.append(
                {
                    "scope": "fold_aggregate",
                    "fold": fold_number,
                    "held_out_cell": "",
                    "model": model_name,
                    **fold_cell_counts,
                    **metrics,
                }
            )
    for model_name, predictions in out_of_fold.items():
        if not np.isfinite(predictions).all():
            raise RuntimeError(f"Out-of-fold predictions for {model_name} are incomplete.")
        records.append(
            {
                "scope": "all_out_of_fold",
                "fold": 0,
                "held_out_cell": "",
                "model": model_name,
                "training_profiles": None,
                "test_profiles": len(np.unique(groups)),
                "training_cycles": None,
                "test_cycles": len(working),
                **calculate_metrics(target, predictions),
            }
        )
    results = pd.DataFrame.from_records(records)
    summary = {
        "task": "Grouped cross-validated prediction of stored capacity_label; this is capacity prediction, not SOH prediction.",
        "data": {
            "profiles": int(np.unique(groups).size),
            "cycles_with_finite_target": int(len(working)),
            "cycles_excluded_for_missing_or_nonfinite_target": int((~valid_target).sum()),
            "target_column": TARGET_COLUMN,
            "target_units": "Unresolved from available local documentation.",
            "initial_capacity_verified": False,
            "soh_prediction_claimed": False,
        },
        "predictors": {
            "count": len(feature_columns),
            "features": feature_columns,
            "excluded_candidate_features": [
                name
                for name in FEATURE_NAMES
                if name in frame.columns and name not in feature_columns
            ],
            "leakage_rules": [
                "Capacity labels, SOH, cycle/profile/cell identifiers, batch, and metadata are not predictors.",
                "Candidate charge-integral features ending in _Q or _energy are excluded because they are capacity/energy-adjacent.",
                "Only registered candidate features are considered.",
                "The remaining charge statistics and phase features are assumed available after observing the corresponding charge trace; no earlier prediction horizon is claimed.",
            ],
            "candidate_formulas_source_verified": False,
        },
        "evaluation": {
            "method": "Five deterministic group-balanced folds by composite batch/profile cell_id; each profile is held out exactly once.",
            "models": ["training_median_baseline", "ridge"],
            "preprocessing": "For each fold, candidate-feature medians, means, and scales are calculated on training rows only. Ridge uses an unpenalized intercept and alpha=1.0, solved by the closed-form regularized least-squares equation.",
            "n_splits": n_splits,
            "folds": per_fold_cell_counts,
            "aggregate_metrics_are": "Pooled out-of-fold predictions; each profile is held out as a group exactly once.",
            "generalization_limit": "Only 55 independent profiles are available. Fold and per-profile results are descriptive and do not establish robust generalization across laboratories, protocols, or chemistries.",
        },
        "metrics": {
            name: calculate_metrics(target, predictions)
            for name, predictions in out_of_fold.items()
        },
        "scientific_limitations": [
            "The local capacity target unit and normalization lineage are not established.",
            "No per-cell initial-capacity reference was found, so no SOH target is calculated.",
            "Original benchmark formulas and authoritative workbook-row/cycle mapping remain unavailable.",
            "Candidate features remain source-unverified; good predictive metrics would not validate their original formulas.",
            "Charge integral features are omitted as leakage-adjacent variables; other charge-derived features can still encode protocol or capacity-related information.",
            "A grouped split prevents within-cell cycle leakage, but the available profile count and protocol/cohort confounding limit generalization claims.",
        ],
    }
    return results, summary


def _write_report(summary: dict[str, Any], results: pd.DataFrame) -> str:
    lines = [
        "# Leakage-Safe Grouped Capacity Prediction",
        "",
        "## Target and scientific scope",
        "",
        "**This experiment predicts the stored capacity label; it does not predict SOH.** "
        "The available local documentation does not establish the target unit, a "
        "per-cell initial capacity, or normalization lineage. The benchmark loader's "
        "fixed scale factor alone is not evidence of an SOH denominator.",
        "",
        "The experiment does not reproduce original SOHbenchmark feature values and "
        "does not validate the candidate feature equations.",
        "",
        "## Data and leakage controls",
        "",
        f"- Profiles: **{summary['data']['profiles']}**; finite-target cycles: "
        f"**{summary['data']['cycles_with_finite_target']}**.",
        f"- Predictors: **{summary['predictors']['count']}** candidate features.",
        "- Grouped by composite batch/profile ID using five deterministic, "
        "sample-balanced folds; all "
        "cycles from a profile are held together.",
        "- Capacity/target labels, SOH, cycle and profile identifiers, batch, "
        "metadata, and all `_Q`/`_energy` integral features are excluded.",
        "- Ridge uses a NumPy closed-form implementation; median imputation "
        "and standardization are fitted independently within each training fold.",
        "- Only a median baseline and Ridge are compared; no hyperparameter "
        "selection or feature selection uses held-out data.",
        "",
        "## Pooled out-of-fold metrics",
        "",
        "| Model | MAE | RMSE | R-squared |",
        "|---|---:|---:|---:|",
    ]
    for model, metrics in summary["metrics"].items():
        r2 = "undefined" if metrics["r2"] is None else f"{metrics['r2']:.6g}"
        lines.append(
            f"| {model} | {metrics['mae']:.6g} | {metrics['rmse']:.6g} | {r2} |"
        )
    lines.extend(
        [
            "",
            "Metrics are in the unresolved stored target scale. Per-fold and "
            "per-held-out-profile MAE/RMSE/R-squared are in the accompanying CSV. R-squared "
            "is undefined for a held-out profile when it has fewer than two "
            "samples or a constant target.",
            "",
            "## Per-held-out-profile results",
            "",
            "| Fold | Held-out profile | Model | Train profiles/cycles | Test profiles/cycles | MAE | RMSE | R-squared |",
            "|---:|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    per_cell = results.loc[results["scope"] == "held_out_profile"]
    for _, row in per_cell.iterrows():
        r2 = "undefined" if pd.isna(row["r2"]) else f"{row['r2']:.6g}"
        lines.append(
            f"| {int(row['fold'])} | {row['held_out_cell']} | {row['model']} | "
            f"{int(row['training_profiles'])}/{int(row['training_cycles'])} | "
            f"{int(row['test_profiles'])}/{int(row['test_cycles'])} | "
            f"{row['mae']:.6g} | {row['rmse']:.6g} | {r2} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation and limitations",
            "",
            "- The grouped split prevents cycles from the same profile appearing "
            "in both training and test sets, but 55 independent profiles are "
            "not enough to support broad claims of robust deployment "
            "generalization.",
            "- All remaining features come from measured charging traces and "
            "could contain protocol or indirect capacity information. Excluding "
            "direct capacity/energy integrals does not prove complete absence "
            "of physical proxy information.",
            "- These are exploratory capacity-prediction metrics, not SOH "
            "prediction results and not evidence for original benchmark formula "
            "correctness.",
            "- Batch and cell cohort differences may be confounded. The held-out "
            "profile split is not an external laboratory or protocol test.",
            "- No per-cell first-observed capacity normalization was applied "
            "because it is not established as a valid initial-capacity "
            "reference.",
            "",
            "## Reproducibility",
            "",
            "From the repository root:",
            "",
            "```powershell",
            ".\\.venv\\Scripts\\python.exe -m scripts.member4_xjtu.aging_prediction",
            "```",
            "",
            "The results CSV includes fold, held-out profile, and pooled "
            "out-of-fold rows for each model.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    frame, counts = load_candidate_frame(DEFAULT_DATA_ROOT)
    results, summary = evaluate_capacity_prediction(frame)
    summary["data"].update(counts)
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    results.to_csv(DEFAULT_CSV, index=False)
    DEFAULT_SUMMARY.write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    DEFAULT_REPORT.write_text(_write_report(summary, results), encoding="utf-8")
    print(
        f"Wrote {DEFAULT_CSV}, {DEFAULT_SUMMARY}, and {DEFAULT_REPORT}: "
        f"{summary['data']['profiles']} profiles, "
        f"{summary['data']['cycles_with_finite_target']} cycles."
    )


if __name__ == "__main__":
    main()
