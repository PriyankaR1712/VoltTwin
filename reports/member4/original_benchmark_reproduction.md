# Original SOHbenchmark Feature Reproduction — Phase 3

## Result

**Status: BLOCKED.** The inspected SOHbenchmark source consumes the precomputed
XJTU feature workbooks but does not generate them. No authoritative original
formula for `CC_Q` and no authoritative workbook-row-to-prepared-cycle mapping
were found. Therefore, no original `CC_Q` workbook value can currently be
independently reproduced from a cycle known to be the one used to create that
row.

This is a bounded finding about inspected local files, repository history, and
the recorded source searches. It does not establish that no private,
unindexed, deleted, or otherwise unavailable source exists.

## Evidence and distinctions

| Question | Finding | Evidence and scope |
|---|---|---|
| Was original feature-generation source code found? | **No, not in inspected sources.** | The pinned SOHbenchmark repository history records the six workbooks as uploaded precomputed data. The local [`XJTU_loader.py`](../../reference/SOHbenchmark/dataloader/XJTU_loader.py) reads Excel sheets and normalizes their values; it does not calculate the features. The source inventory in [`source_evidence.csv`](../member4_original_formula_recovery/source_evidence.csv) records the inspected sources and their limits. |
| Is there an authoritative definition for original `CC_Q`? | **No.** | The formula-recovery audit records the original equation, signal, segment, units, integration convention, and boundaries as unknown. The candidate extractor has an `CC_Q` interpretation, but this is not evidence that it is the workbook formula. See [`feature_evidence.csv`](../member4_original_formula_recovery/feature_evidence.csv). |
| Was authoritative cycle identity established? | **No: 0 verified row/cycle pairs.** | Prepared MAT cycle structs expose relative time and signal arrays plus scalar capacity; workbook rows expose feature values and `label`. Neither has a cycle join key in the inspected prepared files. |
| Were diagnostic associations retained? | **Yes, explicitly unverified.** | The row-level [`cycle_identity_audit.csv`](./cycle_identity_audit.csv) lists candidate positions, capacity differences, ambiguous candidates, and unmatched records. Its `authoritative_identity_verified` column is `false` for every record. |
| Was `CC_Q` reproduced? | **No; blocked before comparison.** | Both source formula provenance and identity-mapped reference row are missing. No absolute or relative reproduction error exists to report. |

### Source and workbook inspection

- [`reference/SOHbenchmark/README.md`](../../reference/SOHbenchmark/README.md)
  says the supplied data are preprocessed, and points to the XJTU dataset
  source. It does not specify the 67 workbook equations or their row mapping.
- [`reference/SOHbenchmark/dataloader/XJTU_loader.py`](../../reference/SOHbenchmark/dataloader/XJTU_loader.py)
  reads feature workbooks by sheet and consumes the `label` column. The raw
  charge-MAT parser reads `relative_time_min`, `current_A`, `voltage_V`,
  `temperature_C`, and `capacity`; it does not read a shared row/cycle key.
- The inspected six workbooks contain 67 feature columns plus `label`, and
  their sheets contain no observed explicit cycle identifier or workbook
  formula cells. Workbook metadata such as creator/editor names and timestamps
  is provenance metadata, not formula or row-identity evidence.
- The repository-history/source inventory records the workbook upload commit
  and the absence of a generator in the inspected history. This does not rule
  out uninspected private or inaccessible author materials.
- The XJTU preprocessing library documents some charge-phase helpers, but the
  inspected code does not tie those helpers to the workbook's 67 columns.
  Likewise, a paper or codebase with a different feature set is not evidence
  for this workbook schema.

## Cycle identity audit

The audit covered **55 profiles**, **27,535 prepared MAT cycles**, and
**26,937 workbook rows**. The batch-2 profile count is different from the other
batches, so the data contain 55 profiles rather than 48.

