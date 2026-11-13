# Member 4 Demo Walkthrough — XJTU 67-Feature Engineering

## Purpose and scientific boundary

This walkthrough is for the Member 4 contribution to **VoltTwin – EV Battery Intelligence**. It explains the XJTU handcrafted-feature work, the Formula Explorer, and what the current validation and research do—and do not—establish.

The central caveat should be stated before showing any error metric:

> The Explorer exposes reproducible candidate calculations for 67 workbook feature names. We have not located the original workbook generator, and we have not established authoritative cycle-to-row identity. Therefore none of these candidates is source-verified, and candidate-to-Excel comparisons are diagnostic only.

Current formula-recovery counts are 0 Source Verified, 0 Partially Verified, 63 Candidate/unverified, and 4 Original formula unavailable. The four unavailable original definitions are the entropy features. There are zero identity-verified cycle/workbook pairs.

## Member 4 contribution

The Member 4 work in this workspace covers:

1. **Feature schema:** a canonical, ordered set of 67 named features, divided into five feature groups.
2. **Candidate computation:** code that loads the prepared XJTU MAT charge cycles, constructs explicit candidate intervals, and computes candidate values and calculation details.
3. **Formula Explorer:** an interactive interface to inspect the candidate definitions and calculate one selected feature from a selected raw prepared cycle.
4. **Candidate validation:** comparisons with the prepared benchmark Excel values, with metric tables and explicit alignment labels.
5. **Error analysis:** feature-, batch-, profile-, and cycle-decile diagnostics; root-cause evidence; sensitivity experiments; figures; and unmatched/invalid counts.
6. **Research transparency:** source searches, a feature-by-feature formula evidence ledger, cycle identity analysis, and inspection of the 2024 paper's supplementary PDF.
7. **Tests:** unit and API tests covering candidate extraction, data/alignment safeguards, analysis metrics, evidence output, and API responses.

The implementation and reports intentionally retain the candidate/unverified distinction. The work provides an auditable investigation, not a claim that the original 67 equations were recovered.

## The 67 features and their groups

The canonical feature names are grouped as follows. The prefixes describe the benchmark's feature naming; they are not proof that the original workbook used the candidate segment definitions below.

### CC — 13 features

`CC_energy`, `CC_Q`, `CC_t_mean`, `CC_V_mean`, `CC_T_mean`, `CC_V_std`, `CC_T_std`, `CC_V_skewness`, `CC_T_skewness`, `CC_V_kurtosis`, `CC_T_kurtosis`, `CC_CCCT`, `CC_entropy`

### dV — 13 features

`dV_energy`, `dV_Q`, `dV_t_mean`, `dV_V_mean`, `dV_T_mean`, `dV_V_std`, `dV_T_std`, `dV_V_skewness`, `dV_T_skewness`, `dV_V_kurtosis`, `dV_T_kurtosis`, `dV_dV_devide_dt`, `dV_entropy`

### CV — 13 features

`CV_energy`, `CV_Q`, `CV_t_mean`, `CV_C_mean`, `CV_T_mean`, `CV_C_std`, `CV_T_std`, `CV_C_skewness`, `CV_T_skewness`, `CV_C_kurtosis`, `CV_T_kurtosis`, `CV_CVCT`, `CV_entropy`

### dI — 13 features

`dI_energy`, `dI_Q`, `dI_t_mean`, `dI_C_mean`, `dI_T_mean`, `dI_C_std`, `dI_T_std`, `dI_C_skewness`, `dI_T_skewness`, `dI_C_kurtosis`, `dI_T_kurtosis`, `dI_dI_devide_dt`, `dI_entropy`

### Charge — 15 features

`Charge_energy`, `Charge_Q`, `Charge_t_mean`, `Charge_V_mean`, `Charge_C_mean`, `Charge_T_mean`, `Charge_C_std`, `Charge_V_std`, `Charge_T_std`, `Charge_C_skewness`, `Charge_V_skewness`, `Charge_T_skewness`, `Charge_C_kurtosis`, `Charge_V_kurtosis`, `Charge_T_kurtosis`

The first four groups have 13 each and Charge has 15, for 67 total. Here `V` denotes voltage, `C` denotes current in the candidate descriptions, and `T` denotes temperature. These labels describe the current project candidate mapping; they are not a recovered original schema specification for every feature.

## How candidate extraction works

### Input data

The local loader reads:

- Prepared charge-cycle traces from `reference/SOHbenchmark/data/XJTU/charge/batch-N.mat`.
- The corresponding `batch-N_features.xlsx` workbook for comparisons.

The prepared cycle fields include relative time in minutes, voltage, current, temperature, and capacity. The inspected prepared cycles contain 128 samples with nonuniform time intervals. The workbook sheets contain feature values and labels, but the inspected files do not provide explicit cycle IDs that prove row identity.

### Candidate segmentation

The extractor computes the following candidate regions:

