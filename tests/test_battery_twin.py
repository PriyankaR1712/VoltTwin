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
def test_hybrid_simulation_uses_baseline_and_recent_trend():
    twin = create_twin()

    for index, soh in enumerate([0.96, 0.93, 0.90]):
        twin.update_from_observation(soh, observation_index=index)

    result = twin.simulate_hybrid(
        future_samples=10,
        baseline_degradation_per_sample=0.001,
        trend_weight=0.5,
    )

    # Recent slope = -0.03 per observation.
    # Hybrid rate = 0.5 * 0.001 + 0.5 * 0.03 = 0.0155.
    # Projection = 0.90 - 10 * 0.0155 = 0.745.
    assert result["projected_soh"] == pytest.approx(0.745)
    assert result["is_simulation"] is True


def test_hybrid_simulation_does_not_modify_twin_state():
    twin = create_twin()

    for index, soh in enumerate([0.96, 0.93, 0.90]):
        twin.update_from_observation(soh, observation_index=index)

    twin.simulate_hybrid(
        future_samples=10,
        baseline_degradation_per_sample=0.001,
        trend_weight=0.5,
    )

    assert twin.state.soh == pytest.approx(0.90)
    assert len(twin.observation_history) == 3


def test_hybrid_simulation_requires_enough_observations():
    twin = create_twin()
    twin.update_from_observation(0.90, observation_index=0)
    twin.update_from_observation(0.89, observation_index=1)

    with pytest.raises(ValueError):
        twin.simulate_hybrid(
            future_samples=10,
            baseline_degradation_per_sample=0.001,
            trend_weight=0.5,
        )


def test_hybrid_simulation_rejects_invalid_weight():
    twin = create_twin()

    for index, soh in enumerate([0.96, 0.93, 0.90]):
        twin.update_from_observation(soh, observation_index=index)

    with pytest.raises(ValueError):
        twin.simulate_hybrid(
            future_samples=10,
            baseline_degradation_per_sample=0.001,
            trend_weight=1.5,
       )
def test_hybrid_weight_is_reduced_for_less_reliable_trend():
    twin = create_twin()

    for index, soh in enumerate([0.96, 0.94, 0.95, 0.90, 0.91]):
        twin.update_from_observation(soh, observation_index=index)

    result = twin.simulate_hybrid(
        future_samples=10,
        baseline_degradation_per_sample=0.001,
        trend_weight=0.5,
    )

    assert result["trend_r_squared"] < 1.0
    assert result["effective_trend_weight"] < 0.5


def test_hybrid_keeps_full_weight_for_perfect_linear_trend():
    twin = create_twin()

    for index, soh in enumerate([0.96, 0.93, 0.90, 0.87, 0.84]):
        twin.update_from_observation(soh, observation_index=index)

    result = twin.simulate_hybrid(
        future_samples=10,
        baseline_degradation_per_sample=0.001,
        trend_weight=0.5,
    )

    assert result["trend_r_squared"] == pytest.approx(1.0)
    assert result["effective_trend_weight"] == pytest.approx(0.5)


def test_hybrid_uses_baseline_when_trend_fit_is_unavailable():
    twin = create_twin()

    for index, soh in enumerate([0.90, 0.90, 0.90]):
        twin.update_from_observation(soh, observation_index=index)

    result = twin.simulate_hybrid(
        future_samples=10,
        baseline_degradation_per_sample=0.001,
        trend_weight=0.5,
    )

    assert result["trend_r_squared"] is None
    assert result["effective_trend_weight"] == pytest.approx(0.0)
    assert result["hybrid_degradation_per_sample"] == pytest.approx(0.001)