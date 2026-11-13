# Independent Scientific Validation of Member 4 XJTU Candidates

## Status and scope

**Overall status: PARTIALLY VALIDATED.** Synthetic tests independently check the numerical behavior of all 67 implemented candidate outputs under their current definitions. This does **not** validate the original SOHbenchmark formulas, the author-intended feature windows, or workbook-row/cycle identity.

- 63 non-entropy candidates were checked against independently written synthetic calculations for their stated candidate operations.
- 4 entropy calculations were checked as 16-bin histogram proxies; their original intended feature definitions remain unknown.
- Original benchmark formulas verified: **0/67**.
- Authoritative workbook-row/cycle mappings: **0**.
- Predictive model or cell-wise/batch-wise predictive experiment: **not run**.

The synthetic oracle uses the extractor's selected candidate intervals as boundaries, then independently computes integration, moments, durations, rates, and histogram entropy. This checks arithmetic given those boundaries; it cannot establish that the candidate segmentation matches the original benchmark.

## Confirmed implementation defect corrected

The synthetic boundary tests exposed a CC interval construction bug: the code calculated interpolated threshold crossings but clamped the start to the first selected sample and the end to the last selected sample. This delayed starts and could reduce a valid positive-duration interval to zero length. [`segments.py`](../../scripts/member4_xjtu/segments.py) now uses the latest applicable interpolated crossing at entry and earliest at exit. Regression tests verify an analytically expected start at 0.5 min and voltage-cutoff end at 0.99 min. No feature equation was changed; actual candidate values and availability were recomputed after the segmentation correction.

## Implementation, units, signals, and candidate assumptions

The following table describes the implementation only. Formula status remains unverified for the original benchmark.

