# Member 4 Final Contribution Audit

## Audit scope and workspace state

This report audits the Member 4 XJTU handcrafted-feature work currently present in the VoltTwin workspace. It does not certify original benchmark formulas or cycle identities.

- Repository: `C:\Users\acer\Desktop\VoltTwin`
- Branch at audit time: `feature/features-ui`
- Worktree was already dirty before this audit. `backend/main.py` and `frontend/src/App.tsx` were modified; the workspace also contained numerous untracked research, UI, backend, and data files. No such existing changes were edited, staged, reverted, or deleted for this audit.
- No branch switch, commit, or push was performed.
- The only files added for this audit are this report and [member4_final_contribution_audit.csv](./member4_final_contribution_audit.csv).

## Executive summary

Member 4's workspace contribution includes a 67-column candidate extractor, raw-cycle diagnostics, comparison and error-analysis tooling, a research evidence ledger, and an interactive Formula Explorer. The implementation separates candidate calculations from original-source claims. The work is useful for transparency, reproducibility of the candidate implementation, and investigating discrepancies.

The central scientific limitation remains unresolved: **no authoritative original implementation or equation set for the SOHbenchmark 67-feature Excel columns was located, and no authoritative row-to-cycle mapping was established.** Consequently, candidate-vs-workbook residuals are diagnostics, not verified formula error measurements. There are currently **0 Source Verified**, **0 Partially Verified**, **63 Candidate/unverified**, and **4 Original formula unavailable** features.

The complete current test suite was run during this audit and passed: **95 passed**. This verifies the tested software behavior, not the scientific provenance of the formulas or the identity of compared workbook/raw-cycle observations.

## Responsibility and implementation present

### Candidate feature extraction

The package under [scripts/member4_xjtu/](../scripts/member4_xjtu/) loads the prepared XJTU MAT charge traces and workbook sheets, validates the signal arrays, constructs candidate phase intervals, and computes all 67 feature names in the canonical schema.

The present candidate conventions include:

- Prepared-cycle channels: relative time in minutes, voltage, current, temperature, and a scalar capacity label. Inspected prepared cycles have 128 signal samples and nonuniform time intervals.
- CC: adaptive current plateau by default; an optional author-helper-style selector uses current at least 3.9 A and voltage at most 4.199 V. Neither is established as the workbook's segmentation rule.
- CV: first rising 4.199 V crossing through the stored trace end.
- dV: candidate rising 3.9-4.0 V window within CC.
- dI: candidate falling 1.0-0.9 A window within CV.
- Charge: full stored charge trace.
- Energy and charge: trapezoidal integration over stored timestamps and interpolated interval boundaries, with minutes converted to hours.
- Time and channel statistics: interpolation onto a 257-point uniform-time grid per candidate interval; population standard deviation (`ddof=0`), biased standardized skewness, and Pearson (not excess) kurtosis.
- Entropy: 16-bin equal-width histogram Shannon proxy in nats. It is explicitly diagnostic only; the original entropy estimator is unknown.
- Missing or disjoint candidate windows are not silently bridged; affected values may be unavailable.

These are documented candidate choices, not recovered workbook conventions. The package README and per-feature definitions record their assumptions.

### Formula Explorer and mathematical transparency

The Formula Explorer is integrated in the current workspace at the `#feature-explorer` route, with the corresponding backend router included in the FastAPI application. The existing UI/API surfaces:

- Search and browse the 67 feature names by group.
- Display candidate notation, a plain-language interpretation, implementation details, input/output units, variables, and calculation steps.
- Display candidate segment definitions and uncertainty warnings.
- Mark the four entropy definitions as original-formula-unknown and show the histogram only as a diagnostic proxy.
- Run a candidate calculation for a selected batch/profile/cycle and show input traces, selected candidate intervals, sample markers, sampling details, calculation intermediates, and the resulting candidate value.

The UI explicitly says that original workbook formulas are not verified and that displayed expressions are candidate implementations. A live shared-browser page at `http://127.0.0.1:5173/#feature-explorer` was readable during the audit. No dedicated Formula Explorer screenshot was saved as a repository artifact. Existing page renders under [member4_supplementary_pdf_inspection/](./member4_supplementary_pdf_inspection/) are screenshots of the supplement, not screenshots of the application.

## Validation and what the results mean

### Candidate-to-workbook comparisons

The candidate validation process checks workbook feature-column order, computes candidate values, and reports MAE, RMSE, maximum absolute error, relative error, and invalid candidates. It examined six batches and 55 profile/sheet ordinals. The existing comparison helper reported 26,320 candidate/workbook pairs:

