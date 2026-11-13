# Leakage-Safe Grouped Capacity Prediction

## Target and scientific scope

**This experiment predicts the stored capacity label; it does not predict SOH.** The available local documentation does not establish the target unit, a per-cell initial capacity, or normalization lineage. The benchmark loader's fixed scale factor alone is not evidence of an SOH denominator.

The experiment does not reproduce original SOHbenchmark feature values and does not validate the candidate feature equations.

## Data and leakage controls

- Profiles: **55**; finite-target cycles: **27535**.
- Predictors: **57** candidate features.
- Grouped by composite batch/profile ID using five deterministic, sample-balanced folds; all cycles from a profile are held together.
- Capacity/target labels, SOH, cycle and profile identifiers, batch, metadata, and all `_Q`/`_energy` integral features are excluded.
- Ridge uses a NumPy closed-form implementation; median imputation and standardization are fitted independently within each training fold.
- Only a median baseline and Ridge are compared; no hyperparameter selection or feature selection uses held-out data.

## Pooled out-of-fold metrics

| Model | MAE | RMSE | R-squared |
|---|---:|---:|---:|
| training_median_baseline | 0.0733097 | 0.0989519 | -0.0456023 |
| ridge | 0.029055 | 0.0398805 | 0.83016 |

Metrics are in the unresolved stored target scale. Per-fold and per-held-out-profile MAE/RMSE/R-squared are in the accompanying CSV. R-squared is undefined for a held-out profile when it has fewer than two samples or a constant target.

## Per-held-out-profile results

