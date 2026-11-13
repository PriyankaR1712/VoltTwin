# XJTU Feature Error Analysis and Root Cause Investigation

## Executive summary

This investigation compares the existing candidate extractor with workbook values. It does not identify or reproduce the original feature generator, and no candidate result is labeled as an original formula.

- Alignment inventory: **19,191 positional, unverified pairs**, **7,129 capacity-match diagnostic pairs**, **0 identity-verified pairs**, **489 ambiguous workbook rows** (included in 617 unmatched workbook rows), and **1,215 unmatched raw cycles**.
- Positional and capacity-match results are kept in separate cohorts. Ambiguous and unmatched workbook rows are not scored. No cohort is described as verified cycle identity.
- Feature-level rankings below use the positional cohort only as a diagnostic; its identity remains unverified. Batch-6 capacity matches are reported separately and are not pooled into the primary ranking.
- Candidate-invalid feature observations in the positional cohort: **975** across the 67 feature summaries.
- MAPE excludes benchmark values at or below 1% of that feature/cohort's median absolute benchmark value (or 1e-12, whichever is larger); both included and excluded counts are reported.
- The four entropy columns remain unknown-original-formula features; every entropy sensitivity is explicitly a proxy diagnostic.

## Methodology and reproducibility

The runner loads each batch's raw prepared MAT cycles and Excel sheets, calls the existing `_profile_pairs` alignment helper unchanged, and evaluates the existing default `SegmentationPolicy()` and `extract_cycle()` candidate values. The workbook feature order is checked against all 67 known names. Candidate and benchmark non-finite values are counted separately and excluded from numeric metrics.

For each feature and scope, signed error is candidate minus workbook. The report computes MAE, RMSE, mean signed bias, median/max absolute error, signed-error quantiles, MAPE with the near-zero exclusion above, relative MAE (`MAE / mean(abs(benchmark))`), and Pearson/Spearman correlations when defined. MAPE is the mean of per-observation absolute percentage errors over non-near-zero references; it is not the aggregate relative MAE.

Scope tables use the same pairs, grouped as overall, batch, profile, and within-profile cycle deciles. The compressed cycle-wise diagnostic file contains one feature-level record per aligned pair; it preserves the alignment cohort and is not ground-truth cycle error.

### Alignment limitations

| Batch | Profile | Alignment cohort | Method | Matched pairs | Unmatched workbook rows | Ambiguous rows (subset) | Unmatched raw cycles | Mean |label Δ| | Max |label Δ| |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Sheet1 | positional_unverified | positional_unverified_equal_counts | 389 | 0 | 0 | 0 | 0 | 0 |
| 1 | Sheet2 | positional_unverified | positional_unverified_equal_counts | 406 | 0 | 0 | 0 | 0 | 0 |
| 1 | Sheet3 | positional_unverified | positional_unverified_equal_counts | 392 | 0 | 0 | 0 | 0 | 0 |
| 1 | Sheet4 | positional_unverified | positional_unverified_equal_counts | 395 | 0 | 0 | 0 | 0 | 0 |
| 1 | Sheet5 | positional_unverified | positional_unverified_equal_counts | 402 | 0 | 0 | 0 | 0 | 0 |
| 1 | Sheet6 | positional_unverified | positional_unverified_equal_counts | 407 | 0 | 0 | 0 | 0 | 0 |
| 1 | Sheet7 | positional_unverified | positional_unverified_equal_counts | 401 | 0 | 0 | 0 | 0 | 0 |
| 1 | Sheet8 | positional_unverified | positional_unverified_equal_counts | 419 | 0 | 0 | 0 | 0 | 0 |
| 2 | Sheet1 | positional_unverified | positional_unverified_equal_counts | 298 | 0 | 0 | 0 | 6.0403e-05 | 0.012 |
| 2 | Sheet2 | positional_unverified | positional_unverified_equal_counts | 291 | 0 | 0 | 0 | 0.00035395 | 0.036 |
| 2 | Sheet3 | positional_unverified | positional_unverified_equal_counts | 285 | 0 | 0 | 0 | 0 | 0 |
| 2 | Sheet4 | positional_unverified | positional_unverified_equal_counts | 321 | 0 | 0 | 0 | 0 | 0 |
| 2 | Sheet5 | positional_unverified | positional_unverified_equal_counts | 296 | 0 | 0 | 0 | 0 | 0 |
| 2 | Sheet6 | positional_unverified | positional_unverified_equal_counts | 321 | 0 | 0 | 0 | 0.00019003 | 0.028 |
| 2 | Sheet7 | positional_unverified | positional_unverified_equal_counts | 318 | 0 | 0 | 0 | 0 | 0 |
| 2 | Sheet8 | positional_unverified | positional_unverified_equal_counts | 269 | 0 | 0 | 0 | 0.00066171 | 0.054 |
| 2 | Sheet9 | positional_unverified | positional_unverified_equal_counts | 286 | 0 | 0 | 0 | 0 | 0 |
| 2 | Sheet10 | positional_unverified | positional_unverified_equal_counts | 163 | 0 | 0 | 0 | 6.135e-05 | 0.01 |
| 2 | Sheet11 | positional_unverified | positional_unverified_equal_counts | 130 | 0 | 0 | 0 | 0.00029231 | 0.025 |
| 2 | Sheet12 | positional_unverified | positional_unverified_equal_counts | 211 | 0 | 0 | 0 | 0.00023697 | 0.025 |
| 2 | Sheet13 | positional_unverified | positional_unverified_equal_counts | 225 | 0 | 0 | 0 | 8.8889e-05 | 0.013 |
| 2 | Sheet14 | positional_unverified | positional_unverified_equal_counts | 146 | 0 | 0 | 0 | 0.00020548 | 0.02 |
| 2 | Sheet15 | positional_unverified | positional_unverified_equal_counts | 167 | 0 | 0 | 0 | 0 | 0 |
| 3 | Sheet1 | positional_unverified | positional_unverified_equal_counts | 591 | 0 | 0 | 0 | 2.0138e-16 | 4.4409e-16 |
| 3 | Sheet2 | positional_unverified | positional_unverified_equal_counts | 551 | 0 | 0 | 0 | 1.9948e-16 | 4.4409e-16 |
| 3 | Sheet3 | positional_unverified | positional_unverified_equal_counts | 666 | 0 | 0 | 0 | 3.7896e-05 | 0.013079 |
| 3 | Sheet4 | positional_unverified | positional_unverified_equal_counts | 556 | 0 | 0 | 0 | 1.9409e-16 | 4.4409e-16 |
| 3 | Sheet5 | positional_unverified | positional_unverified_equal_counts | 561 | 0 | 0 | 0 | 1.9632e-16 | 4.4409e-16 |
| 3 | Sheet6 | positional_unverified | positional_unverified_equal_counts | 541 | 0 | 0 | 0 | 1.9044e-16 | 4.4409e-16 |
| 3 | Sheet7 | positional_unverified | positional_unverified_equal_counts | 526 | 0 | 0 | 0 | 3.984e-05 | 0.010196 |
| 3 | Sheet8 | positional_unverified | positional_unverified_equal_counts | 616 | 0 | 0 | 0 | 1.9321e-16 | 4.4409e-16 |
| 4 | Sheet1 | positional_unverified | positional_unverified_equal_counts | 798 | 0 | 0 | 0 | 0.00070851 | 0.0041869 |
| 4 | Sheet2 | positional_unverified | positional_unverified_equal_counts | 672 | 0 | 0 | 0 | 0.00089545 | 0.014194 |
| 4 | Sheet3 | positional_unverified | positional_unverified_equal_counts | 672 | 0 | 0 | 0 | 0.00082139 | 0.0043294 |
| 4 | Sheet4 | positional_unverified | positional_unverified_equal_counts | 726 | 0 | 0 | 0 | 0.00077767 | 0.0056568 |
| 4 | Sheet5 | positional_unverified | positional_unverified_equal_counts | 738 | 0 | 0 | 0 | 0.00073872 | 0.0045883 |
| 4 | Sheet6 | positional_unverified | positional_unverified_equal_counts | 714 | 0 | 0 | 0 | 0.0011236 | 0.040262 |
| 4 | Sheet7 | positional_unverified | positional_unverified_equal_counts | 600 | 0 | 0 | 0 | 0.0010911 | 0.036846 |
| 4 | Sheet8 | positional_unverified | positional_unverified_equal_counts | 750 | 0 | 0 | 0 | 0.00073516 | 0.0064609 |
| 5 | Sheet1 | positional_unverified | positional_unverified_equal_counts | 196 | 0 | 0 | 0 | 2.3677e-16 | 4.4409e-16 |
| 5 | Sheet2 | positional_unverified | positional_unverified_equal_counts | 306 | 0 | 0 | 0 | 0.00033911 | 0.035355 |
| 5 | Sheet3 | positional_unverified | positional_unverified_equal_counts | 339 | 0 | 0 | 0 | 1.6237e-05 | 0.0055042 |
| 5 | Sheet4 | positional_unverified | positional_unverified_equal_counts | 251 | 0 | 0 | 0 | 0.00059374 | 0.050733 |
| 5 | Sheet5 | positional_unverified | positional_unverified_equal_counts | 273 | 0 | 0 | 0 | 0.00029775 | 0.032831 |
| 5 | Sheet6 | positional_unverified | positional_unverified_equal_counts | 218 | 0 | 0 | 0 | 0.00029249 | 0.032258 |
| 5 | Sheet7 | positional_unverified | positional_unverified_equal_counts | 185 | 0 | 0 | 0 | 0.00031953 | 0.029833 |
| 5 | Sheet8 | positional_unverified | positional_unverified_equal_counts | 207 | 0 | 0 | 0 | 0.00034093 | 0.035647 |
| 6 | Sheet1 | capacity_match_diagnostic | unique_monotone_capacity_diagnostic | 807 | 67 | 60 | 141 | 2.2562e-16 | 4.4409e-16 |
| 6 | Sheet2 | capacity_match_diagnostic | unique_monotone_capacity_diagnostic | 1036 | 95 | 75 | 189 | 2.2204e-16 | 4.4409e-16 |
| 6 | Sheet3 | capacity_match_diagnostic | unique_monotone_capacity_diagnostic | 783 | 54 | 48 | 124 | 2.1496e-16 | 4.4409e-16 |
| 6 | Sheet4 | capacity_match_diagnostic | unique_monotone_capacity_diagnostic | 810 | 58 | 54 | 129 | 2.1081e-16 | 4.4409e-16 |
| 6 | Sheet5 | capacity_match_diagnostic | unique_monotone_capacity_diagnostic | 1107 | 93 | 82 | 180 | 2.2786e-16 | 4.4409e-16 |
| 6 | Sheet6 | capacity_match_diagnostic | unique_monotone_capacity_diagnostic | 909 | 83 | 61 | 153 | 2.1105e-16 | 4.4409e-16 |
| 6 | Sheet7 | capacity_match_diagnostic | unique_monotone_capacity_diagnostic | 798 | 76 | 45 | 136 | 1.9811e-16 | 4.4409e-16 |
| 6 | Sheet8 | capacity_match_diagnostic | unique_monotone_capacity_diagnostic | 879 | 91 | 64 | 163 | 6.1485e-10 | 5.4046e-07 |