| Classification | Count | Interpretation |
|---|---:|---|
| Authoritatively verified workbook-row/cycle pairs | **0** | No shared explicit key, timestamp, or author-provided crosswalk was found. |
| Same-index positional candidates | **19,191** | Existing diagnostic alignment for equal-count profiles; equal counts and ordinal positions do not prove a shared origin or absence of dropped records. |
| Unique monotone capacity candidates | **7,129** | Existing diagnostic matching within `1e-6` capacity tolerance; capacity is not a unique identifier. |
| All helper-matched candidates | **26,320** | Sum of the two diagnostic candidate categories above; none is verified. |
| Ambiguous workbook rows | **489** | More than one remaining raw-cycle capacity met the diagnostic tolerance. |
| Other unmatched workbook rows | **128** | No unique remaining capacity candidate met the tolerance. |
| Total unmatched workbook rows | **617** | Includes 489 ambiguous and 128 unmatched rows. |
| Raw cycles unused by capacity diagnostic | **1,215** | Unused by the capacity-matching helper; this does not prove that no workbook row represents those cycles. |

The 19,191 positional candidates and the 7,129 capacity candidates must not be
used as ground-truth pairs. The counts measure helper behavior only. The
row-level CSV preserves the evidence and avoids converting diagnostic matches
into identity claims.

## `CC_Q` reproduction decision

Reproduction was **not scientifically justified**. The candidate implementation
currently describes `CC_Q` as a trapezoidal integral of current over a
constant-current-like segment with minutes converted to hours. The original
workbook may use a different segment boundary, sampling/interpolation rule,
current sign convention, integration method, or even a different definition.
The original source audit explicitly leaves these conventions unknown.

Even if a candidate value numerically agreed with a workbook row, the result
would not establish a correct formula or same-cycle comparison without the
original formula and row/cycle identity. Consequently:

- No raw-cycle value is presented as an original benchmark reproduction.
- No reproduction test was added; there is no authoritative expected output
  against which such a test could assert.
- `reports/member4/feature_reproduction_results.csv` was not created because
  no actual source-backed reproduction occurred.
- No absolute error, relative error, or feature-level reproduction status of
  `VERIFIED` is claimed.

## Exact blockers and evidence needed

1. **Original formula and extraction definition:** obtain a versioned author
   script/notebook or a source document that explicitly defines the
   67-column workbook schema, including `CC_Q`, signals, segment boundaries,
   units, sample handling, and integration/statistical conventions.
2. **Row-to-cycle provenance:** obtain an author crosswalk or enough original
   identifiers to connect each workbook row to a specific raw/prepared cycle.
   A documented, reproducible preprocessing lineage must explain any filtering,
   omissions, resampling, and ordering between the released raw data, prepared
   MAT files, and workbook rows.
3. **Independent calculation:** after (1) and (2), compute `CC_Q` independently
   from that identified cycle using exactly the sourced definition, then report
   absolute and relative error and add a regression test with the evidence
   recorded.

The next best Member 4 task is to request the versioned feature-generation
source and row/cycle crosswalk from the SOHbenchmark/XJTU authors. Until those
are available, preserve existing comparisons as diagnostics and do not claim
original benchmark reproduction.

## Reproducibility and generated files

- [`cycle_identity_audit.csv`](./cycle_identity_audit.csv) was generated from
  the current prepared MAT/workbook inputs using the existing
  `_profile_pairs` diagnostic alignment in
  [`validation.py`](../../scripts/member4_xjtu/validation.py). Candidate joins
  are marked unverified; ambiguous and unmatched records are retained.
- [`original_benchmark_summary.json`](./original_benchmark_summary.json)
  stores the key counts and reproduction status.
- Existing focused identity-audit tests can be run with:

  ```powershell
  .\.venv\Scripts\python.exe -m pytest -q tests\member4_xjtu\cycle_identity\test_identity_investigation.py
  ```

The row-level CSV is an audit artifact, not a cycle crosswalk. Re-running the
same diagnostic logic does not elevate its candidates to verified identity.