- 19,191 equal-count pairs are positional and **unverified**.
- 7,129 batch-6 capacity-label matches are **diagnostic only**.
- 617 workbook rows were unmatched, including 489 ambiguous rows.
- 1,215 raw cycles were unmatched in the batch-6 comparison.
- **Zero pairs have identity-verified cycle-to-workbook correspondence.**

The candidate error-analysis report keeps positional and capacity-match cohorts separate, excludes ambiguous/unmatched rows, reports feature/batch/profile/cycle-decile metrics, counts invalid candidate values, and distinguishes confirmed observations from causal hypotheses. Its positional cohort includes 975 invalid candidate feature observations across feature accumulators. Sensitivity experiments compare prespecified candidate alternatives; they do not fit corrections to the Excel values or identify the original implementation.

### Trust classification

**Trustworthy as code/data observations, subject to the stated local scope:**

- The canonical workbook schema has 67 feature names.
- Candidate computations follow the implementation's documented rules.
- The local comparison counts, invalid-value counts, and reported metric calculations are reproducible outputs of the analysis scripts.
- The local prepared MAT representation has 128 samples per inspected cycle and nonuniform relative-time intervals.
- The inspected code and sources do not provide a verified workbook generator or authoritative cycle identity mapping.

**Diagnostic only, not ground-truth scientific validation:**

- Candidate MAE/RMSE, relative error, correlation, bias, and rankings against workbook rows. Positional pairs may refer to different cycles; capacity agreement is not a unique identifier.
- Batch/profile/cycle residual patterns and root-cause associations. They describe the current comparisons and cannot be attributed to formula defects without identity and source conventions.
- Sensitivity variants that happen to reduce error. They are not evidence of the original formula and must not be used to tune or relabel candidates.
- The 16-bin entropy proxy results. They cannot validate any original entropy equation.

## Research and formula recovery evidence

The current research artifacts include:

- Formula/source research and original formula verification reports.
- Candidate validation and feature error analysis, including CSV metrics, alignment cohorts, root-cause evidence, sensitivity results, and plots.
- Cycle identity investigation with mapping evidence, profile/schema audits, unmatched/ambiguous counts, and a summary JSON.
- Original formula recovery ledger with per-feature and entropy tables, source evidence, search log, and status totals.
- Supplementary PDF inspection with page-wise evidence, a 67-feature mapping table, the paper-linked PINN4SOH schema, source metadata, and rendered pages.

The inspected 2024 Nature Communications supplement defines a separate selected-window statistical-feature method (including statistics, integrated charge, duration, voltage slope, and generic curve entropy). It does not identify that method as the generator for the SOHbenchmark 67-column workbooks. The author-linked PINN4SOH XJTU CSV schema has 16 input features plus capacity; it is not the 67-column Excel schema. Related CC/CV helpers and mathematical resemblance do not establish original feature definitions.

Current feature classifications:

| Classification | Count | Interpretation |
|---|---:|---|
| Source Verified | 0 | No exact workbook-specific equation or implementation supported by authoritative evidence. |
| Partially Verified | 0 | No feature has sufficient direct evidence to verify a component of its original definition. |
| Candidate/unverified | 63 | Candidate interpretation exists; original formula/provenance remains unestablished. |
| Original formula unavailable | 4 | `CC_entropy`, `dV_entropy`, `CV_entropy`, and `dI_entropy`; original signal/estimator details remain unknown. |

This is a bounded search result, not proof that inaccessible, private, deleted, or unindexed source material does not exist.

## Tests and coverage

The full test command was run in the current workspace:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

**Result: 95 passed in 5.59s.**

Member 4-related tests cover:

- 67-feature schema and extraction on synthetic cycles.
- Segment creation, missing windows, irregular timestamp integration, entropy-proxy detail, and separation of author-helper and adaptive candidate CC selectors.
- Positional/capacity alignment classification and ambiguity safeguards.
- Error metrics, near-zero MAPE exclusions, sensitivity calculations, and explicit diagnostic variants.
- Formula-recovery schema/status generation and report outputs.
- Original-verification metric edge cases.
- Formula Explorer API schema/provenance, candidate calculation details, and invalid profile/cycle handling.

No frontend test files matching common `*.test.*` or `*.spec.*` patterns were found under `frontend/`. The suite passing therefore does not demonstrate cross-browser visual behavior or automated end-to-end UI behavior. The API tests and live shared-browser accessibility are positive evidence of current integration, not a substitute for UI regression tests.