Equal-count pairs are positional and unverified; label equality/near-equality is only a diagnostic. In unequal-count profiles, unique monotone capacity matches are diagnostics, while ambiguous rows stay unmatched. The alignment implementation was not altered. The benchmark has no independent cycle identity field in the inspected workbooks, so reliable cycle identity cannot be asserted.

## Prepared-MAT sampling and candidate phase coverage

Sampling is recomputed from every loaded prepared MAT cycle, not inferred from the 1 Hz release statement. The per-profile details are in `sampling_audit.csv`. Constant spacing within a prepared cycle does not establish that the workbook was generated from these points or resolve the release-to-MAT preprocessing gap.

| Scope | Raw cycles | Min samples/cycle | Max samples/cycle | Median Δt (min) | Min Δt (min) | Max Δt (min) | Nonuniform cycles | Max relative Δt deviation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all profiles | 27535 | 128 | 128 | 0.33927 | 0.091866 | 1.1849 | 0 | 1.0775e-13 |

Candidate phase coverage is computed only for cycles admitted by the unchanged alignment helper; it documents candidate interval availability, not benchmark phase labels.

| Group | Profiles | Matched cycles | Missing segments | Disjoint segments | Median selected samples/profile | Median duration/profile (min) |
| --- | --- | --- | --- | --- | --- | --- |
| CC | 47 | 19191 | 0 | 0 | 53 | 21.614 |
| dV | 47 | 19191 | 0 | 0 | 9 | 3.328 |
| CV | 47 | 19191 | 0 | 0 | 75 | 27.315 |
| dI | 47 | 19191 | 75 | 0 | 2 | 0.69552 |
| Charge | 47 | 19191 | 0 | 0 | 128 | 49.297 |

## Overall feature-wise error statistics

### Positional, unverified cohort (diagnostic only)

