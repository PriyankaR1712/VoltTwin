import pytest

from digital_twin.battery_twin import (
    BatteryState,
    BatteryTwin,
)


def create_twin():
    return BatteryTwin(
        state=BatteryState(
            battery_id="test-battery",
            soh=0.90,
            cycle_count=0,
        )
    )


def test_observation_updates_twin_state():
    twin = create_twin()

    result = twin.update_from_observation(
        observed_soh=0.85,
        observation_index=3,
    )

    assert twin.state.soh == pytest.approx(0.85)
    assert result["observation_index"] == 3
    assert result["observed_soh"] == pytest.approx(0.85)


def test_observation_is_recorded_in_history():
    twin = create_twin()

    twin.update_from_observation(0.88, observation_index=0)
    twin.update_from_observation(0.85, observation_index=1)

    assert len(twin.observation_history) == 2
    assert twin.observation_history[-1]["observed_soh"] == pytest.approx(0.85)


@pytest.mark.parametrize("invalid_soh", [-0.1, 1.1, float("nan"), float("inf")])
def test_invalid_observation_is_rejected(invalid_soh):
    twin = create_twin()

    with pytest.raises(ValueError):
        twin.update_from_observation(invalid_soh)


def test_simulation_does_not_modify_observed_state():
    twin = create_twin()
    twin.update_from_observation(0.85, observation_index=1)

    twin.simulate(additional_cycles=100)

    assert twin.state.soh == pytest.approx(0.85)
    assert len(twin.observation_history) == 1
    