# Member 4 Final Completion Report

**Repository:** VoltTwin
**Branch inspected:** `feature/features-ui`
**Review date:** 2026-11-10

## Verdict

- **IMPLEMENTATION COMPLETE** — the 67-feature candidate extractor, Formula
  Explorer, descriptive aging analysis, and grouped capacity-prediction
  evaluation are implemented.
- **SCIENTIFICALLY PARTIALLY VALIDATED** — mathematical behavior of candidate
  calculations has independent synthetic checks, and descriptive/grouped
  analyses have been run on the prepared data. Neither establishes that the
  candidate features reproduce the original benchmark.
- **ORIGINAL BENCHMARK VALIDATION BLOCKED** — **0/67** original formulas and
  **0** authoritative workbook-row/cycle identities are verified.

The distinction is important: the software computes and explains reproducible
candidate values, but those values must not be presented as recovered or
validated original benchmark values.

**BROWSER-VERIFIED:** the integrated dashboard was exercised in installed
Google Chrome through Playwright: **26 checks passed, 0 failed**, with no page
errors or critical HTTP 5xx responses. **Handoff recommendation: READY WITH
DOCUMENTED LIMITATIONS.** No known mandatory Member 4 coding task remains;
closure is recommended unless the authors provide new scientific provenance
material.

## Completed implementation

- The feature registry defines **67 unique features** in five groups: CC (13),
  dV (13), CV (13), dI (13), and Charge (15).
- The candidate extraction package loads the prepared XJTU charge MAT traces,
  validates the trace inputs, applies explicitly documented candidate segment
  rules, calculates candidate statistics/integrals, and returns intermediate
  diagnostics. Missing or unsupported intervals remain unavailable rather
  than being fabricated.
- The Formula Explorer is registered in the backend and integrated into the
  normal frontend navigation. Its UI/API expose feature groups, units,
  candidate equations and assumptions, batch/profile/cycle selection, raw
  signals, candidate segments, and calculation details.
- Formula Explorer distinguishes candidate values from original benchmark
  values and reports `source_verified_count: 0`. Its warning states that the
  original workbook formulas are not verified. The API assigns the ordinary
  features `candidate_unverified` and the four entropy features
  `original_formula_unknown`.
- `scripts/member4_xjtu/aging_analysis.py` reports per-profile availability,
  feature-vs-cycle and feature-vs-capacity-label Spearman associations,
  cross-profile summaries of within-profile feature redundancy, descriptive
  batch differences, and three trajectory plots. No per-cell normalization or
  cross-profile pooled correlation was used.
- `scripts/member4_xjtu/aging_prediction.py` runs deterministic five-fold
  grouped evaluation by composite batch/profile ID. It compares a training-fold
  median baseline with a NumPy closed-form Ridge model; imputation and scaling
  are fitted only on each training fold. Capacity/metadata fields and all
  `_Q`/`_energy` integral features are excluded from predictors.
- Prediction is explicitly **capacity prediction**, not SOH prediction:
  stored target units and a verified per-cell initial-capacity denominator are
  unavailable. The 57 remaining candidate features are not source-verified
  and may still carry protocol or indirect capacity information.
- No original feature formula was changed. The earlier, independently tested
  CC segment-boundary correction remains in place. Unrelated existing worktree
  changes were preserved.
- Browser verification covered the homepage, Formula Explorer anchor,
  67-feature catalog, all five category filters, search/details, provenance
  warnings, valid calculation, raw plot, batch/profile selection, invalid error
  handling, and return navigation. Evidence is in
  [browser_testing_report.md](../browser_testing_report.md) and the six
  screenshots under `../browser_screenshots/`.

## Software test evidence

Commands were run from the repository root unless noted:

