
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import torch
from models.soh_predictor import SOHPredictor

app = FastAPI(
    title="VoltTwin API",
    description="API for EV battery SOH simulation and maintenance scenarios.",
    version="0.1.0",
)

class SOHFeatureInput(BaseModel):
    features: list[float] = Field(
        ...,
        min_length=67,
        max_length=67,
        description="Exactly 67 handcrafted battery features",
    )

class BatteryFeatureSimulationInput(SOHFeatureInput):
    battery_id: str = Field(min_length=1, max_length=100)
    cycle_count: int = Field(ge=0)
    additional_cycles: int = Field(default=100, ge=0, le=100000)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BatteryInput(BaseModel):
    battery_id: str = Field(min_length=1, max_length=100)
    soh: float = Field(ge=0.0, le=1.0)
    cycle_count: int = Field(ge=0)
    additional_cycles: int = Field(default=100, ge=0, le=100000)


@app.get("/")
def root():
    return {
        "message": "Welcome to VoltTwin API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict-soh")
def predict_soh(request: SOHFeatureInput):
    predictor = SOHPredictor()

    features = torch.tensor(
        [request.features],
        dtype=torch.float32,
    )

    prediction = predictor.predict(features)
    soh = float(prediction.item())

    return {
        "predicted_soh": soh,
        "predicted_soh_percent": round(soh * 100, 2),
        "model": "Clean CNN trained on XJTU batch-1",
        "input_feature_count": len(request.features),
        "is_prediction": True,
    }

@app.post("/simulate")
def simulate_battery(data: BatteryInput):
    from digital_twin.battery_twin import (
        BatteryState,
        BatteryTwin,
        SimulationAssumptions,
    )
    from digital_twin.counterfactual import (
        MaintenanceScenario,
        compare_scenarios,
    )
    from digital_twin.maintenance_agent import recommend_maintenance

    twin = BatteryTwin(
        state=BatteryState(
            battery_id=data.battery_id,
            soh=data.soh,
            cycle_count=data.cycle_count,
        ),
        assumptions=SimulationAssumptions(
            degradation_per_cycle=0.0001
        ),
    )

    scenarios = [
        MaintenanceScenario("No maintenance", data.additional_cycles, 0.0),
        MaintenanceScenario("Maintenance A", data.additional_cycles, 0.005),
        MaintenanceScenario("Maintenance B", data.additional_cycles, 0.01),
    ]

    results = compare_scenarios(twin, scenarios)
    recommendation = recommend_maintenance(
        results,
        minimum_acceptable_soh=0.80,
    )

    return {
        "battery": twin.get_state(),
        "scenarios": results,
        "recommendation": recommendation,
        "notice": (
            "Scenario outcomes use illustrative assumptions. "
            "They are simulations, not validated maintenance effects."
        ),
    }

@app.post("/simulate-from-features")
def simulate_from_features(data: BatteryFeatureSimulationInput):
    from digital_twin.battery_twin import (
        BatteryState,
        BatteryTwin,
        SimulationAssumptions,
    )
    from digital_twin.counterfactual import (
        MaintenanceScenario,
        compare_scenarios,
    )
    from digital_twin.maintenance_agent import recommend_maintenance

    # Step 1: Predict SOH from the 67 input features.
    predictor = SOHPredictor()
    features = torch.tensor(
        [data.features],
        dtype=torch.float32,
    )
    predicted_soh = float(predictor.predict(features).item())

    # Step 2: Initialize the Digital Twin with predicted SOH.
    twin = BatteryTwin(
        state=BatteryState(
            battery_id=data.battery_id,
            soh=predicted_soh,
            cycle_count=data.cycle_count,
        ),
        assumptions=SimulationAssumptions(
            degradation_per_cycle=0.0001,
        ),
    )

    # Step 3: Compare the maintenance scenarios.
    scenarios = [
        MaintenanceScenario(
            "No maintenance", data.additional_cycles, 0.0
        ),
        MaintenanceScenario(
            "Maintenance A", data.additional_cycles, 0.005
        ),
        MaintenanceScenario(
            "Maintenance B", data.additional_cycles, 0.01
        ),
    ]

    results = compare_scenarios(twin, scenarios)
    recommendation = recommend_maintenance(
        results,
        minimum_acceptable_soh=0.80,
    )

    return {
        "battery": twin.get_state(),
        "predicted_soh": predicted_soh,
        "predicted_soh_percent": round(predicted_soh * 100, 2),
        "scenarios": results,
        "recommendation": recommendation,
        "notice": (
            "SOH is predicted by the trained CNN. "
            "Future degradation and maintenance effects use illustrative "
            "simulation assumptions, not validated maintenance effects."
        ),
    }

