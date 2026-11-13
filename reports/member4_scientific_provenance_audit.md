# Member 4 XJTU Feature Scientific Provenance Audit

**Audit scope:** The 67 feature columns in the six SOHbenchmark XJTU Excel workbooks, the available prepared MAT traces, the current Member 4 candidate extractor, and the formula/dataset sources already present in the repository research record.

**Audit date:** 2026-11-10
**Branch inspected:** `feature/features-ui`

## Executive findings

- **0/67 original SOHbenchmark workbook formulas are source-verified.** No reviewed primary source identifies the exact workbook generator, exact feature equations, and matching per-cycle input identity.
- The current implementation does compute 67 **candidate values**. It does not reproduce an author-confirmed feature pipeline.
- For classification of the *implemented expressions*: **A direct authoritative match: 0; B same mathematical operation described in related source: 14; C engineering candidate without matching formula evidence: 49; D diagnostic proxy: 4; E no implemented expression: 0.** B means only that a mathematical operation appears in a source; it does not verify the feature name, segment, sampling convention, workbook generation, or cycle alignment. The four D features are histogram entropy proxies; their original benchmark definitions are unavailable.
- A, the question of whether an **original benchmark formula** is verified, remains **No for all 67**. The four entropy formulas have particularly explicit “original formula unknown” status.
- The inspected local XJTU charge MAT files are prepared traces, not demonstrated original 1 Hz acquisition records. Each of the 27,535 available cycles has 128 samples. The timestamps are uniform *within each cycle* at the precision tested, but the per-cycle interval varies; the local files do not document the transformation from the dataset release’s stated 1 Hz sampling.
- The workbooks have 67 feature columns plus `label`, with the expected feature header order. The six workbooks contain 26,937 rows; the prepared MAT files contain 27,535 cycles. The 598-row net difference is entirely in batch 6, which has 8,344 prepared charge cycles but 7,746 workbook rows. Equal row counts in batches 1–5 do not establish cycle identity.
- Existing candidate-to-workbook MAE/RMSE comparisons are **diagnostic only**. They use positional pairing for equal-count profiles and capacity matching for some unequal-count profiles. No paired row is identity-verified.

The per-feature provenance and diagnostic metrics are in the [67-row CSV](./member4_scientific_provenance_audit.csv) and [machine-readable JSON](./member4_scientific_provenance_audit.json).

## Classification scheme

This scheme classifies the formula currently displayed/implemented, not the truth of the original Excel formula:

| Class | Meaning in this audit |
|---|---|
| **A — Verified directly** | An authoritative source explicitly defines this exact workbook feature and its matching calculation context. |
| **B — Same mathematical operation supported** | A source states the same algebraic operation, but the source does not establish that it generated this workbook feature or that its signal segment, samples, preprocessing, units, or numerical convention match. |
| **C — Candidate only** | A reproducible engineering interpretation exists, but no inspected source supports the same complete feature definition. |
| **D — Proxy/approximation** | The code computes a diagnostic surrogate for a feature whose original definition is unknown. |
| **E — No implemented expression** | No calculation is currently available. |

Accordingly, **Class B is not “partially verified”** and no Class B row may be promoted to Verified. Source location, uncertainty, validation status, and evidence needed are recorded separately for every row in the CSV and JSON.

## Primary evidence inspected