| Fold | Held-out profile | Model | Train profiles/cycles | Test profiles/cycles | MAE | RMSE | R-squared |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | batch-1:Sheet5 | training_median_baseline | 44/22022 | 11/5513 | 0.0862629 | 0.114889 | -0.100706 |
| 1 | batch-2:Sheet10 | training_median_baseline | 44/22022 | 11/5513 | 0.0627478 | 0.0958669 | -0.442201 |
| 1 | batch-2:Sheet5 | training_median_baseline | 44/22022 | 11/5513 | 0.0672222 | 0.0965081 | -0.0651957 |
| 1 | batch-2:Sheet8 | training_median_baseline | 44/22022 | 11/5513 | 0.0559377 | 0.0803666 | -0.0203837 |
| 1 | batch-3:Sheet4 | training_median_baseline | 44/22022 | 11/5513 | 0.0908634 | 0.111532 | -6.05258e-05 |
| 1 | batch-3:Sheet5 | training_median_baseline | 44/22022 | 11/5513 | 0.0919414 | 0.113274 | -8.24182e-07 |
| 1 | batch-4:Sheet3 | training_median_baseline | 44/22022 | 11/5513 | 0.075574 | 0.103592 | -0.0219236 |
| 1 | batch-4:Sheet8 | training_median_baseline | 44/22022 | 11/5513 | 0.0728659 | 0.0969619 | -0.074966 |
| 1 | batch-5:Sheet3 | training_median_baseline | 44/22022 | 11/5513 | 0.0735055 | 0.108153 | -0.338526 |
| 1 | batch-5:Sheet6 | training_median_baseline | 44/22022 | 11/5513 | 0.0677376 | 0.103864 | -0.30776 |
| 1 | batch-6:Sheet5 | training_median_baseline | 44/22022 | 11/5513 | 0.0804175 | 0.0995602 | -0.411193 |
| 1 | batch-1:Sheet5 | ridge | 44/22022 | 11/5513 | 0.0373457 | 0.0423869 | 0.850177 |
| 1 | batch-2:Sheet10 | ridge | 44/22022 | 11/5513 | 0.0381859 | 0.0416995 | 0.727134 |
| 1 | batch-2:Sheet5 | ridge | 44/22022 | 11/5513 | 0.0144338 | 0.01676 | 0.967874 |
| 1 | batch-2:Sheet8 | ridge | 44/22022 | 11/5513 | 0.0220987 | 0.0252945 | 0.89892 |
| 1 | batch-3:Sheet4 | ridge | 44/22022 | 11/5513 | 0.0276716 | 0.0322911 | 0.916172 |
| 1 | batch-3:Sheet5 | ridge | 44/22022 | 11/5513 | 0.0317877 | 0.0362284 | 0.897709 |
| 1 | batch-4:Sheet3 | ridge | 44/22022 | 11/5513 | 0.0190645 | 0.0314752 | 0.905659 |
| 1 | batch-4:Sheet8 | ridge | 44/22022 | 11/5513 | 0.0184476 | 0.0228763 | 0.940164 |
| 1 | batch-5:Sheet3 | ridge | 44/22022 | 11/5513 | 0.0263664 | 0.0377634 | 0.836812 |
| 1 | batch-5:Sheet6 | ridge | 44/22022 | 11/5513 | 0.0225422 | 0.0356285 | 0.846117 |
| 1 | batch-6:Sheet5 | ridge | 44/22022 | 11/5513 | 0.0642125 | 0.0687435 | 0.327212 |
| 2 | batch-1:Sheet1 | training_median_baseline | 44/22051 | 11/5484 | 0.0770071 | 0.0999928 | -0.0544403 |
| 2 | batch-1:Sheet2 | training_median_baseline | 44/22051 | 11/5484 | 0.0833919 | 0.110601 | -0.103443 |
| 2 | batch-2:Sheet11 | training_median_baseline | 44/22051 | 11/5484 | 0.0612896 | 0.0951837 | -0.560356 |
| 2 | batch-2:Sheet2 | training_median_baseline | 44/22051 | 11/5484 | 0.0671546 | 0.0893218 | -0.00039706 |
| 2 | batch-3:Sheet7 | training_median_baseline | 44/22051 | 11/5484 | 0.0803718 | 0.0996451 | -0.000689799 |
| 2 | batch-4:Sheet1 | training_median_baseline | 44/22051 | 11/5484 | 0.0729311 | 0.101376 | -0.0921487 |
| 2 | batch-4:Sheet2 | training_median_baseline | 44/22051 | 11/5484 | 0.0665024 | 0.092521 | -0.0134278 |
| 2 | batch-4:Sheet7 | training_median_baseline | 44/22051 | 11/5484 | 0.0714175 | 0.0910662 | -0.0824679 |
| 2 | batch-5:Sheet1 | training_median_baseline | 44/22051 | 11/5484 | 0.0655485 | 0.0964999 | -0.351463 |
| 2 | batch-5:Sheet4 | training_median_baseline | 44/22051 | 11/5484 | 0.0682312 | 0.104989 | -0.189221 |
| 2 | batch-6:Sheet2 | training_median_baseline | 44/22051 | 11/5484 | 0.0612222 | 0.084363 | -0.00653815 |
| 2 | batch-1:Sheet1 | ridge | 44/22051 | 11/5484 | 0.0196764 | 0.024212 | 0.938178 |
| 2 | batch-1:Sheet2 | ridge | 44/22051 | 11/5484 | 0.0276449 | 0.0370047 | 0.876477 |
| 2 | batch-2:Sheet11 | ridge | 44/22051 | 11/5484 | 0.0485769 | 0.0540749 | 0.496394 |
| 2 | batch-2:Sheet2 | ridge | 44/22051 | 11/5484 | 0.0608091 | 0.0681463 | 0.417707 |
| 2 | batch-3:Sheet7 | ridge | 44/22051 | 11/5484 | 0.0252681 | 0.0307822 | 0.904504 |
| 2 | batch-4:Sheet1 | ridge | 44/22051 | 11/5484 | 0.0291 | 0.0419447 | 0.813034 |
| 2 | batch-4:Sheet2 | ridge | 44/22051 | 11/5484 | 0.0148539 | 0.0253614 | 0.923852 |
| 2 | batch-4:Sheet7 | ridge | 44/22051 | 11/5484 | 0.0114343 | 0.0150434 | 0.970461 |
| 2 | batch-5:Sheet1 | ridge | 44/22051 | 11/5484 | 0.0393507 | 0.0676074 | 0.336656 |
| 2 | batch-5:Sheet4 | ridge | 44/22051 | 11/5484 | 0.0206343 | 0.0291532 | 0.908303 |
| 2 | batch-6:Sheet2 | ridge | 44/22051 | 11/5484 | 0.0204827 | 0.0308226 | 0.865642 |
| 3 | batch-1:Sheet4 | training_median_baseline | 44/22007 | 11/5528 | 0.0809516 | 0.10783 | -0.0708793 |
| 3 | batch-2:Sheet12 | training_median_baseline | 44/22007 | 11/5528 | 0.0571125 | 0.0891628 | -0.367224 |
| 3 | batch-2:Sheet4 | training_median_baseline | 44/22007 | 11/5528 | 0.0694336 | 0.0982304 | -0.142992 |
| 3 | batch-3:Sheet1 | training_median_baseline | 44/22007 | 11/5528 | 0.0936252 | 0.114295 | -8.17194e-05 |
| 3 | batch-3:Sheet2 | training_median_baseline | 44/22007 | 11/5528 | 0.094903 | 0.115407 | -4.74192e-05 |
| 3 | batch-4:Sheet4 | training_median_baseline | 44/22007 | 11/5528 | 0.0712023 | 0.0984419 | -0.00883448 |
| 3 | batch-5:Sheet2 | training_median_baseline | 44/22007 | 11/5528 | 0.0598427 | 0.0893281 | -0.176621 |
| 3 | batch-5:Sheet5 | training_median_baseline | 44/22007 | 11/5528 | 0.0701905 | 0.10986 | -0.283579 |
| 3 | batch-5:Sheet7 | training_median_baseline | 44/22007 | 11/5528 | 0.0634353 | 0.0951805 | -0.236823 |
| 3 | batch-6:Sheet3 | training_median_baseline | 44/22007 | 11/5528 | 0.0664167 | 0.0920572 | -0.0242735 |
| 3 | batch-6:Sheet6 | training_median_baseline | 44/22007 | 11/5528 | 0.0761195 | 0.100053 | -0.00853058 |
| 3 | batch-1:Sheet4 | ridge | 44/22007 | 11/5528 | 0.0155158 | 0.0214961 | 0.957442 |
| 3 | batch-2:Sheet12 | ridge | 44/22007 | 11/5528 | 0.0143362 | 0.0167516 | 0.95174 |
| 3 | batch-2:Sheet4 | ridge | 44/22007 | 11/5528 | 0.0392111 | 0.0403383 | 0.807253 |
| 3 | batch-3:Sheet1 | ridge | 44/22007 | 11/5528 | 0.0307964 | 0.0382386 | 0.88806 |
| 3 | batch-3:Sheet2 | ridge | 44/22007 | 11/5528 | 0.0273134 | 0.0332353 | 0.917062 |
| 3 | batch-4:Sheet4 | ridge | 44/22007 | 11/5528 | 0.0468265 | 0.0507225 | 0.732168 |
| 3 | batch-5:Sheet2 | ridge | 44/22007 | 11/5528 | 0.0412103 | 0.0466106 | 0.679646 |
| 3 | batch-5:Sheet5 | ridge | 44/22007 | 11/5528 | 0.0377434 | 0.0474619 | 0.760431 |
| 3 | batch-5:Sheet7 | ridge | 44/22007 | 11/5528 | 0.0207936 | 0.0343107 | 0.839279 |
| 3 | batch-6:Sheet3 | ridge | 44/22007 | 11/5528 | 0.0210593 | 0.0363298 | 0.840476 |
| 3 | batch-6:Sheet6 | ridge | 44/22007 | 11/5528 | 0.057122 | 0.0624968 | 0.606504 |
| 4 | batch-1:Sheet3 | training_median_baseline | 44/22036 | 11/5499 | 0.0858487 | 0.11551 | -0.137547 |
| 4 | batch-1:Sheet6 | training_median_baseline | 44/22036 | 11/5499 | 0.0853268 | 0.11034 | -0.0872722 |
| 4 | batch-1:Sheet8 | training_median_baseline | 44/22036 | 11/5499 | 0.0764225 | 0.100581 | -0.121008 |
| 4 | batch-2:Sheet13 | training_median_baseline | 44/22036 | 11/5499 | 0.0592281 | 0.0928533 | -0.308393 |
| 4 | batch-2:Sheet14 | training_median_baseline | 44/22036 | 11/5499 | 0.0634724 | 0.0980103 | -0.642166 |
| 4 | batch-2:Sheet7 | training_median_baseline | 44/22036 | 11/5499 | 0.0804194 | 0.106669 | -0.0253532 |
| 4 | batch-2:Sheet9 | training_median_baseline | 44/22036 | 11/5499 | 0.0671351 | 0.100108 | -0.467053 |
| 4 | batch-3:Sheet8 | training_median_baseline | 44/22036 | 11/5499 | 0.0806701 | 0.0998193 | -0.000280894 |
| 4 | batch-4:Sheet6 | training_median_baseline | 44/22036 | 11/5499 | 0.0635438 | 0.0866894 | -0.0346199 |
| 4 | batch-6:Sheet7 | training_median_baseline | 44/22036 | 11/5499 | 0.0620742 | 0.0843764 | -0.0614942 |
| 4 | batch-6:Sheet8 | training_median_baseline | 44/22036 | 11/5499 | 0.0595859 | 0.0814544 | -0.0402416 |
| 4 | batch-1:Sheet3 | ridge | 44/22036 | 11/5499 | 0.037919 | 0.048627 | 0.798404 |
| 4 | batch-1:Sheet6 | ridge | 44/22036 | 11/5499 | 0.0395472 | 0.042589 | 0.838018 |
| 4 | batch-1:Sheet8 | ridge | 44/22036 | 11/5499 | 0.0207949 | 0.0243133 | 0.934496 |
| 4 | batch-2:Sheet13 | ridge | 44/22036 | 11/5499 | 0.0104628 | 0.013924 | 0.970578 |
| 4 | batch-2:Sheet14 | ridge | 44/22036 | 11/5499 | 0.0277776 | 0.0356942 | 0.782194 |
| 4 | batch-2:Sheet7 | ridge | 44/22036 | 11/5499 | 0.0227567 | 0.0266841 | 0.935834 |
| 4 | batch-2:Sheet9 | ridge | 44/22036 | 11/5499 | 0.0245821 | 0.0275187 | 0.889143 |
| 4 | batch-3:Sheet8 | ridge | 44/22036 | 11/5499 | 0.014489 | 0.0176691 | 0.968658 |
| 4 | batch-4:Sheet6 | ridge | 44/22036 | 11/5499 | 0.0143223 | 0.0188141 | 0.951268 |
| 4 | batch-6:Sheet7 | ridge | 44/22036 | 11/5499 | 0.0216536 | 0.0307704 | 0.85883 |
| 4 | batch-6:Sheet8 | ridge | 44/22036 | 11/5499 | 0.0335894 | 0.0413698 | 0.731667 |
| 5 | batch-1:Sheet7 | training_median_baseline | 44/22024 | 11/5511 | 0.0874439 | 0.113222 | -0.0716668 |
| 5 | batch-2:Sheet1 | training_median_baseline | 44/22024 | 11/5511 | 0.0636611 | 0.0903256 | -0.0375854 |
| 5 | batch-2:Sheet15 | training_median_baseline | 44/22024 | 11/5511 | 0.0716946 | 0.104609 | -0.862157 |
| 5 | batch-2:Sheet3 | training_median_baseline | 44/22024 | 11/5511 | 0.0755053 | 0.101342 | -0.00341514 |
| 5 | batch-2:Sheet6 | training_median_baseline | 44/22024 | 11/5511 | 0.0629907 | 0.0879769 | -0.0364499 |
| 5 | batch-3:Sheet3 | training_median_baseline | 44/22024 | 11/5511 | 0.0790317 | 0.0994603 | -6.77528e-05 |
| 5 | batch-3:Sheet6 | training_median_baseline | 44/22024 | 11/5511 | 0.0874579 | 0.108542 | -0.00586225 |
| 5 | batch-4:Sheet5 | training_median_baseline | 44/22024 | 11/5511 | 0.0696495 | 0.0932769 | -0.0796291 |
| 5 | batch-5:Sheet8 | training_median_baseline | 44/22024 | 11/5511 | 0.0766604 | 0.119793 | -0.253816 |
| 5 | batch-6:Sheet1 | training_median_baseline | 44/22024 | 11/5511 | 0.0698956 | 0.0969613 | -0.00117811 |
| 5 | batch-6:Sheet4 | training_median_baseline | 44/22024 | 11/5511 | 0.0677962 | 0.0948832 | -0.0261007 |
| 5 | batch-1:Sheet7 | ridge | 44/22024 | 11/5511 | 0.0170243 | 0.0243437 | 0.950459 |
| 5 | batch-2:Sheet1 | ridge | 44/22024 | 11/5511 | 0.00751208 | 0.00939231 | 0.988781 |
| 5 | batch-2:Sheet15 | ridge | 44/22024 | 11/5511 | 0.0251946 | 0.0312355 | 0.833975 |
| 5 | batch-2:Sheet3 | ridge | 44/22024 | 11/5511 | 0.0613897 | 0.108841 | -0.15741 |
| 5 | batch-2:Sheet6 | ridge | 44/22024 | 11/5511 | 0.0171054 | 0.021483 | 0.938199 |
| 5 | batch-3:Sheet3 | ridge | 44/22024 | 11/5511 | 0.0271901 | 0.0366745 | 0.864025 |
| 5 | batch-3:Sheet6 | ridge | 44/22024 | 11/5511 | 0.0160358 | 0.0201789 | 0.965235 |
| 5 | batch-4:Sheet5 | ridge | 44/22024 | 11/5511 | 0.0149533 | 0.0183639 | 0.958154 |
| 5 | batch-5:Sheet8 | ridge | 44/22024 | 11/5511 | 0.0326179 | 0.0444111 | 0.827672 |
| 5 | batch-6:Sheet1 | ridge | 44/22024 | 11/5511 | 0.0438592 | 0.0493131 | 0.741036 |
| 5 | batch-6:Sheet4 | ridge | 44/22024 | 11/5511 | 0.0269869 | 0.0383591 | 0.832294 |

## Interpretation and limitations

- The grouped split prevents cycles from the same profile appearing in both training and test sets, but 55 independent profiles are not enough to support broad claims of robust deployment generalization.
- All remaining features come from measured charging traces and could contain protocol or indirect capacity information. Excluding direct capacity/energy integrals does not prove complete absence of physical proxy information.
- These are exploratory capacity-prediction metrics, not SOH prediction results and not evidence for original benchmark formula correctness.
- Batch and cell cohort differences may be confounded. The held-out profile split is not an external laboratory or protocol test.
- No per-cell first-observed capacity normalization was applied because it is not established as a valid initial-capacity reference.

## Reproducibility

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m scripts.member4_xjtu.aging_prediction
```

The results CSV includes fold, held-out profile, and pooled out-of-fold rows for each model.