| Command | Result |
|---|---|
| `.\.venv\Scripts\python.exe -m pytest -q tests\member4_xjtu` | **49 passed** (including grouped splitting, leakage exclusion, target handling, fold-local preprocessing, metric tests, and formula-provenance audit checks). |
| `.\.venv\Scripts\python.exe -m pytest -q tests\test_formula_explorer_api.py` | **13 passed**. |
| `.\.venv\Scripts\python.exe -m pytest -q tests\member4_xjtu\test_original_formula_recovery_audit.py` | **2 passed**; all 67 audit rows remain unverified/unknown and the API preserves the distinct candidate/original warning. |
| `.\.venv\Scripts\python.exe -m pytest -q` | **132 passed**. |
| `.\.venv\Scripts\python.exe -m scripts.member4_xjtu.aging_analysis` | **Recorded completed run**; processed 27,535 cycles and 67 features and generated 3 plots. |
| `.\.venv\Scripts\python.exe -m scripts.member4_xjtu.aging_prediction` | **Recorded completed run**; evaluated 55 profiles and 27,535 finite target cycles. |
| From `frontend\`: `npm run build` | **Passed**; TypeScript build and Vite production build succeeded. Vite emitted a non-blocking warning that a minified JavaScript chunk exceeds 500 kB. |
| From `frontend\`: `npm run lint` | **Passed**. |
| Python JSON/CSV integrity check over `reports\` | **Passed**; all 33 CSV and 14 JSON files parsed, and all 107,277 CSV data rows matched their header widths. |
| `git diff --check` | **Passed** |
| Real Chrome/Playwright browser E2E (`node frontend/browser_e2e.mjs`) | **26 passed, 0 failed**; 0 page errors, 0 critical 5xx responses, 6 screenshots. |

These tests support implementation behavior and integration; they do not
establish scientific correctness of a candidate formula or the identity of a
workbook row and raw cycle. The first attempted frontend commands ran from the
repository root and failed to locate `package.json`; the documented reruns
from `frontend\` passed. The environment also blocks scikit-learn's compiled
`_ball_tree` extension through Application Control; the reproducible Ridge
implementation therefore uses NumPy directly and is covered by focused tests.
The full-data aging analysis and grouped prediction are expensive completed
Member 4 runs; their existing reports, summaries, plots, and regression tests
were reconciled during closure rather than regenerated again.
Browser automation was executed separately against the live local Uvicorn/Vite
application in installed Google Chrome. The browser report records intentional
invalid-cycle 404 checks and the restricted-environment Google Fonts fallback;
neither was an application defect.

The Phase 2 artifact regression test
(`tests/member4_xjtu/test_formula_verification_phase2.py`) passed **2 tests**;
it verifies one row per feature, required evidence columns, and the separate
related-method/original-provenance counts.

### Live integration checks

The local Uvicorn/Vite application also passed the recorded endpoint checks:

| Request | Result |
|---|---|
| `/health` | **200**, `healthy` |
| Formula catalog | **200**, all 67 features, `source_verified_count: 0` |
| Batch 1 profiles | **200**, 8 profiles |
| Candidate calculation (`batch=1`, `Sheet1`, `cycle=1`, `Charge_energy`) | **200**, 128 raw samples, explicitly not an original benchmark value |
| Invalid feature / invalid batch / missing cycle | **422 / 422 / 404** |

These checks are consistent with the browser report and do not establish
scientific provenance for any candidate formula.

## Scientific validation completed

- **Candidate implementation and diagnostics:** the current code and its
  assumptions are documented and testable. Prior candidate-vs-workbook metrics
  are retained only as diagnostic comparisons.
- **Formula/source investigation:** inspected project evidence did not recover
  an original generator or an authoritative equation set for the 67 workbook
  columns. This is a bounded search result, not proof that private or
  inaccessible materials do not exist.
- **Paper comparison:** the Nature Communications paper defines its own
  16-feature method. The comparison records **0 exact equivalences** to the 67
  candidate features and **0 original 67-feature formulas verified by that
  paper**. Mathematical similarities do not establish matching signals,
  intervals, units, sampling, or conventions.
- **Cycle/data audit:** the prepared files contain **27,535 cycles across 55
  profiles**; the six workbooks contain **26,937 rows**. The available prepared
  MAT and workbook schemas do not provide an authoritative shared cycle key.
- **Original value reproduction:** no original `CC_Q` value was reproduced.
  Without both a source-backed formula and a verified row-to-cycle mapping, an
  error value would be unjustified.

### Original formula recovery follow-up

A focused source recovery pass inspected the local SOHbenchmark tree, the
author's public [SOHbenchmark repository](https://github.com/wang-fujin/SOHbenchmark/tree/62230dd9a857f5c05ac641227b52ec2ffbeb9e15),
the [commit that adds the six workbooks](https://github.com/wang-fujin/SOHbenchmark/commit/611bb5948fe4a7914486ded7be238db24faabb23),
the author's [XJTU preprocessing library](https://github.com/wang-fujin/Battery-dataset-preprocessing-code-library/blob/main/XJTUBatteryClass.py),
the [official XJTU dataset site](https://wang-fujin.github.io/), the available
SOHbenchmark appendix PDF, and previous exact-name/source inventories.

- The benchmark's `XJTUDdataset.get_features` reads precomputed Excel columns
  and `label`; it is not a feature generator. The workbook-upload commit adds
  prepared files and no generation code.
- The separate author preprocessing class documents phase selectors and
  `dQ/dV` helpers, but does not map them to the SOHbenchmark workbook columns.
  Similarity to candidate CC/CV or derivative names is not treated as formula
  evidence.
- The available appendix PDF's text contains benchmark result tables but no
  exact 67-column formula definitions. The main article's full text was not
  accessible through the available source endpoint during this pass.
- Direct inspection of all six local XJTU workbooks confirmed the 67 feature
  headers plus `label`, consistent header ordering across sheets, and **zero**
  spreadsheet formula cells, comments, or defined names.
- Final recovery count: **0 source-verified**, **0 partially verified**,
  **63 candidate-unverified**, and **4 original-formula-unknown** (the entropy
  definitions). The exact per-feature record and evidence inventory are in
  [original_formula_recovery_audit.md](./original_formula_recovery_audit.md),
  [original_formula_recovery.csv](./original_formula_recovery.csv), and
  [original_formula_recovery_summary.json](./original_formula_recovery_summary.json).
- Formula Explorer was **not changed** because no original formula was
  recovered. Its candidate expressions, unavailable-original-formula text,
  and provenance warning remain separate. The new audit test and existing API
  tests verify all 67 names and the candidate/unknown statuses.

### Deep research Phase 2 update

The Phase 2 source pass added the current author preprocessing repository's
`XJTU数据集分析.ipynb` to the inspected evidence. Its plotting examples use a
CC voltage selector of `[3.8, 4.0] V` and a CV current selector of `[1.0, 0.5] A`;
the accompanying `XJTUBatteryClass.py` provides CC/CV helpers and dQ/dV
routines. Neither artifact exports the 67 workbook columns or maps a helper
output to a workbook feature, so these observations are **related-method
evidence only** and do not justify changing VoltTwin's candidate windows.

The author repository inventory, current `PINN4SOH` tree, XJTU papers-summary
repository, and public forks `rosyeeBen/SOHbenchmark2`,
`armand00000/SOHbenchmarkT`, and `Yike-Lin/SOH-Baseline-test` were also checked.
They retain prepared-data benchmark layouts and do not expose a versioned
67-feature generator. The publisher supplement's equations remain a separate
16-feature method. The complete Phase 2 row-level record is in
[formula_verification_phase2.csv](./formula_verification_phase2.csv), with
methodology and counts in [formula_verification_phase2.md](./formula_verification_phase2.md)
and [formula_verification_phase2_summary.json](./formula_verification_phase2_summary.json).

Phase 2 evidence labels are intentionally separate from Formula Explorer's
original-provenance status. They classify **32** rows as
`RELATED_METHOD_ONLY`, **31** as `CANDIDATE_UNVERIFIED`, and the four entropy
rows as `ORIGINAL_FORMULA_UNKNOWN`; `SOURCE_VERIFIED` and `PARTIALLY_VERIFIED`
remain zero. The original-provenance count remains **0/67 verified**, **0/67
partially verified**, **63/67 candidate-unverified**, and **4/67
original-formula-unknown**. No candidate equation or Formula Explorer warning
was modified.

## Feature aging analysis

- The analysis covered **55 profiles**, **27,535 prepared cycles**, and all
  **67 candidate features**. Workbook rows (**26,937**) are reported only for
  context; no row/cycle mapping was used.
- Candidate values were unavailable for some cycles in **39 features**:
  CC-family outputs were unavailable in 109 cycles (111 for `CC_CCCT`),
  dV-family outputs in 433 cycles, and dI-family outputs in 75 cycles. The
  other features had no unavailable values in this prepared run.
- Candidate features with the largest absolute median within-profile
  Spearman association with the stored capacity label included
  `Charge_C_mean` (**0.964**), `Charge_energy` (**0.963**),
  `Charge_C_skewness` (**-0.963**), `Charge_Q` (**0.961**), and `CC_Q`
  (**0.959**), each based on 55 profiles. These are exploratory
  within-profile associations, not causal evidence or validated predictors;
  capacity/energy integrals are not evidence of leakage-safe predictive value.
- The redundancy screen flagged **134** feature pairs whose median
  within-profile Spearman correlation had absolute value at least 0.9 across
  at least 10 profiles. Batch differences remain confounded by cell cohort and
  protocol.
- Three unnormalized per-profile trajectory plots were generated. No SOH
  plots or claims were made because a valid per-cell initial-capacity
  denominator is unavailable.

## Leakage-safe capacity prediction

The target is `capacity_label` in its **unresolved stored scale**. No
first-observed capacity was assumed to be a valid beginning-of-life reference,
so no SOH target or per-cell capacity normalization was created. Five
deterministic, sample-balanced group folds held out **11 profiles** at a time
and trained on **44 profiles**; per-fold test sizes ranged from 5,484 to 5,528
cycles. Each profile was held out once, with no profile appearing in both the
training and test partitions of a fold.

| Model | Pooled out-of-fold MAE | RMSE | R-squared |
|---|---:|---:|---:|
| Training-fold median baseline | 0.07331 | 0.09895 | -0.04560 |
| Ridge regression | 0.02905 | 0.03988 | 0.83016 |

These errors are in the unresolved stored target scale. The Ridge result is an
exploratory capacity prediction result, not SOH prediction, original
benchmark validation, or a claim of strong external generalization. The five
fold aggregate Ridge R-squared values ranged from **0.8052 to 0.8767**;
folds contain cells from the same batches in both training and evaluation, so
this does not establish batch- or protocol-independent performance. All
`_Q`/`_energy` features were excluded, but other charge-derived features may
still encode protocol or indirect capacity information.

The full per-profile results are in
[aging_prediction_results.csv](./aging_prediction_results.csv), with
methodology and interpretation limits in
[leakage_safe_prediction.md](./leakage_safe_prediction.md). The aging report,
JSON summary, and plots are also under `reports/member4/`.

## Exact verification and mapping counts

### Formula definitions

| Measure | Count | Meaning |
|---|---:|---|
| Original workbook formulas source-verified | **0 / 67** | No exact feature and matching calculation context tied to an authoritative source. |
| Original workbook formulas partially verified | **0 / 67** | Related equations or operations are not partial verification of the workbook feature. |
| Candidate/unverified formulas | **63 / 67** | Candidate interpretations are implemented, but original workbook definitions remain unverified. |
| Original formula unavailable | **4 / 67** | Entropy definitions are unidentified; the implemented histogram entropy is only a proxy. |

The provenance audit has a separate evidence classification for the current
expressions: **A 0**, **B 14**, **C 49**, **D 4**, **E 0**. Its 14 class-B
entries indicate that a mathematical operation appears in a related source;
they do **not** establish exact workbook feature provenance or context and do
not change the **0/67** original-formula-verified count.

### Paper mapping and row/cycle identity

| Measure | Count | Meaning |
|---|---:|---|
| Exact paper-to-candidate feature equivalences | **0 / 16** | Paper features are not the source definitions of the SOHbenchmark 67-column schema. |
| Authoritatively verified workbook-row/cycle pairs | **0** | No validated key or crosswalk was found. |
| Positional candidates | **19,191** | Equal-count ordinal pairings; unverified. |
| Capacity-matched candidates | **7,129** | Unique monotone matches within the diagnostic capacity tolerance; unverified. |
| Total helper-matched candidates | **26,320** | Sum of the positional and capacity candidates; none is authoritative. |
| Ambiguous workbook rows | **489** | Multiple remaining capacity candidates met the matching tolerance. |
| Other unmatched workbook rows | **128** | No unique remaining capacity candidate met the tolerance. |
| Total unmatched workbook rows | **617** | 489 ambiguous plus 128 other unmatched. |
| Raw cycles unused by the capacity diagnostic | **1,215** | Unused in that diagnostic cohort; not proof that no workbook row represents them. |

Neither equal profile counts, row order, nor capacity agreement proves cycle
identity. The candidate-error rankings and residuals inherit this limitation
and must not be described as ground-truth formula errors.

## Scientific claims that remain unverified or unavailable

- The original formulas, signals, segment boundaries, units, sampling,
  integration, interpolation, and statistical conventions for the 67 workbook
  features.
- The source and preprocessing lineage that created the prepared 128-sample
  MAT traces and the feature workbooks, including omissions, resampling, and
  row ordering.
- Any authoritative mapping between workbook rows and prepared/raw XJTU
  cycles.
- Independent reproduction of any original workbook feature value, including
  `CC_Q`.
- The original entropy estimator and its signal, bins/probabilities, and
  logarithm convention.
- An author-provided, versioned feature-generation source or specification
  mapping the 67 workbook columns to exact signals, windows, units, and
  numerical conventions. The available author code and paper appendix do not
  provide this mapping.
- Exact equivalence between any of the paper's 16 features and the SOHbenchmark
  67-feature workbook. The paper's own results, including its reported MAPE,
  are not VoltTwin results.

## Completion status and remaining work

There is **no known mandatory engineering implementation task** remaining in
the requested Member 4 scope. Remaining work is research needed for original
benchmark scientific validation:

1. Request the authors' versioned 67-feature generator or full formula
   specification.
2. Request an author-provided workbook-row-to-cycle crosswalk, or acquire
   source identifiers and a documented preprocessing lineage sufficient to
   establish one.
3. If both become available, reproduce one feature (starting with `CC_Q`) from
   an identity-mapped cycle, document exact conventions and error, and add a
   source-backed regression test.

Until then, retain **0 verified formulas** and **0 verified cycle mappings**;
do not tune candidate formulas to diagnostic metrics or relabel candidates as
verified.

The completed browser run does not identify an implementation defect: Chrome
and Playwright exercised the integrated UI and API paths with **26 passed and 0
failed** checks. Accordingly, no additional coding task is justified for
closure. The handoff status is **READY WITH DOCUMENTED LIMITATIONS**: the
software is integrated and testable, while original benchmark reproduction
remains blocked by missing source formulas and cycle identity.

## Evidence files

- [Formula Explorer backend](../../backend/formula_explorer_api.py)
- [Formula Explorer frontend](../../frontend/src/components/FormulaExplorer.tsx)
- [Feature definitions](../../scripts/member4_xjtu/feature_definitions.py)
- [Candidate extractor](../../scripts/member4_xjtu/extractor.py)
- [Candidate segment policy](../../scripts/member4_xjtu/segments.py)
- [Scientific provenance audit](../member4_scientific_provenance_audit.md)
- [Paper methodology comparison](./paper_methodology_comparison.md)
- [Cycle identity investigation](../member4_cycle_identity_investigation.md)
- [Original benchmark reproduction audit](./original_benchmark_reproduction.md)
- [Row-level diagnostic identity audit](./cycle_identity_audit.csv)
