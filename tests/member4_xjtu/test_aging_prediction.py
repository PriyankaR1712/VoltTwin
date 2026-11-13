from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.member4_xjtu.aging_prediction import (
    TARGET_COLUMN,
    _preprocess_fold,
    calculate_metrics,
    evaluate_capacity_prediction,
    make_grouped_splits,
    select_predictor_columns,
)
from scripts.member4_xjtu.feature_definitions import FEATURE_NAMES


def _small_frame() -> pd.DataFrame:
    rows = []
    for cell in range(6):
        for cycle in range(5):
            rows.append(
                {
                    "cell_id": f"batch-{cell // 2 + 1}:Sheet{cell + 1}",
                    "batch": cell // 2 + 1,
                    "profile": f"Sheet{cell + 1}",
                    "cycle_index": cycle + 1,
                    "capacity_label": 2.0 - 0.01 * cycle + 0.02 * cell,
                    "CC_V_mean": 3.5 + 0.01 * cycle + 0.005 * cell,
                    "CV_C_mean": 1.0 - 0.01 * cycle,
                    "CC_Q": 1.0,
                    "CC_energy": 3.0,
                    "Charge_Q": 1.1,
                    "Charge_energy": 4.0,
                }
            )
    return pd.DataFrame(rows)


def test_grouped_splits_never_share_profiles() -> None:
    groups = [f"cell-{cell}" for cell in range(6) for _ in range(4)]
    for train_indices, test_indices in make_grouped_splits(groups, n_splits=3):
        train_groups = {groups[index] for index in train_indices}
        test_groups = {groups[index] for index in test_indices}
        assert train_groups.isdisjoint(test_groups)


def test_grouped_splits_require_enough_independent_profiles() -> None:
    with pytest.raises(ValueError, match="at least 5 independent profiles"):
        make_grouped_splits(["cell-a"] * 4 + ["cell-b"] * 4, n_splits=5)


def test_predictor_selection_excludes_targets_metadata_and_integrals() -> None:
    columns = [
        *FEATURE_NAMES,
        "capacity_label",
        "soh",
        "cycle_index",
        "profile",
        "cell_id",
        "batch",
    ]
    predictors = select_predictor_columns(columns)
    assert predictors
    assert "CC_V_mean" in predictors
    assert "CV_C_mean" in predictors
    assert all(not name.endswith(("_Q", "_energy")) for name in predictors)
    assert not set(predictors) & {
        "capacity_label",
        "soh",
        "cycle_index",
        "profile",
        "cell_id",
        "batch",
    }


def test_metrics_calculate_mae_rmse_and_r2() -> None:
    metrics = calculate_metrics([1.0, 2.0, 3.0], [1.0, 2.0, 2.0])
    assert metrics["mae"] == pytest.approx(1 / 3)
    assert metrics["rmse"] == pytest.approx(np.sqrt(1 / 3))
    assert metrics["r2"] == pytest.approx(0.5)


def test_metrics_reject_invalid_values_and_report_undefined_r2() -> None:
    assert calculate_metrics([4.0], [3.0]) == {
        "mae": 1.0,
        "rmse": 1.0,
        "r2": None,
    }
    with pytest.raises(ValueError, match="only finite"):
        calculate_metrics([1.0, np.nan], [1.0, 2.0])
    with pytest.raises(ValueError, match="equal length"):
        calculate_metrics([1.0], [1.0, 2.0])


def test_fold_preprocessing_fits_imputation_and_scaling_from_training_only() -> None:
    train = np.array([[1.0, np.nan], [3.0, 2.0], [5.0, 4.0]])
    test = np.array([[1000.0, np.nan]])
    transformed_train, transformed_test = _preprocess_fold(train, test)
    assert transformed_train[:, 0] == pytest.approx([-1.22474487, 0.0, 1.22474487])
    assert transformed_train[:, 1] == pytest.approx([0.0, -1.22474487, 1.22474487])
    assert transformed_test[0, 0] > 100
    assert transformed_test[0, 1] == pytest.approx(0.0)


def test_evaluation_uses_capacity_label_as_target_not_soh() -> None:
    results, summary = evaluate_capacity_prediction(_small_frame())
    assert summary["data"]["target_column"] == TARGET_COLUMN == "capacity_label"
    assert summary["data"]["soh_prediction_claimed"] is False
    assert summary["data"]["initial_capacity_verified"] is False
    assert set(summary["metrics"]) == {
        "training_median_baseline",
        "ridge",
    }
    assert set(results["scope"]) == {
        "held_out_profile",
        "fold_aggregate",
        "all_out_of_fold",
    }
    assert len(results.loc[results["scope"] == "held_out_profile"]) == 12
    assert "CC_Q" not in summary["predictors"]["features"]
    assert "CC_energy" not in summary["predictors"]["features"]


def test_nonfinite_capacity_labels_are_excluded_and_counted() -> None:
    frame = _small_frame()
    frame.loc[0, "capacity_label"] = np.nan
    results, summary = evaluate_capacity_prediction(frame)
    assert summary["data"]["cycles_with_finite_target"] == len(frame) - 1
    assert summary["data"]["cycles_excluded_for_missing_or_nonfinite_target"] == 1
    assert results.loc[results["scope"] == "all_out_of_fold", "test_cycles"].eq(
        len(frame) - 1
    ).all()


def test_prediction_requires_capacity_target_and_profile_group() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        evaluate_capacity_prediction(pd.DataFrame({"CC_V_mean": [3.5]}))
