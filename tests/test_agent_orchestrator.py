
import pytest

from digital_twin import agent_orchestrator
from digital_twin.agent_orchestrator import run_agent_orchestrator
from digital_twin.counterfactual_service import simulate_registered_twin


SCENARIOS = [
    {
        "scenario": "No maintenance",
        "initial_soh": 0.79,
        "projected_soh": 0.78,
        "projected_soh_percent": 78.0,
        "additional_cycles": 100,
        "recovery_assumption": 0.0,
        "difference_vs_baseline": 0.0,
        "is_simulation": True,
    },
    {
        "scenario": "Maintenance A",
        "initial_soh": 0.79,
        "projected_soh": 0.785,
        "projected_soh_percent": 78.5,
        "additional_cycles": 100,
        "recovery_assumption": 0.005,
        "difference_vs_baseline": 0.005,
        "is_simulation": True,
    },
    {
        "scenario": "Maintenance B",
        "initial_soh": 0.79,
        "projected_soh": 0.79,
        "projected_soh_percent": 79.0,
        "additional_cycles": 100,
        "recovery_assumption": 0.01,
        "difference_vs_baseline": 0.01,
        "is_simulation": True,
    },
]


class FakeManager:
    def __init__(self, soh=0.79, prediction_count=4, trend=-0.002):
        self.state_calls = 0
        self.history_calls = 0
        self.state = {
            "battery_id": "battery-1",
            "twin_state": {
                "battery_id": "battery-1",
                "soh": soh,
                "soh_percent": soh * 100,
                "cycle_count": 0,
            },
            "last_observation_index": 17,
            "prediction_count": prediction_count,
            "degradation": (
                {"trend_per_sample": trend, "status": "estimated"}
                if prediction_count >= 3 else None
            ),
            "rul": (
                {"rul_observations": 12, "status": "estimated"}
                if prediction_count >= 3 else None
            ),
            "state_source": "cnn_prediction",
            "rul_unit": "observations",
        }
        self.history = {
            "battery_id": "battery-1",
            "prediction_history": [
                {"observation_index": i + 14, "predicted_soh": soh}
                for i in range(prediction_count)
            ],
            "observation_history": [],
            "observation_count": prediction_count,
            "state_source": "cnn_prediction",
        }

    def get_state(self):
        self.state_calls += 1
        return self.state

    def get_history(self):
        self.history_calls += 1
        return self.history


class FakeRegistry:
    def __init__(self, manager=None):
        self.manager = manager or FakeManager()

    def get(self, battery_id):
        if battery_id != "battery-1":
            raise KeyError(f"No Digital Twin initialized for battery '{battery_id}'.")
        return self.manager


@pytest.fixture
def registered(monkeypatch):
    manager = FakeManager()
    registry = FakeRegistry(manager)
    service_calls = []

    def fake_simulate_registered_twin(**kwargs):
        service_calls.append(kwargs)
        return {
            "battery_id": "battery-1",
            "snapshot_soh": manager.state["twin_state"]["soh"],
            "snapshot_soh_percent": manager.state["twin_state"]["soh"] * 100,
            "state_source": "cnn_prediction",
            "latest_observation_index": 17,
            "prediction_count": manager.state["prediction_count"],
            "scenarios": [
                {**item, "initial_soh": manager.state["twin_state"]["soh"]}
                for item in SCENARIOS
            ],
            "is_simulation": True,
            "is_physically_validated": False,
        }

    monkeypatch.setattr(
        agent_orchestrator,
        "simulate_registered_twin",
        fake_simulate_registered_twin,
    )
    return manager, registry, service_calls


def test_agent_resolves_registered_battery_and_reads_state_and_history(registered):
    manager, registry, _ = registered
    result = run_agent_orchestrator(
        "battery-1", twin_registry=registry
    )

    assert manager.state_calls == 1
    assert manager.history_calls == 1
    assert result["tool_results"]["battery_state"]["soh"] == pytest.approx(0.79)
    assert result["tool_results"]["history_state_source"] == "cnn_prediction"


def test_agent_reuses_manager_degradation_and_rul_without_recomputing(registered):
    manager, registry, _ = registered
    result = run_agent_orchestrator("battery-1", twin_registry=registry)

    assert result["tool_results"]["degradation"] is manager.state["degradation"]
    assert result["tool_results"]["rul_estimate"] is manager.state["rul"]


def test_agent_requires_prediction_and_rejects_unknown_battery(registered):
    _, registry, _ = registered
    registry.manager.state["prediction_count"] = 0
    registry.manager.history["prediction_history"] = []
    with pytest.raises(ValueError, match="no CNN prediction"):
        run_agent_orchestrator("battery-1", twin_registry=registry)
    with pytest.raises(KeyError, match="No Digital Twin initialized"):
        run_agent_orchestrator("unknown", twin_registry=registry)


def test_agent_preserves_prediction_provenance_and_index_count(registered):
    _, registry, _ = registered
    result = run_agent_orchestrator("battery-1", twin_registry=registry)

    assert result["state_source"] == "cnn_prediction"
    assert result["observation_index"] == 17
    assert result["prediction_count"] == 4
    assert result["tool_results"]["prediction_history"]
    assert result["tool_results"]["state_source"] == "cnn_prediction"


def test_agent_rejects_non_prediction_state(registered):
    _, registry, _ = registered
    registry.manager.state["state_source"] = "observation"
    with pytest.raises(ValueError, match="not CNN-prediction sourced"):
        run_agent_orchestrator("battery-1", twin_registry=registry)