| Feature | Group | Current candidate expression | Signal(s) | Output unit | Candidate segment | Assumptions / provenance status |
|---|---|---|---|---|---|---|
| CC_energy | CC | Trapezoidal integral of V(t)*I(t), with minutes converted to hours. | voltage and current | Wh | constant-current-like charge candidate | Workbook formula and exact segment convention remain unverified. Current sign, integration convention, and interval boundaries are not source-confirmed. |
| CC_Q | CC | Trapezoidal integral of I(t), with minutes converted to hours. | current and time | Ah | constant-current-like charge candidate | Workbook formula and exact segment convention remain unverified. Current sign, integration convention, and interval boundaries are not source-confirmed. |
| CC_t_mean | CC | Arithmetic mean of elapsed time on a 257-point uniform-time interpolation grid. | elapsed time | min | constant-current-like charge candidate | Workbook formula and exact segment convention remain unverified. Grid and time origin are candidate conventions. |
| CC_V_mean | CC | Arithmetic mean of voltage on a 257-point uniform-time interpolation grid. | voltage | V | constant-current-like charge candidate | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| CC_T_mean | CC | Arithmetic mean of temperature on a 257-point uniform-time interpolation grid. | temperature | degC | constant-current-like charge candidate | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| CC_V_std | CC | Population standard deviation (ddof=0) of voltage on that grid. | voltage | V | constant-current-like charge candidate | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| CC_T_std | CC | Population standard deviation (ddof=0) of temperature on that grid. | temperature | degC | constant-current-like charge candidate | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| CC_V_skewness | CC | Biased third standardized central moment of voltage. | voltage | dimensionless | constant-current-like charge candidate | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| CC_T_skewness | CC | Biased third standardized central moment of temperature. | temperature | dimensionless | constant-current-like charge candidate | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| CC_V_kurtosis | CC | Pearson fourth standardized central moment of voltage. | voltage | dimensionless | constant-current-like charge candidate | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| CC_T_kurtosis | CC | Pearson fourth standardized central moment of temperature. | temperature | dimensionless | constant-current-like charge candidate | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| CC_CCCT | CC | Candidate interval end minus start. | time | min | constant-current-like charge candidate | Workbook formula and exact segment convention remain unverified. Exact phase selector and treatment of gaps are not source-confirmed. |
| CC_entropy | CC | Diagnostic proxy: Shannon entropy in nats of a 16-bin equal-width histogram. | voltage proxy | nats | constant-current-like charge candidate | Original entropy signal, estimator, binning, and logarithm base were not located. |
| dV_energy | dV | Trapezoidal integral of V(t)*I(t), with minutes converted to hours. | voltage and current | Wh | candidate rising 3.9-4.0 V window within CC | Workbook formula and exact segment convention remain unverified. Current sign, integration convention, and interval boundaries are not source-confirmed. |
| dV_Q | dV | Trapezoidal integral of I(t), with minutes converted to hours. | current and time | Ah | candidate rising 3.9-4.0 V window within CC | Workbook formula and exact segment convention remain unverified. Current sign, integration convention, and interval boundaries are not source-confirmed. |
| dV_t_mean | dV | Arithmetic mean of elapsed time on a 257-point uniform-time interpolation grid. | elapsed time | min | candidate rising 3.9-4.0 V window within CC | Workbook formula and exact segment convention remain unverified. Grid and time origin are candidate conventions. |
| dV_V_mean | dV | Arithmetic mean of voltage on a 257-point uniform-time interpolation grid. | voltage | V | candidate rising 3.9-4.0 V window within CC | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| dV_T_mean | dV | Arithmetic mean of temperature on a 257-point uniform-time interpolation grid. | temperature | degC | candidate rising 3.9-4.0 V window within CC | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| dV_V_std | dV | Population standard deviation (ddof=0) of voltage on that grid. | voltage | V | candidate rising 3.9-4.0 V window within CC | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| dV_T_std | dV | Population standard deviation (ddof=0) of temperature on that grid. | temperature | degC | candidate rising 3.9-4.0 V window within CC | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| dV_V_skewness | dV | Biased third standardized central moment of voltage. | voltage | dimensionless | candidate rising 3.9-4.0 V window within CC | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| dV_T_skewness | dV | Biased third standardized central moment of temperature. | temperature | dimensionless | candidate rising 3.9-4.0 V window within CC | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| dV_V_kurtosis | dV | Pearson fourth standardized central moment of voltage. | voltage | dimensionless | candidate rising 3.9-4.0 V window within CC | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| dV_T_kurtosis | dV | Pearson fourth standardized central moment of temperature. | temperature | dimensionless | candidate rising 3.9-4.0 V window within CC | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| dV_dV_devide_dt | dV | Endpoint signal difference divided by candidate interval duration. | voltage and time | V/min | candidate rising 3.9-4.0 V window within CC | Workbook formula and exact segment convention remain unverified. Derivative estimator and candidate window boundaries are not source-confirmed. |
| dV_entropy | dV | Diagnostic proxy: Shannon entropy in nats of a 16-bin equal-width histogram. | voltage proxy | nats | candidate rising 3.9-4.0 V window within CC | Original entropy signal, estimator, binning, and logarithm base were not located. |
| CV_energy | CV | Trapezoidal integral of V(t)*I(t), with minutes converted to hours. | voltage and current | Wh | constant-voltage-like charge candidate | Workbook formula and exact segment convention remain unverified. Current sign, integration convention, and interval boundaries are not source-confirmed. |
| CV_Q | CV | Trapezoidal integral of I(t), with minutes converted to hours. | current and time | Ah | constant-voltage-like charge candidate | Workbook formula and exact segment convention remain unverified. Current sign, integration convention, and interval boundaries are not source-confirmed. |
| CV_t_mean | CV | Arithmetic mean of elapsed time on a 257-point uniform-time interpolation grid. | elapsed time | min | constant-voltage-like charge candidate | Workbook formula and exact segment convention remain unverified. Grid and time origin are candidate conventions. |
| CV_C_mean | CV | Arithmetic mean of current on a 257-point uniform-time interpolation grid. | current | A | constant-voltage-like charge candidate | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| CV_T_mean | CV | Arithmetic mean of temperature on a 257-point uniform-time interpolation grid. | temperature | degC | constant-voltage-like charge candidate | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| CV_C_std | CV | Population standard deviation (ddof=0) of current on that grid. | current | A | constant-voltage-like charge candidate | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| CV_T_std | CV | Population standard deviation (ddof=0) of temperature on that grid. | temperature | degC | constant-voltage-like charge candidate | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| CV_C_skewness | CV | Biased third standardized central moment of current. | current | dimensionless | constant-voltage-like charge candidate | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| CV_T_skewness | CV | Biased third standardized central moment of temperature. | temperature | dimensionless | constant-voltage-like charge candidate | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| CV_C_kurtosis | CV | Pearson fourth standardized central moment of current. | current | dimensionless | constant-voltage-like charge candidate | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| CV_T_kurtosis | CV | Pearson fourth standardized central moment of temperature. | temperature | dimensionless | constant-voltage-like charge candidate | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| CV_CVCT | CV | Candidate interval end minus start. | time | min | constant-voltage-like charge candidate | Workbook formula and exact segment convention remain unverified. Exact phase selector and treatment of gaps are not source-confirmed. |
| CV_entropy | CV | Diagnostic proxy: Shannon entropy in nats of a 16-bin equal-width histogram. | current proxy | nats | constant-voltage-like charge candidate | Original entropy signal, estimator, binning, and logarithm base were not located. |
| dI_energy | dI | Trapezoidal integral of V(t)*I(t), with minutes converted to hours. | voltage and current | Wh | candidate falling 1.0-0.9 A window within CV | Workbook formula and exact segment convention remain unverified. Current sign, integration convention, and interval boundaries are not source-confirmed. |
| dI_Q | dI | Trapezoidal integral of I(t), with minutes converted to hours. | current and time | Ah | candidate falling 1.0-0.9 A window within CV | Workbook formula and exact segment convention remain unverified. Current sign, integration convention, and interval boundaries are not source-confirmed. |
| dI_t_mean | dI | Arithmetic mean of elapsed time on a 257-point uniform-time interpolation grid. | elapsed time | min | candidate falling 1.0-0.9 A window within CV | Workbook formula and exact segment convention remain unverified. Grid and time origin are candidate conventions. |
| dI_C_mean | dI | Arithmetic mean of current on a 257-point uniform-time interpolation grid. | current | A | candidate falling 1.0-0.9 A window within CV | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| dI_T_mean | dI | Arithmetic mean of temperature on a 257-point uniform-time interpolation grid. | temperature | degC | candidate falling 1.0-0.9 A window within CV | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| dI_C_std | dI | Population standard deviation (ddof=0) of current on that grid. | current | A | candidate falling 1.0-0.9 A window within CV | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| dI_T_std | dI | Population standard deviation (ddof=0) of temperature on that grid. | temperature | degC | candidate falling 1.0-0.9 A window within CV | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| dI_C_skewness | dI | Biased third standardized central moment of current. | current | dimensionless | candidate falling 1.0-0.9 A window within CV | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| dI_T_skewness | dI | Biased third standardized central moment of temperature. | temperature | dimensionless | candidate falling 1.0-0.9 A window within CV | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| dI_C_kurtosis | dI | Pearson fourth standardized central moment of current. | current | dimensionless | candidate falling 1.0-0.9 A window within CV | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| dI_T_kurtosis | dI | Pearson fourth standardized central moment of temperature. | temperature | dimensionless | candidate falling 1.0-0.9 A window within CV | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| dI_dI_devide_dt | dI | Endpoint signal difference divided by candidate interval duration. | current and time | A/min | candidate falling 1.0-0.9 A window within CV | Workbook formula and exact segment convention remain unverified. Derivative estimator and candidate window boundaries are not source-confirmed. |
| dI_entropy | dI | Diagnostic proxy: Shannon entropy in nats of a 16-bin equal-width histogram. | current proxy | nats | candidate falling 1.0-0.9 A window within CV | Original entropy signal, estimator, binning, and logarithm base were not located. |
| Charge_energy | Charge | Trapezoidal integral of V(t)*I(t), with minutes converted to hours. | voltage and current | Wh | complete stored charge trace | Workbook formula and exact segment convention remain unverified. Current sign, integration convention, and interval boundaries are not source-confirmed. |
| Charge_Q | Charge | Trapezoidal integral of I(t), with minutes converted to hours. | current and time | Ah | complete stored charge trace | Workbook formula and exact segment convention remain unverified. Current sign, integration convention, and interval boundaries are not source-confirmed. |
| Charge_t_mean | Charge | Arithmetic mean of elapsed time on a 257-point uniform-time interpolation grid. | elapsed time | min | complete stored charge trace | Workbook formula and exact segment convention remain unverified. Grid and time origin are candidate conventions. |
| Charge_V_mean | Charge | Arithmetic mean of voltage on a 257-point uniform-time interpolation grid. | voltage | V | complete stored charge trace | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| Charge_C_mean | Charge | Arithmetic mean of current on a 257-point uniform-time interpolation grid. | current | A | complete stored charge trace | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| Charge_T_mean | Charge | Arithmetic mean of temperature on a 257-point uniform-time interpolation grid. | temperature | degC | complete stored charge trace | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| Charge_C_std | Charge | Population standard deviation (ddof=0) of current on that grid. | current | A | complete stored charge trace | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| Charge_V_std | Charge | Population standard deviation (ddof=0) of voltage on that grid. | voltage | V | complete stored charge trace | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| Charge_T_std | Charge | Population standard deviation (ddof=0) of temperature on that grid. | temperature | degC | complete stored charge trace | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| Charge_C_skewness | Charge | Biased third standardized central moment of current. | current | dimensionless | complete stored charge trace | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| Charge_V_skewness | Charge | Biased third standardized central moment of voltage. | voltage | dimensionless | complete stored charge trace | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| Charge_T_skewness | Charge | Biased third standardized central moment of temperature. | temperature | dimensionless | complete stored charge trace | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| Charge_C_kurtosis | Charge | Pearson fourth standardized central moment of current. | current | dimensionless | complete stored charge trace | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| Charge_V_kurtosis | Charge | Pearson fourth standardized central moment of voltage. | voltage | dimensionless | complete stored charge trace | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |
| Charge_T_kurtosis | Charge | Pearson fourth standardized central moment of temperature. | temperature | dimensionless | complete stored charge trace | Workbook formula and exact segment convention remain unverified. Statistical weighting and sample/bias/excess conventions are not source-confirmed. |

