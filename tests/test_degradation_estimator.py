
import pytest

from digital_twin.degradation_estimator import DegradationEstimator


def test_estimates_recent_soh_trend():
    estimator = DegradationEstimator(window_size=3)

    result = estimator.estimate([1.0, 0.99, 0.98, 0.97])

    assert result["observation_count"] == 4
    assert result["window_size_used"] == 3
    assert result["latest_observed_soh"] == pytest.approx(0.97)
    assert result["trend_per_sample"] == pytest.approx(-0.01)
    assert result["trend_percentage_points_per_sample"] == pytest.approx(-1.0)
    assert result["is_historical_estimate"] is True
    assert result["is_future_forecast"] is False


def test_projects_future_soh():
    estimator = DegradationEstimator(window_size=3)

    result = estimator.project(
        [1.0, 0.99, 0.98, 0.97],
        future_samples=2,
    )

    assert result["projected_soh"] == pytest.approx(0.95)
    assert result["future_samples"] == 2
    assert result["is_future_forecast"] is True
    assert result["forecast_type"] == "experimental_linear_extrapolation"


def test_window_uses_available_observations():
    estimator = DegradationEstimator(window_size=25)

    result = estimator.estimate([0.95, 0.94, 0.93])

    assert result["window_size_used"] == 3


@pytest.mark.parametrize(
    "values",
    [
        [0.95, 0.94],
        [0.95, float("nan"), 0.93],
        [0.95, float("inf"), 0.93],
        [1.1, 0.94, 0.93],
        [0.95, -0.1, 0.93],
        [[0.95, 0.94, 0.93]],
    ],
)
def test_rejects_invalid_soh_history(values):
    estimator = DegradationEstimator()

    with pytest.raises(ValueError):
        estimator.estimate(values)


@pytest.mark.parametrize("future_samples", [-1, 1.5, True])
def test_rejects_invalid_future_sample_count(future_samples):
    estimator = DegradationEstimator()

    with pytest.raises(ValueError):
        estimator.project([0.95, 0.94, 0.93], future_samples)


@pytest.mark.parametrize("window_size", [0, 1, 2, 2.5, True])
def test_rejects_invalid_window_size(window_size):
    with pytest.raises(ValueError):
        DegradationEstimator(window_size=window_size)