| Feature | Group | Valid | Invalid candidate | MAE | RMSE | MAPE % | MAPE n | Bias | Median |err| | Max |err| | Error q05 | Error median | Error q95 | Relative MAE % | Pearson r | Spearman ρ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CC_energy | CC | 19191 | 0 | 0.062367 | 0.075142 | 1.0932 | 19191 | -0.062313 | 0.060693 | 1.1018 | -0.12328 | -0.060693 | -0.0048708 | 1.0794 | 0.99682 | 0.99613 |
| CC_Q | CC | 19191 | 0 | 0.014885 | 0.018036 | 1.0133 | 19191 | -0.014866 | 0.014406 | 0.29717 | -0.029762 | -0.014406 | -0.00096595 | 1.0004 | 0.99747 | 0.99693 |
| CC_t_mean | CC | 19191 | 0 | 0.20905 | 1.6277 | 1.4314 | 19191 | 0.0037732 | 0.097501 | 29.446 | -0.2003 | -0.09648 | -0.005577 | 2.0042 | 0.92732 | 0.99852 |
| CC_V_mean | CC | 19191 | 0 | 0.0034056 | 0.0038855 | 0.087596 | 19191 | -0.0031525 | 0.0033086 | 0.015903 | -0.0063609 | -0.0032267 | -0.00012381 | 0.087653 | 0.99729 | 0.99653 |
| CC_T_mean | CC | 19191 | 0 | 0.020968 | 0.029869 | 0.074131 | 19191 | -0.016677 | 0.014319 | 0.17027 | -0.067903 | -0.011503 | 0.015716 | 0.075027 | 0.99996 | 0.99995 |
| CC_V_std | CC | 19191 | 0 | 0.0017058 | 0.0023812 | 1.1424 | 19191 | -0.00041988 | 0.001356 | 0.016982 | -0.0041581 | -0.00019987 | 0.002627 | 1.1437 | 0.98324 | 0.97961 |
| CC_T_std | CC | 19191 | 0 | 0.0099295 | 0.021621 | 0.77354 | 19191 | -0.0029771 | 0.0063641 | 0.71573 | -0.022907 | -0.0033087 | 0.020228 | 0.63301 | 0.99968 | 0.99975 |
| CC_V_skewness | CC | 19191 | 0 | 0.085399 | 0.099794 | 83.403 | 19129 | -0.071448 | 0.079193 | 0.64616 | -0.1763 | -0.075138 | 0.043755 | 30.301 | 0.95295 | 0.93728 |
| CC_T_skewness | CC | 19191 | 0 | 0.019534 | 0.091917 | 6.5771 | 19161 | 0.01288 | 0.0095178 | 3.4283 | -0.015542 | 0.0073211 | 0.048936 | 3.4622 | 0.99258 | 0.99514 |
| CC_V_kurtosis | CC | 19191 | 0 | 0.15941 | 0.20798 | 6.09 | 19191 | 0.13388 | 0.13412 | 1.9478 | -0.083254 | 0.12262 | 0.41681 | 6.4008 | 0.92157 | 0.89824 |
| CC_T_kurtosis | CC | 19191 | 0 | 0.052871 | 0.33497 | 2.0514 | 19191 | 0.021084 | 0.013084 | 11.287 | -0.047105 | -0.0078955 | 0.13613 | 2.1859 | 0.96692 | 0.98101 |
| CC_CCCT | CC | 19191 | 0 | 0.41793 | 3.2562 | 1.4306 | 19191 | 0.0077281 | 0.19494 | 58.9 | -0.39942 | -0.19292 | -0.010854 | 2.0034 | 0.92728 | 0.99853 |
| CC_entropy | CC | 19191 | 0 | 5.0564 | 5.0568 | 66.64 | 19191 | -5.0564 | 5.0615 | 5.3268 | -5.1495 | -5.0615 | -4.9378 | 66.633 | 0.91348 | 0.88481 |
| dV_energy | dV | 19191 | 0 | 0.0058099 | 0.0086482 | 0.58018 | 19191 | 0.0055918 | 0.0054008 | 0.32544 | 0.00099084 | 0.0053548 | 0.010646 | 0.58498 | 0.99925 | 0.99939 |
| dV_Q | dV | 19191 | 0 | 0.0014719 | 0.0021928 | 0.58006 | 19191 | 0.0014162 | 0.0013675 | 0.082578 | 0.00025049 | 0.001357 | 0.0026984 | 0.58484 | 0.99925 | 0.9994 |
| dV_t_mean | dV | 19191 | 0 | 0.024822 | 0.20345 | 1.0942 | 19191 | 0.024214 | 0.009417 | 2.8021 | 0.0014288 | 0.009314 | 0.017155 | 1.4614 | 0.86797 | 0.99863 |
| dV_V_mean | dV | 19191 | 0 | 0.00011444 | 0.00019143 | 0.0028998 | 19191 | 1.2058e-05 | 8.9681e-05 | 0.0060325 | -0.00021063 | 5.9853e-06 | 0.00022947 | 0.0028999 | 0.97145 | 0.9764 |
| dV_T_mean | dV | 19191 | 0 | 0.0068634 | 0.016053 | 0.024051 | 19191 | -0.00073253 | 0.0054792 | 0.978 | -0.014442 | -0.00052124 | 0.012899 | 0.023948 | 0.99999 | 0.99999 |
| dV_V_std | dV | 19191 | 0 | 0.00013031 | 0.00015032 | 0.45272 | 19191 | 0.0001262 | 0.00012552 | 0.00072667 | 1.5137e-06 | 0.00012467 | 0.00025446 | 0.45208 | 0.81436 | 0.76883 |
| dV_T_std | dV | 19191 | 0 | 0.0075556 | 0.013602 | 5.9006 | 19135 | -0.001315 | 0.0057079 | 0.28375 | -0.015672 | -0.0020904 | 0.012587 | 3.0709 | 0.99797 | 0.99602 |
| dV_V_skewness | dV | 19191 | 0 | 0.002431 | 0.006251 | 2.4005 | 19190 | 0.00015929 | 0.0015423 | 0.24647 | -0.0040883 | 0.0004374 | 0.0046169 | 1.5687 | 0.98382 | 0.9934 |
| dV_T_skewness | dV | 19191 | 0 | 0.1553 | 0.4888 | 193.82 | 19097 | 0.013479 | 0.067065 | 15.768 | -0.28211 | -0.0010348 | 0.30605 | 56.393 | 0.61932 | 0.86053 |
| dV_V_kurtosis | dV | 19191 | 0 | 0.0022427 | 0.0035185 | 0.12266 | 19191 | 0.00023242 | 0.0015831 | 0.043829 | -0.0041597 | 0.0002567 | 0.0046175 | 0.12283 | 0.9753 | 0.97318 |
| dV_T_kurtosis | dV | 19191 | 0 | 0.46388 | 4.895 | 17.114 | 19191 | -0.0032348 | 0.093874 | 253.44 | -0.64277 | -0.03908 | 0.34938 | 21.01 | 0.11096 | 0.8001 |
| dV_dV_devide_dt | dV | 19191 | 0 | 6.8697e-05 | 0.00043291 | 0.27789 | 19191 | 6.162e-06 | 3.3897e-05 | 0.027239 | -6.4541e-05 | 1.4418e-05 | 0.00011758 | 0.23199 | 0.99057 | 0.99925 |
| dV_entropy | dV | 19191 | 0 | 4.762 | 4.7636 | 63.268 | 19191 | -4.762 | 4.78 | 5.1638 | -4.908 | -4.78 | -4.5192 | 63.278 | 0.39543 | 0.2034 |
| CV_energy | CV | 19191 | 0 | 0.036161 | 0.043174 | 2.4173 | 19191 | -0.035009 | 0.038181 | 0.70752 | -0.068635 | -0.03809 | 0.0026328 | 2.4086 | 0.99207 | 0.98958 |
| CV_Q | CV | 19191 | 0 | 0.0086096 | 0.010279 | 2.4172 | 19191 | -0.0083351 | 0.0090895 | 0.16844 | -0.01634 | -0.0090687 | 0.0006278 | 2.4086 | 0.99207 | 0.98958 |
| CV_t_mean | CV | 19191 | 0 | 0.070599 | 0.14788 | 0.48752 | 19191 | -0.058481 | 0.069022 | 6.7755 | -0.11874 | -0.068432 | -0.00078667 | 0.49541 | 0.99792 | 0.99966 |
| CV_C_mean | CV | 19191 | 0 | 0.012394 | 0.018537 | 1.6676 | 19191 | -0.010378 | 0.01115 | 0.27038 | -0.024801 | -0.011095 | 0.0062989 | 1.6251 | 0.98888 | 0.985 |
| CV_T_mean | CV | 19191 | 0 | 0.017032 | 0.022514 | 0.06765 | 19191 | -0.015638 | 0.015862 | 0.5576 | -0.038042 | -0.015825 | 0.0056239 | 0.067757 | 0.99998 | 0.99998 |
| CV_C_std | CV | 19191 | 0 | 0.021799 | 0.026005 | 2.3759 | 19191 | -0.017523 | 0.020236 | 0.071601 | -0.047602 | -0.019661 | 0.01328 | 2.3625 | 0.99448 | 0.91013 |
| CV_T_std | CV | 19191 | 0 | 0.011471 | 0.020315 | 0.50677 | 19191 | -0.008712 | 0.0098648 | 0.96356 | -0.024951 | -0.0093937 | 0.0068296 | 0.47741 | 0.99974 | 0.99977 |
| CV_C_skewness | CV | 19191 | 0 | 0.018338 | 0.023443 | 0.93228 | 19191 | -0.014268 | 0.016431 | 1.0965 | -0.038504 | -0.015926 | 0.012661 | 0.90375 | 0.99678 | 0.99617 |
| CV_T_skewness | CV | 19191 | 0 | 0.011634 | 0.054984 | 1.6018 | 19191 | 0.0040167 | 0.0072834 | 1.3865 | -0.004783 | 0.0068653 | 0.0172 | 1.6086 | 0.91884 | 0.98249 |
| CV_C_kurtosis | CV | 19191 | 0 | 0.089042 | 0.11015 | 1.3849 | 19191 | -0.071052 | 0.082866 | 3.8233 | -0.18004 | -0.081882 | 0.057224 | 1.3296 | 0.99687 | 0.99583 |
| CV_T_kurtosis | CV | 19191 | 0 | 0.019717 | 0.046974 | 0.90584 | 19191 | 0.015808 | 0.015832 | 2.8166 | -0.011229 | 0.01489 | 0.039637 | 0.91864 | 0.97726 | 0.99342 |
| CV_CVCT | CV | 19191 | 0 | 0.13344 | 0.29047 | 0.46002 | 19191 | -0.10914 | 0.12995 | 13.562 | -0.22754 | -0.12887 | 0.0049944 | 0.46831 | 0.99795 | 0.99967 |
| CV_entropy | CV | 19191 | 0 | 4.6748 | 4.6755 | 72.122 | 19191 | -4.6748 | 4.7004 | 4.9418 | -4.7619 | -4.7004 | -4.527 | 72.084 | 0.98977 | 0.98848 |
| dI_energy | dI | 19116 | 75 | 0.0011928 | 0.0033389 | 2.7426 | 19116 | 0.0010665 | 0.00094857 | 0.11308 | -9.2024e-06 | 0.00094415 | 0.001909 | 2.591 | 0.9384 | 0.99 |
| dI_Q | dI | 19116 | 75 | 0.000284 | 0.00079498 | 2.7426 | 19116 | 0.00025393 | 0.00022582 | 0.026925 | -2.2222e-06 | 0.00022479 | 0.00045451 | 2.591 | 0.93839 | 0.99 |
| dI_t_mean | dI | 19116 | 75 | 0.0089589 | 0.025116 | 2.7342 | 19116 | 0.0079984 | 0.0071247 | 0.84523 | -0.00015671 | 0.0070889 | 0.014346 | 2.5835 | 0.93855 | 0.9899 |
| dI_C_mean | dI | 19116 | 75 | 0.00059581 | 0.0020227 | 0.062823 | 19116 | -3.2185e-05 | 0.00042216 | 0.048897 | -0.00095453 | 5.5957e-05 | 0.0010676 | 0.062826 | 0.35034 | 0.79297 |
| dI_T_mean | dI | 19116 | 75 | 0.015556 | 0.063713 | 0.057678 | 19116 | -0.00049023 | 0.013055 | 8.4138 | -0.031572 | -0.00095731 | 0.029778 | 0.057376 | 0.99971 | 0.99986 |
| dI_C_std | dI | 19116 | 75 | 0.00034086 | 0.001267 | 1.1673 | 19116 | -1.0249e-05 | 0.00023534 | 0.031135 | -0.00053213 | 3.3792e-05 | 0.00059863 | 1.179 | -0.1761 | 0.095253 |
| dI_T_std | dI | 19116 | 75 | 0.012653 | 0.015904 | 12.254 | 19067 | -0.0052776 | 0.010833 | 0.15482 | -0.029217 | -0.0055052 | 0.019179 | 11.171 | 0.92827 | 0.89555 |
| dI_C_skewness | dI | 19116 | 75 | 0.009785 | 0.020791 | 22.458 | 19098 | -0.00014255 | 0.0066378 | 0.5504 | -0.018613 | 0.00031689 | 0.019188 | 14.599 | 0.87632 | 0.92552 |
| dI_T_skewness | dI | 19116 | 75 | 0.24392 | 0.3634 | 231.13 | 18865 | 0.00061551 | 0.19583 | 15.804 | -0.4896 | 0.0016434 | 0.48842 | 96.735 | 0.38894 | 0.44888 |
| dI_C_kurtosis | dI | 19116 | 75 | 0.012859 | 0.018536 | 0.71234 | 19116 | 0.002084 | 0.0097968 | 0.42067 | -0.025286 | 0.0019044 | 0.02966 | 0.71183 | 0.35062 | 0.37402 |
| dI_T_kurtosis | dI | 19116 | 75 | 0.34054 | 2.395 | 15.938 | 19116 | -0.14996 | 0.21989 | 252.19 | -0.80878 | -0.14251 | 0.31887 | 16.572 | 0.025484 | 0.34703 |
| dI_dI_devide_dt | dI | 19116 | 75 | 0.001358 | 0.0052763 | 0.87497 | 19116 | -0.00026879 | 0.00071653 | 0.10325 | -0.0021577 | -0.00031949 | 0.0015578 | 0.93113 | 0.98466 | 0.99418 |
| dI_entropy | dI | 19116 | 75 | 2.5844 | 2.5999 | 48.118 | 19116 | -2.5844 | 2.5901 | 3.5334 | -3.0187 | -2.5901 | -2.087 | 48.269 | -0.20316 | -0.089614 |
| Charge_energy | Charge | 19191 | 0 | 0.0068436 | 0.032 | 0.097422 | 19191 | -0.0067129 | 0.0010971 | 0.7433 | -0.036523 | -0.0010891 | 0.00054304 | 0.093924 | 0.9969 | 0.99815 |
| Charge_Q | Charge | 19191 | 0 | 0.0016747 | 0.0078352 | 0.093195 | 19191 | -0.00156 | 0.00015173 | 0.19076 | -0.01026 | -8.643e-05 | 0.00029738 | 0.09067 | 0.99755 | 0.99799 |
| Charge_t_mean | Charge | 19191 | 0 | 0.17174 | 2.2508 | 0.47185 | 19191 | 0.14078 | 0.0052766 | 39.147 | -0.06993 | -0.0047285 | 0.0048068 | 0.69675 | 0.89477 | 0.99942 |
| Charge_V_mean | Charge | 19191 | 0 | 0.001095 | 0.0012888 | 0.026952 | 19191 | -0.00081664 | 0.0010559 | 0.013176 | -0.0014161 | -0.0010292 | 0.00070267 | 0.02693 | 0.99964 | 0.99955 |
| Charge_C_mean | Charge | 19191 | 0 | 0.0016585 | 0.0034835 | 0.076132 | 19191 | -0.00023588 | 0.00090879 | 0.15053 | -0.0054506 | 1.2505e-05 | 0.0030455 | 0.07246 | 0.99995 | 0.9999 |
| Charge_T_mean | Charge | 19191 | 0 | 0.0077913 | 0.011647 | 0.029417 | 19191 | -0.0057776 | 0.0070888 | 0.55773 | -0.015941 | -0.00618 | 0.0082319 | 0.029645 | 0.99999 | 0.99999 |
| Charge_C_std | Charge | 19191 | 0 | 0.001028 | 0.0032941 | 0.056304 | 19191 | 0.00030847 | 0.00058939 | 0.098239 | -3.884e-05 | 0.00056482 | 0.0015103 | 0.052506 | 0.99997 | 0.99963 |
| Charge_V_std | Charge | 19191 | 0 | 0.002123 | 0.0023433 | 1.211 | 19191 | 0.0018029 | 0.0020658 | 0.013272 | -0.00072212 | 0.0020052 | 0.0034785 | 1.1689 | 0.99815 | 0.99789 |
| Charge_T_std | Charge | 19191 | 0 | 0.0082561 | 0.062495 | 0.33321 | 19191 | 0.0069823 | 0.0022958 | 1.5783 | -0.0033473 | 0.0015114 | 0.021191 | 0.32261 | 0.99725 | 0.99831 |
| Charge_C_skewness | Charge | 19191 | 0 | 0.0019553 | 0.0040555 | 1.6078 | 19114 | -0.00035734 | 0.0012222 | 0.13153 | -0.0034329 | -0.00085019 | 0.0052336 | 0.77145 | 0.99992 | 0.99992 |
| Charge_V_skewness | Charge | 19191 | 0 | 0.038396 | 0.049304 | 3.8286 | 19159 | -0.035092 | 0.033538 | 0.51042 | -0.091792 | -0.03256 | 0.0057165 | 3.8017 | 0.99669 | 0.99669 |
| Charge_T_skewness | Charge | 19191 | 0 | 0.0087759 | 0.054726 | 10.226 | 19087 | 0.0020295 | 0.0039916 | 1.459 | -0.0026042 | 0.003769 | 0.022421 | 4.1385 | 0.97999 | 0.99382 |
| Charge_C_kurtosis | Charge | 19191 | 0 | 0.0035549 | 0.02428 | 0.23327 | 19191 | 0.00061323 | 0.0006707 | 1.0075 | -0.0048511 | -0.0005693 | 0.0006596 | 0.29069 | 0.9908 | 0.99975 |
| Charge_V_kurtosis | Charge | 19191 | 0 | 0.21452 | 0.36704 | 7.0491 | 19191 | 0.19742 | 0.15089 | 9.0123 | -0.035668 | 0.14413 | 0.5871 | 8.0487 | 0.97444 | 0.98872 |
| Charge_T_kurtosis | Charge | 19191 | 0 | 0.016629 | 0.10659 | 0.91035 | 19191 | 0.013117 | 0.0023484 | 2.0431 | -0.0060143 | 0.00019424 | 0.045112 | 0.9876 | 0.9246 | 0.99344 |

