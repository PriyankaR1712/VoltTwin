# VoltTwin

**Adaptive EV Battery Maintenance Using an Agentic Digital Twin with Counterfactual Reasoning**

VoltTwin is a software-based project for estimating electric vehicle (EV) battery State of Health (SOH), replaying historical battery observations, simulating alternative maintenance scenarios, and generating explainable maintenance recommendations.

The project combines a CNN-based SOH prediction model with a software digital twin and rule-based maintenance decision logic. Counterfactual scenarios explore how different assumed maintenance outcomes could affect projected battery health.

> **Project status:** Ongoing academic project. Battery degradation and maintenance effects in the digital twin currently use illustrative assumptions and are not physically validated.

## Project Objectives

- Estimate battery SOH using a deep learning model.
- Evaluate predictions on a held-out XJTU battery.
- Represent battery health using a software-based digital twin.
- Replay historical battery observations and analyze prediction errors.
- Compare counterfactual maintenance scenarios.
- Generate explainable maintenance recommendations using explicit decision rules.
- Visualize battery predictions, historical trends, and simulation results through a web dashboard.

## Technology Stack

| Component | Technologies |
|---|---|
| Programming language | Python |
| Deep learning | PyTorch |
| Data processing | pandas, NumPy |
| Machine learning utilities | scikit-learn |
| Backend API | FastAPI |
| Frontend | React, TypeScript |
| Data visualization | Dashboard tables and charts |
| Testing | pytest |
| Dataset | XJTU lithium-ion battery dataset |

## System Workflow

1. **Battery data:** Load handcrafted battery features and capacity labels from the XJTU dataset.
2. **SOH prediction:** Use the trained CNN model to estimate battery health.
3. **Sequential replay:** Process historical observations in order, compare predicted SOH against actual SOH, and update the software twin's observed state.
4. **Digital twin:** Maintain a software representation of battery health and simulate projected changes.
5. **Counterfactual scenarios:** Compare a baseline scenario with alternative maintenance assumptions.
6. **Maintenance recommendation:** Apply explicit decision rules to the simulated outcomes.
7. **Dashboard:** Present prediction results, historical degradation analysis, replay metrics, and scenario comparisons.

**Important:** The current sequential replay evaluates predictions in batch inference and records observations in order; it is not yet a live streaming battery system. The replay workflow and the scenario-based maintenance workflow are implemented as separate capabilities and should not be interpreted as a fully integrated autonomous maintenance loop.

## Implemented Features

- [x] Environment and reference dataset setup
- [x] CNN-based SOH baseline training
- [x] Feature normalization fitted on training data
- [x] Saved model checkpoint and inference module
- [x] Evaluation on one held-out XJTU battery
- [x] FastAPI endpoints for SOH prediction and simulation
- [x] Software digital twin with configurable illustrative assumptions
- [x] Counterfactual maintenance scenario comparison
- [x] Rule-based maintenance recommendation
- [x] Historical SOH trend analysis
- [x] Experimental linear degradation estimation
- [x] Sequential battery observation replay
- [x] React and TypeScript dashboard integration
- [x] Automated tests for implemented functionality

## SOH Model Evaluation

**Dataset:** XJTU, Batch 1 handcrafted features
**Held-out battery:** Battery 1
**Training samples:** 2,257
**Validation samples:** 565
**Test samples:** 389

| Metric | Result |
|---|---:|
| MAE | 0.015332 |
| MSE | 0.000457 |
| RMSE | 0.021377 |

SOH labels are calculated by dividing capacity by the assumed maximum capacity of 2.0. The reported MAE corresponds to approximately **1.53 SOH percentage points**, and the RMSE corresponds to approximately **2.14 SOH percentage points**.

These results describe evaluation on one held-out battery. The validation split contains samples from batteries used in training, so it does not establish generalization to entirely unseen batteries across the dataset.

See [`BASELINE_RESULTS.md`](BASELINE_RESULTS.md) for additional experiment details and limitations.

