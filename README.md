# VoltTwin

**Adaptive EV Battery Maintenance Using an Agentic Digital Twin with Counterfactual Reasoning**

VoltTwin is a software-based project that aims to estimate electric vehicle battery State of Health (SOH), simulate alternative maintenance scenarios using a digital twin, and recommend maintenance actions based on simulated outcomes and explicit constraints.

## Project Goals

- Estimate battery SOH using machine learning.
- Build a software-based battery digital twin.
- Compare alternative maintenance scenarios using counterfactual reasoning.
- Develop an agentic decision workflow for maintenance recommendations.
- Evaluate model predictions and scenario-based decisions.

## Technology Stack

- Python
- PyTorch
- pandas and NumPy
- scikit-learn
- FastAPI (planned)
- React and TypeScript (planned)
- PostgreSQL (planned)

## Current Progress

- [x] Environment and reference dataset setup
- [x] Initial CNN SOH baseline experiment
- [x] Training-only feature normalization
- [x] Clean CNN checkpoint and inference module
- [x] Initial evaluation on one held-out XJTU battery
- [ ] Digital twin simulation
- [ ] Counterfactual maintenance scenarios
- [ ] Agentic recommendation workflow
- [ ] FastAPI integration
- [ ] React dashboard
- [ ] Evaluation across multiple held-out batteries

## Initial SOH Experiment

Dataset: XJTU, Batch 1 handcrafted features  
Held-out battery: Battery 1  
Training samples: 2,257  
Validation samples: 565  
Test samples: 389  

| Metric | Result |
|---|---:|
| MAE | 0.015332 |
| MSE | 0.000457 |
| RMSE | 0.021377 |

The experiment uses SOH labels normalized by a capacity of 2.0. The metrics are from a single held-out battery and do not establish generalization across the full dataset.

See `BASELINE_RESULTS.md` for experiment details and limitations.

## Reference

The initial SOH benchmarking work is based on:

Wang et al. (2024), *Open access dataset, code library and benchmarking deep learning approaches for state-of-health estimation of lithium-ion batteries*, Journal of Energy Storage, 77, 109884.

- Paper: https://doi.org/10.1016/j.est.2023.109884
- Reference code: https://github.com/wang-fujin/SOHbenchmark
- Dataset information: https://wang-fujin.github.io/

Download the dataset and reference code from their original sources. They are not included in this repository.

## Project Status

This is an ongoing academic project. Digital twin behavior and maintenance scenario outcomes will be simulations, and their assumptions and limitations will be documented separately from measured data and model predictions.
