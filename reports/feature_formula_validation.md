# XJTU Handcrafted Feature Formula Validation

## Conclusion

**None of the 67 workbook formulas is source-verified.** The repository search did not locate the original feature-extraction implementation or feature-specific equations. All comparisons below are explicitly candidate approximations; matching workbook values, where seen, does not establish provenance or correctness. Every feature has the status: **"Original formula implementation not located; candidate approximation only."**

The final run covers all six batches and all 55 workbook/raw-data profiles (batch 2 has 15 sheets; each other batch has 8). It pairs 26,726 cycle rows, with 211 unmatched batch-6 workbook rows excluded. Candidate performance varies considerably by feature, and some per-cycle errors are large even where aggregate MAE is small.

## Repository evidence and provenance

- The 67 workbook columns are in `reference/SOHbenchmark/data/XJTU/handcraft_features/batch-1_features.xlsx` through `batch-6_features.xlsx`; corresponding raw charging traces are in `reference/SOHbenchmark/data/XJTU/charge/batch-*.mat`.
- [`feature_metadata.json`](../feature_metadata.json) and [`frontend/src/data/feature_metadata.json`](../frontend/src/data/feature_metadata.json) enumerate features but do not provide usable original formula definitions. The feature API consumes metadata; it is not an extractor.
- [`XJTUBatteryClass.py`](../temp_preprocessing_source/XJTUBatteryClass.py) documents a CC selector (`current >= 3.9 A` intersected with `voltage <= 4.199 V`, or a voltage sub-range intersected with the current threshold) and a CV selector (`voltage >= 4.199 V`, or an optional current range). It also includes IC-curve helpers. It does **not** implement the 67 workbook features. The adaptive CC rule used in this validation is not identical to its fixed 3.9 A condition.
- [`XJTU_loader.py`](../temp_sohbenchmark/dataloader/XJTU_loader.py) reads raw charge cycles and prepared workbook features; it does not calculate the handcrafted columns. Its raw-data parser expects 128 samples per cycle.
- The repository copy of the benchmark paper, *Open access dataset, code library and deep learning benchmark for state-of-health estimation of lithium-ion batteries* (Wang et al.), has the "Appendix B. Feature engineering" heading in [`appendix_extracted.txt`](../reference/SOHbenchmark/appendix_extracted.txt), but the inspected extracted text contains no feature-specific equations or source implementation. Other local notebooks, search results, and the bundled source/archive material did not yield an exact implementation of these named columns.
- [`check_skew.py`](../check_skew.py) is a limited batch-1 `CC_energy` check, not a 67-feature definition or validation suite. No original formulas or citations have been inferred from feature names.

## Data coverage and alignment

| Batch | Profiles | Paired rows | Unmatched workbook rows | Mean absolute label difference | Maximum absolute label difference |
|---|---:|---:|---:|---:|---:|
| 1 | 8 | 3,211 | 0 | 0 | 0 |
| 2 | 15 | 3,727 | 0 | 0.000136303 | 0.0540000 |
| 3 | 8 | 4,608 | 0 | 0.0000100249 | 0.0130788 |
| 4 | 8 | 5,670 | 0 | 0.000853106 | 0.0402616 |
| 5 | 8 | 1,975 | 0 | 0.000269891 | 0.0507328 |
| 6 | 8 | 7,535 | 211 | 0.000000000130 | 0.000000540 |
| **Total** | **55** | **26,726** | **211** | - | - |

For batches 1-5, raw cycles and workbook rows have equal counts, so the script pairs them by cycle order; the label differences are diagnostics, not used to rearrange rows. In batch 6, raw-cycle count exceeds workbook-row count, so rows are matched monotonically by capacity label within `1e-6`; unmatched workbook rows are not scored. Capacity labels alone do not prove cycle identity: repeated/nearby capacities can make a label-based match ambiguous. The low batch-6 label residual therefore must not be interpreted as verified feature-row correspondence. In the equal-length batches, the small mean but sometimes large maximum label differences likewise warrant caution.

The metric `valid_pairs` is feature-specific: dV candidates were unavailable on 2 of the 26,726 paired rows, and dI candidates on 75 rows, because the inferred interval could not be formed. Those rows are reported as skipped, not assigned fabricated values. All other features have 26,726 scored pairs.

