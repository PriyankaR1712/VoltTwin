"""Structural and provenance validation for registered counterfactual results."""

import math
from dataclasses import dataclass
from typing import Mapping

from digital_twin.planner_config import DEFAULT_PLANNER_CONFIG, PlannerConfig


EXPECTED_SCENARIOS = (
    "No maintenance",
    "Maintenance A",
    "Maintenance B",
)


def _number(value: object, field: str, low: float, high: float) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not low <= value <= high
    ):
        raise ValueError(f"{field} must be finite and between {low} and {high}.")
    return float(value)


def _required_equal(actual, expected, field: str) -> None:
    if type(actual) is not type(expected) or actual != expected:
        raise ValueError(f"Counterfactual {field} does not match the snapshot.")


@dataclass(frozen=True)
class ValidatedScenarioSet:
    battery_id: str
    snapshot_version: int
    state_source: str
    observation_index: object
    prediction_count: int
    snapshot_soh: float
    additional_cycles: int
    scenarios: Mapping[str, dict]

    @property
    def baseline(self) -> dict:
        return self.scenarios["No maintenance"]

    @property
    def interventions(self) -> Mapping[str, dict]:
        return {
            name: self.scenarios[name]
            for name in ("Maintenance A", "Maintenance B")
        }


def validate_counterfactual_response(
    response: object,
    captured_snapshot: object,
    requested_horizon: int,
    config: PlannerConfig = DEFAULT_PLANNER_CONFIG,
) -> ValidatedScenarioSet:
    """Validate the complete response; partial sets are never rankable."""
    if type(requested_horizon) is not int or not 0 <= requested_horizon <= 100000:
        raise ValueError("requested_horizon must be an integer between 0 and 100000.")
    if not isinstance(captured_snapshot, dict):
        raise ValueError("Captured snapshot must be a dictionary.")
    if not isinstance(response, dict):
        raise ValueError("Counterfactual response must be a dictionary.")

    battery_id = captured_snapshot.get("battery_id")
    state = captured_snapshot.get("state")
    history = captured_snapshot.get("history")
    if not isinstance(battery_id, str) or not battery_id:
        raise ValueError("Captured snapshot has no battery identity.")
    if not isinstance(state, dict) or not isinstance(history, dict):
        raise ValueError("Captured snapshot is missing state or history.")
    if state.get("state_source") != "cnn_prediction" or history.get(
        "state_source"
    ) != "cnn_prediction":
        raise ValueError("Captured snapshot lacks CNN prediction provenance.")
    twin_state = state.get("twin_state")
    if not isinstance(twin_state, dict) or twin_state.get("battery_id") != battery_id:
        raise ValueError("Captured snapshot state identity is inconsistent.")
    snapshot_soh = _number(twin_state.get("soh"), "snapshot SOH", 0.0, 1.0)
    snapshot_version = captured_snapshot.get("version")
    prediction_count = state.get("prediction_count")
    observation_index = state.get("last_observation_index")
    if type(snapshot_version) is not int or type(prediction_count) is not int:
        raise ValueError("Captured snapshot version or prediction count is invalid.")
    if prediction_count < 1:
        raise ValueError("Captured snapshot has no CNN predictions.")
    if observation_index is not None and (
        type(observation_index) is not int or observation_index < 0
    ):
        raise ValueError("Captured snapshot observation index is invalid.")

    _required_equal(response.get("battery_id"), battery_id, "battery identity")
    _required_equal(response.get("snapshot_version"), snapshot_version, "version")
    _required_equal(response.get("state_source"), "cnn_prediction", "provenance")
    _required_equal(
        response.get("latest_observation_index"), observation_index, "observation index"
    )
    _required_equal(response.get("prediction_count"), prediction_count, "prediction count")
    response_soh = _number(response.get("snapshot_soh"), "response snapshot SOH", 0.0, 1.0)
    if abs(response_soh - snapshot_soh) > (
        config.scenario_soh_rounding_tolerance + 1e-12
    ):
        raise ValueError("Counterfactual snapshot SOH does not match the captured snapshot.")

    rows = response.get("scenarios")
    if not isinstance(rows, list) or len(rows) != config.expected_scenario_count:
        raise ValueError("Counterfactual response must contain exactly three scenarios.")
    by_name = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Every counterfactual scenario must be a dictionary.")
        name = row.get("scenario")
        if name not in EXPECTED_SCENARIOS:
            raise ValueError(f"Unexpected counterfactual scenario: {name!r}")
        if name in by_name:
            raise ValueError(f"Duplicate counterfactual scenario: {name}")
        by_name[name] = row
    if set(by_name) != set(EXPECTED_SCENARIOS):
        raise ValueError("Counterfactual response is missing a required scenario.")

    expected_recovery_by_scenario = dict(
        zip(EXPECTED_SCENARIOS, config.expected_recovery_assumptions)
    )
    for name in EXPECTED_SCENARIOS:
        row = by_name[name]
        initial = _number(row.get("initial_soh"), f"{name} initial SOH", 0.0, 1.0)
        _number(row.get("projected_soh"), f"{name} projected SOH", 0.0, 1.0)
        if abs(initial - snapshot_soh) > (
            config.scenario_soh_rounding_tolerance + 1e-12
        ):
            raise ValueError(f"{name} initial SOH does not match the snapshot.")
        if type(row.get("additional_cycles")) is not int or row[
            "additional_cycles"
        ] != requested_horizon:
            raise ValueError(f"{name} horizon does not match the requested horizon.")
        recovery = row.get("recovery_assumption")
        if (
            isinstance(recovery, bool)
            or not isinstance(recovery, (int, float))
            or not math.isfinite(recovery)
            or abs(recovery - expected_recovery_by_scenario[name])
            > config.recovery_assumption_tolerance
        ):
            raise ValueError(f"{name} recovery assumption is inconsistent.")

    baseline_soh = by_name["No maintenance"]["projected_soh"]
    for name, row in by_name.items():
        delta = row.get("difference_vs_baseline")
        if (
            isinstance(delta, bool)
            or not isinstance(delta, (int, float))
            or not math.isfinite(delta)
        ):
            raise ValueError(f"{name} baseline delta must be a finite number.")
        expected_delta = row["projected_soh"] - baseline_soh
        if abs(delta - expected_delta) > (
            config.baseline_delta_consistency_tolerance + 1e-12
        ):
            raise ValueError(f"{name} baseline delta is inconsistent.")

    return ValidatedScenarioSet(
        battery_id=battery_id,
        snapshot_version=snapshot_version,
        state_source="cnn_prediction",
        observation_index=observation_index,
        prediction_count=prediction_count,
        snapshot_soh=snapshot_soh,
        additional_cycles=requested_horizon,
        scenarios=by_name,
    )