### Highest relative MAE — diagnostic only

| Feature | Relative MAE % | MAE | RMSE | Bias | Valid n |
| --- | --- | --- | --- | --- | --- |
| dI_T_skewness | 96.735 | 0.24392 | 0.3634 | 0.00061551 | 19116 |
| CV_entropy | 72.084 | 4.6748 | 4.6755 | -4.6748 | 19191 |
| CC_entropy | 66.633 | 5.0564 | 5.0568 | -5.0564 | 19191 |
| dV_entropy | 63.278 | 4.762 | 4.7636 | -4.762 | 19191 |
| dV_T_skewness | 56.393 | 0.1553 | 0.4888 | 0.013479 | 19191 |
| dI_entropy | 48.269 | 2.5844 | 2.5999 | -2.5844 | 19116 |
| CC_V_skewness | 30.301 | 0.085399 | 0.099794 | -0.071448 | 19191 |
| dV_T_kurtosis | 21.01 | 0.46388 | 4.895 | -0.0032348 | 19191 |
| dI_T_kurtosis | 16.572 | 0.34054 | 2.395 | -0.14996 | 19116 |
| dI_C_skewness | 14.599 | 0.009785 | 0.020791 | -0.00014255 | 19116 |

### Lowest relative MAE — diagnostic only