## Limitations and unresolved questions

1. **Original 67-feature generator:** unavailable in inspected sources; exact equations, signal choices, units, phase boundaries, sampling, integration, and statistical conventions remain unknown.
2. **Cycle identity:** no shared cycle ID or authoritative join exists in inspected prepared MAT/workbook files; equal lengths and capacity agreement are insufficient to establish identity.
3. **Prepared-data lineage:** the official release describes 1 Hz acquisition, whereas prepared MAT cycles contain 128 samples with nonuniform relative times. The transformation from original source samples to prepared traces is undocumented in the inspected materials.
4. **Entropy:** all four original entropy definitions remain unknown, including signal, estimator, normalization, binning/probabilities, and logarithm base.
5. **Root causes:** segmentation, sampling, statistical convention, and alignment are plausible mechanisms for discrepancies, but none explains a particular feature residual with verified ground truth.
6. **Frontend regression evidence:** no frontend/browser test files were found; no app-specific screenshot artifact has been saved.
7. **Submission reproducibility:** individual script READMEs and commands exist, but a guide-specific, consolidated demonstration path and expected interpretation should be presented explicitly to the project guide.

## Prioritized remaining checklist

### Critical

1. **Obtain an authoritative 67-feature source or generator.**
   - Missing: direct source code, equations, or feature-to-workbook mapping from the workbook authors.
   - Why it matters: Without it, candidate formulas cannot be represented as original or verified.
   - Implementable now: No, not without new authoritative evidence. The evidence ledger and conservative labels are the appropriate current implementation.
   - Completion evidence: pinned source/document with equations or code mapped to all 67 columns; independent review; source references recorded feature by feature.
   - Show the guide: repository/source-history search coverage and the 0/0/63/4 status table; ask whether the author can provide the workbook generator.

2. **Establish authoritative cycle-to-row identity.**
   - Missing: a cycle ID, mapping file, or documented generation/order rule joining each workbook row to its raw/prepared cycle.
   - Why it matters: Current error metrics may compare different cycles and cannot establish formula accuracy.
   - Implementable now: No, not safely, absent IDs or provenance evidence. Do not replace this gap with positional or capacity matching.
   - Completion evidence: author-provided mapping or independently corroborated stable IDs/timestamps; ambiguity/unmatched accounting; tests covering the join.
   - Show the guide: the lineage diagram and observed counts, emphasizing zero identity-verified pairs.

### Important

3. **Present candidate comparison results with cohort caveats.**
   - Missing: no new data gap; the reporting obligation is to keep every metric labeled by alignment cohort and candidate status in slides/demo.
   - Why it matters: Large correlations or low relative errors can be misread as formula verification.
   - Implementable now: Yes, through documentation and presentation; no formula change is needed.
   - Completion evidence: every table/slide states positional or capacity-diagnostic cohort, sample count, invalid/missing counts, and lack of identity verification.
   - Show the guide: candidate validation summary, error-analysis alignment table, and root-cause evidence table.

4. **Make a single guide-facing reproducibility walkthrough.**
   - Missing: a consolidated run order and expected outputs across candidate extraction, validation, research ledgers, and Formula Explorer.
   - Why it matters: Reviewers need a repeatable demonstration and a correct interpretation of each artifact.
   - Implementable now: Yes; document environment/data prerequisites, exact commands, outputs, and known limitations.
   - Completion evidence: a clean-session walkthrough that runs the approved relevant commands and produces the documented files without modifying existing results unexpectedly.
   - Show the guide: Formula Explorer interaction plus candidate validation/research outputs, clearly labeled as unverified.

5. **Add frontend/browser-level regression coverage if required for submission.**
   - Missing: no frontend test files were found; current tests validate the API but not interactive rendering or browser workflows.
   - Why it matters: UI behavior can regress while Python/API tests continue to pass.
   - Implementable now: Technically yes, but it requires a separately approved frontend testing change and ownership coordination.
   - Completion evidence: an automated browser test covering loading, feature search/selection, unknown status, candidate calculation, and API error states.
   - Show the guide: live Formula Explorer and distinguish manual browser inspection from automated tests.

### Optional

6. **Save a dedicated Formula Explorer demo capture.**
   - Missing: no application screenshot/video artifact is stored; available page renders are from the supplementary PDF.
   - Why it matters: A stable visual artifact helps explain the UI without depending on the live development server.
   - Implementable now: Yes, without changing application behavior, after coordination on where to store the capture.
   - Completion evidence: dated screenshot(s) showing candidate warning, formula/variables/segments, and a candidate trace/calculation, with no sensitive data.
   - Show the guide: feature list, an entropy unknown example, and one raw-cycle calculation with the candidate-only warning visible.

