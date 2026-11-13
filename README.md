# VoltTwin

**Adaptive EV Battery Maintenance Using an Agentic Digital Twin with Counterfactual Reasoning**

VoltTwin is an ongoing academic software project for estimating electric-vehicle (EV) battery State of Health (SOH), analyzing historical battery observations, simulating alternative maintenance scenarios, and producing explainable maintenance recommendations.

The project combines a convolutional neural network (CNN) for SOH prediction with a software-based digital twin, historical replay and trend analysis, counterfactual scenario comparison, and rule-based maintenance decision logic.

> **Project status:** Ongoing academic project. The CNN produces SOH estimates, while future degradation and maintenance recovery use illustrative assumptions. These simulation assumptions and recommendations are not physically validated. The current maintenance logic is rule-based; this is not yet a fully autonomous agent or a live battery-management system.

## Table of Contents

- [Project Objectives](#project-objectives)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [System Workflow](#system-workflow)
- [Dashboard Modules](#dashboard-modules)
- [SOH Model Evaluation](#soh-model-evaluation)
- [Historical Degradation Analysis](#historical-degradation-analysis)
- [Digital Twin and Counterfactual Simulation](#digital-twin-and-counterfactual-simulation)
- [Dataset and Reference Implementation](#dataset-and-reference-implementation)
- [Running the Project Locally](#running-the-project-locally)
- [Troubleshooting](#troubleshooting)
- [Limitations and Future Work](#limitations-and-future-work)
- [Repository Structure](#repository-structure)

## Project Objectives

- Estimate battery SOH using a trained deep-learning model.
- Evaluate SOH predictions against capacity-derived reference labels.
- Replay recorded battery observations and analyze prediction errors.
- Represent battery state using a software-based digital twin.
- Analyze historical SOH trends and generate experimental projections.
- Compare a baseline with hypothetical maintenance scenarios.
- Generate explainable recommendations using explicit decision rules.
- Present model outputs and simulation results through an interactive web dashboard.

## Key Features

- **CNN-based SOH prediction:** Uses 67 handcrafted battery features as model inputs.
- **Battery selection:** The dashboard supports selecting batteries represented by the eight sheets in the XJTU Batch 1 handcrafted-features workbook. The sample loader fetches feature values from the selected sheet.
- **Historical SOH analysis:** Summarizes observed SOH, net change, and degradation trends across the workbook's sheets.
- **Sequential replay:** Runs CNN inference across recorded observations and compares predictions with capacity-derived SOH labels.
- **Prediction metrics:** Reports mean absolute error (MAE) and root mean squared error (RMSE) for replayed observations.
- **Experimental RUL estimate:** Estimates remaining observations to a configured SOH threshold; this is not a validated estimate of physical battery life.
- **Digital twin:** Maintains a software representation of battery state during simulation and historical replay.
- **Counterfactual maintenance scenarios:** Compares no-maintenance and illustrative Maintenance A and Maintenance B assumptions.
- **Rule-based recommendation:** Selects a scenario using explicit rules and a configured SOH threshold.
- **Interactive dashboard charts:** Displays actual versus predicted SOH, SOH projection, maintenance scenario comparisons, and current SOH against the end-of-life reference threshold.
- **Diagnostic evidence inputs:** Allows users to enter reported thermal alerts, cell-voltage imbalance, charging anomalies, confirmed faults, and BMS codes. These are user-supplied inputs, not automatically detected by the dataset.

## Technology Stack

| Component | Technologies |
|---|---|
| Programming language | Python |
| Deep learning | PyTorch |
| Data processing | pandas, NumPy |
| Machine-learning utilities | scikit-learn |
| Backend API | FastAPI |
| Frontend | React, TypeScript |
| Charts | Recharts |
| API/data validation | Pydantic |
| Testing | pytest |
| Dataset | XJTU lithium-ion battery dataset |

## System Workflow

1. **Load battery data:** Read handcrafted features and capacity-derived labels from the XJTU dataset.
2. **Predict SOH:** Supply the expected 67 feature values to the trained CNN.
3. **Analyze history:** Summarize observed SOH and estimate a recent degradation trend.
4. **Replay observations:** Run model inference across recorded observations and compare predictions against reference SOH labels.
5. **Update the software twin:** Represent the observed battery state and replay progress.
6. **Simulate scenarios:** Compare a no-maintenance baseline with alternative hypothetical maintenance assumptions.
7. **Generate a recommendation:** Apply rule-based decision logic to the simulated outcomes and available diagnostic evidence.
8. **Visualize results:** Display predictions, trends, errors, RUL estimates, and scenario comparisons in the React dashboard.

> **Workflow distinction:** Historical sequential replay and the scenario-based adaptive-maintenance workflow are separate capabilities in the current implementation. The dashboard is not connected to a live EV or BMS, and the workflow should not be described as a fully autonomous, real-time maintenance loop.

## Dashboard Modules

### 1. Battery Configuration

- Select an XJTU Batch 1 battery sheet through the battery selector.
- Load a sample row from the selected sheet into the 67-feature input.
- Set the request's cycle-count field and the future simulation horizon.
- Run the SOH prediction and scenario simulation.

The sample loader uses the last row in the selected sheet. Sequential replay processes recorded XJTU dataset rows offline; it is a simulated dataset replay, not live EV telemetry and it does not connect to a vehicle or BMS. The row's position is an observation index; it should not be treated as a verified physical cycle number unless the dataset's cycle ordering has been independently confirmed. The feature columns must match the model's expected input order, and the label must not be included among the model inputs.

### 2. Battery Health Estimate

Displays the CNN's predicted SOH, the battery identifier, and the cycle-count value supplied in the request. The predicted SOH is a model output, not a direct physical measurement.

### 3. Counterfactual Maintenance Scenarios

Compares:
- **No maintenance:** baseline without an assumed recovery effect.
- **Maintenance A:** scenario with an illustrative recovery assumption.
- **Maintenance B:** scenario with a different illustrative recovery assumption.

Projected values depend on the configured degradation and recovery assumptions. They are not experimentally measured maintenance outcomes.

### 4. Current Recommendation

Displays the selected scenario, its projected SOH, and whether the projected result meets the configured SOH threshold. The recommendation is generated by explicit rules and should be interpreted as a simulation-based decision aid, not a professional battery diagnosis.

### 5. Historical Trend and SOH Projection

Uses historical SOH observations to estimate a recent trend and extrapolate it over a chosen number of future observations. The interface can load historical analysis from the XJTU Batch 1 workbook.

The projection is an experimental trend extrapolation. Observation order has not been verified as physical cycle order, and the projection is not a physically validated battery forecast.

### 6. Sequential Replay

Replays recorded observations from a selected dataset sheet. The dashboard displays:
- Number of observations processed
- MAE and RMSE
- Remaining Useful Life (RUL) estimate relative to the configured SOH threshold
- Actual-versus-predicted SOH chart
- A subset of observation-level results
- Final software digital-twin state

The reported metrics are calculated over the observations in the selected replay sheet. They should not be presented as evidence of generalization to unseen batteries unless the training and evaluation protocol supports that conclusion.

### 7. Integrated Adaptive Maintenance

Combines battery-history replay, counterfactual scenario comparison, and manually supplied diagnostic evidence. Inputs may include reported thermal alerts, cell-voltage imbalance, charging anomalies, confirmed diagnostic faults, and BMS fault codes.

The dashboard does not automatically detect these diagnostic conditions from the XJTU dataset. Users should enter only evidence that has actually been observed or confirmed.

## SOH Model Evaluation

The current baseline experiment documented for this project uses the XJTU Batch 1 handcrafted-feature data.

**Recorded evaluation setup**

- **Held-out battery:** Battery 1
- **Training samples:** 2,257
- **Validation samples:** 565
- **Test samples:** 389

| Metric | Recorded result |
|---|---:|
| MAE | 0.015332 |
| MSE | 0.000457 |
| RMSE | 0.021377 |

SOH labels are calculated by dividing capacity by the assumed maximum capacity of 2.0. The recorded MAE corresponds to approximately **1.53 SOH percentage points**, and RMSE corresponds to approximately **2.14 SOH percentage points**.

These figures are retained from the project's existing baseline results. They describe the documented evaluation setup and should not be confused with metrics from every interactive replay. The validation split contains samples from batteries used in training, so it does not establish generalization to entirely unseen batteries across the dataset.

See [`BASELINE_RESULTS.md`](BASELINE_RESULTS.md) for further experiment details and limitations.

## Historical Degradation Analysis

VoltTwin summarizes historical SOH observations and explores simple trend-based forecasting.

An exploratory evaluation on XJTU Batch 1 compared baseline and linear-trend methods using chronological data splits. The recent-window linear trend with a window of 25 observations achieved the following recorded results:

- **MAE:** approximately 2.31 SOH percentage points
- **RMSE:** approximately 2.88 SOH percentage points

These are exploratory results on the available dataset, not evidence of general performance across other datasets or real-world batteries. Observation order is used as the trend index; it has not been verified as physical cycle count. Future SOH values are experimental extrapolations.

## Digital Twin and Counterfactual Simulation

The software twin maintains battery state information such as battery identifier, SOH, and the supplied cycle-count field. It supports simulation of projected SOH under different assumed future usage and maintenance conditions.

The current scenario comparison includes:

- **No maintenance:** baseline simulation without recovery.
- **Maintenance A:** simulation with an illustrative recovery assumption.
- **Maintenance B:** simulation with a different illustrative recovery assumption.

The maintenance recommendation uses explicit rules and a configured SOH threshold. It is not currently a trained reinforcement-learning agent or a validated autonomous maintenance system.

Simulated degradation and maintenance recovery values are hypothetical. They should not be interpreted as measured maintenance effectiveness or real battery-life improvements.

## Dataset and Reference Implementation

The initial SOH benchmarking implementation is based on:

Wang et al. (2024), *Open access dataset, code library and benchmarking deep learning approaches for state-of-health estimation of lithium-ion batteries*, *Journal of Energy Storage*, 77, 109884.

- **Paper:** https://doi.org/10.1016/j.est.2023.109884
- **Reference implementation:** https://github.com/wang-fujin/SOHbenchmark
- **Dataset information:** https://wang-fujin.github.io/

The current workflow requires the external XJTU handcrafted-feature workbook and a trained CNN checkpoint. Neither asset, nor the reference dataset repository, is included in this Git repository. Obtain them from their original sources. The current backend expects the workbook at `reference/SOHbenchmark/data/XJTU/handcraft_features/batch-1_features.xlsx` and the checkpoint at `models/soh_cnn_xjtu_batch1_clean.pt`; keep these local assets out of Git.

## Running the Project Locally

### Prerequisites

- Git
- Python 3.11
- Node.js and npm
- The external XJTU Batch 1 handcrafted-features workbook
- The external trained CNN checkpoint

These assets are not included in this repository. For the current backend configuration, place the workbook at `reference/SOHbenchmark/data/XJTU/handcraft_features/batch-1_features.xlsx` and the checkpoint at `models/soh_cnn_xjtu_batch1_clean.pt`. Obtain both from their original sources; do not commit them.

### 1. Clone the repository

```powershell
git clone https://github.com/PriyankaR1712/VoltTwin.git
cd VoltTwin
```

### 2. Set up and start the backend

Run these commands from the project root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
# Needed for the Starlette TestClient-based API tests:
python -m pip install -r requirements-dev.txt
python -m uvicorn backend.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

Keep this terminal running.

> `requirements.txt` declares the Python application dependencies. `requirements-dev.txt` adds the `httpx2` dependency used by Starlette's TestClient in API tests. Install both files in a test environment with `python -m pip install -r requirements.txt -r requirements-dev.txt`.

If your existing local environment is named `.venv311`, activate that environment instead of creating a new one. Use the environment in which your dependencies are installed.

### Stage 5 adaptive workflow demonstration

For the Stage 5 demonstration, run `scripts/start_stage5_demo.ps1` from the repository root in a PowerShell window. The launcher uses the active virtual environment, if one is activated; otherwise it uses the repository's `.venv` or `.venv311` when present, then falls back to the current `python` command. To select the existing VoltTwin environment explicitly, run:

```powershell
.\scripts\start_stage5_demo.ps1 -PythonExe '.\.venv311\Scripts\python.exe'
```

When `-PythonExe` is supplied, the launcher verifies that the path exists and uses that executable. It starts Uvicorn from this worktree with exactly one worker and without reload mode. The demo configuration is scoped to that launched process.

The launcher supplies the following **illustrative demonstration values only**. They are not calibrated thresholds and are not approved for operational use:

```text
VOLTTWIN_ADAPTIVE_MINIMUM_GAP=3
VOLTTWIN_ADAPTIVE_EPSILON_SOH=0.01
VOLTTWIN_ADAPTIVE_POLICY_VERSION=volttwin-demo-v1
```

It sets `VOLTTWIN_ADAPTIVE_DB_PATH` to `data/stage5-demo/adaptive_evaluation.db`. The Stage 5 store may also create the adjacent `.worker.lock` file. This is a dedicated demo event store; the existing Stage 4 decision history remains at `data/decision_history.db`. Do not remove or replace either database to repeat the demonstration. Stage 5's existing validation, event reservation, recovery, idempotency, and process-lease safeguards remain in effect.

The demonstration battery ID is `STAGE5-DEMO`. The launcher checks that the API port is available before starting. If another backend is already listening, it checks that battery's state and stops visibly if the ID is registered; it also stops if the port is occupied even when that ID is absent, so it cannot accidentally use a different running process. With no server already running, the launcher does not query a live registry; the new process will start with a fresh in-memory TwinRegistry. Before initializing the Twin, verify `GET /twin/STAGE5-DEMO/state` returns 404 (not initialized); if it returns 200, stop the demonstration and choose a new ID rather than resetting the Twin.

With the backend running, use a second PowerShell window. Supply exactly 67 numeric feature values from a valid input row for each observation; the placeholders below are not valid model input. Use the same feature row if no separate rows are being replayed, and label observations with increasing indices.

1. Initialize the fresh Twin:

   ```powershell
   Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/twin/STAGE5-DEMO/initialize -ContentType 'application/json' -Body '{"initial_soh":1.0}'
   ```

2. Process at least one observation by posting `{"observation_index":0,"features":[...67 numeric values...]}` to `/twin/STAGE5-DEMO/observation`. Then run the first Stage 3 assessment by posting the goal below to `/api/agent/decide`:

   ```json
   {"battery_id":"STAGE5-DEMO","goal":{"goal_id":"stage5-demo","horizon_cycles":100,"assessment_scope":"baseline_only"}}
   ```

   Confirm the response header `X-Decision-Persistence-Status` is `saved` or `already_saved`, and note the returned `decision_id`.

3. Confirm that Stage 4 saved the first decision:

   ```text
   GET /api/agent/batteries/STAGE5-DEMO/decisions
   ```

   The response should list the decision ID from Stage 3.

4. Process at least three additional observations for `STAGE5-DEMO`, with increasing `observation_index` values and valid 67-value feature arrays. After processing them, fetch `GET /twin/STAGE5-DEMO/state` and use its current `prediction_count` and `last_observation_index`. The state endpoint does not expose the snapshot version; in this Twin, each accepted prediction advances the version once, so the adaptive API watermark requires `version` to equal `prediction_count`. Use those current values as `prediction_count`, `version`, and `observation_index` in the next request. Do not reuse a stale watermark.

5. Post to `/api/agent/adaptive-decide` with the same goal and that exact latest watermark:

   ```json
   {
     "battery_id":"STAGE5-DEMO",
     "goal":{"goal_id":"stage5-demo","horizon_cycles":100,"assessment_scope":"baseline_only"},
     "event_watermark":{"prediction_count":4,"version":4,"observation_index":3}
   }
   ```

   The numeric watermark above is only an illustration; substitute the values returned by the Twin.

6. Check the adaptive response and then list Stage 4 history again using the GET request above. `evaluation_status: reassessed` means Stage 3 ran and Stage 4 should contain its associated decision ID. `evaluation_status: held` means no reassessment was required for that event; the Stage 4 list should not gain a decision from that held event. `evaluation_status: indeterminate` means the event outcome cannot safely be retried as if it had not run; preserve the event record and inspect the returned IDs and server logs. HTTP 409 indicates a stale or mismatched watermark/request, while HTTP 503 indicates adaptive evaluation is unavailable or indeterminate; startup/configuration errors are reported in the launcher/backend terminal. A reassessment is not guaranteed: the minimum gap must be met, or another existing trigger condition must apply.

The supplied policy values are for repeatable demonstration mechanics only. They do not establish calibrated SOH hysteresis or a suitable operational reassessment interval.

#### Stage 5 feasibility scope

Stage 5 feasibility is a model-based eligibility assessment against documented intervention rules. It is not physical safety validation and does not establish that an intervention is safe or effective in operation. The production intervention-rule registry is currently empty, so undocumented interventions such as Maintenance A and Maintenance B remain `unknown`; when documented rules and evidence do not support an eligible candidate, the system returns no intervention recommendation.
### 3. Set up and start the frontend

Open a second terminal from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, typically `http://localhost:5173/`.

Keep this terminal running too.

### 4. Run the tests

From the project root, with the Python environment activated:

```powershell
python -m pytest
```

## Troubleshooting

- **Python version:** Use Python 3.11 for the project environment.
- **Missing model or dataset:** Confirm the required checkpoint and XJTU workbook exist at the paths expected by the backend.
- **Backend errors:** Check the backend terminal and visit `http://127.0.0.1:8000/docs` to verify that the API is running.
- **Frontend errors:** Check the frontend terminal and confirm npm dependencies installed successfully. Run `npm run build` inside `frontend` to reveal TypeScript and production-build errors.
- **PowerShell activation blocked:** If your system prevents virtual-environment activation, use an appropriate local execution-policy setting or invoke the environment's Python executable directly.
- **Battery features fail to load:** Confirm the selected sheet exists in the expected workbook and that its feature columns match the model's expected 67-feature order.

## Limitations and Future Work

- Evaluate SOH prediction across additional independently held-out batteries and datasets.
- Verify the feature-column mapping and observation ordering for each dataset sheet.
- Strengthen validation of the degradation estimator using independent test sequences.
- Integrate sequential replay outputs with counterfactual simulation and maintenance recommendations into one end-to-end workflow.
- Develop a more condition-aware adaptive maintenance policy and evaluate cases where the recommendation changes.
- Investigate physics-based battery simulation if suitable input data and project requirements support it.
- Validate simulated degradation and maintenance assumptions against suitable experimental or published evidence.
- Explore ways to connect diagnostic evidence to reliable data sources rather than relying only on manual input.

## Repository Structure

```text
VoltTwin/
├── backend/                    # FastAPI application
├── digital_twin/                # Twin, replay, simulation, and decision logic
├── frontend/                    # React + TypeScript dashboard
├── models/                      # Model inference code and checkpoint location
├── preprocessing/               # Data preprocessing utilities
├── tests/                       # Automated tests
├── train_soh.py                 # CNN training pipeline
├── validate_degradation.py      # Exploratory degradation evaluation
├── BASELINE_RESULTS.md          # Baseline experiment details
└── README.md
```

## Project Status

VoltTwin is an ongoing academic project. CNN predictions, observed historical trends, and simulated scenario outcomes are distinct outputs and should be evaluated separately. Current maintenance decisions are rule-based, future degradation and recovery assumptions are illustrative, and RUL is expressed in observations rather than verified physical battery cycles. Future work will focus on stronger validation and integrating the components into a more coherent adaptive-maintenance workflow.