| Feature | Relative MAE % | MAE | RMSE | Bias | Valid n |
| --- | --- | --- | --- | --- | --- |
| dV_V_mean | 0.0028999 | 0.00011444 | 0.00019143 | 1.2058e-05 | 19191 |
| dV_T_mean | 0.023948 | 0.0068634 | 0.016053 | -0.00073253 | 19191 |
| Charge_V_mean | 0.02693 | 0.001095 | 0.0012888 | -0.00081664 | 19191 |
| Charge_T_mean | 0.029645 | 0.0077913 | 0.011647 | -0.0057776 | 19191 |
| Charge_C_std | 0.052506 | 0.001028 | 0.0032941 | 0.00030847 | 19191 |
| dI_T_mean | 0.057376 | 0.015556 | 0.063713 | -0.00049023 | 19116 |
| dI_C_mean | 0.062826 | 0.00059581 | 0.0020227 | -3.2185e-05 | 19116 |
| CV_T_mean | 0.067757 | 0.017032 | 0.022514 | -0.015638 | 19191 |
| Charge_C_mean | 0.07246 | 0.0016585 | 0.0034835 | -0.00023588 | 19191 |
| CC_T_mean | 0.075027 | 0.020968 | 0.029869 | -0.016677 | 19191 |

Low relative error is not formula verification; relative error is scale-normalized and cannot neutralize alignment uncertainty.

## Feature-group findings