## Synthetic mathematical tests

The isolated test suite was run with `.\.venv\Scripts\python.exe -m pytest -q tests\member4_xjtu\test_independent_mathematical_validation.py` and passed **15 tests**.

It covers all 67 output names using a CC-to-CV synthetic trace and independent calculations, plus constant-current and constant-voltage signals, a linear ramp, changing current, duration scaling, nonuniform timestamps and trapezoidal unit conversion, constant signals, histogram proxy entropy, very short/two-point segments, missing/non-finite samples, mismatched channels, non-increasing timestamps, zero-duration interval rejection, and independence from the capacity label.

These tests demonstrate behavior of the current code on controlled inputs. They do not prove source provenance, physical model adequacy, robustness to untested operating conditions, or agreement with the original workbook generator.

## Software test results

| Check | Command | Result |
|---|---|---|
| Synthetic mathematical tests | `.\.venv\Scripts\python.exe -m pytest -q tests\member4_xjtu\test_independent_mathematical_validation.py` | **15 passed** |
| Focused Member 4 tests | `.\.venv\Scripts\python.exe -m pytest -q tests\member4_xjtu` | **38 passed** |
| Formula Explorer API tests | `.\.venv\Scripts\python.exe -m pytest -q tests\test_formula_explorer_api.py` | **13 passed** |
| Full repository tests | `.\.venv\Scripts\python.exe -m pytest -q` | **119 passed** |
| Frontend production build/type check | `Set-Location frontend; npm run build` | **Passed**, with non-blocking Vite large-chunk warning |
| Frontend lint | `Set-Location frontend; npm run lint` | **Passed** |
| `git diff --check` | `git diff --check` | **Passed** |