- **CC:** adaptive current plateau by default. An optional author-helper-style mode uses current at least 3.9 A and voltage at most 4.199 V. The helper is related author code, not proof of the workbook rule.
- **CV:** starts at the first rising crossing of 4.199 V and ends at the stored trace end.
- **dV:** candidate rising 3.9–4.0 V window within CC.
- **dI:** candidate falling 1.0–0.9 A window within CV.
- **Charge:** the full stored charge trace.

The dV/dI windows and the default CC/CV boundaries are candidate assumptions. A missing or disjoint candidate window is surfaced as unavailable for affected boundary-dependent values rather than silently filled or bridged.

### Candidate mathematics and numerical conventions

- Candidate energy integrates voltage times current using trapezoids over stored timestamps and interpolated interval boundaries. Minutes are converted to hours.
- Candidate charge integrates current in the same manner.
- Candidate time/channel statistics interpolate onto a 257-point uniform-time grid per interval.
- The candidate uses population standard deviation (`ddof=0`), biased standardized skewness, and Pearson kurtosis (not excess kurtosis).
- Entropy is a diagnostic 16-bin equal-width histogram Shannon proxy in nats. It is not the recovered original entropy method.

Every choice above is reproducible in the code but unverified against the Excel generator.

## How to use Formula Explorer

The Explorer is available in the project UI under `#feature-explorer`. The current shared local browser used during the audit displayed `http://127.0.0.1:5173/#feature-explorer`; availability depends on the development frontend and backend being started and the XJTU reference data being present.

### Browse and select a feature

1. Open **Formula Explorer** from the project navigation.
2. Read the formula-provenance warning and status counts before interpreting the equations.
3. Use the search field to find a feature name, or select `All`, `CC`, `dV`, `CV`, `dI`, or `Charge`.
4. Click a feature in the list. The detail panel shows its group, order, status, candidate notation, candidate plain-language interpretation, implementation description, input/output units, segment description, calculation steps, and variable definitions.
5. For `*_entropy`, point out the `Original Formula Unknown` status and the warning that the histogram is only a diagnostic proxy.

### Select a batch, profile, and cycle

Within **Run candidate calculation on a raw cycle**:

1. Select one of the six batches.
2. Select an available battery profile, shown as `SheetN` with its cycle count.
3. Enter a positive integer cycle within the displayed profile count.
4. Keep a feature selected in the feature browser. The calculation request includes that feature name together with the selected batch/profile/cycle.
5. Click **Calculate candidate**.

Changing the batch refreshes the available profiles. Changing the profile or cycle clears the prior calculation so an old result is not mistaken for the new selection. The controls select a prepared MAT profile ordinal and cycle ordinal; they do not prove corresponding Excel row identity.

### Explain the output

After calculation, the Explorer displays:

- **Candidate result and units:** the selected feature's value from the Python candidate extractor, or “Not available for this cycle” if the candidate interval/calculation cannot be formed.
- **Trace plot:** raw MAT voltage/current/temperature against relative time; the selected group's candidate interval is shaded and selected raw samples are marked. Interpolation used by the calculation does not turn the plotted curve into original acquisition data.
- **Sampling summary:** raw sample count, minimum/median/maximum time step, selected raw sample count, and whether the prepared time values are uniform.
- **Segment evidence:** the candidate selector, its evidence note, and its interval boundaries.
- **Calculation details:** operation-specific intermediates. For integrations these include trapezoid panels and time conversion; for statistics, the interpolation grid and moments; for entropy, histogram bins/probabilities/contributions.
- **Candidate warning:** outputs are not original workbook values or author-confirmed feature formulas.

This is a live candidate calculation from the chosen prepared raw trace, not an Excel comparison view or an alignment proof.

## Validation and error analysis

The validation runner checks workbook feature names/order and computes candidate-vs-Excel statistics. It evaluated all six batches. The existing cycle identity audit records:

- 27,535 prepared raw cycles and 26,937 workbook rows.
- 26,320 comparison pairs from the existing alignment helper.
- 19,191 equal-count positional pairs, explicitly unverified.
- 7,129 batch-6 capacity-label matches, diagnostic only.
- 617 unmatched workbook rows, including 489 ambiguous rows.
- 1,215 unmatched raw cycles in the batch-6 capacity-match cohort.
- Zero cycle/workbook pairs with authoritative identity verification.

The error-analysis report calculates feature-wise MAE, RMSE, signed bias, median and maximum absolute error, error quantiles, relative error/MAPE with near-zero safeguards, Pearson/Spearman correlations, and valid/invalid observation counts. It also provides batch/profile/cycle-decile views and prespecified candidate sensitivity comparisons.

**How to explain the metrics:** they summarize how the current candidate outputs differ from the workbook values under the reported comparison cohort. They do not measure verified original-formula accuracy because both formula provenance and cycle identity remain unresolved. Positional and capacity cohorts are kept separate; ambiguous/unmatched rows are not silently treated as valid pairs. A sensitivity variant with smaller residuals is not evidence that it is the original formula.