| Ref. | Source and location | What it establishes | What it does not establish |
|---|---|---|---|
| **S1** | [SOHbenchmark repository at inspected commit `62230dd`](https://github.com/wang-fujin/SOHbenchmark/tree/62230dd9a857f5c05ac641227b52ec2ffbeb9e15); local [README](../reference/SOHbenchmark/README.md) and [XJTU loader](../reference/SOHbenchmark/dataloader/XJTU_loader.py) | The benchmark consumes prepared data. `get_features` reads `batch-*_features.xlsx`; `_parser_xlsx` separates feature columns and `label`. The MAT loader expects 128-element `relative_time_min`, `current_A`, `voltage_V`, and `temperature_C` arrays. The SOH loader divides capacity labels by a hard-coded nominal capacity of 2.0. | No 67-feature extraction equations, workbook generator, or per-row join between workbook and MAT data. The unit of the hard-coded 2.0 is not declared in that loader. |
| **S2** | [SOHbenchmark workbook-upload commit `611bb59`](https://github.com/wang-fujin/SOHbenchmark/commit/611bb5948fe4a7914486ded7be238db24faabb23) | The six feature workbooks were added as prepared data. | The commit does not include their generating script or formula specification. |
| **S3** | [XJTU authors’ preprocessing repository at inspected commit `e986a740`](https://github.com/wang-fujin/Battery-dataset-preprocessing-code-library/tree/e986a74054fb64c0f5134f2cc97f4643cd7699d2), especially `XJTUBatteryClass.py::get_CC_value`, `get_CV_value`, and `get_IC_curve*` | The author helpers contain CC/CV sample selectors and incremental-capacity (dQ/dV) calculations. The documented default CC selector includes current ≥3.9 A and voltage ≤4.199 V; CV selection uses voltage ≥4.199 V. | No mapping from these helper methods to the 67 workbook columns and no evidence that these methods generated the workbooks. dQ/dV is not either `*_devide_dt` workbook feature. |
| **S4** | [Official XJTU Zenodo dataset record 10963339](https://zenodo.org/records/10963339) and the official [XJTU dataset site](https://wang-fujin.github.io/) | Release-level dataset metadata, experiment descriptions, links to author preprocessing resources, and the stated 1 Hz acquisition rate referenced in the existing research record. | No exact 67-feature formulas, 67-feature workbook generator, workbook-to-cycle key, or documented transformation from the original release to the local 128-point MAT traces. |
| **S5** | Wang et al. (2024), *Nature Communications* 15, 4332, [article DOI](https://doi.org/10.1038/s41467-024-48779-z); [publisher supplementary information](https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-024-48779-z/MediaObjects/41467_2024_48779_MOESM1_ESM.pdf), Supplementary Note 2, printed p. 6 | Equations for that paper’s own selected-curve mean, sample standard deviation, skewness, kurtosis, selected-window duration, accumulated charge, endpoint voltage slope, and entropy. | No assertion that this is the SOHbenchmark Excel generator or that any of its columns are the corresponding named workbook feature. Its windows, sample conventions, and entropy probability definition do not establish the benchmark’s conventions. |
| **S6** | Wang et al. (2024), *Journal of Energy Storage* 77, 109884, [SOHbenchmark paper DOI](https://doi.org/10.1016/j.est.2023.109884); local [appendix PDF](../reference/SOHbenchmark/SOHbenchmark%20-%20Appendix.pdf) and [text extraction](../reference/SOHbenchmark/appendix_extracted.txt) | The supplied appendix begins Appendix B “Feature engineering” but proceeds to Appendix C results without equations for this schema in the inspected text. The main repository loader consumes prepared workbooks. | No exact 67-feature equation table or feature-generator implementation. |
| **S7** | Member 4 candidate code: [feature registry](../scripts/member4_xjtu/feature_definitions.py), [segment selector](../scripts/member4_xjtu/segments.py), [extractor](../scripts/member4_xjtu/extractor.py), [loader](../scripts/member4_xjtu/loader.py), and [API metadata](../backend/formula_explorer_api.py) | What this project currently calculates, its candidate units and segment conventions, interpolation/integration choices, and provenance warnings. | It is implementation evidence for our candidate only, not primary evidence for the original workbook. |
| **S8** | Existing [original formula recovery evidence](./member4_original_formula_recovery/source_evidence.csv), [per-feature evidence ledger](./member4_original_formula_recovery/feature_evidence.csv), and [supplement mapping](./member4_supplementary_pdf_inspection/feature_mapping.csv) | Search coverage, exact original-formula status, source authority limits, and feature-by-feature related-method screening already recorded in the repository. | A repository search cannot prove that private, deleted, or inaccessible source code does not exist. |

## Dataset integrity audit

The data inspection used the six local MAT files under `reference/SOHbenchmark/data/XJTU/charge/`, the six corresponding workbooks under `handcraft_features/`, and the Member 4 `load_batch` parser. Workbook formulas/comments/defined names and numeric missing/duplicate rows were checked independently.

| Batch | Profiles / sheets | Prepared MAT cycles | Workbook rows | MAT samples per cycle | Workbook feature columns | Missing workbook cells | Duplicate complete workbook rows |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 8 | 3,211 | 3,211 | 128 | 67 | 0 | 0 |
| 2 | 15 | 3,727 | 3,727 | 128 | 67 | 0 | 0 |
| 3 | 8 | 4,608 | 4,608 | 128 | 67 | 0 | 0 |
| 4 | 8 | 5,670 | 5,670 | 128 | 67 | 0 | 0 |
| 5 | 8 | 1,975 | 1,975 | 128 | 67 | 0 | 0 |
| 6 | 8 | 8,344 | 7,746 | 128 | 67 | 0 | 0 |
| **Total** | **55** | **27,535** | **26,937** | **128 each** | **67 each** | **0** | **0** |

Additional observed integrity facts:

- Every workbook has 68 columns: the canonical 67 feature headers, in registry order, followed by `label`. Across the six files: 55 sheets, 26,937 data rows, zero formula cells, zero cell comments, and zero defined names. Thus the workbooks contain stored values rather than usable Excel formula provenance.
- Every loaded MAT cycle passed the code’s structural checks: four equal-length arrays, at least two samples, finite channels and labels, and strictly increasing time. Across all profiles, 3,496,945 adjacent timestamp intervals were checked; none were nonpositive. No non-finite signal or capacity values were found.
- No exact repeated full `(time, voltage, current, temperature)` sample rows within cycles, or duplicate complete trace signatures across the available set, were found. This is not a claim that no sensor-level repeated values occur; repeated voltage/current readings alone are expected in plateaus.
- Each prepared trace has 128 samples. Within each trace, every time increment matched that trace’s own median increment within `rtol=1e-6`, `atol=1e-9`; intervals are therefore uniform within each prepared cycle under this test. The increments differ across cycles: observed range **0.0919–1.1849 min**, pooled median **0.3770 min**. This per-cycle result supersedes earlier broad descriptions of the prepared timestamps as nonuniform within each trace.
- The field names encode voltage in V, current in A, temperature in °C, and relative time in minutes. The capacity field is a scalar label; benchmark loader code divides it by 2.0 to form normalized SOH. This audit found no independent unit declaration in that loader for the constant 2.0.
- The local `charge` MAT files are the benchmark’s available prepared representation. No original 1 Hz sample stream, transformation script, or explicit source-cycle identifier linking it to the 128-point representation was found in the inspected local data tree. The official release’s 1 Hz statement and local prepared time steps cannot be reconciled from available lineage evidence.
- The MAT profile ordinal and workbook sheet ordinal are used by the benchmark loader as battery IDs. Inside the prepared MAT structs, the Member 4 loader assigns cycle indices by array order. No explicit cycle ID or cycle timestamp join was observed in the prepared MAT/workbook representation. Matching profile counts or labels does not prove individual cycle identity.
- Batches 1–5 have equal raw/workbook row counts per profile; this permits a *positional diagnostic*, not a verified join. Batch 6 has 598 fewer workbook rows overall. The existing identity investigation reports 19,191 positional-unverified pairs, 7,129 capacity-match diagnostics, 617 unmatched workbook rows (489 ambiguous), 1,215 unmatched raw cycles in the batch-6 cohort, and **zero identity-verified pairs**.

### Capacity and preprocessing lineage

The prepared MAT stores `capacity` per cycle; the XJTU benchmark loader uses `label / 2.0` as normalized SOH. The feature workbooks store `label`. Capacity similarity is useful for diagnostic alignment but is not a unique identifier: repeated/rounded labels and missing cycles create ambiguity. The workbook row order’s correspondence to MAT array order is undocumented. No capacity matching, positional pairing, or nominal-capacity normalization is treated here as a scientific identity key.

## Implemented candidate calculations and sampling conventions

The expressions in the Formula Explorer are generated from the Member 4 registry and extractor. The JSON/CSV carry the candidate expression, source support scope, per-feature signal and units, current code location, candidate segment, uncertainty, evidence required, and validation diagnostic fields for every feature.

Observed candidate conventions:

- **CC:** default adaptive current plateau based on 0.975 × the 95th percentile of positive current, with a 4.199 V ceiling. A separate `author_documented` selector uses current ≥3.9 A and voltage ≤4.199 V. The latter reflects a source helper selector, not evidence that the Excel used it.
- **CV:** candidate interval begins at the first rising crossing of 4.199 V and continues to the stored trace endpoint.
- **dV:** candidate rising 3.9–4.0 V window within candidate CC.
- **dI:** candidate falling 1.0–0.9 A window within candidate CV.
- **Charge:** entire stored prepared charge trace.
- Segment boundaries use threshold crossings/interpolation as implemented in `segments.py`; disjoint runs may be combined for some calculations, while duration/rate features that require a contiguous interval can be unavailable.
- Energy uses trapezoidal integration of interpolated \(V I\); charge uses trapezoidal integration of current. Time is in minutes and the integral is divided by 60 for Wh/Ah.
- Means, standard deviations, skewness, kurtosis, `t_mean`, and entropy use 257-point uniform-time interpolated grids. Standard deviation is population (`ddof=0`); skewness is the biased standardized third central moment; kurtosis is Pearson, not excess.
- Derivative-named candidates use interpolated endpoint differences divided by candidate interval duration, in V/min or A/min.
- Entropy candidates use Shannon entropy of a 16-bin equal-width histogram with natural logarithms (nats). This is a diagnostic proxy only; the original entropy signal, normalization, estimator, bins and log base were not recovered.

These are **implementation facts**, not claims about the source workbook. Exact assumptions and equations vary by feature; consult the 67 row records rather than assuming all members of a feature group share a source definition.

## Source support and feature classification

Supplementary Note 2, p. 6 of S5 defines formulas for its own short-window feature method. The note includes:

- arithmetic mean of selected curve samples;
- sample standard deviation using \(n-1\);
- printed skewness and kurtosis formulas using its specified \(\sigma\) and denominators;
- \(\Delta t=t_{\mathrm{end}}-t_{\mathrm{start}}\);
- accumulated charge \(\Delta Q=\int I\,dt\);
- endpoint voltage slope \((V_{\mathrm{end}}-V_{\mathrm{start}})/(t_{\mathrm{end}}-t_{\mathrm{start}})\);
- generic curve entropy \(-\sum p_i \log(p_i)\), without a complete probability/binning convention.

The paper’s voltage window, current window, sample conventions, feature schema, and code pipeline do not establish identity with the SOHbenchmark 67-column workbooks. For example, the candidate standard deviation is population-based while S5 prints a sample standard deviation; candidate entropy specifies 16 equal-width bins while S5 does not define its \(p_i\) sufficiently to reproduce it. The four entropy candidates are therefore D, not B. No candidate is A.

Classification totals for the **implemented candidate expression**:

| Class | Count | Interpretation |
|---|---:|---|
| A | 0 | No exact original workbook formula and context verified. |
| B | 14 | Same operation appears in S5 p. 6: six voltage/current mean candidates, five current-integral candidates, two duration candidates, and the dV endpoint-rate candidate. Every one remains unverified as a workbook feature because the feature mapping, segment, or sampling details are not established. |
| C | 49 | Engineering candidates without an inspected source that supports the complete formula as implemented. |
| D | 4 | Entropy histogram proxies; original feature definitions remain unknown. |
| E | 0 | All 67 names currently have a computed candidate expression or explicit entropy proxy; this does not mean original formulas are available. |

**Original-benchmark formula status:** 0 verified; 0 partially verified; 63 candidate/unverified; 4 original entropy formulas unavailable. This source-status count is separate from the candidate-operation classes above.

## Existing candidate-to-workbook validation: diagnostic only

Existing scripts compare candidate outputs to workbook values. Those metrics test numerical agreement under a chosen alignment, not formula identity. The two available cohorts in `reports/member4_feature_error_analysis/feature_error.csv` are:

1. `positional_unverified`: 19,191 valid observations for most features, using equal-count profile row/index pairing. Matching counts do not prove equal origins, omissions, or order.
2. `capacity_match_diagnostic`: 7,129 capacity-matched diagnostic observations for most features. Capacity matches can be repeated or ambiguous and do not prove cycle identity.

For example, the existing analysis reports `CC_energy` relative MAE of approximately 1.08% in the positional-unverified cohort and 2.14% in the capacity-match-diagnostic cohort. These figures are intentionally not interpreted as formula validation. Per-feature diagnostic metrics are carried into the CSV/JSON; cohort values must remain separate rather than being presented as verified references.

No experiment in this audit independently reproduces an original workbook value from an author-identified raw cycle using the original generating code. Passing tests validates the behavior of our implementation against test expectations, not the provenance of those expectations.

## Independent validation opportunities

| Opportunity | What it can validate | Required signals | Independence and comparison | Main limitations |
|---|---|---|---|---|
| S5 p. 6 equations | The stated algebraic operation for selected-window mean, sample std, charge integral, duration, voltage slope, and generic entropy. | S5’s own selected voltage/current curves and exact time window. | Independent published methodology. Reimplement its printed equations separately and compare against a direct calculation from its paper-specific data, if that data is available. | It does not validate the workbook’s 67 features; the sampling, window mapping, entropy probability semantics, and several conventions differ or are unspecified. |
| S3 author preprocessing helpers | CC/CV selectors and IC/dQ/dV helper behavior. | Source-cycle current, voltage, time and helper parameters. | Author-provided reference implementation. Compare selected indices/threshold crossings to a separate implementation of the exact helper. | It does not calculate the 67 workbook features or prove workbook segment definitions. The helper is an independent reference only for itself. |
| Original 1 Hz XJTU release plus documented preprocessor | The transformation from original acquisition to prepared 128-sample MAT traces, sampling/time units, and cycle order. | Original source IDs, timestamps, voltage, current, temperature, and labels/capacity. | Independent data lineage reference once release source IDs and preprocessing steps are known. Compare signal values, time intervals, and cycle sequence after replaying the published transformation. | Original acquisition and a traceable local mapping are not currently present; this cannot be resolved by comparing arrays without identifiers. |
| Synthetic analytic traces and independent numerical integration | Correctness of candidate code’s arithmetic, endpoint interpolation, unit conversion, moment conventions, and missing-window behavior. | Constructed time/signal arrays with known analytic integrals and moments. | Independent expected values can be derived analytically or by a separate implementation. Compare outputs within numeric tolerances. | Validates software arithmetic only; cannot establish that the workbook used those formulas, signals, or segments. |
| Author-provided workbook generator and cycle mapping (not currently located) | Exact reproduction of workbook feature cells. | Generator/version/dependencies, matching raw trace identifiers, original formula parameters. | Strongest independent reproduction: run the original code on an author-identified input, compare all intermediate values and final workbook cells. | This evidence is the primary missing source. Without it, current numerical comparisons cannot verify the formulas. |

## Prioritized next validation experiments

### Priority 0 — Obtain provenance needed to make an original-value test possible

Request from the SOHbenchmark authors the exact script/notebook/version that generated the six `handcraft_features` workbooks and a cycle-level key linking each workbook row to its source trace. Request signal/phase definitions, units, timebase and resampling, boundary-crossing rules, integration method, statistical conventions, entropy estimator, and missing/rest handling. In parallel request the XJTU authors’ original-to-prepared 128-sample preprocessing lineage and cycle identifiers. Preserve the response or source archive with version/checksum. Do not treat filenames, equal counts, row order, or capacity labels as a substitute.

### Priority 1 — First feature experiment after obtaining an authoritative join: `CC_Q`

Use **CC_Q** as the first target because the independent S5 p. 6 method states accumulated charge as \(\Delta Q=\int I\,dt\), and the XJTU author helper documents a CC sample selector. These are only related-method references until the workbook mapping is established.

Exact protocol:

1. Select one batch-1 workbook row and source cycle with an author-provided unique identity key; do not select by row position or capacity alone.
2. Freeze the original generator version, data/preprocessing version, signal units, and exact CC boundary convention.
3. Independently reimplement its documented current integration and unit conversion from the identified original signal data. Retain all selected timestamps, current samples, boundary interpolation, panel integrals, and conversion factors.
4. Run both the original feature generator and independent reimplementation on that exact source cycle. Compare the resulting CC_Q to each other and to the mapped Excel cell; report absolute/relative error and all intermediate values.
5. If the original code cannot be obtained, report the experiment as blocked at provenance acquisition. A Member 4 candidate-versus-Excel comparison can still be run as a diagnostic, but it cannot graduate the feature to verified.

After CC_Q, repeat the same process for `CC_energy`, then statistical/segment-dependent groups. Entropy requires a separately specified source estimator before any numerical reproduction is possible.

### Priority 2 — Independently test numerical implementation, not source equivalence

Create a separate validation protocol for the candidate extractor using analytically integrable constant/linear signals, uniform and irregular timestamp arrays, and threshold crossings between samples. Compare to closed-form charge/energy integrals and independently coded moment calculations. Keep this as software correctness evidence, not original benchmark formula validation.

## Files and limitations

This audit created only:

- `reports/member4_scientific_provenance_audit.md`
- `reports/member4_scientific_provenance_audit.csv`
- `reports/member4_scientific_provenance_audit.json`

No source formulas, API/UI code, existing reports, feature metadata, workbooks, or teammate files were modified. The current branch and dirty worktree were preserved. No commit or push was performed.

### Direct answers

1. **What is scientifically verified?** Dataset file structure, observed prepared-trace values/units encoded in field names, code behavior of the current candidate implementation, and related mathematical operations described by published/source code references. No original workbook feature formula is verified.
2. **What remains unverified?** All 67 original formulas and their segment/sampling conventions; the raw 1 Hz to prepared 128-point lineage; and cycle identity between every workbook row and prepared MAT cycle.
3. **Which group should be validated first?** `CC_Q`, after authoritative source formula and cycle identity are obtained.
4. **Next exact scientific validation experiment?** Obtain the original feature-generation source and identity key, then independently recompute one source-identified batch-1 `CC_Q` and compare against both the original generator output and its mapped Excel cell.
5. **Files created or modified?** Only the three audit deliverables listed above were created; no existing files were modified.