Frontend files were not changed during this validation. No browser automation was performed.

## Prepared dataset integrity

- Profiles: **55**; prepared cycles: **27535**; workbook rows: **26937** (cycle-row difference **598**).
- Sample counts per cycle: `{'128': 27535}`.
- Non-finite input values: **0**; non-positive time intervals: **0**; cycles with nonuniform within-cycle time grids: **0**.
- Missing workbook cells including labels: **0**.

The prepared MAT data are not the demonstrated original 1 Hz acquisition. Every inspected cycle has 128 samples; regular within-cycle time spacing in these files does not establish how the prepared representation was produced.

## Candidate availability and descriptive aging association

The association target is the raw `CycleTrace.capacity_label`, used only as an available-capacity/aging proxy. Its unit and normalization lineage are not explicit in the inspected loader; it is not reported here as calibrated SOH. Spearman coefficients are descriptive, not causal or predictive. Within-profile values pair feature and capacity values from the same prepared MAT cycle record; they do not depend on workbook row identity.

| Feature | Finite cycles | Unavailable cycles | Within-profile median Spearman rho | Profiles with rho | Batch-median spread / pooled IQR |
|---|---:|---:|---:|---:|---:|
| CC_energy | 27426 | 109 | 0.9497 | 55 | 1.0489 |
| CC_Q | 27426 | 109 | 0.95919 | 55 | 1.0523 |
| CC_t_mean | 27426 | 109 | 0.95912 | 55 | 1.0986 |
| CC_V_mean | 27426 | 109 | -0.86943 | 55 | 1.0723 |
| CC_T_mean | 27426 | 109 | 0.46955 | 55 | 1.4145 |
| CC_V_std | 27426 | 109 | 0.45632 | 55 | 1.1244 |
| CC_T_std | 27426 | 109 | -0.28994 | 55 | 2.1165 |
| CC_V_skewness | 27426 | 109 | 0.61974 | 55 | 1.3473 |
| CC_T_skewness | 27426 | 109 | -0.39137 | 55 | 1.6698 |
| CC_V_kurtosis | 27426 | 109 | -0.16192 | 55 | 1.2931 |
| CC_T_kurtosis | 27426 | 109 | 0.25941 | 55 | 1.0992 |
| CC_CCCT | 27424 | 111 | 0.95912 | 55 | 1.0986 |
| CC_entropy | 27426 | 109 | 0.1059 | 55 | 1.2484 |
| dV_energy | 27102 | 433 | -0.64732 | 55 | 2.9946 |
| dV_Q | 27102 | 433 | -0.64739 | 55 | 2.9934 |
| dV_t_mean | 27102 | 433 | -0.64738 | 55 | 1.0146 |
| dV_V_mean | 27102 | 433 | 0.40067 | 55 | 1.5933 |
| dV_T_mean | 27102 | 433 | 0.56323 | 55 | 1.6571 |
| dV_V_std | 27102 | 433 | 0.71205 | 55 | 1.9076 |
| dV_T_std | 27102 | 433 | -0.50393 | 55 | 1.7149 |
| dV_V_skewness | 27102 | 433 | -0.41455 | 55 | 1.5121 |
| dV_T_skewness | 27102 | 433 | -0.064561 | 55 | 0.3251 |
| dV_V_kurtosis | 27102 | 433 | -0.53859 | 55 | 1.4971 |
| dV_T_kurtosis | 27102 | 433 | 0.048458 | 55 | 0.23737 |
| dV_dV_devide_dt | 27102 | 433 | 0.64738 | 55 | 1.12 |
| dV_entropy | 27102 | 433 | 0.40336 | 55 | 1.7264 |
| CV_energy | 27535 | 0 | -0.88151 | 55 | 0.97075 |
| CV_Q | 27535 | 0 | -0.88153 | 55 | 0.971 |
| CV_t_mean | 27535 | 0 | -0.94048 | 55 | 0.5488 |
| CV_C_mean | 27535 | 0 | 0.5208 | 55 | 2.4947 |
| CV_T_mean | 27535 | 0 | 0.56002 | 55 | 1.2824 |
| CV_C_std | 27535 | 0 | 0.29684 | 55 | 5.3139 |
| CV_T_std | 27535 | 0 | -0.79561 | 55 | 2.5771 |
| CV_C_skewness | 27535 | 0 | -0.4422 | 55 | 1.6206 |
| CV_T_skewness | 27535 | 0 | -0.70284 | 55 | 0.65595 |
| CV_C_kurtosis | 27535 | 0 | -0.44032 | 55 | 1.6216 |
| CV_T_kurtosis | 27535 | 0 | -0.74073 | 55 | 0.69937 |
| CV_CVCT | 27535 | 0 | -0.94048 | 55 | 0.5488 |
| CV_entropy | 27535 | 0 | 0.60105 | 55 | 1.6127 |
| dI_energy | 27460 | 75 | -0.48791 | 55 | 0.80519 |
| dI_Q | 27460 | 75 | -0.48789 | 55 | 0.80525 |
| dI_t_mean | 27460 | 75 | -0.48721 | 55 | 0.79943 |
| dI_C_mean | 27460 | 75 | 0.0024362 | 55 | 0.75472 |
| dI_T_mean | 27460 | 75 | 0.50654 | 55 | 1.423 |
| dI_C_std | 27460 | 75 | -0.055745 | 55 | 0.30177 |
| dI_T_std | 27460 | 75 | -0.23361 | 55 | 1.7106 |
| dI_C_skewness | 27460 | 75 | 0.017196 | 55 | 0.751 |
| dI_T_skewness | 27460 | 75 | -0.013758 | 55 | 1.7699e-13 |
| dI_C_kurtosis | 27460 | 75 | -0.00476 | 55 | 0.52429 |
| dI_T_kurtosis | 27460 | 75 | 0.015945 | 55 | 0.11679 |
| dI_dI_devide_dt | 27460 | 75 | -0.50093 | 55 | 0.78562 |
| dI_entropy | 27460 | 75 | -0.010933 | 55 | 0.78047 |
| Charge_energy | 27535 | 0 | 0.96278 | 55 | 1.0683 |
| Charge_Q | 27535 | 0 | 0.96085 | 55 | 1.0665 |
| Charge_t_mean | 27535 | 0 | -0.82342 | 55 | 1.3046 |
| Charge_V_mean | 27535 | 0 | -0.9529 | 55 | 1.186 |
| Charge_C_mean | 27535 | 0 | 0.96428 | 55 | 1.549 |
| Charge_T_mean | 27535 | 0 | 0.58347 | 55 | 1.3716 |
| Charge_C_std | 27535 | 0 | 0.55618 | 55 | 6.6608 |
| Charge_V_std | 27535 | 0 | 0.88057 | 55 | 1.0789 |
| Charge_T_std | 27535 | 0 | -0.61331 | 55 | 1.7639 |
| Charge_C_skewness | 27535 | 0 | -0.96276 | 55 | 1.3379 |
| Charge_V_skewness | 27535 | 0 | 0.92897 | 55 | 1.2391 |
| Charge_T_skewness | 27535 | 0 | -0.5462 | 55 | 1.115 |
| Charge_C_kurtosis | 27535 | 0 | -0.5423 | 55 | 1.2615 |
| Charge_V_kurtosis | 27535 | 0 | -0.8783 | 55 | 1.1864 |
| Charge_T_kurtosis | 27535 | 0 | -0.11499 | 55 | 1.1345 |

