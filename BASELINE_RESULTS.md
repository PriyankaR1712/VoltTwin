
# VoltTwin — Initial SOH Baseline

## Reference
Wang et al. (2024), Open access dataset, code library and benchmarking deep learning approaches for state-of-health estimation of lithium-ion batteries.

## Experiment Configuration
- Dataset: XJTU
- Batch: 1
- Input type: Handcrafted features
- Model: CNN
- Test battery ID: 1
- Feature normalization: Min-max, range (-1, 1)
- Training device: CPU
- Maximum epochs: 30
- Training samples: 2,822
- Test samples: 389

## Evaluation Results
- MAE: 0.045100
- MAPE: 4.8819%
- MSE: 0.002418
- RMSE: 0.049169

## Limitations
- Results represent one held-out battery and one experiment.
- Generalization across batteries has not yet been established.
- The reference implementation's preprocessing and model behavior
  must be preserved or documented when reproducing this baseline.
- This baseline estimates SOH; it does not validate maintenance
  interventions, counterfactual outcomes, or Digital Twin accuracy.

### Integrated Predictor Test — XJTU Batch 1, Battery 1

- Dataset: XJTU handcrafted features
- Held-out test battery: Battery 1
- Test samples: 389
- Training samples: 2,822 across the remaining seven batteries
- Model: CNN with a 67-feature preprocessing network
- Checkpoint: `models/soh_cnn_xjtu_batch1.pkl`
- MAE: 0.049498
- RMSE: 0.058164

Status: The copied checkpoint loads successfully and produces predictions on real dataset features.

Limitation: The reference preprocessing fits the scaler separately on each battery's complete feature set, including the held-out test battery. These metrics reproduce that pipeline and should not be presented as leakage-free deployment performance.

### Clean Training-Only Normalization Experiment

- Dataset: XJTU Batch 1 handcrafted features
- Held-out test battery: Battery 1
- Training samples: 2,257
- Validation samples: 565
- Test samples: 389
- Model: CNN with a 67-to-512 preprocessing network
- Scaler: Min-max scaler fitted on training samples only
- Best epoch: 5
- Best validation MSE: 0.000242
- Test MAE: 0.015332
- Test MSE: 0.000457
- Test RMSE: 0.021377

Checkpoint: `models/soh_cnn_xjtu_batch1_clean.pt`

Results directory: `results/clean_xjtu_batch1/`

Limitation: This is a single-batch, single-held-out-battery experiment. Validation samples were randomly split from pooled training-battery samples, so the validation set is not battery-independent. Further evaluation across multiple held-out batteries is required before claiming generalization.
### Inference Integration Verification

- Clean checkpoint: `models/soh_cnn_xjtu_batch1_clean.pt`
- Predictor: `models/soh_predictor.py`
- Held-out battery: XJTU Batch 1, Battery 1
- Test samples: 389
- MAE: 0.015332
- RMSE: 0.021377
- Predicted SOH range: 0.757762–0.995242

Status: The saved checkpoint, training architecture, scaler parameters, and inference implementation now produce consistent predictions.

Correction: Removed the duplicate `predict()` method that overrode the raw-input inference implementation.

Limitation: Results are from a single held-out battery and do not establish generalization across the full dataset.