def test_counterfactual_delegates_to_registered_twin_service(registered):
    _, registry, service_calls = registered
    result = run_agent_orchestrator(
        "battery-1", additional_cycles=222, twin_registry=registry
    )

    assert service_calls == [{
        "twin_registry": registry,
        "battery_id": "battery-1",
        "additional_cycles": 222,
    }]
    assert result["recommended_scenario"] == "Maintenance B"


def test_agent_does_not_construct_an_independent_twin(registered):
    _, registry, _ = registered
    assert not hasattr(agent_orchestrator, "BatteryTwin")
    run_agent_orchestrator("battery-1", twin_registry=registry)


def test_stable_battery_uses_baseline_assessment(registered):
    manager, registry, _ = registered
    manager.state["twin_state"]["soh"] = 0.95
    manager.state["degradation"] = {"trend_per_sample": 0.0}
    manager.history["prediction_history"] = [
        {"observation_index": 14 + i, "predicted_soh": 0.95}
        for i in range(4)
    ]
    result = run_agent_orchestrator("battery-1", twin_registry=registry)

    assert "baseline_battery_assessment" in result["analysis_plan"]
    assert "counterfactual_simulation" not in result["analysis_plan"]
    assert [item["scenario"] for item in result["tool_results"]["scenario_results"]] == [
        "No maintenance"
    ]


def test_maintenance_recommendation_uses_existing_policy(registered):
    _, registry, _ = registered
    result = run_agent_orchestrator(
        "battery-1",
        diagnostic_evidence={"confirmed_fault": True},
        twin_registry=registry,
    )
    assert result["recommended_action"] == "Qualified Repair/Replacement Assessment"


@pytest.mark.parametrize("additional_cycles", [True, False, 1.5, "10", None, -1, 100001])
def test_agent_rejects_invalid_additional_cycles(registered, additional_cycles):
    _, registry, _ = registered
    with pytest.raises(ValueError, match="Additional cycles"):
        run_agent_orchestrator(
            "battery-1",
            additional_cycles=additional_cycles,
            twin_registry=registry,
        )


def test_agent_rejects_empty_battery_id(registered):
    _, registry, _ = registered
    with pytest.raises(ValueError, match="Battery ID"):
        run_agent_orchestrator(" ", twin_registry=registry)


@pytest.mark.parametrize(
    "additional_cycles", [True, False, 1.5, "10", None, -1, 100001]
)
def test_counterfactual_service_rejects_invalid_additional_cycles(
    additional_cycles,
):
    class UnusedRegistry:
        def get(self, battery_id):
            raise AssertionError("Horizon must be validated before registry access")

    with pytest.raises(ValueError, match="Additional cycles"):
        simulate_registered_twin(
            UnusedRegistry(), "battery-1", additional_cycles
        )


def test_registered_manager_and_counterfactual_service_integrate_together(
    monkeypatch,
):
    from backend import twin_registry as registry_module
    from digital_twin.twin_manager import TwinManager
    import torch

    class ConstantPredictor:
        def predict(self, features):
            return torch.tensor([0.95], dtype=torch.float32)

    monkeypatch.setattr(
        registry_module,
        "TwinManager",
        lambda battery_id, initial_soh=1.0: TwinManager(
            battery_id=battery_id,
            initial_soh=initial_soh,
            predictor=ConstantPredictor(),
        ),
    )
    registry = registry_module.TwinRegistry()
    manager = registry.initialize("battery-1")
    for index in range(3):
        manager.process_observation([0.5] * 67, observation_index=index + 10)

    calculation_counts = {"degradation": 0, "rul": 0}
    original_degradation_estimate = manager.degradation_estimator.estimate
    original_rul_estimate = manager.rul_estimator.estimate

    def count_degradation(values):
        calculation_counts["degradation"] += 1
        return original_degradation_estimate(values)

    def count_rul(values):
        calculation_counts["rul"] += 1
        return original_rul_estimate(values)

    monkeypatch.setattr(manager.degradation_estimator, "estimate", count_degradation)
    monkeypatch.setattr(manager.rul_estimator, "estimate", count_rul)

    result = run_agent_orchestrator(
        "battery-1", additional_cycles=50, twin_registry=registry
    )

    assert result["state_source"] == "cnn_prediction"
    assert result["observation_index"] == 12
    assert result["prediction_count"] == 3
    assert result["tool_results"]["degradation"]["observation_count"] == 3
    assert result["tool_results"]["rul_estimate"]["status"] == "no_declining_trend"
    assert result["tool_results"]["scenario_results"][0]["scenario"] == "No maintenance"
    assert calculation_counts == {"degradation": 1, "rul": 1}

    # Returned state is detached from the cache, and a new CNN prediction
    # invalidates it so the next orchestration sees current registered state.
    cached_state = manager.get_state()
    cached_state["twin_state"]["soh"] = 0.1
    assert manager.get_state()["twin_state"]["soh"] == pytest.approx(0.95)

    manager.process_observation([0.5] * 67, observation_index=13)
    updated = run_agent_orchestrator(
        "battery-1", additional_cycles=50, twin_registry=registry
    )
    assert updated["observation_index"] == 13
    assert updated["prediction_count"] == 4
    assert calculation_counts == {"degradation": 3, "rul": 3}
