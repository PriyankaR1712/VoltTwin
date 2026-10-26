import math
from dataclasses import dataclass
from digital_twin.degradation_estimator import DegradationEstimator
@dataclass
class BatteryState:
    """Represents the current state of one battery."""

    battery_id: str
    soh: float
    cycle_count: int = 0

    def __post_init__(self):
        if not self.battery_id.strip():
            raise ValueError("Battery ID cannot be empty.")

        if not 0.0 <= self.soh <= 1.0:
            raise ValueError("SOH must be between 0.0 and 1.0.")

        if self.cycle_count < 0:
            raise ValueError("Cycle count cannot be negative.")


@dataclass
class SimulationAssumptions:
    """Explicit assumptions used for a simulated scenario."""

    degradation_per_cycle: float = 0.0001
    maintenance_recovery: float = 0.0

    def __post_init__(self):
        if not 0.0 <= self.degradation_per_cycle <= 1.0:
            raise ValueError(
                "Degradation per cycle must be between 0 and 1."
            )

        if not 0.0 <= self.maintenance_recovery <= 1.0:
            raise ValueError(
                "Maintenance recovery must be between 0 and 1."
            )


class BatteryTwin:
    """
    Software Digital Twin for one battery.

    This initial version uses explicit illustrative assumptions.
    It is not a physically validated battery degradation model.
    """

    def __init__(
        self,
        state: BatteryState,
        assumptions: SimulationAssumptions | None = None,
    ):
        self.state = state
        self.assumptions = assumptions or SimulationAssumptions()
        self.observation_history: list[dict] = []
        self.prediction_history: list[dict] = []
    def get_state(self) -> dict:
        """Return the current battery state."""
        return {
            "battery_id": self.state.battery_id,
            "soh": self.state.soh,
            "soh_percent": round(self.state.soh * 100, 2),
            "cycle_count": self.state.cycle_count,
        }

    def update_from_observation(
        self,
        observed_soh: float,
        observation_index: int | None = None,
    ) -> dict:
        """
        Update the twin using an observed SOH value.

        Observation indices represent positions in the supplied
        history, not verified physical battery cycle counts.
        """
        if not isinstance(observed_soh, (int, float)):
            raise ValueError("Observed SOH must be a finite number.")

        if not math.isfinite(observed_soh):
            raise ValueError("Observed SOH must be a finite number.")

        if not 0.0 <= observed_soh <= 1.0:
            raise ValueError("Observed SOH must be between 0 and 1.")

        if observation_index is not None:
            if (
                not isinstance(observation_index, int)
                or isinstance(observation_index, bool)
                or observation_index < 0
            ):
                raise ValueError(
                    "Observation index must be a non-negative integer."
                )

        self.state.soh = float(observed_soh)

        record = {
            "observation_index": observation_index,
            "observed_soh": float(observed_soh),
            "observed_soh_percent": round(float(observed_soh) * 100, 2),
        }
        self.observation_history.append(record)

        return record
    def record_prediction(
        self,
        predicted_soh: float,
        observation_index: int | None = None,
    ) -> dict:
        """Record predicted SOH separately from observed battery state."""
        if (
            not isinstance(predicted_soh, (int, float))
            or isinstance(predicted_soh, bool)
            or not math.isfinite(predicted_soh)
        ):
            raise ValueError("Predicted SOH must be a finite number.")

        if not 0.0 <= predicted_soh <= 1.0:
            raise ValueError("Predicted SOH must be between 0 and 1.")

        if observation_index is not None and (
            not isinstance(observation_index, int)
            or isinstance(observation_index, bool)
            or observation_index < 0
        ):
            raise ValueError(
                "Observation index must be a non-negative integer."
            )

        record = {
            "observation_index": observation_index,
            "predicted_soh": float(predicted_soh),
            "predicted_soh_percent": round(float(predicted_soh) * 100, 2),
        }
        self.prediction_history.append(record)
        return record

    def simulate(
        self,
        additional_cycles: int,
        maintenance_recovery: float | None = None,
    ) -> dict:
        """
        Simulate future SOH without modifying the current battery state.

        maintenance_recovery is an illustrative scenario assumption,
        not a measured or proven maintenance benefit.
        """
        if additional_cycles < 0:
            raise ValueError("Additional cycles cannot be negative.")

        recovery = (
            self.assumptions.maintenance_recovery
            if maintenance_recovery is None
            else maintenance_recovery
        )

        if not 0.0 <= recovery <= 1.0:
            raise ValueError(
                "Maintenance recovery must be between 0 and 1."
            )

        initial_soh = self.state.soh

        projected_soh = (
            initial_soh
            - additional_cycles
            * self.assumptions.degradation_per_cycle
            + recovery
        )

        projected_soh = max(0.0, min(1.0, projected_soh))

        return {
            "battery_id": self.state.battery_id,
            "initial_soh": round(initial_soh, 4),
            "projected_soh": round(projected_soh, 4),
            "projected_soh_percent": round(projected_soh * 100, 2),
            "initial_cycle_count": self.state.cycle_count,
            "projected_cycle_count": (
                self.state.cycle_count + additional_cycles
            ),
            "additional_cycles": additional_cycles,
            "maintenance_recovery_assumption": recovery,
            "degradation_per_cycle_assumption": (
                self.assumptions.degradation_per_cycle
            ),
            "is_simulation": True,
        }
    def simulate_hybrid(
        self,
        future_samples: int,
        baseline_degradation_per_sample: float = 0.001,
        trend_weight: float = 0.5,
    ) -> dict:
        """
        Project future SOH using baseline degradation and recent trend.

        This is an experimental simulation, not a validated
        physical battery degradation model.
        """
        if (
            not isinstance(future_samples, int)
            or isinstance(future_samples, bool)
            or future_samples < 0
        ):
            raise ValueError(
                "Future samples must be a non-negative integer."
            )

        if (
            not isinstance(baseline_degradation_per_sample, (int, float))
            or not math.isfinite(baseline_degradation_per_sample)
            or not 0.0 <= baseline_degradation_per_sample <= 1.0
        ):
            raise ValueError(
                "Baseline degradation must be between 0 and 1."
            )

        if (
            not isinstance(trend_weight, (int, float))
            or not math.isfinite(trend_weight)
            or not 0.0 <= trend_weight <= 1.0
        ):
            raise ValueError("Trend weight must be between 0 and 1.")

        if len(self.observation_history) < 3:
            raise ValueError(
                "At least 3 SOH observations are required."
            )

        observations = [
            record["observed_soh"]
            for record in self.observation_history
        ]

        window_size = min(25, len(observations))
        estimator = DegradationEstimator(window_size=window_size)
        trend = estimator.estimate(observations)

        trend_per_sample = float(trend["trend_per_sample"])
        trend_based_rate = max(0.0, -trend_per_sample)

        trend_r_squared = trend["trend_r_squared"]

        if trend_r_squared is None:
            effective_trend_weight = 0.0
        else:
            effective_trend_weight = (
                trend_weight * max(0.0, min(1.0, trend_r_squared))
            )

        hybrid_rate = (
            (1.0 - effective_trend_weight)
            * baseline_degradation_per_sample
            + effective_trend_weight * trend_based_rate
        )

        projected_soh = max(
            0.0,
            min(
                1.0,
                self.state.soh - future_samples * hybrid_rate,
            ),
        )

        return {
            "battery_id": self.state.battery_id,
            "initial_soh": round(self.state.soh, 4),
            "projected_soh": round(projected_soh, 4),
            "projected_soh_percent": round(projected_soh * 100, 2),
            "future_samples": future_samples,
            "baseline_degradation_per_sample": (
                baseline_degradation_per_sample
            ),
            "trend_per_sample": trend_per_sample,
            "trend_based_degradation_per_sample": trend_based_rate,
                        "trend_weight": trend_weight,
            "trend_r_squared": trend_r_squared,
            "effective_trend_weight": effective_trend_weight,
            "hybrid_degradation_per_sample": hybrid_rate,
            "model_type": "hybrid_baseline_recent_trend",
            "is_simulation": True,
            "is_physically_validated": False,
        }