## Candidate segmentation and formulas

The raw cycle channels are relative time (minutes), voltage (V), current (A), and temperature (degC). The recordings have 128 samples per cycle, so inferred sub-phase intervals, especially narrow derivative windows, are coarse and resampling-sensitive. All boundaries below are candidate choices, not source-confirmed definitions.

| Group prefix | Candidate interval | Signal / segment interpretation | Evidence and assumptions |
|---|---|---|---|
| `CC` | Points satisfying `I >= 0.975 * percentile_95(I)` and `V <= 4.199 V`; interval is the envelope from first to last qualifying point, with threshold-crossing boundaries linearly interpolated. | Voltage/current constant-current-like charge. | Inspired by the local CC selector, but the adaptive current threshold and resulting interval envelope are validation assumptions; gaps inside the envelope are interpolated over. |
| `CV` | First rising crossing of `V = 4.199 V` through the final recorded charge time. | Voltage/current constant-voltage-like charge. | Voltage threshold appears in the local CV selector; first-crossing and endpoint conventions are candidate choices. |
| `dV` | Rising `3.9-4.0 V` window inside the candidate CC interval. | Voltage window / derivative candidate. | Window inferred from feature names and values; no local source defines it. Interpolate threshold crossings; if the recorded CC interval starts or ends inside the window, use that interval boundary. |
| `dI` | Falling `1.0-0.9 A` window inside the candidate CV interval. | Current window / derivative candidate. | Window inferred from feature names and values; no local source defines it. Some windows have too few raw points or do not occur. |
| `Charge` | First through last raw time in the cycle. | Complete recorded charge record. | Record endpoints are not independently validated against the workbook feature definition. |

For interval endpoints `t0,t1` (minutes), signals are linearly interpolated at boundaries. Integrals use the native time samples plus interpolated endpoints and trapezoidal integration:

- **Energy:** `integral(V(t)*I(t) dt) / 60` in Wh.
- **Charge:** `integral(I(t) dt) / 60` in Ah.
- **Elapsed-time mean:** arithmetic mean of `t - t0` on a 257-point uniform-time grid from `t0` through `t1`.
- **Duration (`CC_CCCT`, `CV_CVCT`):** `t1 - t0`.
- **Derivative features:** endpoint difference divided by candidate interval duration, e.g. `(V(t1)-V(t0))/(t1-t0)` for dV.
- **Signal statistics:** mean, population standard deviation (`ddof=0`), biased standardized third central moment (`m3/m2^(3/2)`), or Pearson kurtosis (`m4/m2^2`; normal reference 3) on the 257-point uniform-time grid. Feature suffix `V`, `C`, and `T` selects voltage, current, and temperature, respectively.
- **Entropy:** `-sum(p_i*ln(p_i))` (nats) for a 16-bin equal-width histogram of a proxy channel: voltage for CC/dV and current for CV/dI/Charge. Neither the original entropy signal nor estimator, bins, or log base was located; this is only a reproducible diagnostic proxy.

The feature table below applies these operations to each named workbook column. For example, `CC_V_std` is population standard deviation of voltage on the candidate CC interval; `dI_T_kurtosis` is Pearson kurtosis of temperature on the candidate dI interval. The operation key is expanded per feature in the table; the full equations and conventions are defined above. `Wh`, `Ah`, etc. are candidate units, not workbook metadata recovered from source.

## Per-feature results

MAE, RMSE, and maximum absolute error are in each feature's candidate unit. Relative error is `100 * MAE / mean(abs(workbook feature))`; it is a ratio of aggregate quantities, **not** the mean of per-cycle percentage errors. Worst-error rows/cycles are 1-based. These metrics compare candidates to workbook values and do not verify original formulas.

