# Original XJTU SOHbenchmark Formula Recovery Audit

**Audit result: no original feature equations were recovered.** The current
VoltTwin equations remain candidate implementations. None is marked
`SOURCE_VERIFIED` or `PARTIALLY_VERIFIED`.

## Status counts

| Verification status | Features | Meaning |
|---|---:|---|
| `SOURCE_VERIFIED` | 0 | No exact workbook-feature formula with authoritative source context was found. |
| `PARTIALLY_VERIFIED` | 0 | Related helper operations are not sufficient to establish even a partial match to a workbook column without an explicit mapping. |
| `CANDIDATE_UNVERIFIED` | 63 | VoltTwin has a candidate expression, but the original equation and/or its exact extraction conventions were not recovered. |
| `ORIGINAL_FORMULA_UNKNOWN` | 4 | The original entropy definition, including signal, estimator and parameters, was not found. The current histogram calculation is only a diagnostic proxy. |

The row-level inventory is [original_formula_recovery.csv](./original_formula_recovery.csv);
machine-readable counts and source inventory are in
[original_formula_recovery_summary.json](./original_formula_recovery_summary.json).
The CSV preserves the current candidate expression separately from the
unrecovered original expression for every feature.

## Sources inspected

| ID | Source and location | What the source establishes | Authority and limitation |
|---|---|---|---|
| S1 | [SOHbenchmark author repository at inspected commit](https://github.com/wang-fujin/SOHbenchmark/tree/62230dd9a857f5c05ac641227b52ec2ffbeb9e15); local [README](../reference/SOHbenchmark/README.md) and [XJTU loader](../reference/SOHbenchmark/dataloader/XJTU_loader.py) | README describes supplied data as preprocessed. `XJTUDdataset.get_features` reads `data/XJTU/handcraft_features/batch-{batch}_features.xlsx`, takes feature columns and `label`, then normalizes them for model input. The MAT loader reads time, current, voltage, temperature and capacity. | Author benchmark source; authoritative for how the benchmark consumes these data, not for generating the 67 feature values. No formula-generation function is present in the inspected repository tree. |
| S2 | [Author commit adding XJTU workbooks](https://github.com/wang-fujin/SOHbenchmark/commit/611bb5948fe4a7914486ded7be238db24faabb23) | The six `batch-*_features.xlsx` files were added as uploaded, precomputed data. The commit does not contain a generator or equations. | Author repository history; authoritative for this commit's contents, not for the prior derivation of the values. |
| S3 | [Author XJTU preprocessing library](https://github.com/wang-fujin/Battery-dataset-preprocessing-code-library/blob/main/XJTUBatteryClass.py); local [inspected copy](../temp_xjtu_source/XJTUBatteryClass.py) | `get_partial_value` selects phases using `relative_time_min == 0`; `get_CC_value` uses charging-stage values and current/voltage selectors; `get_CV_value` has voltage/current selectors; `get_IC_curve1/2` calculates incremental capacity `dQ/dV`. | Author code is authoritative for these helper methods. It does not name or map any helper output to a SOHbenchmark workbook column, and `dQ/dV` is not proof of the distinct candidate `dV_dV_devide_dt`. |
| S4 | [Official XJTU dataset site](https://wang-fujin.github.io/); [Zenodo record](https://zenodo.org/records/10963339) | Dataset chemistry, charge/discharge protocols and sampling description. | Authoritative dataset documentation; does not define the 67 workbook equations or join workbook rows to cycles. |
| S5 | [Wang et al., Nature Communications (2024)](https://doi.org/10.1038/s41467-024-48779-z) | Describes a separate physics-informed prognostics method and its own statistical charging features. | Authoritative for that paper's method, but no mapping to the 67 SOHbenchmark workbook columns was found. The paper's features are not substituted for this schema. |
| S6 | [SOHbenchmark paper](https://doi.org/10.1016/j.est.2023.109884) and supplied [appendix PDF](../reference/SOHbenchmark/SOHbenchmark%20-%20Appendix.pdf) | The supplied PDF identifies Appendices A, B and C; the available 22-page text contains benchmark result tables. Exact feature names and equations were not found in the appendix text. | Benchmark-associated publication material, but the available appendix does not provide the requested 67-column formula specification. The main article's full text was not accessible through the available source endpoint during this pass. |
| S7 | VoltTwin [feature definitions](../scripts/member4_xjtu/feature_definitions.py), [extractor](../scripts/member4_xjtu/extractor.py) and [Formula Explorer API](../backend/formula_explorer_api.py) | Defines and computes the current VoltTwin candidate expressions and their assumptions. | Authoritative only for VoltTwin's implementation, not for original SOHbenchmark provenance. |
| S8 | Existing [source inventory](./member4_original_formula_recovery/source_evidence.csv), [search log](./member4_original_formula_recovery/search_log.csv), and exact-name searches scoped to the author repository | Records earlier searches for the feature names, source files and literature. Searches did not recover an exact generator. | Search results are discovery evidence, not proof that no private, unindexed, removed or unavailable source exists. |

### Direct workbook checks

All six local benchmark workbooks were opened and their sheets inspected.
They contain 67 feature headers followed by `label`; every sheet has the same
header order as VoltTwin's 67-name registry. Sheet counts are 8, 15, 8, 8, 8
and 8 for batches 1–6, respectively. Across the inspected workbooks there
were **zero spreadsheet formula cells, comments, or defined names**. These
checks confirm the released values/schema available locally, not the
calculation that produced them.

### Exact-name investigation

The audit searched for the named columns and groups, including
`CC_energy`, `CC_CCCT`, `dV_dV_devide_dt`, `CV_CVCT`,
`dI_dI_devide_dt`, `Charge_energy`, and entropy names, in local benchmark
code/reports and in the author GitHub code index scoped to
`wang-fujin/SOHbenchmark`. In the author repository, the relevant code hits
are the loader's generic `handcraft_features` workbook path; no exact
feature-name calculation implementation was found. Feature-name strings in
the Excel headers and downstream value tables are not formula evidence.

The source investigation also examined the author's preprocessing class.
Its phase selectors and incremental-capacity functions are useful descriptions
of those separate helpers, but there is no evidence that the benchmark's
67-column generator called them with the same windows or used their output
for a similarly named workbook column. Accordingly, no feature is assigned
`PARTIALLY_VERIFIED` based solely on a name or shared operation.

## Feature-group findings

The full per-feature record is the CSV. At group level:

| Group | Count | Original definitions recovered | Candidate formula notes |
|---|---:|---:|---|
| `CC` | 13 | 0 | Candidate charge integrals, timing, statistics, phase duration and entropy proxy. Exact CC selector, boundaries, sampling/statistical conventions and workbook mapping remain unknown. |
| `dV` | 13 | 0 | Candidate window features and endpoint rate are not proven to be the original workbook's dV definitions. Author `dQ/dV` helpers are a different named quantity and are not formula evidence. |
| `CV` | 13 | 0 | Candidate CV selector, current/temperature statistics, charge/energy and duration are not mapped to workbook equations. |
| `dI` | 13 | 0 | Candidate current-window and endpoint-rate definitions are not mapped to workbook equations. |
| `Charge` | 15 | 0 | Candidate full-trace expressions are not mapped to the original workbook's charging interval or definitions. |

For **all 67 rows**, original signal, original segment, original units,
statistical/integration convention, preprocessing and exact source equation
reference remain unknown. Candidate units and assumptions in the CSV refer
only to the current VoltTwin implementation. Where a potentially related
author helper exists, the CSV explicitly states that no mapping/equivalence
was established.

## Formula Explorer decision

No original formula was recovered, so Formula Explorer was **not changed**.
Its existing API and UI continue to show the candidate equation separately
from the unavailable original benchmark formula, retain the source-verification
warning, and classify the four entropy entries as original-formula-unknown.
The existing Formula Explorer API tests assert all 67 feature names, zero
source-verified features, candidate status for the 63 non-entropy entries,
and unknown-original status for the four entropy entries.

## Remaining evidence needed

To recover and verify original definitions, obtain from the benchmark authors
a versioned feature-generation script/notebook or a complete schema document
that explicitly connects each of the 67 workbook columns to its signal,
segment/window, units, sampling/interpolation, and numerical/statistical
conventions. A source-backed row-to-cycle crosswalk and preprocessing lineage
are additionally needed for independent value reproduction. Neither numeric
agreement nor a similar feature name can replace that evidence.

This audit is bounded to the local repository/data, pinned or linked author
sources, the available appendix, and the recorded exact-name searches. It
does not claim that inaccessible or private source material does not exist.
