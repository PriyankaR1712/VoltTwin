"""Run counterfactual scenarios from a registered CNN-driven twin."""

from digital_twin.battery_twin import (
    BatteryState,
    BatteryTwin,
    SimulationAssumptions,
)
from digital_twin.counterfactual import (
    MaintenanceScenario,
    compare_scenarios,
)


class CounterfactualStateUnavailable(ValueError):
    """Raised when a registered twin has no CNN prediction yet."""


def simulate_registered_twin(
    twin_registry,
    battery_id: str,
    additional_cycles: int,
) -> dict:
    """Compare standard scenarios from a read-only snapshot of a twin."""
    manager = twin_registry.get(battery_id)
    manager_state = manager.get_state()
    prediction_count = manager_state["prediction_count"]
    if prediction_count < 1:
        raise CounterfactualStateUnavailable(
            f"Battery '{battery_id}' has no CNN prediction yet. "
            "Process an observation before running counterfactual scenarios."
        )

    operational_state = manager_state["twin_state"]
    operational_assumptions = manager.twin.assumptions
    snapshot = BatteryTwin(
        state=BatteryState(
            battery_id=operational_state["battery_id"],
            soh=operational_state["soh"],
            cycle_count=operational_state["cycle_count"],
        ),
        assumptions=SimulationAssumptions(
            degradation_per_cycle=(
                operational_assumptions.degradation_per_cycle
            ),
            maintenance_recovery=(
                operational_assumptions.maintenance_recovery
            ),
        ),
    )

    scenarios = [
        MaintenanceScenario("No maintenance", additional_cycles, 0.0),
        MaintenanceScenario("Maintenance A", additional_cycles, 0.005),
        MaintenanceScenario("Maintenance B", additional_cycles, 0.01),
    ]
    results = compare_scenarios(snapshot, scenarios)

    return {
        "battery_id": battery_id,
        "snapshot_soh": operational_state["soh"],
        "snapshot_soh_percent": operational_state["soh_percent"],
        "state_source": manager_state["state_source"],
        "latest_observation_index": manager_state[
            "last_observation_index"
        ],
        "prediction_count": prediction_count,
        "scenarios": results,
        "is_simulation": True,
        "is_physically_validated": False,
        "notice": (
            "Scenario outcomes use illustrative degradation and "
            "maintenance recovery assumptions. They are simulations, "
            "not validated maintenance effects."
        ),
    }