| Feature | Group / segment | Signal | Candidate operation | Unit | MAE | RMSE | Max abs. error | Rel. MAE (%) | Valid pairs | Worst-error profile; workbook row / raw cycle |
|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| `CC_energy` | CC: initial constant-current charge candidate | voltage and current | integral(V*I dt) / 60 | Wh | 0.0164571 | 0.054145 | 1.94562 | 0.345224 | 26726 | batch-6/Sheet8; 123 / 204 |
| `CC_Q` | CC: initial constant-current charge candidate | current and time | integral(I dt) / 60 | Ah | 0.00414595 | 0.0136655 | 0.481962 | 0.33941 | 26726 | batch-6/Sheet8; 123 / 204 |
| `CC_t_mean` | CC: initial constant-current charge candidate | elapsed time | mean(t - t0), 257-point grid | min | 0.102976 | 1.38859 | 29.6592 | 1.1697 | 26726 | batch-5/Sheet2; 13 / 13 |
| `CC_V_mean` | CC: initial constant-current charge candidate | voltage | mean(V) | V | 0.0011677 | 0.00348548 | 0.141474 | 0.029726 | 26726 | batch-6/Sheet8; 123 / 204 |
| `CC_T_mean` | CC: initial constant-current charge candidate | temperature | mean(T) | degC | 0.00700141 | 0.0469796 | 5.17592 | 0.0256916 | 26726 | batch-6/Sheet2; 721 / 779 |
| `CC_V_std` | CC: initial constant-current charge candidate | voltage | population_sd(V) | V | 0.00215675 | 0.00267285 | 0.0752639 | 1.63549 | 26726 | batch-6/Sheet8; 123 / 204 |
| `CC_T_std` | CC: initial constant-current charge candidate | temperature | population_sd(T) | degC | 0.00663713 | 0.0309859 | 2.98776 | 0.533076 | 26726 | batch-6/Sheet5; 1121 / 1202 |
| `CC_V_skewness` | CC: initial constant-current charge candidate | voltage | m3/m2^(3/2) (V) | dimensionless | 0.0551012 | 0.0799413 | 1.25103 | 22.1342 | 26726 | batch-6/Sheet8; 625 / 668 |
| `CC_T_skewness` | CC: initial constant-current charge candidate | temperature | m3/m2^(3/2) (T) | dimensionless | 0.0399007 | 0.313915 | 13.9408 | 7.53515 | 26726 | batch-6/Sheet4; 272 / 294 |
| `CC_V_kurtosis` | CC: initial constant-current charge candidate | voltage | m4/m2^2 (V) | dimensionless | 0.099652 | 0.152686 | 1.86817 | 4.34511 | 26726 | batch-1/Sheet2; 390 / 390 |
| `CC_T_kurtosis` | CC: initial constant-current charge candidate | temperature | m4/m2^2 (T) | dimensionless | 0.132972 | 1.76776 | 115.455 | 5.43955 | 26726 | batch-6/Sheet4; 272 / 294 |
| `CC_CCCT` | CC: initial constant-current charge candidate | time | t1 - t0 | min | 0.205701 | 2.77793 | 59.3264 | 1.16828 | 26726 | batch-5/Sheet2; 13 / 13 |
| `CC_entropy` | CC: initial constant-current charge candidate | voltage (proxy channel) | H16 = -sum(p_i*ln(p_i)) | nats | 5.08961 | 5.09023 | 5.60688 | 66.2069 | 26726 | batch-6/Sheet5; 1121 / 1202 |
| `dV_energy` | dV: candidate CC voltage window: 3.9-4.0 V | voltage and current | integral(V*I dt) / 60 | Wh | 0.00929089 | 0.0461568 | 0.945185 | 0.973898 | 26724 | batch-6/Sheet8; 625 / 668 |
| `dV_Q` | dV: candidate CC voltage window: 3.9-4.0 V | current and time | integral(I dt) / 60 | Ah | 0.00235384 | 0.0117144 | 0.239573 | 0.973726 | 26724 | batch-6/Sheet8; 625 / 668 |
| `dV_t_mean` | dV: candidate CC voltage window: 3.9-4.0 V | elapsed time | mean(t - t0), 257-point grid | min | 0.0191823 | 0.172993 | 2.80205 | 1.1073 | 26724 | batch-5/Sheet4; 2 / 2 |
| `dV_V_mean` | dV: candidate CC voltage window: 3.9-4.0 V | voltage | mean(V) | V | 0.000237909 | 0.00110497 | 0.0320106 | 0.0060283 | 26724 | batch-6/Sheet8; 625 / 668 |
| `dV_T_mean` | dV: candidate CC voltage window: 3.9-4.0 V | temperature | mean(T) | degC | 0.0066111 | 0.031449 | 4.46835 | 0.0239216 | 26724 | batch-6/Sheet8; 625 / 668 |
| `dV_V_std` | dV: candidate CC voltage window: 3.9-4.0 V | voltage | population_sd(V) | V | 0.000123584 | 0.0002034 | 0.0162042 | 0.428494 | 26724 | batch-6/Sheet8; 625 / 668 |
| `dV_T_std` | dV: candidate CC voltage window: 3.9-4.0 V | temperature | population_sd(T) | degC | 0.0074434 | 0.0183516 | 0.584155 | 3.12063 | 26724 | batch-6/Sheet2; 1102 / 1192 |
| `dV_V_skewness` | dV: candidate CC voltage window: 3.9-4.0 V | voltage | m3/m2^(3/2) (V) | dimensionless | 0.00709805 | 0.0454608 | 0.545697 | 4.8453 | 26724 | batch-6/Sheet2; 1104 / 1194 |
| `dV_T_skewness` | dV: candidate CC voltage window: 3.9-4.0 V | temperature | m3/m2^(3/2) (T) | dimensionless | 0.156913 | 0.508732 | 19.3106 | 54.2894 | 26724 | batch-6/Sheet1; 171 / 185 |
| `dV_V_kurtosis` | dV: candidate CC voltage window: 3.9-4.0 V | voltage | m4/m2^2 (V) | dimensionless | 0.00426372 | 0.0208766 | 0.287332 | 0.23387 | 26724 | batch-6/Sheet6; 2 / 4 |
| `dV_T_kurtosis` | dV: candidate CC voltage window: 3.9-4.0 V | temperature | m4/m2^2 (T) | dimensionless | 0.518311 | 4.85286 | 253.437 | 22.6311 | 26724 | batch-5/Sheet3; 5 / 5 |
| `dV_dV_devide_dt` | dV: candidate CC voltage window: 3.9-4.0 V | voltage and time | (V1 - V0) / (t1 - t0) | V/min | 0.000483539 | 0.00512614 | 0.483132 | 1.65819 | 26724 | batch-6/Sheet8; 625 / 668 |
| `dV_entropy` | dV: candidate CC voltage window: 3.9-4.0 V | voltage (proxy channel) | H16 = -sum(p_i*ln(p_i)) | nats | 4.78487 | 4.78665 | 5.16378 | 63.3869 | 26724 | batch-5/Sheet1; 15 / 15 |
| `CV_energy` | CV: candidate constant-voltage charge candidate | voltage and current | integral(V*I dt) / 60 | Wh | 0.0314965 | 0.0403459 | 1.37877 | 2.16348 | 26726 | batch-6/Sheet5; 1121 / 1202 |
| `CV_Q` | CV: candidate constant-voltage charge candidate | current and time | integral(I dt) / 60 | Ah | 0.007499 | 0.00960628 | 0.328575 | 2.16341 | 26726 | batch-6/Sheet5; 1121 / 1202 |
| `CV_t_mean` | CV: candidate constant-voltage charge candidate | elapsed time | mean(t - t0), 257-point grid | min | 0.0629957 | 0.134087 | 6.77555 | 0.448327 | 26726 | batch-5/Sheet1; 1 / 1 |
| `CV_C_mean` | CV: candidate constant-voltage charge candidate | current | mean(I) | A | 0.0105792 | 0.0176285 | 1.16126 | 1.41562 | 26726 | batch-6/Sheet5; 1121 / 1202 |
| `CV_T_mean` | CV: candidate constant-voltage charge candidate | temperature | mean(T) | degC | 0.015029 | 0.0980441 | 15.5315 | 0.0612171 | 26726 | batch-6/Sheet5; 1121 / 1202 |
| `CV_C_std` | CV: candidate constant-voltage charge candidate | current | population_sd(I) | A | 0.0184343 | 0.0235366 | 0.905932 | 2.08306 | 26726 | batch-6/Sheet5; 1121 / 1202 |
| `CV_T_std` | CV: candidate constant-voltage charge candidate | temperature | population_sd(T) | degC | 0.0097405 | 0.039288 | 5.42331 | 0.44509 | 26726 | batch-6/Sheet5; 1121 / 1202 |
| `CV_C_skewness` | CV: candidate constant-voltage charge candidate | current | m3/m2^(3/2) (I) | dimensionless | 0.0159756 | 0.022855 | 1.28264 | 0.817779 | 26726 | batch-6/Sheet5; 1121 / 1202 |
| `CV_T_skewness` | CV: candidate constant-voltage charge candidate | temperature | m3/m2^(3/2) (T) | dimensionless | 0.0135797 | 0.0820546 | 3.76948 | 1.95694 | 26726 | batch-6/Sheet2; 883 / 957 |
| `CV_C_kurtosis` | CV: candidate constant-voltage charge candidate | current | m4/m2^2 (I) | dimensionless | 0.0769993 | 0.101494 | 3.82326 | 1.21198 | 26726 | batch-1/Sheet2; 390 / 390 |
| `CV_T_kurtosis` | CV: candidate constant-voltage charge candidate | temperature | m4/m2^2 (T) | dimensionless | 0.0179476 | 0.126214 | 19.5024 | 0.854567 | 26726 | batch-6/Sheet2; 883 / 957 |
| `CV_CVCT` | CV: candidate constant-voltage charge candidate | time | t1 - t0 | min | 0.118179 | 0.263135 | 13.5619 | 0.420647 | 26726 | batch-5/Sheet1; 1 / 1 |
| `CV_entropy` | CV: candidate constant-voltage charge candidate | current (proxy channel) | H16 = -sum(p_i*ln(p_i)) | nats | 4.70151 | 4.70238 | 4.97186 | 71.789 | 26726 | batch-6/Sheet8; 123 / 204 |
| `dI_energy` | dI: candidate CV current window: 1.0-0.9 A | voltage and current | integral(V*I dt) / 60 | Wh | 0.00120629 | 0.00319315 | 0.113078 | 2.65703 | 26651 | batch-3/Sheet4; 512 / 512 |
| `dI_Q` | dI: candidate CV current window: 1.0-0.9 A | current and time | integral(I dt) / 60 | Ah | 0.000287215 | 0.000760284 | 0.0269253 | 2.65703 | 26651 | batch-3/Sheet4; 512 / 512 |
| `dI_t_mean` | dI: candidate CV current window: 1.0-0.9 A | elapsed time | mean(t - t0), 257-point grid | min | 0.00905893 | 0.0240256 | 0.845233 | 2.64928 | 26651 | batch-3/Sheet4; 512 / 512 |
| `dI_C_mean` | dI: candidate CV current window: 1.0-0.9 A | current | mean(I) | A | 0.000563953 | 0.00174555 | 0.0488971 | 0.0594594 | 26651 | batch-5/Sheet8; 8 / 8 |
| `dI_T_mean` | dI: candidate CV current window: 1.0-0.9 A | temperature | mean(T) | degC | 0.0157897 | 0.144625 | 21.5505 | 0.0599103 | 26651 | batch-6/Sheet5; 1121 / 1202 |
| `dI_C_std` | dI: candidate CV current window: 1.0-0.9 A | current | population_sd(I) | A | 0.000320943 | 0.00108783 | 0.0311349 | 1.11013 | 26651 | batch-5/Sheet8; 8 / 8 |
| `dI_T_std` | dI: candidate CV current window: 1.0-0.9 A | temperature | population_sd(T) | degC | 0.0122887 | 0.0156524 | 0.170183 | 11.9286 | 26651 | batch-6/Sheet5; 1121 / 1202 |
| `dI_C_skewness` | dI: candidate CV current window: 1.0-0.9 A | current | m3/m2^(3/2) (I) | dimensionless | 0.00917612 | 0.0192602 | 0.550399 | 14.8572 | 26651 | batch-3/Sheet4; 507 / 507 |
| `dI_T_skewness` | dI: candidate CV current window: 1.0-0.9 A | temperature | m3/m2^(3/2) (T) | dimensionless | 0.284329 | 0.49052 | 16.185 | 102.099 | 26651 | batch-6/Sheet6; 800 / 854 |
| `dI_C_kurtosis` | dI: candidate CV current window: 1.0-0.9 A | current | m4/m2^2 (I) | dimensionless | 0.0109459 | 0.016377 | 0.420673 | 0.606369 | 26651 | batch-3/Sheet4; 512 / 512 |
| `dI_T_kurtosis` | dI: candidate CV current window: 1.0-0.9 A | temperature | m4/m2^2 (T) | dimensionless | 0.490527 | 3.30351 | 253.268 | 23.1968 | 26651 | batch-6/Sheet6; 800 / 854 |
| `dI_dI_devide_dt` | dI: candidate CV current window: 1.0-0.9 A | current and time | (I1 - I0) / (t1 - t0) | A/min | 0.00120166 | 0.00487233 | 0.143496 | 0.816454 | 26651 | batch-6/Sheet8; 123 / 204 |
| `dI_entropy` | dI: candidate CV current window: 1.0-0.9 A | current (proxy channel) | H16 = -sum(p_i*ln(p_i)) | nats | 2.56818 | 2.58167 | 3.53344 | 48.1086 | 26651 | batch-3/Sheet7; 497 / 497 |
| `Charge_energy` | Charge: complete charge record | voltage and current | integral(V*I dt) / 60 | Wh | 0.00536438 | 0.0378981 | 2.35279 | 0.086164 | 26726 | batch-6/Sheet8; 123 / 204 |
| `Charge_Q` | Charge: complete charge record | current and time | integral(I dt) / 60 | Ah | 0.00131193 | 0.00929793 | 0.578894 | 0.0836292 | 26726 | batch-6/Sheet8; 123 / 204 |
| `Charge_t_mean` | Charge: complete charge record | elapsed time | mean(t - t0), 257-point grid | min | 0.127403 | 1.91058 | 39.1466 | 0.557996 | 26726 | batch-5/Sheet4; 3 / 3 |
| `Charge_V_mean` | Charge: complete charge record | voltage | mean(V) | V | 0.000928199 | 0.00146597 | 0.0617224 | 0.0226817 | 26726 | batch-6/Sheet8; 123 / 204 |
| `Charge_C_mean` | Charge: complete charge record | current | mean(I) | A | 0.00182846 | 0.00984789 | 1.25698 | 0.0893206 | 26726 | batch-6/Sheet5; 1121 / 1202 |
| `Charge_T_mean` | Charge: complete charge record | temperature | mean(T) | degC | 0.00701318 | 0.0727138 | 11.2514 | 0.0274607 | 26726 | batch-6/Sheet5; 1121 / 1202 |
| `Charge_C_std` | Charge: complete charge record | current | population_sd(I) | A | 0.00117173 | 0.0046882 | 0.380748 | 0.064694 | 26726 | batch-6/Sheet2; 721 / 779 |
| `Charge_V_std` | Charge: complete charge record | voltage | population_sd(V) | V | 0.00181338 | 0.00257732 | 0.0849438 | 1.17898 | 26726 | batch-6/Sheet8; 123 / 204 |
| `Charge_T_std` | Charge: complete charge record | temperature | population_sd(T) | degC | 0.00674305 | 0.0671345 | 6.31915 | 0.287682 | 26726 | batch-6/Sheet5; 1121 / 1202 |
| `Charge_C_skewness` | Charge: complete charge record | current | m3/m2^(3/2) (I) | dimensionless | 0.00256087 | 0.0135402 | 1.37253 | 0.699777 | 26726 | batch-6/Sheet8; 123 / 204 |
| `Charge_V_skewness` | Charge: complete charge record | voltage | m3/m2^(3/2) (V) | dimensionless | 0.0317986 | 0.0817928 | 8.0563 | 2.52402 | 26726 | batch-6/Sheet8; 123 / 204 |
| `Charge_T_skewness` | Charge: complete charge record | temperature | m3/m2^(3/2) (T) | dimensionless | 0.00911329 | 0.0652504 | 1.45896 | 4.70322 | 26726 | batch-5/Sheet5; 86 / 86 |
| `Charge_C_kurtosis` | Charge: complete charge record | current | m4/m2^2 (I) | dimensionless | 0.00517636 | 0.0370128 | 2.78952 | 0.379662 | 26726 | batch-6/Sheet8; 123 / 204 |
| `Charge_V_kurtosis` | Charge: complete charge record | voltage | m4/m2^2 (V) | dimensionless | 0.186022 | 0.797868 | 96.4598 | 5.50286 | 26726 | batch-6/Sheet8; 123 / 204 |
| `Charge_T_kurtosis` | Charge: complete charge record | temperature | m4/m2^2 (T) | dimensionless | 0.0151689 | 0.104511 | 2.04314 | 0.941949 | 26726 | batch-5/Sheet5; 19 / 19 |