## Historical Degradation Analysis

VoltTwin analyzes historical SOH observations to calculate degradation trends and compare simple forecasting approaches.

An exploratory evaluation on XJTU Batch 1 compared baseline and linear-trend methods using chronological data splits. The recent-window linear trend with a window of 25 observations achieved:

- **MAE:** approximately 2.31 SOH percentage points
- **RMSE:** approximately 2.88 SOH percentage points

These are exploratory results on the available dataset, not evidence of general performance across other datasets or real-world batteries. Observation order is used as the trend index; it has not been verified as physical cycle count.

## Digital Twin and Counterfactual Simulation

The software twin maintains a battery's observed SOH and associated state information. It can simulate projected SOH under different assumed future usage and maintenance conditions.

The current scenario comparison includes:

- **No maintenance:** baseline simulation without recovery.
- **Maintenance A:** simulation with an illustrative recovery assumption.
- **Maintenance B:** simulation with a different illustrative recovery assumption.

The maintenance recommendation uses explicit rules and an SOH threshold. It is not currently a trained reinforcement-learning agent or a validated autonomous maintenance system.

Simulated maintenance recovery values are hypothetical. They should not be interpreted as measured maintenance effectiveness or real battery-life improvements.

## Dataset and Reference Implementation

The initial SOH benchmarking implementation is based on:

Wang et al. (2024), *Open access dataset, code library and benchmarking deep learning approaches for state-of-health estimation of lithium-ion batteries*. *Journal of Energy Storage*, 77, 109884.

- **Paper:** https://doi.org/10.1016/j.est.2023.109884
- **Reference implementation:** https://github.com/wang-fujin/SOHbenchmark
- **Dataset information:** https://wang-fujin.github.io/

Download the dataset and reference code from their original sources. They are not included in this repository.

## Running the Project Locally

### Prerequisites

- Python 3.11
- Node.js and npm
- The XJTU Batch 1 handcrafted-features workbook
- The trained CNN checkpoint

Place the dataset and checkpoint in the locations expected by the project configuration.

### 1. Start the backend

From the project root, activate your Python environment and install the project's required Python dependencies.

```powershell
.\.venv311\Scripts\Activate.ps1
```

Start the FastAPI application:

```powershell
python -m uvicorn backend.main:app --reload
```

The API is typically available at `http://127.0.0.1:8000`. Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

### 2. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, typically `http://localhost:5173`.

**Setup note:** A `requirements.txt` or other dependency lock file should be provided for reproducible installation. If the repository does not yet contain one, the exact Python dependency installation command still needs to be documented.

## Project Limitations and Future Work

- Evaluate SOH prediction across additional independently held-out batteries and datasets.
- Strengthen validation of the degradation estimator using independent test sequences.
- Integrate sequential replay outputs with counterfactual simulation and maintenance recommendations into one end-to-end workflow.
- Develop a more condition-aware adaptive maintenance policy and evaluate cases where the recommendation changes.
- Investigate physics-based battery simulation if suitable input data and project requirements support it.
- Validate simulated degradation and maintenance assumptions against suitable experimental or published evidence.

## Repository Structure

```text
VoltTwin/
├── backend/                 # FastAPI application
├── digital_twin/            # Twin, replay, simulation, and decision logic
├── frontend/                # React + TypeScript dashboard
├── models/                  # Model inference code and checkpoint location
├── preprocessing/            # Data preprocessing utilities
├── tests/                   # Automated tests
├── train_soh.py             # CNN training pipeline
├── validate_degradation.py  # Exploratory degradation evaluation
├── BASELINE_RESULTS.md      # Baseline experiment details
└── README.md
```

## Project Status

VoltTwin is an ongoing academic project. Model predictions, observed historical trends, and simulated scenario outcomes are distinct outputs and should be evaluated separately. Future work will focus on integrating these components into a coherent adaptive maintenance workflow and improving the validation of its decisions.
