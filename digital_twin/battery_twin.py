
from dataclasses import dataclass


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

    def get_state(self) -> dict:
        """Return the current battery state."""
        return {
            "battery_id": self.state.battery_id,
            "soh": self.state.soh,
            "soh_percent": round(self.state.soh * 100, 2),
            "cycle_count": self.state.cycle_count,
        }

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