| Group | Features | Median feature relative MAE % | Median relative bias % | Valid n min | Valid n max |
| --- | --- | --- | --- | --- | --- |
| CC | 13 | 2.0034 | -0.081139 | 19191 | 19191 |
| dV | 13 | 0.58498 | 0.020809 | 19191 | 19191 |
| CV | 13 | 1.3296 | -0.70315 | 19191 | 19191 |
| dI | 13 | 2.591 | -0.0033938 | 19116 | 19116 |
| Charge | 15 | 0.32261 | 0.015755 | 19191 | 19191 |

The group median relative MAE summarizes per-feature ratios; it does not pool unlike physical units. Individual features must be interpreted using their own units and near-zero policy.

## Batch, profile, and cycle-range findings

Machine-readable outputs contain the complete feature × batch, feature × profile, and feature × within-profile cycle-decile tables. They are split by positional versus capacity-diagnostic cohort. Profile/cycle clustering is descriptive, not causal.

### Largest positional profile relative errors

| Batch | Profile | Feature | Relative MAE % | MAE | Bias | Valid n |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | Sheet2 | dI_T_skewness | 116.48 | 0.15938 | 0.014641 | 291 |
| 5 | Sheet7 | dI_T_skewness | 114.75 | 0.41108 | -0.09996 | 175 |
| 5 | Sheet4 | dI_T_skewness | 111.69 | 0.28059 | -0.0056252 | 240 |
| 3 | Sheet2 | dI_T_skewness | 108.53 | 0.26811 | 0.029447 | 551 |
| 2 | Sheet8 | CC_V_skewness | 107.21 | 0.13591 | -0.13591 | 269 |
| 2 | Sheet4 | dI_T_skewness | 106.34 | 0.2295 | -0.0065596 | 321 |
| 2 | Sheet1 | dI_T_skewness | 104.47 | 0.19816 | -0.010515 | 298 |
| 4 | Sheet5 | dI_T_skewness | 102.56 | 0.24879 | 0.0062315 | 738 |
| 1 | Sheet1 | dI_T_skewness | 102.47 | 0.22726 | -0.0036202 | 389 |
| 5 | Sheet2 | dI_T_skewness | 102.44 | 0.21735 | 0.026734 | 301 |
| 5 | Sheet6 | dI_T_skewness | 102.44 | 0.29602 | -0.00019384 | 206 |
| 3 | Sheet1 | dI_T_skewness | 102.18 | 0.24323 | 0.002896 | 591 |
| 5 | Sheet3 | dV_T_skewness | 101.05 | 0.2284 | -0.02551 | 339 |
| 1 | Sheet6 | dI_T_skewness | 100.68 | 0.30956 | 0.013972 | 407 |
| 5 | Sheet8 | dI_T_skewness | 100.44 | 0.32577 | 0.014529 | 196 |
| 2 | Sheet5 | dI_T_skewness | 100.18 | 0.19206 | 0.0078439 | 296 |
| 2 | Sheet13 | dI_T_skewness | 99.581 | 0.17172 | 0.010919 | 225 |
| 2 | Sheet7 | dI_T_skewness | 99.573 | 0.21335 | -0.016777 | 318 |
| 3 | Sheet6 | dI_T_skewness | 99.531 | 0.24111 | 0.0031431 | 541 |
| 5 | Sheet1 | dI_T_skewness | 98.591 | 0.37356 | 0.034272 | 191 |

### Cycle-decile errors for the 10 highest overall relative-MAE features

| Batch | Profile | Cycle decile | Feature | MAE | Bias | Valid n |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Sheet1 | D01 | CC_V_skewness | 0.038952 | -0.038952 | 39 |
| 1 | Sheet1 | D01 | CC_entropy | 5.0701 | -5.0701 | 39 |
| 1 | Sheet1 | D01 | dV_T_skewness | 0.13991 | 0.010399 | 39 |
| 1 | Sheet1 | D01 | dV_T_kurtosis | 0.19775 | -0.045469 | 39 |
| 1 | Sheet1 | D01 | dV_entropy | 4.7908 | -4.7908 | 39 |
| 1 | Sheet1 | D01 | CV_entropy | 4.7143 | -4.7143 | 39 |
| 1 | Sheet1 | D01 | dI_C_skewness | 0.017507 | -0.0021285 | 39 |
| 1 | Sheet1 | D01 | dI_T_skewness | 0.20847 | -0.04798 | 39 |
| 1 | Sheet1 | D01 | dI_T_kurtosis | 0.4068 | -0.32202 | 39 |
| 1 | Sheet1 | D01 | dI_entropy | 2.266 | -2.266 | 39 |
| 1 | Sheet1 | D02 | CC_V_skewness | 0.057359 | -0.057359 | 39 |
| 1 | Sheet1 | D02 | CC_entropy | 5.0826 | -5.0826 | 39 |
| 1 | Sheet1 | D02 | dV_T_skewness | 0.11186 | -0.046646 | 39 |
| 1 | Sheet1 | D02 | dV_T_kurtosis | 0.19702 | -0.040137 | 39 |
| 1 | Sheet1 | D02 | dV_entropy | 4.7707 | -4.7707 | 39 |
| 1 | Sheet1 | D02 | CV_entropy | 4.7328 | -4.7328 | 39 |
| 1 | Sheet1 | D02 | dI_C_skewness | 0.008972 | -3.6041e-05 | 39 |
| 1 | Sheet1 | D02 | dI_T_skewness | 0.18821 | 0.054032 | 39 |
| 1 | Sheet1 | D02 | dI_T_kurtosis | 0.20508 | -0.11696 | 39 |
| 1 | Sheet1 | D02 | dI_entropy | 2.5202 | -2.5202 | 39 |
| 1 | Sheet1 | D03 | CC_V_skewness | 0.071087 | -0.071087 | 39 |
| 1 | Sheet1 | D03 | CC_entropy | 5.0688 | -5.0688 | 39 |
| 1 | Sheet1 | D03 | dV_T_skewness | 0.14121 | -0.023197 | 39 |
| 1 | Sheet1 | D03 | dV_T_kurtosis | 0.15734 | 0.00095702 | 39 |
| 1 | Sheet1 | D03 | dV_entropy | 4.7724 | -4.7724 | 39 |
| 1 | Sheet1 | D03 | CV_entropy | 4.7367 | -4.7367 | 39 |
| 1 | Sheet1 | D03 | dI_C_skewness | 0.0081763 | 0.0011608 | 39 |
| 1 | Sheet1 | D03 | dI_T_skewness | 0.28799 | 0.036495 | 39 |
| 1 | Sheet1 | D03 | dI_T_kurtosis | 0.25135 | -0.18539 | 39 |
| 1 | Sheet1 | D03 | dI_entropy | 2.5732 | -2.5732 | 39 |
| 1 | Sheet1 | D04 | CC_V_skewness | 0.078816 | -0.078816 | 39 |
| 1 | Sheet1 | D04 | CC_entropy | 5.0594 | -5.0594 | 39 |
| 1 | Sheet1 | D04 | dV_T_skewness | 0.10792 | 0.028258 | 39 |
| 1 | Sheet1 | D04 | dV_T_kurtosis | 0.172 | -0.096107 | 39 |
| 1 | Sheet1 | D04 | dV_entropy | 4.7624 | -4.7624 | 39 |
| 1 | Sheet1 | D04 | CV_entropy | 4.7456 | -4.7456 | 39 |
| 1 | Sheet1 | D04 | dI_C_skewness | 0.0086954 | 0.0016542 | 39 |
| 1 | Sheet1 | D04 | dI_T_skewness | 0.27597 | -0.012638 | 39 |
| 1 | Sheet1 | D04 | dI_T_kurtosis | 0.3081 | -0.2052 | 39 |
| 1 | Sheet1 | D04 | dI_entropy | 2.5302 | -2.5302 | 39 |
| 1 | Sheet1 | D05 | CC_V_skewness | 0.085804 | -0.085804 | 39 |
| 1 | Sheet1 | D05 | CC_entropy | 5.0585 | -5.0585 | 39 |
| 1 | Sheet1 | D05 | dV_T_skewness | 0.13472 | -0.014176 | 39 |
| 1 | Sheet1 | D05 | dV_T_kurtosis | 0.21639 | 0.024643 | 39 |
| 1 | Sheet1 | D05 | dV_entropy | 4.7604 | -4.7604 | 39 |
| 1 | Sheet1 | D05 | CV_entropy | 4.7545 | -4.7545 | 39 |
| 1 | Sheet1 | D05 | dI_C_skewness | 0.0076308 | 0.00080027 | 39 |
| 1 | Sheet1 | D05 | dI_T_skewness | 0.21112 | 0.001627 | 39 |
| 1 | Sheet1 | D05 | dI_T_kurtosis | 0.32566 | -0.20307 | 39 |
| 1 | Sheet1 | D05 | dI_entropy | 2.4603 | -2.4603 | 39 |
| 1 | Sheet1 | D06 | CC_V_skewness | 0.085834 | -0.085834 | 39 |
| 1 | Sheet1 | D06 | CC_entropy | 5.0615 | -5.0615 | 39 |
| 1 | Sheet1 | D06 | dV_T_skewness | 0.085088 | -0.0027086 | 39 |
| 1 | Sheet1 | D06 | dV_T_kurtosis | 0.16117 | -0.12558 | 39 |
| 1 | Sheet1 | D06 | dV_entropy | 4.7822 | -4.7822 | 39 |
| 1 | Sheet1 | D06 | CV_entropy | 4.7372 | -4.7372 | 39 |
| 1 | Sheet1 | D06 | dI_C_skewness | 0.008276 | -0.00021961 | 39 |
| 1 | Sheet1 | D06 | dI_T_skewness | 0.23355 | -0.012785 | 39 |
| 1 | Sheet1 | D06 | dI_T_kurtosis | 0.30392 | -0.26162 | 39 |
| 1 | Sheet1 | D06 | dI_entropy | 2.5288 | -2.5288 | 39 |