All rows above carry the same status: **"Original formula implementation not located; candidate approximation only."** The machine-readable CSV also contains the source notes, formula status, batch-level rows, alignment diagnostics, and sensitivity metrics.

## Sensitivity checks and interpretation

- **Boundary/sampling:** The CSV compares the primary candidate against raw/native-grid statistics (`native_sampling_mae`) and observed-point rather than interpolated threshold boundaries (`point_boundary_mae`). Across features, native-grid MAE is higher than the primary candidate for 50/67 features (lower for 2); observed-point-boundary MAE is higher for 62/67 (lower for 2). Thus interpolation choices materially affect results; this does not establish that the primary interpolation is the original method.
- **Integration convention:** Left- and right-rectangle integrals are separately reported for all 10 energy/charge features. Each has lower MAE than trapezoidal integration for 4/10 features and higher MAE for 6/10; there is no universally superior alternative. The comparison uses the same candidate intervals and therefore does not resolve interval-definition uncertainty.
- **Statistical convention:** Sample-standard-deviation, adjusted-skewness, and bias-corrected Fisher/excess-kurtosis alternatives are in the CSV. For each of the 11 features with kurtosis, the bias-corrected Fisher alternative has higher MAE; the median alternative-to-primary MAE ratio is about 38.6. This is evidence that convention matters, not proof the workbook uses Pearson kurtosis. The original population/sample, bias, and excess/Pearson conventions remain unknown.
- **Entropy:** The 4 histogram-proxy entropy features have relative MAE from 48.1% to 71.8%; the proxy is notably not source-validated.
- **Outliers:** The worst relative MAE among the 67 features is 102.1% (`dI_T_skewness`). The largest absolute errors include 253.44 for `dV_T_kurtosis`, 253.27 for `dI_T_kurtosis`, 115.46 for `CC_T_kurtosis`, and 96.46 for `Charge_V_kurtosis`; units and scales differ, so these absolute values should not be pooled.
- **Segment mismatch example:** For batch-5 Sheet2 workbook row 13, candidate `CC_CCCT` is about 106.20 min versus workbook 46.875 min (absolute error about 59.33 min), while candidate CC energy/charge are much closer. This suggests duration/statistical group features may use different boundaries or conventions, or that row correspondence is uncertain; it is not appropriate to tune the formula silently to force a match.
- **Alignment warning example:** In batch-6 Sheet8 workbook row 625, the monotone capacity match pairs the row to raw cycle 668 within the label tolerance, but that pair has large discrepancies (for example, `Charge_energy` about 1.866 Wh candidate versus 3.951 Wh workbook). Nearby raw cycles can have slightly different capacities but more similar feature values. This makes capacity-only pairing insufficient evidence of the correct cycle identity; the residual may reflect alignment, formula, or both.

The per-feature MAEs are generally more informative than a pooled average because the 67 features mix Wh, Ah, minutes, volts, amps, degrees Celsius, and dimensionless statistics. Small aggregate errors for some integrals or means must not be presented as source verification, particularly with large maxima, segment ambiguity, and coarse 128-point traces.

## Reproduction

From the repository root, with the project's existing Python dependencies available:

```powershell
.venv\Scripts\python.exe scripts\validate_all_batches.py
.venv\Scripts\python.exe scripts\validate_features.py --batch 1 --battery-id 1
```

The all-batch command rewrites [`feature_validation_results.csv`](./feature_validation_results.csv) with 469 rows: 67 features for `overall` and each batch. The single-batch command reports candidate metrics for the selected batch/profile; use `--output <path>` to save its CSV. No metadata, API code, `main.py`, or teammate source files were changed, and no commits or pushes were made.
