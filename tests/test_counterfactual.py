
import pytest

from digital_twin.battery_twin import (
    BatteryState,
    BatteryTwin,
    SimulationAssumptions,
)
from digital_twin.counterfactual import (
    MaintenanceScenario,
    compare_scenarios,
)


def make_twin():
    return BatteryTwin(
        state=BatteryState(
            battery_id="VoltTwin-Test",
            soh=0.90,
            cycle_count=100,
        ),
        assumptions=SimulationAssumptions(
            degradation_per_cycle=0.0001,
        ),
    )


def make_scenarios():
    return [
        MaintenanceScenario("No maintenance", 100, 0.0),
        MaintenanceScenario("Maintenance A", 100, 0.005),
        MaintenanceScenario("Maintenance B", 100, 0.01),
    ]


def test_scenarios_share_initial_state_and_compare_to_baseline():
    twin = make_twin()

    results = compare_scenarios(twin, make_scenarios())

    assert len(results) == 3
    assert all(result["initial_soh"] == pytest.approx(0.90)
               for result in results)

    assert results[0]["projected_soh"] == pytest.approx(0.89)
    assert results[1]["projected_soh"] == pytest.approx(0.895)
    assert results[2]["projected_soh"] == pytest.approx(0.90)

    assert results[0]["difference_vs_baseline"] == pytest.approx(0.0)
    assert results[1]["difference_vs_baseline"] == pytest.approx(0.005)
    assert results[2]["difference_vs_baseline"] == pytest.approx(0.01)


def test_scenario_comparison_does_not_modify_twin():
    twin = make_twin()
    original_state = twin.get_state()

    compare_scenarios(twin, make_scenarios())

    assert twin.get_state() == original_state


def test_empty_scenario_list_is_rejected():
    with pytest.raises(ValueError, match="At least one scenario"):
        compare_scenarios(make_twin(), [])


@pytest.mark.parametrize(
    "name, cycles, recovery",
    [
        ("", 100, 0.0),
        ("Maintenance A", -1, 0.0),
        ("Maintenance A", 100, -0.1),
        ("Maintenance A", 100, 1.1),
    ],
)
def test_invalid_scenario_inputs_are_rejected(name, cycles, recovery):
    with pytest.raises(ValueError):
        MaintenanceScenario(name, cycles, recovery)