## Root-cause evidence table

| ID | Classification | Suspected cause | Affected features | Evidence | Mechanism | Confidence | Cannot establish |
| --- | --- | --- | --- | --- | --- | --- | --- |
| alignment_identity | Confirmed observation | Cycle identity uncertainty | All 67; affects interpretation of every candidate-vs-workbook residual | 19,191 equal-count pairs are positional and unverified; 7,129 batch-6 matches are capacity-label diagnostics; 489 workbook rows are ambiguous (subset of 617 unmatched workbook rows). | A wrong cycle-to-row pairing can create apparent feature error or hide real error. | High for uncertainty; no cycle identity ground truth is available. | Which residuals are caused by row identity rather than formula/segment differences. |
| candidate_phase_rules | Evidence-supported explanation | Candidate phase boundary and segmentation conventions | CC and dV families directly; CV and dI boundary-dependent features | The code uses an adaptive CC plateau, CV first 4.199 V crossing, dV 3.9–4.0 V, and dI 1.0–0.9 A. The author helper only documents a fixed 3.9 A CC selector and V≥4.199 V CV selector; it does not connect those rules to workbook generation. 52 feature sensitivity rows compare the fixed-CC selector against baseline. | Changing segment endpoints changes durations, integrals, elapsed-time statistics, and all within-segment statistics. | High that implementations differ in assumptions; low that this explains any specific workbook residual. | Original workbook phase thresholds, disconnected-run handling, or boundary inclusion. |
| entropy_proxy | Confirmed observation | Unknown original entropy definition versus diagnostic histogram proxy | CC_entropy, dV_entropy, CV_entropy, dI_entropy | All four entropy definitions remain unknown. The candidate uses a 16-bin equal-width histogram with natural logarithms; 4 positional feature summaries retain that proxy label. Sensitivity outputs include 8/32 bins, bits, and normalized entropy as diagnostics only. | Signal choice, estimator, bin edges/count, and logarithm base directly determine entropy scale and value. | High that the candidate proxy is not source-verified; no attribution of the mismatch mechanism to any original formula. | Whether Excel entropy uses histogram entropy, another entropy estimator, another signal, or another normalization. |
| coarse_prepared_sampling | Evidence-supported explanation | Prepared-cycle sampling and preprocessing | All phase-dependent features; strongest potential sensitivity for narrow dV/dI windows and derivatives | Prepared MAT traces have 128 samples per cycle and measured time intervals from about 0.092 to 1.185 minutes; the dataset release states 1 Hz acquisition. The transformation between these representations is undocumented. | Sparse prepared points can make threshold crossings, endpoint slopes, integrals, and moments sensitive to interpolation and sampling convention. | High for observed representation mismatch; medium for likely sensitivity; low for attributing particular residuals. | Whether workbook features were calculated from the original 1 Hz stream or from the prepared 128-point traces. |
| statistics_conventions | Plausible hypothesis | Time weighting and statistical estimator conventions | Mean/std/skewness/kurtosis and elapsed-time features across CC, dV, CV, dI, Charge | Candidate moments use a 257-point uniform-time interpolation grid and population/biased Pearson moments. The sensitivity CSV reports native-sample and alternative statistical-convention errors for the same paired observations. | Equal weighting of interpolated times differs from equal weighting of recorded samples when intervals/segments differ; ddof, bias correction, and excess/Pearson conventions alter moments. | Medium as a general mechanism; feature-specific evidence is in the sensitivity output and does not identify workbook convention. | The original sampling weights or statistical library/conventions. |
| outlier_concentration | Confirmed observation | Concentration of residuals in feature/profile subsets | dI_T_skewness, CV_entropy, CC_entropy, dV_entropy, dV_T_skewness, dI_entropy, CC_V_skewness, dV_T_kurtosis, dI_T_kurtosis, dI_C_skewness | Top positional relative-MAE feature is dI_T_skewness (96.74%, n=19116) | Report profile, batch, and cycle-decile tables show whether aggregate errors are broadly distributed or concentrated. | High for descriptive concentration; low for causal interpretation. | Whether clustering by a batch/profile characteristic is causal or an alignment artifact. |
| invalid_candidate_segments | Confirmed observation | Candidate intervals unavailable or degenerate | Features whose candidate segment cannot be formed (especially dV/dI and phase-duration features) | Across 67 feature accumulators in the positional cohort there are 975 candidate-invalid feature observations. | Missing threshold crossings or disjoint/missing intervals prevent feature calculation; these values are excluded rather than imputed. | High for candidate invalid count; not evidence that the benchmark row is invalid. | Whether corresponding workbook features use different windows or an alternative fallback. |

