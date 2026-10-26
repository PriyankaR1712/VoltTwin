
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import torch
from models.soh_predictor import SOHPredictor
from digital_twin.historical_degradation import analyze_xjtu_workbook
from digital_twin.degradation_estimator import DegradationEstimator
from pathlib import Path
from digital_twin.sequential_replay import replay_battery
from digital_twin.agentic_controller import run_agentic_maintenance_loop

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


class SOHHistoryInput(BaseModel):
    observed_soh: list[float] = Field(
        ...,
        min_length=3,
        max_length=10000,
        description="Historical SOH observations as fractions between 0 and 1",
    )
    future_samples: int = Field(
        default=25,
        ge=0,
        le=10000,
        description="Number of future observation samples for experimental projection",
    )
    window_size: int = Field(
        default=25,
        ge=3,
        le=1000,
        description="Number of recent observations used to estimate the trend",
    )
    @field_validator("observed_soh")
    @classmethod
    def validate_observed_soh(cls, values):
        if any(not 0.0 <= value <= 1.0 for value in values):
            raise ValueError(
                "Every SOH observation must be between 0.0 and 1.0."
            )
        return values


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

@app.get("/historical-analysis")
def historical_analysis():
    project_root = Path(__file__).resolve().parent.parent

    workbook_path = (
        project_root
        / "reference"
        / "SOHbenchmark"
        / "data"
        / "XJTU"
        / "handcraft_features"
        / "batch-1_features.xlsx"
    )

    result = analyze_xjtu_workbook(workbook_path)

    return result

@app.post("/estimate-degradation")
def estimate_degradation(request: SOHHistoryInput):
    estimator = DegradationEstimator(window_size=request.window_size)

    result = estimator.project(
        observed_soh=request.observed_soh,
        future_samples=request.future_samples,
    )

    return {
        "battery_id": None,
        "analysis_type": "historical_trend_and_experimental_projection",
        **result,
        "notice": (
            "The trend is estimated from observed SOH samples. "
            "Future SOH is an experimental linear extrapolation, "
            "not a physically validated battery forecast. "
            "Sample indices are not verified physical cycle counts."
        ),
    }

class SequentialReplayInput(BaseModel):
    sheet_name: str = Field(min_length=1, max_length=100)
    battery_id: str = Field(min_length=1, max_length=100)

class AdaptiveMaintenanceInput(SequentialReplayInput):
    diagnostic_evidence: dict = Field(default_factory=dict)


@app.post("/replay-battery")
def replay_battery_endpoint(request: SequentialReplayInput):
    project_root = Path(__file__).resolve().parent.parent

    workbook_path = (
        project_root
        / "reference"
        / "SOHbenchmark"
        / "data"
        / "XJTU"
        / "handcraft_features"
        / "batch-1_features.xlsx"
    )

    return replay_battery(
        workbook_path=workbook_path,
        sheet_name=request.sheet_name,
        battery_id=request.battery_id,
    )



@app.post("/adaptive-maintenance")
def adaptive_maintenance(request: AdaptiveMaintenanceInput):
    project_root = Path(__file__).resolve().parent.parent
    workbook_path = (
        project_root
        / "reference"
        / "SOHbenchmark"
        / "data"
        / "XJTU"
        / "handcraft_features"
        / "batch-1_features.xlsx"
    )

    # 1. Replay historical battery observations.
    replay = replay_battery(
        workbook_path=workbook_path,
        sheet_name=request.sheet_name,
        battery_id=request.battery_id,
    )

    observed_soh = [
        observation["actual_soh"]
        for observation in replay["observations"]
    ]

    # 2. Estimate the recent degradation trend.
    estimator = DegradationEstimator(window_size=25)
    trend = estimator.estimate(observed_soh)

    current_soh = replay["final_twin_state"]["soh"]

    # 3. Run the integrated Digital Twin decision loop.
    try:
        controller_result = run_agentic_maintenance_loop(
            battery_id=request.battery_id,
            current_soh=current_soh,
            cycle_count=0,
            trend_per_sample=trend["trend_per_sample"],
            additional_cycles=100,
            minimum_acceptable_soh=0.80,
            diagnostic_evidence=request.diagnostic_evidence,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    # 4. Return the replay, simulation results, and final recommendation.
    return {
        "battery": controller_result["observed_battery_state"],
        "replay": replay,
        "degradation_trend": trend,
        "interventions": controller_result["intervention_proposals"],
        "scenarios": controller_result["simulation_outcomes"],
        "selected_scenario": controller_result["selected_scenario"],
        "selected_action": controller_result["selected_action"],
        "recommendation": controller_result["recommendation"],
        "controller_type": controller_result["controller_type"],
        "maintenance_effects_validated": controller_result[
            "maintenance_effects_validated"
        ],
        "notice": (
            "The CNN predictions are evaluated against recorded labels. "
            "The degradation trend uses observation indices, not verified "
            "physical cycles. Future degradation and maintenance effects "
            "are illustrative simulations, not validated real-world effects. "
            "The current decision controller is deterministic and rule-based."
        ),
    }