### Strongest within-profile monotone associations

| Feature | Median within-profile Spearman rho | Profiles contributing |
|---|---:|---:|
| Charge_C_mean | 0.96428 | 55 |
| Charge_energy | 0.96278 | 55 |
| Charge_C_skewness | -0.96276 | 55 |
| Charge_Q | 0.96085 | 55 |
| CC_Q | 0.95919 | 55 |
| CC_t_mean | 0.95912 | 55 |
| CC_CCCT | 0.95912 | 55 |
| Charge_V_mean | -0.9529 | 55 |
| CC_energy | 0.9497 | 55 |
| CV_t_mean | -0.94048 | 55 |

These ranks describe monotone co-variation in the prepared records. They do not demonstrate causality, predictive performance, or feature quality.

### Largest between-batch distribution differences

| Feature | Batch-median spread / pooled IQR | Batch-median spread |
|---|---:|---:|
| Charge_C_std | 6.6608 | 1.0707 |
| CV_C_std | 5.3139 | 0.36612 |
| dV_energy | 2.9946 | 0.37684 |
| dV_Q | 2.9934 | 0.0956 |
| CV_T_std | 2.5771 | 1.9284 |
| CV_C_mean | 2.4947 | 0.18248 |
| CC_T_std | 2.1165 | 2.4677 |
| dV_V_std | 1.9076 | 0.0002772 |
| Charge_T_std | 1.7639 | 1.7967 |
| dV_entropy | 1.7264 | 0.0065416 |