The reports identify observed facts (such as sample counts, residual distributions, unavailable candidate windows) separately from hypotheses about segmentation, sampling, or statistical conventions. Correlated errors do not establish causal root causes.

## Formula recovery investigation

The research inspected local reports, candidate definitions/extractor/segments, workbooks, SOHbenchmark loader/history, XJTU author preprocessing code, dataset documentation, papers, supplementary materials, public repositories/search, and the PINN4SOH paper-linked code/schema.

The 2024 Nature Communications supplementary material gives equations for its own selected-window statistical-feature method, including mean, sample standard deviation, skewness, kurtosis, time duration, accumulated charge, endpoint voltage slope, and generic curve entropy. It uses voltage/current selection windows for that paper. It does **not** map those methods to the SOHbenchmark 67-column workbooks. The author-linked PINN4SOH XJTU CSV schema has 16 input features plus capacity; this is different from the benchmark's 67 features.

Current formula-recovery ledger:

| Status | Features | Meaning |
|---|---:|---|
| Source Verified | 0 | No exact workbook-specific source equation or implementation was found. |
| Partially Verified | 0 | No original workbook definition has enough direct feature-specific evidence for partial verification. |
| Candidate/unverified | 63 | Candidate implementations exist; original definitions and conventions remain unestablished. |
| Original formula unavailable | 4 | Original entropy signal/estimator and conventions remain unknown. |

This is a bounded search finding. It does not prove that private, deleted, inaccessible, or unindexed source material does not exist.

## What remains unresolved

1. **Original 67-feature formulas and generator:** not found. Exact signals, phases, units, numerical conventions, and preprocessing cannot be asserted.
2. **Cycle identity:** no common explicit ID, timestamp join, or author-provided mapping was found between prepared cycles and workbook rows.
3. **Prepared-data lineage:** the dataset release states 1 Hz acquisition, whereas the prepared MAT traces contain 128 nonuniform-time samples. The transformation from original samples to these traces is not documented in inspected material.
4. **Entropy definitions:** all four original estimators remain unknown. The paper's generic entropy equation does not specify enough details to recover the benchmark estimator.
5. **Root cause attribution:** phase boundaries, sampling, units, and statistical conventions are possible discrepancy mechanisms, but the current evidence does not prove which caused any particular residual.

## What I can confidently explain in the viva

- What the feature groups and their canonical 67 names are.
- How the **candidate** extractor handles timestamps, segments, integrations, statistics, and missing intervals.
- How to navigate Formula Explorer and inspect one candidate calculation from raw prepared data.
- Why numerical fit is not formula provenance and why cycle identity must be established before treating residuals as ground truth.
- What authoritative sources and supplementary materials were inspected and what they do (and do not) establish.
- Why entropy is especially underdetermined and why a histogram proxy is labeled diagnostic.
- Which tests passed and the distinction between software tests and scientific validation.
- The next evidence needed to advance the science: author generator/formula documentation and an authoritative cycle-to-workbook mapping.

## High-priority work that can be done without inventing evidence

1. **Finalize a reproducible demo environment.** Confirm the required Python/frontend dependencies and reference data are available, start the app, and verify one candidate calculation and one entropy-unavailable explanation from a clean session. Evidence: a short run log and captured UI state showing warnings.
2. **Capture a Formula Explorer demonstration screenshot.** Save a privacy-safe image with the provenance warning, a feature definition, selected batch/profile/cycle, and candidate-only result visible. This improves presentation evidence without changing scientific claims.
3. **Add browser-level UI regression tests only if approved and in scope.** Existing Python/API tests do not establish interactive frontend behavior. Test loading, feature search/selection, entropy status, candidate calculation, and error state; do not alter formulas.
4. **Request primary-source evidence from the dataset/benchmark authors.** Ask for the workbook generator, exact feature/segment equations, preprocessing description, and row-cycle mapping. No code change can replace this evidence.

## Key files and reports

- Candidate package and commands: [scripts/member4_xjtu/README.md](../scripts/member4_xjtu/README.md)
- Feature definitions: [feature_definitions.py](../scripts/member4_xjtu/feature_definitions.py)
- Extractor: [extractor.py](../scripts/member4_xjtu/extractor.py)
- Segmentation policy: [segments.py](../scripts/member4_xjtu/segments.py)
- Candidate comparison: [member4_candidate_validation.md](./member4_candidate_validation.md)
- Feature error analysis: [member4_feature_error_analysis.md](./member4_feature_error_analysis.md)
- Cycle identity investigation: [member4_cycle_identity_investigation.md](./member4_cycle_identity_investigation.md)
- Formula recovery: [member4_original_formula_recovery.md](./member4_original_formula_recovery.md)
- Supplementary PDF inspection: [member4_supplementary_pdf_inspection.md](./member4_supplementary_pdf_inspection.md)
- Contribution audit: [member4_final_contribution_audit.md](./member4_final_contribution_audit.md)
