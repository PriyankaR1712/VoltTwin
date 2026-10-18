
import numpy as np


class DegradationEstimator:
    """
    Estimate a local linear SOH trend from observed historical values.

    The estimator works in observation-index units, not verified
    physical cycle units. Its projections are experimental estimates,
    not physically validated battery forecasts.
    """

    def __init__(self, window_size: int = 25):
        if not isinstance(window_size, int) or isinstance(window_size, bool):
            raise ValueError("Window size must be an integer.")

        if window_size < 3:
            raise ValueError("Window size must be at least 3.")

        self.window_size = window_size

    def estimate(self, observed_soh) -> dict:
        """
        Fit a linear trend to the most recent observations.

        observed_soh contains SOH fractions between 0 and 1,
        ordered from oldest to newest.
        """
        soh = np.asarray(observed_soh, dtype=np.float64)

        if soh.ndim != 1:
            raise ValueError("SOH history must be one-dimensional.")

        if len(soh) < 3:
            raise ValueError("At least 3 observations are required.")

        if not np.isfinite(soh).all():
            raise ValueError("SOH history contains NaN or infinite values.")

        if np.any((soh < 0.0) | (soh > 1.0)):
            raise ValueError("SOH values must be between 0 and 1.")

        used_window = min(self.window_size, len(soh))
        recent = soh[-used_window:]

        # Center indices on the latest observation.
        x = np.arange(-used_window + 1, 1, dtype=np.float64)
        slope, intercept = np.polyfit(x, recent, 1)

        fitted = slope * x + intercept
        residuals = recent - fitted
        ss_res = float(np.sum(residuals**2))
        ss_tot = float(np.sum((recent - np.mean(recent))**2))

        r_squared = (
            1.0 - ss_res / ss_tot
            if ss_tot > 0
            else None
        )

        return {
            "observation_count": int(len(soh)),
            "window_size_used": int(used_window),
            "latest_observed_soh": round(float(soh[-1]), 6),
            "trend_per_sample": round(float(slope), 8),
            "trend_percentage_points_per_sample": round(
                float(slope * 100), 6
            ),
            "trend_r_squared": (
                round(r_squared, 6) if r_squared is not None else None
            ),
            "is_historical_estimate": True,
            "is_future_forecast": False,
        }

    def project(
        self,
        observed_soh,
        future_samples: int,
    ) -> dict:
        """
        Project SOH using the estimated recent linear trend.

        This is an experimental extrapolation. It is not a validated
        physical degradation model.
        """
        if (
            not isinstance(future_samples, int)
            or isinstance(future_samples, bool)
            or future_samples < 0
        ):
            raise ValueError("Future samples must be a non-negative integer.")

        estimate = self.estimate(observed_soh)

        # Refit using the same recent window as estimate().
        soh = np.asarray(observed_soh, dtype=np.float64)
        used_window = estimate["window_size_used"]
        recent = soh[-used_window:]
        x = np.arange(-used_window + 1, 1, dtype=np.float64)
        slope, intercept = np.polyfit(x, recent, 1)

        projected = intercept + slope * future_samples

        # Keep the reported SOH within its valid numerical range.
        projected = float(np.clip(projected, 0.0, 1.0))

        return {
            **estimate,
            "future_samples": future_samples,
            "projected_soh": round(projected, 6),
            "projected_soh_percent": round(projected * 100, 2),
            "is_historical_estimate": False,
            "is_future_forecast": True,
            "forecast_type": "experimental_linear_extrapolation",
        }
