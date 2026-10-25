import math
from dataclasses import dataclass, field



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
