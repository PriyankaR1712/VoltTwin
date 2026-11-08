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


def _validate_additional_cycles(additional_cycles: object) -> None:
    if type(additional_cycles) is not int or not 0 <= additional_cycles <= 100000:
        raise ValueError(
            "Additional cycles must be an integer between 0 and 100000."
        )


def _get_registered_snapshot(
    twin_registry,
    battery_id: str,
    state_snapshot: dict | None,
) -> tuple[object, dict]:
    manager = twin_registry.get(battery_id)
    snapshot = (
        manager.get_snapshot()
        if state_snapshot is None
        else state_snapshot
    )
    if not isinstance(snapshot, dict) or snapshot.get("battery_id") != battery_id:
        raise ValueError("Twin snapshot is missing or belongs to another battery.")
    if snapshot.get("_manager_identity") != id(manager):
        raise ValueError("Twin snapshot does not belong to the registered manager.")

    state = snapshot.get("state")
    history = snapshot.get("history")
    if (
        not isinstance(state, dict)
        or state.get("battery_id") != battery_id
        or state.get("state_source") != "cnn_prediction"
        or not isinstance(history, dict)
        or history.get("state_source") != "cnn_prediction"
    ):
        raise ValueError("Twin snapshot is incomplete or lacks CNN provenance.")

    predictions = history.get("prediction_history")
    prediction_count = state.get("prediction_count")
    if (
        not isinstance(predictions, list)
        or not isinstance(prediction_count, int)
        or isinstance(prediction_count, bool)
        or len(predictions) != prediction_count
    ):
        raise ValueError("Twin snapshot prediction history is inconsistent.")
    if prediction_count < 1:
        raise CounterfactualStateUnavailable(
            f"Battery '{battery_id}' has no CNN prediction yet. "
            "Process an observation before running simulation."
        )
    return manager, snapshot


def _snapshot_twin(snapshot: dict) -> BatteryTwin:
    state = snapshot["state"]["twin_state"]
    assumptions = snapshot["simulation_assumptions"]
    return BatteryTwin(
        state=BatteryState(
            battery_id=state["battery_id"],
            soh=state["soh"],
            cycle_count=state["cycle_count"],
        ),
        assumptions=SimulationAssumptions(
            degradation_per_cycle=assumptions["degradation_per_cycle"],
            maintenance_recovery=assumptions["maintenance_recovery"],
        ),
    )


def simulate_registered_twin(
    twin_registry,
    battery_id: str,
    additional_cycles: int,
    state_snapshot: dict | None = None,
) -> dict:
    """Compare scenarios from one coherent, isolated registered-twin snapshot."""
    _validate_additional_cycles(additional_cycles)
    _, snapshot = _get_registered_snapshot(
        twin_registry, battery_id, state_snapshot
    )
    manager_state = snapshot["state"]
    prediction_count = manager_state["prediction_count"]
    operational_state = manager_state["twin_state"]
    snapshot_twin = _snapshot_twin(snapshot)

    scenarios = [
        MaintenanceScenario("No maintenance", additional_cycles, 0.0),
        MaintenanceScenario("Maintenance A", additional_cycles, 0.005),
        MaintenanceScenario("Maintenance B", additional_cycles, 0.01),
    ]
    results = compare_scenarios(snapshot_twin, scenarios)

    return {
        "battery_id": battery_id,
        "snapshot_version": snapshot["version"],
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


def assess_registered_baseline(
    twin_registry,
    battery_id: str,
    additional_cycles: int,
    state_snapshot: dict,
) -> dict:
    """Run only the no-maintenance baseline from a captured twin snapshot."""
    _validate_additional_cycles(additional_cycles)
    _, snapshot = _get_registered_snapshot(
        twin_registry, battery_id, state_snapshot
    )
    outcome = _snapshot_twin(snapshot).simulate(
        additional_cycles=additional_cycles,
        maintenance_recovery=0.0,
    )
    return {
        "scenario": "No maintenance",
        "initial_soh": outcome["initial_soh"],
        "projected_soh": outcome["projected_soh"],
        "projected_soh_percent": outcome["projected_soh_percent"],
        "additional_cycles": additional_cycles,
        "recovery_assumption": 0.0,
        "difference_vs_baseline": 0.0,
        "is_simulation": True,
        "snapshot_version": snapshot["version"],
    }
