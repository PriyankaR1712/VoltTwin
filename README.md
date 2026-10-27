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

The sample loader uses the last row in the selected sheet. The row's position is an observation index; it should not be treated as a verified physical cycle number unless the dataset's cycle ordering has been independently confirmed. The feature columns must match the model's expected input order, and the label must not be included among the model inputs.

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

The project uses the XJTU handcrafted-feature workbook for the current workflow. The dataset and trained model checkpoint are not included in this repository; obtain required data and reference files from their original sources and place them at the paths expected by the project.

## Running the Project Locally

### Prerequisites

- Git
- Python 3.11
- Node.js and npm
- The XJTU Batch 1 handcrafted-features workbook
- The trained CNN checkpoint expected by the project

The dataset and trained checkpoint are not included in this repository. Confirm that required files exist at the paths expected by the backend before starting the application.

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
python -m uvicorn backend.main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

Keep this terminal running.

> If your existing local environment is named `.venv311`, activate that environment instead of creating a new one. Use the environment in which your dependencies and trained-model setup are installed.

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