Between-batch differences are descriptive only. Batch labels combine charging protocol with cell composition and other possible differences; these statistics cannot isolate a protocol effect.

## Missing and potentially unstable features

Unavailable values are counted when the current candidate segment or a required calculation is not available. The feature table reports the observed counts for each feature. These are not missing raw input samples: all loaded raw records passed the existing channel/time validation in this run. Constant-signal moments are implemented as zero standard deviation, skewness, and Pearson kurtosis; this is a code convention, not a benchmark-verified statistical convention.

## Target leakage and validation design

- The extractor does not read `capacity_label`; synthetic tests confirm changing that field alone does not change feature values.
- Charge and energy integrals use current, voltage, and elapsed time, not the target field. They may be physically associated with capacity and should be treated as potentially target-adjacent predictors in any later model, but are not direct reuse of the capacity label.
- No predictive model was trained. No cycle-wise random split was used. No claim of cell-wise/batch-wise generalization is made.

## Feature status counts

| Status | Count | Interpretation |
|---|---:|---|
| Candidate arithmetic checked on synthetic signals | 63 | Numerical behavior of the stated candidate formula tested; original formula and source segment remain unverified. |
| Entropy proxy calculation checked | 4 | 16-bin histogram implementation tested; original entropy feature definition remains unknown. |
| Original SOHbenchmark formulas verified | 0 | No original feature generator or authoritative equation set was recovered. |
| Authoritative cycle-to-workbook mappings | 0 | Positional/capacity associations remain unverified. |