7. **Continue source recovery only when new evidence becomes available.**
   - Missing: author-supplied workbook extraction code or clarified provenance.
   - Why it matters: Searches of current public/local sources are bounded and cannot rule out inaccessible material.
   - Implementable now: Further targeted research is possible, but it cannot manufacture a verified result.
   - Completion evidence: a newly located authoritative source that can be pinned, inspected, and tied to the exact workbook schema.
   - Show the guide: the existing source/search ledger and the new evidence required to change a status.

## Safe project-evaluation claims

The following statements are supported by the current workspace evidence:

- “I implemented a reproducible **candidate** extractor for the 67 named workbook features and exposed its assumptions and calculations in the Formula Explorer.”
- “The explorer shows candidate signals, units, mathematical notation, segment rules, and raw-cycle calculation diagnostics, and warns that these are not verified original workbook formulas.”
- “I compared candidate outputs with benchmark workbook values across the available batches, while separating unverified positional comparisons from capacity-based diagnostics and reporting ambiguous/unmatched observations.”
- “The candidate/error and sensitivity reports are descriptive diagnostics; cycle identity and original formula conventions are unresolved, so their errors do not establish formula correctness.”
- “I searched available author, benchmark, paper, supplementary, and local sources but did not locate the authoritative generator for the 67 columns.”
- “The complete current test suite passed 95 tests; that demonstrates tested software behavior, not scientific formula validity.”

Do **not** claim that the original 67 formulas were recovered, that any feature is verified, that candidate formulas exactly reproduce Excel, that positional/capacity pairs are ground truth, or that a suspected root cause has been proven.

## Guide demonstration outline

1. Open the Formula Explorer from the shared local app or project start page.
2. Point out the warning and status counts before selecting a feature.
3. Select a straightforward candidate such as `CC_energy`; explain the equation and units as candidate-only, then show its selected raw interval and calculation trace.
4. Select an entropy feature; explain that the histogram is only a diagnostic proxy and the original definition is unavailable.
5. Show the candidate validation and error-analysis reports. Explain that positional pairs are unverified, batch-6 capacity matches are diagnostic, and zero identities are verified.
6. Show the formula-recovery and cycle-identity reports as scientific honesty deliverables: they document the evidence boundary and what must be obtained next.
7. State that the 95-test pass is software evidence only.

## Evidence index

- Candidate package and commands: [scripts/member4_xjtu/README.md](../scripts/member4_xjtu/README.md)
- Feature schema and candidate definitions: [feature_definitions.py](../scripts/member4_xjtu/feature_definitions.py)
- Extraction math and calculation details: [extractor.py](../scripts/member4_xjtu/extractor.py)
- Segment policies: [segments.py](../scripts/member4_xjtu/segments.py)
- Candidate comparison report: [member4_candidate_validation.md](./member4_candidate_validation.md)
- Error/root-cause report: [member4_feature_error_analysis.md](./member4_feature_error_analysis.md)
- Cycle identity report: [member4_cycle_identity_investigation.md](./member4_cycle_identity_investigation.md)
- Formula research report: [member4_formula_research.md](./member4_formula_research.md)
- Original formula recovery report: [member4_original_formula_recovery.md](./member4_original_formula_recovery.md)
- Original formula verification report: [member4_original_formula_verification.md](./member4_original_formula_verification.md)
- Supplementary PDF inspection: [member4_supplementary_pdf_inspection.md](./member4_supplementary_pdf_inspection.md)
- Formula Explorer API implementation: [formula_explorer_api.py](../backend/formula_explorer_api.py)
- Formula Explorer UI implementation: [FormulaExplorer.tsx](../frontend/src/components/FormulaExplorer.tsx)
- Candidate extraction tests: [test_candidate_extraction.py](../tests/member4_xjtu/test_candidate_extraction.py)
- Analysis tests: [test_analysis.py](../tests/member4_xjtu/error_analysis/test_analysis.py)
- Cycle identity tests: [test_identity_investigation.py](../tests/member4_xjtu/cycle_identity/test_identity_investigation.py)
- Formula recovery tests: [test_recover.py](../tests/member4_xjtu/formula_recovery/test_recover.py)
- Formula Explorer API tests: [test_formula_explorer_api.py](../tests/test_formula_explorer_api.py)
