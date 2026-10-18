
from dataclasses import dataclass
from typing import List

from digital_twin.battery_twin import BatteryTwin


@dataclass
class MaintenanceScenario:
    """A hypothetical maintenance scenario for comparison."""

    name: str
    additional_cycles: int
    recovery_assumption: float = 0.0

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Scenario name cannot be empty.")

        if self.additional_cycles < 0:
            raise ValueError("Additional cycles cannot be negative.")

        if not 0.0 <= self.recovery_assumption <= 1.0:
            raise ValueError(
                "Recovery assumption must be between 0 and 1."
            )


def compare_scenarios(
    battery_twin: BatteryTwin,
    scenarios: List[MaintenanceScenario],
) -> List[dict]:
    """
    Compare hypothetical scenarios using the same initial battery state.

    Recovery values are illustrative assumptions, not measured
    or validated maintenance effects.
    """
    if not scenarios:
        raise ValueError("At least one scenario is required.")

    results = []

    for scenario in scenarios:
        outcome = battery_twin.simulate(
            additional_cycles=scenario.additional_cycles,
            maintenance_recovery=scenario.recovery_assumption,
        )

        results.append(
            {
                "scenario": scenario.name,
                "initial_soh": outcome["initial_soh"],
                "projected_soh": outcome["projected_soh"],
                "projected_soh_percent": (
                    outcome["projected_soh_percent"]
                ),
                "additional_cycles": outcome["additional_cycles"],
                "recovery_assumption": (
                    scenario.recovery_assumption
                ),
                "is_simulation": True,
            }
        )

    baseline = next(
        (
            result
            for result in results
            if result["scenario"] == "No maintenance"
        ),
        None,
    )

    for result in results:
        if baseline is None:
            result["difference_vs_baseline"] = None
        else:
            result["difference_vs_baseline"] = round(
                result["projected_soh"]
                - baseline["projected_soh"],
                4,
            )

    return results
