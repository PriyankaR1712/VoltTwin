
import math

from digital_twin.degradation_estimator import DegradationEstimator


class RULEstimator:
    """
    Experimental Remaining Useful Life (RUL) estimator.

    RUL is reported in observations because physical cycle order
    has not yet been verified. Estimates are not physically validated.
    """

    def __init__(
        self,
        eol_threshold: float = 0.80,
        window_size: int = 25,
        minimum_r_squared: float = 0.50,
    ):
        if not 0.0 < eol_threshold < 1.0:
            raise ValueError("EOL threshold must be between 0 and 1.")

        if not 0.0 <= minimum_r_squared <= 1.0:
            raise ValueError("Minimum R-squared must be between 0 and 1.")

        self.eol_threshold = eol_threshold
        self.estimator = DegradationEstimator(window_size=window_size)
        self.minimum_r_squared = minimum_r_squared

    def estimate(self, observed_soh) -> dict:
        """
        Estimate observations remaining until the EOL threshold.

        Returns an unavailable estimate when the recent trend is
        not sufficiently reliable or is not declining.
        """
        trend = self.estimator.estimate(observed_soh)
        current_soh = float(trend["latest_observed_soh"])
        slope = float(trend["trend_per_sample"])
        r_squared = trend["trend_r_squared"]

        result = {
            "current_soh": round(current_soh, 6),
            "current_soh_percent": round(current_soh * 100, 2),
            "eol_threshold": self.eol_threshold,
            "eol_threshold_percent": round(
                self.eol_threshold * 100, 2
            ),
            "rul_observations": None,
            "status": "unavailable",
            "trend_per_sample": slope,
            "trend_r_squared": r_squared,
            "unit": "observations",
            "is_physically_validated": False,
            "method": "recent_linear_trend_extrapolation",
        }

        if current_soh <= self.eol_threshold:
            result["rul_observations"] = 0
            result["status"] = "threshold_already_reached"
            return result

        if slope >= 0:
            result["status"] = "no_declining_trend"
            return result

        if (
            r_squared is None
            or not math.isfinite(float(r_squared))
            or r_squared < self.minimum_r_squared
        ):
            result["status"] = "trend_confidence_too_low"
            return result

        remaining = (current_soh - self.eol_threshold) / abs(slope)

        if not math.isfinite(remaining):
            result["status"] = "unavailable"
            return result

        result["rul_observations"] = max(0, math.ceil(remaining))
        result["status"] = "estimated"
        return result