## Sensitivity experiments

Every variant was declared before comparing its benchmark error and is reported, not selected. No threshold, offset, coefficient, or correction was fitted to workbook values. Segment-changing sensitivity rows use the same preserved alignment pairs. Results are differences in candidate MAE from the baseline candidate on the same cohort; they are not evidence of original-formula recovery.

| Cohort | Variant | Feature | Baseline MAE | Variant MAE | Δ relative MAE (percentage points) | Δ MAE (feature units) | Valid n | Evidence class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| positional_unverified | time_seconds_interpretation | dI_t_mean | 0.0089589 | 20.94 | 6035.8 | 20.931 | 19116 | unit-scale diagnostic |
| positional_unverified | time_seconds_interpretation | dV_t_mean | 0.024822 | 101.67 | 5984.1 | 101.64 | 19191 | unit-scale diagnostic |
| positional_unverified | time_seconds_interpretation | Charge_t_mean | 0.17174 | 1462.7 | 5933.6 | 1462.5 | 19191 | unit-scale diagnostic |
| positional_unverified | time_seconds_interpretation | CC_CCCT | 0.41793 | 1231.3 | 5900.2 | 1230.8 | 19191 | unit-scale diagnostic |
| positional_unverified | time_seconds_interpretation | CC_t_mean | 0.20905 | 615.63 | 5900.2 | 615.42 | 19191 | unit-scale diagnostic |
| positional_unverified | time_seconds_interpretation | CV_CVCT | 0.13344 | 1674.5 | 5876.5 | 1674.4 | 19191 | unit-scale diagnostic |
| positional_unverified | time_seconds_interpretation | CV_t_mean | 0.070599 | 837.27 | 5874.9 | 837.2 | 19191 | unit-scale diagnostic |
| positional_unverified | native_sample_statistics | dI_C_skewness | 0.009785 | 0.18789 | 265.73 | 0.1781 | 19116 | candidate convention comparison |
| positional_unverified | fisher_excess_kurtosis | Charge_C_kurtosis | 0.0035549 | 3.0107 | 245.91 | 3.0072 | 19191 | statistical convention comparison |
| positional_unverified | fisher_excess_kurtosis | Charge_T_kurtosis | 0.016629 | 2.9889 | 176.53 | 2.9723 | 19191 | statistical convention comparison |
| positional_unverified | fisher_excess_kurtosis | dI_C_kurtosis | 0.012859 | 2.9977 | 165.23 | 2.9849 | 19116 | statistical convention comparison |
| positional_unverified | fisher_excess_kurtosis | dV_V_kurtosis | 0.0022427 | 2.9992 | 164.14 | 2.997 | 19191 | statistical convention comparison |
| positional_unverified | fisher_excess_kurtosis | dI_T_kurtosis | 0.34054 | 3.1999 | 139.15 | 2.8593 | 19116 | statistical convention comparison |
| positional_unverified | fisher_excess_kurtosis | CV_T_kurtosis | 0.019717 | 2.977 | 137.78 | 2.9573 | 19191 | statistical convention comparison |
| positional_unverified | fisher_excess_kurtosis | dV_T_kurtosis | 0.46388 | 3.2826 | 127.67 | 2.8188 | 19191 | statistical convention comparison |
| positional_unverified | fisher_excess_kurtosis | CC_T_kurtosis | 0.052871 | 2.9815 | 121.08 | 2.9286 | 19191 | statistical convention comparison |
| positional_unverified | fisher_excess_kurtosis | CC_V_kurtosis | 0.15941 | 2.8498 | 108.03 | 2.6904 | 19191 | statistical convention comparison |
| positional_unverified | time_seconds_interpretation | Charge_Q | 0.0016747 | 1.8162 | 98.244 | 1.8146 | 19191 | unit-scale diagnostic |
| positional_unverified | time_seconds_interpretation | Charge_energy | 0.0068436 | 7.165 | 98.241 | 7.1581 | 19191 | unit-scale diagnostic |
| positional_unverified | time_seconds_interpretation | dV_dV_devide_dt | 6.8697e-05 | 0.029119 | 98.101 | 0.02905 | 19191 | unit-scale diagnostic |

Fixed sensitivity variants include: documented fixed-current versus adaptive CC selector; native versus uniform-time statistics; observed-point versus interpolated endpoints; left/right rectangles versus trapezoids; sample standard deviation; adjusted skewness; Fisher/excess kurtosis; least-squares versus endpoint derivative; 8/32 bins, log2, and normalized entropy; and a factor-of-60 time-unit diagnostic. Entropy variants are proxy-only. The time-unit scenario is deliberately a diagnostic counterfactual, not an endorsed unit reinterpretation.

No arbitrary dV/dI threshold perturbation was run: the original ranges are unknown and no defensible source-backed range is available. The only phase sensitivity uses the documented author helper selector as a distinct, clearly labeled option.

## Confirmed observations, unresolved questions, and limitations

- **Confirmed observation:** workbook-value differences exist under the current candidate definitions in each reported cohort; these are benchmark mismatches, not proof the extractor code is incorrect or that the workbook is correct.
- **Confirmed observation:** the four entropy definitions are unknown and candidate entropy values are histogram proxies.
- **Confirmed observation:** alignment is unverified; ambiguous and unmatched workbook rows are excluded, and all remaining comparisons are still diagnostic.
- **Evidence-supported explanation:** the candidate uses explicit segmentation, interpolation, and moment conventions. The source does not establish that the workbook uses these conventions.
- **Unresolved:** cycle identity for equal-count positional profiles; correctness of batch-6 capacity matches; original signal preprocessing and workbook formulas; whether the workbook was computed from 1 Hz source data or 128-point prepared MAT traces; source statistical weighting; exact phase thresholds; derivative and entropy definitions.
- **Not investigated:** arbitrary threshold fitting, learned corrections, and any attempt to optimize candidate settings against workbook values.

## Generated artifacts

- `feature_error.csv`: overall feature summaries split by alignment cohort.
- `batch_error.csv`, `profile_error.csv`, `cycle_decile_error.csv`: scoped summaries.
- `cycle_wise_diagnostic_errors.csv.gz`: compressed long-form errors for all pairs retained by the existing alignment helper; every row carries its unverified/diagnostic cohort.
- `cycle_wise_identity_verified_errors.csv`: header-only because no identity-verified matched observations exist.
- `alignment_audit.csv`: matched, ambiguous, and unmatched row/cycle accounting.
- `root_cause_evidence.csv` and `sensitivity_results.csv`: machine-readable evidence/hypotheses and controlled sensitivity results.
- `sampling_audit.csv` and `phase_coverage.csv`: measured prepared-MAT sampling and candidate interval availability.
- `top_relative_errors.png`: visualization.
- `profile_error_heatmap.png`: visualization.

No prior report, candidate extractor, segmentation implementation, alignment behavior, API, UI, metadata, or model code was modified.
