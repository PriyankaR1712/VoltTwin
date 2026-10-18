
import numpy as np
import pytest

from digital_twin.historical_degradation import (
    analyze_soh_history,
    analyze_xjtu_workbook,
)


def test_analyze_soh_history_calculates_observed_trend():
    labels = np.array([2.0, 1.9, 1.8, 1.7])

    result = analyze_soh_history(labels)

    assert result["observation_count"] == 4
    assert result["first_observed_soh"] == 1.0
    assert result["last_observed_soh"] == 0.85
    assert result["net_change_percentage_points"] == -15.0
    assert result["trend_unit"] == "percentage_points_per_sample"
    assert result["is_historical_analysis"] is True
    assert result["is_future_forecast"] is False


def test_analyze_soh_history_rejects_too_few_observations():
    with pytest.raises(ValueError, match="At least 3 observations"):
        analyze_soh_history([2.0, 1.9])


def test_analyze_soh_history_rejects_non_finite_labels():
    with pytest.raises(ValueError, match="NaN or infinite"):
        analyze_soh_history([2.0, np.nan, 1.8])


def test_analyze_soh_history_rejects_invalid_soh():
    with pytest.raises(ValueError, match="between 0 and 1"):
        analyze_soh_history([2.0, 2.1, 1.8])


def test_analyze_xjtu_workbook_analyzes_all_sheets():
    from pathlib import Path

    workbook = (
        Path(__file__).resolve().parents[1]
        / "reference"
        / "SOHbenchmark"
        / "data"
        / "XJTU"
        / "handcraft_features"
        / "batch-1_features.xlsx"
    )

    if not workbook.is_file():
        pytest.skip("Local XJTU workbook is not available.")

    result = analyze_xjtu_workbook(workbook)

    assert result["sheet_count"] == 8
    assert len(result["sheets"]) == 8

    for metrics in result["sheets"].values():
        assert metrics["observation_count"] >= 3
        assert metrics["is_historical_analysis"] is True
        assert metrics["is_future_forecast"] is False