## Reproducibility

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests\member4_xjtu\test_independent_mathematical_validation.py
.\.venv\Scripts\python.exe -m scripts.member4_xjtu.independent_validation
```

The analysis command reads all six prepared MAT batches and workbook sheets, recalculates candidate features, and writes the machine-readable summary JSON beside this report. It does not modify source data.

No feature-versus-SOH plot was generated because the available target field is an unnormalized capacity label with unresolved unit/lineage; associations are therefore reported numerically against that field only as a proxy.

## Reviewed implementation and prior evidence

- [Feature definitions](../../scripts/member4_xjtu/feature_definitions.py)
- [Candidate extractor](../../scripts/member4_xjtu/extractor.py)
- [Candidate segments](../../scripts/member4_xjtu/segments.py)
- [Prepared data loader](../../scripts/member4_xjtu/loader.py)
- [Cycle input validation](../../scripts/member4_xjtu/models.py)
- [Original formula provenance audit](../member4_scientific_provenance_audit.md)
- [Original benchmark reproduction status](./original_benchmark_reproduction.md)

## Remaining scientific limitations

- Original feature equations, boundaries, and preprocessing conventions remain unavailable.
- No authoritative mapping links prepared cycles to workbook rows; the validation here therefore avoids treating workbook values as expected references.
- The prepared MAT traces contain 128 samples per cycle and their lineage to original acquisition data is unresolved.
- Candidate segment thresholds and policies are implementation assumptions. Mathematical agreement with synthetic expectations does not establish that they describe the authors' feature windows.
- Descriptive capacity associations and batch differences are not causal findings or validated predictors.

No original formula was changed, and no scientific accuracy or benchmark reproduction claim is made.
