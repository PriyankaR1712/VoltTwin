# Member 4 Final Evaluation Preparation — Mock Viva and Code Walkthrough

## Evidence boundary

This guide was cross-checked against the current Member 4 source and the five requested preparation/audit documents. Descriptions of equations and thresholds below are facts about the **current candidate implementation**, not evidence that the benchmark authors used those definitions.

- Formula recovery status in the existing evidence ledger: **0 Source Verified, 0 Partially Verified, 63 Candidate/unverified, 4 Original formula unavailable**.
- Cycle identity status: **0 identity-verified cycle/workbook pairs**. Equal-count positional comparisons are unverified; capacity-label matches are diagnostic.
- The last recorded full-suite result in the contribution audit is **95 passed**. That is software-test evidence, not scientific validation. This preparation task did not rerun the tests.
- The current implementation’s assumptions, outputs, and candidate labels can be explained confidently. Original formula provenance and cycle-to-workbook identity cannot.

## Code walkthrough

### Important implementation files

| File | Responsibility |
|---|---|
| [`feature_definitions.py`](../scripts/member4_xjtu/feature_definitions.py) | Defines the five groups, channels, statistic suffixes, the canonical ordered 67-name schema, and candidate formula/status metadata. |
| [`models.py`](../scripts/member4_xjtu/models.py) | Defines `CycleTrace`, `TimeInterval`, and `PhaseSegment`; validates aligned finite channels, increasing time, and interval boundaries. |
| [`loader.py`](../scripts/member4_xjtu/loader.py) | Reads `charge/batch-N.mat` and `handcraft_features/batch-N_features.xlsx`; converts MAT cycles into `CycleTrace` objects and checks workbook labels/profile counts. It does not reconstruct missing cycle IDs or preprocess the original acquisition data. |
| [`segments.py`](../scripts/member4_xjtu/segments.py) | Implements threshold crossing, interval selection, and the CC/CV/dV/dI/Charge candidate segments under `SegmentationPolicy`. |
| [`extractor.py`](../scripts/member4_xjtu/extractor.py) | Computes candidate integrations, time and channel statistics, rates, durations, entropy proxies, and optional calculation intermediates. |
| [`validation.py`](../scripts/member4_xjtu/validation.py) | Checks workbook feature columns, chooses the existing positional/capacity diagnostic pairing rule, calculates feature metrics, and writes the candidate validation report and CSV. |
| [`error_analysis/analysis.py`](../scripts/member4_xjtu/error_analysis/analysis.py) | Separates alignment cohorts; calculates feature, batch, profile, and cycle-decile error summaries; records unmatched rows/cycles; and compares predeclared sensitivity variants without fitting corrections. |
| [`extract.py`](../scripts/member4_xjtu/extract.py) / [`validate.py`](../scripts/member4_xjtu/validate.py) | CLI entry points for per-cycle candidate CSV extraction and all-batch candidate/workbook comparison. Their default batch list is 1–6. |
| [`formula_explorer_api.py`](../backend/formula_explorer_api.py) | Provides feature metadata, profile lists, and candidate calculation endpoints; validates selections and returns trace, segments, values, and diagnostics. |
| [`FormulaExplorer.tsx`](../frontend/src/components/FormulaExplorer.tsx) | React feature browser, selection controls, candidate-result display, signal plot, sampling summary, and calculation-detail panels. |
| [`main.py`](../backend/main.py) and [`vite.config.ts`](../frontend/vite.config.ts) | Register the Formula Explorer router and proxy frontend `/api` requests to the local FastAPI server (removing the `/api` prefix). These are shared app integration points, not proof of individual authorship. |

### Data loading and preprocessing flow

1. `loader.load_batch(batch, data_root)` restricts `batch` to 1–6, checks that the MAT and workbook files exist, and reads them using SciPy `loadmat(..., squeeze_me=True, struct_as_record=False)` and pandas `read_excel(..., sheet_name=None)`.
2. The loader expects a top-level `battery` array and checks that its number of profiles equals the number of workbook sheets. It enumerates profiles and cycles to create local ordinals such as `Sheet1` and `cycle_index=1`.
3. Each cycle reads `relative_time_min`, `voltage_V`, `current_A`, `temperature_C`, and the first finite scalar `capacity`. The arrays are flattened to one-dimensional float arrays; `CycleTrace.validate()` requires equal channel lengths of at least two, finite channel values, strictly increasing time, and a finite capacity label.
4. The loader checks that each workbook sheet contains a `label` column. It does not verify a cycle ID, timestamp join, or feature-row identity. In the comparison code, the enumerated MAT profiles and workbook sheets are traversed in order; equal counts do not prove that the two orders correspond.
5. Prepared MAT traces are already prepared inputs. The Member 4 loader does not transform an original 1 Hz acquisition trace into the inspected 128-point, nonuniform-time representation. The provenance of that preparation remains unresolved.

### Feature schema and segmentation

`feature_definitions.py` creates the canonical sequence from `GROUPS`, `CHANNELS`, and `STATISTICS`, then asserts 67 unique names. Counts are CC 13, dV 13, CV 13, dI 13, and Charge 15. The signal assignments and candidate meanings are definitions in this project, not recovered workbook metadata.

`segment_cycle(cycle, policy)` first validates the cycle and returns five `PhaseSegment` objects:

- **CC default:** current at least `0.975 × percentile_95(current)` and voltage at most 4.199 V. The optional `author_documented` mode uses current at least 3.9 A and voltage at most 4.199 V. The source helper documents a related selector; it does not establish that the workbook generator used it.
- **CV:** first rising 4.199 V crossing to the end of the stored trace.
- **dV:** first rising 3.9 V then 4.0 V threshold window inside a single CC interval.
- **dI:** first falling 1.0 A then 0.9 A threshold window inside a single CV interval.
- **Charge:** the complete stored trace interval.

Crossing times are linearly interpolated. Separate runs are kept separate rather than bridged. A missing threshold or a missing/disjoint parent phase can make a window unavailable. These rules make the candidate deterministic; they are not established original workbook boundaries.

### Candidate calculation path

`extract_cycle_with_details(cycle, policy)` validates the trace, calls `segment_cycle`, then computes each group through `_features_for_segment`. It returns:

1. `dict[feature_name, float | None]` containing all 67 names (unavailable calculations are `None`);
2. the five `PhaseSegment` objects; and
3. per-feature calculation details for the Formula Explorer.

For each interval, `_interval_arrays(..., dense=False)` uses stored interior timestamps plus interpolated endpoints. Energy integrates `V × I`; charge integrates `I`. `_trapezoid_details` computes each trapezoid panel over minutes, and the totals are divided by 60 to express Wh or Ah.

For statistics, `_interval_arrays(..., dense=True)` linearly interpolates to 257 equally spaced times **per interval**. `_moments` computes population moments (`ddof=0`), biased standardized skewness, and Pearson kurtosis (not excess kurtosis). If the variance is at or below machine epsilon, this implementation returns zero standard deviation, skewness, and kurtosis. Elapsed time is reset to each interval’s own start before the interval arrays are concatenated; these are explicit candidate conventions.

The four entropy outputs call `_entropy_proxy`: a 16-bin equal-width NumPy histogram of the selected dense-grid values, normalized nonzero counts, and `-Σ p ln(p)` in nats. The original entropy signal and estimator remain unknown. For CC/CV duration features, the implementation returns the duration only for a contiguous segment; a disjoint segment yields `None`, although diagnostic details still list its interval durations. The dV/dI rate outputs use the signal difference at candidate interval endpoints divided by interval duration.

If a group has no candidate intervals, `_features_for_segment` returns no values for it; `extract_cycle_with_details` then supplies `None` for that group’s feature names. It does not silently manufacture a result.

### Formula Explorer frontend-to-backend flow

1. `FormulaExplorer.tsx` loads the feature catalog once from `/api/formula-explorer/features`. It accepts the catalog only if its count and array length are both 67. It also loads profiles for the currently selected batch from `/api/formula-explorer/batches/{batch}/profiles`.
2. The Vite development proxy forwards `/api/...` to `http://127.0.0.1:8000` and removes `/api`; FastAPI’s router prefix is `/formula-explorer`.
3. The user searches or filters by group and selects a feature, batch, `SheetN` profile, and positive integer cycle. Batch/profile/cycle changes clear a prior result to avoid showing stale output for the new selection.
4. Clicking **Calculate candidate** requests `/api/formula-explorer/calculate` with `batch`, `profile`, `cycle`, and `feature_name` query parameters. The API restricts batch to 1–6, the profile string to the `Sheet<number>` pattern, and cycle to a positive integer; it rejects unknown feature names and out-of-range profiles/cycles.
5. The backend loads the batch (using a one-entry `lru_cache`), selects the ordinal trace, calls `extract_cycle_with_details`, and returns candidate values, segment evidence/intervals, selected sample indices, raw sampling statistics, and calculation intermediates. The response explicitly includes `is_candidate_calculation: true` and `values_are_original_benchmark_values: false`.
6. The UI shows the candidate equation/status, result and unit (or “Not available for this cycle”), selected candidate interval, raw MAT voltage/current/temperature plot, sampling summary, and operation-specific details such as trapezoid panels, statistical moments, or entropy-bin probabilities. It does not show a workbook value paired to that live cycle.
7. `fetchJson` parses API errors and displays an error message. The API returns a validation error for an unknown feature, unavailable-data errors when local input files are missing, and not-found errors for invalid profile/cycle ordinals.

### Validation and error analysis

`validate_batches` checks that each workbook’s non-`label` columns exactly match the canonical feature names/order. `_profile_pairs` uses equal-count positional pairing when counts are equal; if there are fewer raw cycles than workbook rows, it pairs none; if there are more raw cycles, it attempts unique monotone capacity-label matches with tolerance `1e-6`. Ambiguous or unmatched rows are excluded. None of these rules proves cycle identity.

The basic validation report calculates MAE, RMSE, maximum absolute error, and relative MAE (`MAE / mean(abs(benchmark)) × 100`) for finite candidate/benchmark values. `error_analysis/analysis.py` additionally reports signed error, quantiles, near-zero-filtered MAPE, correlations when defined, invalid counts, cohort-specific batch/profile/decile summaries, and declared sensitivity comparisons. The cohorts remain labeled `positional_unverified` and `capacity_match_diagnostic`. The analysis report states that sensitivity alternatives were not fitted or selected to reproduce Excel.

The existing audit records 27,535 prepared cycles and 26,937 workbook rows, with 19,191 positional-unverified pairs, 7,129 batch-6 capacity diagnostics, 617 unmatched workbook rows (489 ambiguous), 1,215 unmatched raw cycles in that batch-6 diagnostic cohort, and zero identity-verified pairs. These are counts from the documented local audit/helper, not identities or ground-truth error sample counts.

### Existing tests and their limits

Key tests include:

- [`test_candidate_extraction.py`](../tests/member4_xjtu/test_candidate_extraction.py): schema size, synthetic-cycle extraction, missing segments, irregular-time integration, capacity ambiguity, and separation of adaptive/documented CC selectors.
- [`test_formula_explorer_api.py`](../tests/test_formula_explorer_api.py): feature catalog status/schema, candidate response details, and invalid profile/cycle behavior.
- [`test_analysis.py`](../tests/member4_xjtu/error_analysis/test_analysis.py), [`test_identity_investigation.py`](../tests/member4_xjtu/cycle_identity/test_identity_investigation.py), and [`test_recover.py`](../tests/member4_xjtu/formula_recovery/test_recover.py): analysis metrics/outputs, identity-audit behavior, and recovery evidence/report structure.

The contribution audit records 95 tests passing in the last full-suite run. This rehearsal did not run the suite. Tests demonstrate the tested software behavior on their fixtures; they do not prove original formulas, cycle mapping, or scientific correctness. The audit found no frontend test files, so do not claim automated end-to-end UI coverage.

## Mock viva: 30 questions with follow-ups

Use the short spoken answer as a concise first response. Expand with the technical answer if the examiner asks for detail. The questions progress from easy to difficult.

### Easy (1–10)

#### 1. What was your individual responsibility?

- **Examiner is testing:** Whether you can state your scope without claiming the entire project.
- **Technically accurate answer:** My assigned Member 4 scope is the XJTU 67-feature engineering work: candidate extraction, formula transparency in Formula Explorer, candidate/workbook comparison and error analysis, and investigation of formula and cycle provenance. The source shows how these surfaces work; individual authorship of shared application integration should be established from team records, not inferred from the current worktree.
- **Short spoken answer:** “My scope was the XJTU 67-feature candidate pipeline, Formula Explorer, and the associated validation and provenance investigation.”
- **Possible follow-up:** Which parts belong to the rest of the team?
- **Strong honest response:** “VoltTwin also has shared backend, frontend, and modeling work. I can describe the interfaces my contribution uses, but I won’t claim ownership of other members’ components without the team’s assignment record.”

#### 2. What are the 67 features?

- **Examiner is testing:** Understanding of the schema rather than just the number.
- **Technically accurate answer:** They are the named feature columns in the supplied XJTU handcrafted-feature workbooks, represented in a canonical ordered tuple in `feature_definitions.py`. The groups are CC, dV, CV, dI, and Charge, with 13, 13, 13, 13, and 15 names respectively. The schema does not tell us the exact generating formulas.
- **Short spoken answer:** “They are the 67 workbook feature names organized into five groups; their names are known, but their exact original equations are not.”
- **Possible follow-up:** Why implement them if their formulas are unknown?
- **Strong honest response:** “The code implements clearly labeled candidate interpretations so the calculations and assumptions can be inspected and compared. It does not present them as recovered originals.”

#### 3. What does Formula Explorer do?

- **Examiner is testing:** Whether the UI’s purpose and scientific boundary are clear.
- **Technically accurate answer:** It browses the feature catalog, displays candidate notation and assumptions, lets a user select a batch/profile/cycle, and shows the candidate extractor’s result, trace, selected interval, sampling details, and calculation intermediates. It does not establish a matching workbook row or display a verified benchmark value for that live cycle.
- **Short spoken answer:** “It is an interactive explanation and candidate-calculation tool, not a verified benchmark reproduction screen.”
- **Possible follow-up:** What prevents users mistaking the displayed equation for the original?
- **Strong honest response:** “The UI labels it candidate/unverified, says the original formula is unavailable, and the calculation response explicitly marks the result as not an original benchmark value.”

#### 4. Which signals are present in a prepared cycle?

- **Examiner is testing:** Whether you know the input data model.
- **Technically accurate answer:** `CycleTrace` contains relative time in minutes, voltage in volts, current in amperes, temperature in degrees Celsius, and a scalar capacity label. `loader.py` reads these from the prepared MAT cycle fields.
- **Short spoken answer:** “The prepared trace has time, voltage, current, temperature, and a capacity label.”
- **Possible follow-up:** Does the loader resample the trace?
- **Strong honest response:** “No. It flattens the stored fields and validates them; the prepared MAT representation is already prepared upstream.”

#### 5. How many features are in each group?

- **Examiner is testing:** Basic schema familiarity.
- **Technically accurate answer:** CC 13; dV 13; CV 13; dI 13; Charge 15; total 67. `feature_definitions.py` constructs these and raises if the names are not 67 unique entries.
- **Short spoken answer:** “Four groups have 13 each, and Charge has 15, giving 67.”
- **Possible follow-up:** Are the group prefixes proof of the original charge segments?
- **Strong honest response:** “No. The prefixes come from the workbook names. The implemented segment interpretations remain candidates.”

#### 6. What does the tool show when a candidate value cannot be calculated?

- **Examiner is testing:** How missing data and missing segments are handled.
- **Technically accurate answer:** An absent candidate segment causes that group’s values to be unavailable (`None`). The API serializes these as `null`; the UI displays “Not available for this cycle.” Missing or disjoint parent windows are not silently bridged.
- **Short spoken answer:** “It reports the candidate as unavailable instead of filling in a fabricated value.”
- **Possible follow-up:** Could that bias your comparison metrics?
- **Strong honest response:** “Yes, missing candidate observations affect the valid sample count. The reports track invalid candidate counts; they should be stated with every metric.”

#### 7. What is the status of the original formulas?

- **Examiner is testing:** Scientific honesty and formula provenance.
- **Technically accurate answer:** The evidence ledger reports zero source-verified, zero partially verified, 63 candidate/unverified, and four original entropy formulas unavailable. No candidate becomes original merely because its numerical output is close to an Excel value.
- **Short spoken answer:** “None of the 67 original formulas is verified from an authoritative source.”
- **Possible follow-up:** Then why show formula equations at all?
- **Strong honest response:** “They are explicitly candidate equations that expose what our code computes. Showing the assumptions is more transparent than hiding them.”

#### 8. What is the status of cycle mapping?

- **Examiner is testing:** Whether you distinguish row ordering from identity.
- **Technically accurate answer:** Zero raw-cycle/workbook-row pairs are identity-verified. Equal-count rows are paired positionally only as an unverified diagnostic; unique capacity matches are also diagnostics because capacity is not a guaranteed unique cycle ID.
- **Short spoken answer:** “We have diagnostic pairings, but no authoritative cycle-to-row identity mapping.”
- **Possible follow-up:** Does matching cycle counts prove the order matches?
- **Strong honest response:** “No. Two lists can have equal lengths and different omissions, start points, or order.”

#### 9. What is the last recorded test result?

- **Examiner is testing:** Whether you can state test evidence precisely.
- **Technically accurate answer:** The audit records 95 tests passing in the last full-suite run. It includes Python extraction, API, analysis, identity, and recovery coverage, but no frontend end-to-end suite was found. This rehearsal did not rerun those tests.
- **Short spoken answer:** “The last audited full suite passed 95 tests; that verifies tested software behavior, not scientific formula validity.”
- **Possible follow-up:** Did those tests verify every real battery cycle?
- **Strong honest response:** “No. Many are unit/API tests on synthetic fixtures; the full pass does not prove all real cycles, formulas, or alignments.”

#### 10. What is the most important caveat to state in the demo?

- **Examiner is testing:** Whether you can frame results responsibly.
- **Technically accurate answer:** The current formulas are candidates and the workbook/raw-cycle correspondence is not authoritative. Thus candidate-to-Excel residuals are diagnostic rather than ground-truth formula errors.
- **Short spoken answer:** “These are candidate calculations compared under unverified alignment—not verified original formulas or ground-truth errors.”
- **Possible follow-up:** If the metric is low, can you call it accurate?
- **Strong honest response:** “I can say it agrees numerically under the stated diagnostic cohort. I cannot call it formula accuracy without source definitions and verified cycle identity.”

### Intermediate (11–20)

#### 11. Explain the default CC selector.

- **Examiner is testing:** Whether you know the actual code’s threshold rule.
- **Technically accurate answer:** The default `SegmentationPolicy` sets `cc_method="adaptive_candidate"`. `segment_cycle` computes the current threshold as 0.975 times the 95th percentile of the cycle current, then selects samples with current at least that threshold and voltage at most 4.199 V. Runs remain separate.
- **Short spoken answer:** “Default CC is an adaptive current plateau—97.5% of the 95th-percentile current—intersected with voltage at or below 4.199 V.”
- **Possible follow-up:** Why is 97.5% scientifically correct?
- **Strong honest response:** “It is a declared candidate rule, not a source-verified constant. It is reproducible and can be studied as a sensitivity choice, but I cannot call it the original threshold.”

#### 12. What is the “author-documented” CC option?

- **Examiner is testing:** Whether you overstate related source evidence.
- **Technically accurate answer:** The separate mode uses current ≥3.9 A and voltage ≤4.199 V, matching a related selector in the XJTU author helper. The implementation’s evidence string explicitly says it is not workbook formula evidence.
- **Short spoken answer:** “It is a related author-helper selector, not proof of the workbook’s CC rule.”
- **Possible follow-up:** Why not use it as the default since it is author code?
- **Strong honest response:** “The helper’s existence does not connect it to the 67-column Excel generator. Keeping it as a distinct option avoids turning related methodology into unsupported provenance.”

#### 13. How are CV, dV, dI, and full-charge regions selected?

- **Examiner is testing:** Understanding of `segments.py`.
- **Technically accurate answer:** CV runs from the first rising 4.199 V crossing to stored trace end. dV is a rising 3.9-to-4.0 V window within one CC interval. dI is a falling 1.0-to-0.9 A window within one CV interval. Charge is the complete stored trace. Threshold crossings are interpolated in time.
- **Short spoken answer:** “CV uses a rising voltage cutoff, dV and dI use candidate threshold windows inside their parent phases, and Charge uses the stored trace.”
- **Possible follow-up:** Where did the dV and dI thresholds come from?
- **Strong honest response:** “They are candidate interpretations, not definitions located in the original benchmark source. We should not present them as author-established.”

#### 14. How does candidate energy integration work?

- **Examiner is testing:** Numerical method and unit conversion.
- **Technically accurate answer:** At stored interior samples plus linearly interpolated interval endpoints, the code forms `V × I`, applies the composite trapezoidal rule using each timestamp difference in minutes, sums interval integrals, and divides by 60 to convert Wh-like minute integration to Wh. Candidate charge integrates current in the same way to Ah.
- **Short spoken answer:** “It integrates V times I—or I for charge—by trapezoids over actual timestamps, then divides by 60 because time is in minutes.”
- **Possible follow-up:** Is trapezoidal integration the workbook’s method?
- **Strong honest response:** “Unknown. It is the candidate method in the current extractor; original integration and sign conventions were not located.”

#### 15. Why use a 257-point grid for statistics?

- **Examiner is testing:** Awareness of nonuniform sampling and implementation choices.
- **Technically accurate answer:** The statistics interpolate each selected interval to 257 equally spaced timestamps before computing moments. This avoids applying an unweighted statistic directly to the irregular stored sample times, but it does not prove the workbook used this grid or weighting.
- **Short spoken answer:** “The candidate uses a uniform-time interpolation grid to define its statistical convention; 257 is an implementation choice, not a recovered benchmark setting.”
- **Possible follow-up:** Is interpolation equivalent to time-weighted statistics?
- **Strong honest response:** “It approximates uniform-time weighting for this candidate calculation, but it is not identical to every possible continuous-time estimator and is not known to match the workbook.”

#### 16. Which standard-deviation, skewness, and kurtosis conventions are used?

- **Examiner is testing:** Statistical definition details.
- **Technically accurate answer:** `_moments` uses the mean of centered powers. Standard deviation is population (`ddof=0`); skewness is the biased third central moment divided by variance to the 3/2 power; kurtosis is the fourth central moment divided by variance squared (Pearson, not excess). Near-constant values return zeros for standard deviation, skewness, and kurtosis when the second moment is below machine epsilon.
- **Short spoken answer:** “Population standard deviation, biased moment skewness, and Pearson kurtosis; degenerate variance is returned as zero by this implementation.”
- **Possible follow-up:** Is returning zero for constant-signal kurtosis mathematically universal?
- **Strong honest response:** “No. Higher standardized moments are undefined when variance is zero; zero is the implementation’s explicit fallback, not a universal convention or verified benchmark choice.”

#### 17. How is entropy calculated?

- **Examiner is testing:** Whether you know the proxy and its limitations.
- **Technically accurate answer:** The extractor makes a 16-bin equal-width histogram of dense-grid signal values, normalizes nonzero bin counts to probabilities, and sums `-p ln(p)` in nats. CC/dV use voltage in the candidate; CV/dI use current. The original signal, estimator, bins, normalization, and log base are unknown.
- **Short spoken answer:** “It is a 16-bin Shannon histogram proxy in nats, not the recovered original entropy.”
- **Possible follow-up:** Why not use the paper’s entropy equation?
- **Strong honest response:** “Related paper methodology does not identify this exact workbook schema, and its description does not specify enough estimator details to prove equivalence.”

#### 18. Describe the live API request and response.

- **Examiner is testing:** Frontend/backend integration knowledge.
- **Technically accurate answer:** The frontend calls `GET /api/formula-explorer/calculate` with `batch`, `profile`, `cycle`, and `feature_name`. Vite strips `/api`; FastAPI receives `/formula-explorer/calculate`. The response includes selected identifiers and capacity label, trace arrays, candidate segment metadata, all feature values, selected calculation details, raw sample indices, sampling statistics, and flags saying it is a candidate calculation and not an original benchmark value.
- **Short spoken answer:** “The UI sends batch, profile, cycle, and feature name; the API returns candidate values plus trace, segment, sampling, and calculation evidence.”
- **Possible follow-up:** Does the response include the matching workbook row?
- **Strong honest response:** “No. The live endpoint selects a prepared MAT ordinal and does not resolve or return an authoritative workbook row.”

#### 19. How are invalid API selections handled?

- **Examiner is testing:** Validation and error handling.
- **Technically accurate answer:** Query constraints restrict batches to 1–6 and cycles to positive integers; the profile must match `Sheet<number>`. Unknown feature names produce a 422 HTTP error, unavailable profile/cycle ordinals produce 404, and missing raw/workbook files are reported as 503 by the API. The frontend shows parsed error details.
- **Short spoken answer:** “Inputs are constrained at the API boundary, and invalid features or unavailable selections produce explicit HTTP errors rather than fabricated values.”
- **Possible follow-up:** What if the server returns invalid JSON?
- **Strong honest response:** “The frontend’s `fetchJson` catches JSON parsing failure and throws a clear invalid-response error for the UI to show.”

#### 20. How are candidate and workbook observations paired?

- **Examiner is testing:** Knowledge of validation logic and alignment caveats.
- **Technically accurate answer:** `_profile_pairs` pairs equal-length sequences by index and labels the method positional-unverified. If raw cycles are fewer than workbook rows, it pairs none. If raw cycles are more, it seeks unique monotone capacity-label matches within `1e-6`, retaining ambiguous and unmatched rows as excluded. This method does not establish identity.
- **Short spoken answer:** “Equal counts use unverified positional pairing; unequal counts use only unique monotone capacity diagnostics, with ambiguous rows excluded.”
- **Possible follow-up:** Why does it use capacity at all if it is not authoritative?
- **Strong honest response:** “It is a conservative diagnostic to explore candidate pairings when counts differ. We label it explicitly and do not promote it to ground truth.”

### Difficult (21–30)

#### 21. What exactly does a low MAE or high correlation establish here?

- **Examiner is testing:** Interpretation of comparison metrics.
- **Technically accurate answer:** It establishes numerical agreement or association for finite observations in the named candidate and alignment cohort, subject to the metric definition and exclusions. Since both formula provenance and cycle identity are unresolved, it does not establish accuracy against the original formula or same physical cycle.
- **Short spoken answer:** “It describes agreement under a diagnostic pairing rule; it does not verify the formula or the cycle identity.”
- **Possible follow-up:** Would a very high correlation solve the identity problem?
- **Strong honest response:** “No. Similar trends can occur across different cycles or repeated capacity regions. Correlation is not an identifier and cannot repair missing provenance.”

#### 22. Distinguish relative MAE from MAPE in the reports.

- **Examiner is testing:** Whether you know the metric implementation rather than just the labels.
- **Technically accurate answer:** Basic validation’s relative error is `MAE / mean(abs(reference)) × 100`. Error analysis also reports MAPE, but excludes near-zero references using a floor equal to the larger of `1e-12` and 1% of the median absolute reference. It reports the MAPE observation count and exclusions. Both remain cohort-dependent diagnostics.
- **Short spoken answer:** “Relative MAE scales total MAE by mean absolute reference; MAPE averages per-row relative errors after a near-zero safeguard.”
- **Possible follow-up:** Which one should you quote to an examiner?
- **Strong honest response:** “Only with its formula, valid sample count, excluded count where relevant, and alignment cohort. Neither should be called verified accuracy here.”

#### 23. What does the error-analysis sensitivity study do—and not do?

- **Examiner is testing:** Whether analysis became model/formula tuning.
- **Technically accurate answer:** It evaluates predeclared alternatives such as native versus uniform-grid statistics, rectangle versus trapezoid integration, statistical conventions, rate estimators, entropy proxy settings, and the distinct author-helper CC selector. It preserves the comparison pairs for paired sensitivity where applicable. It does not fit thresholds, offsets, or coefficients to workbook values or choose a “best” formula as original.
- **Short spoken answer:** “It measures how declared candidate choices change diagnostics; it does not tune a formula to Excel or recover provenance.”
- **Possible follow-up:** If one variant has the lowest error, why not use it?
- **Strong honest response:** “It may be reported as a lower-error diagnostic candidate on that cohort, but selecting it as original would be circular without source evidence and verified identities.”

#### 24. What do the 128 samples and the 1 Hz documentation imply?

- **Examiner is testing:** Data lineage and sampling interpretation.
- **Technically accurate answer:** The local prepared MAT cycles inspected contain 128 samples and nonuniform `relative_time_min` steps. Dataset documentation states 1 Hz acquisition, but the inspected repository evidence does not explain the transformation from acquisition data to these prepared traces. The candidate uses the time values actually stored and does not assume uniform one-second sampling.
- **Short spoken answer:** “The acquisition description and prepared representation are different layers; the transformation between them is not documented in the inspected materials.”
- **Possible follow-up:** Can you say the prepared trace is downsampled to 128 points?
- **Strong honest response:** “Not from current evidence. It has 128 samples, but without an authoritative transformation record I cannot say whether it was downsampled, filtered, selected, or otherwise transformed.”

#### 25. What is the confirmed finding versus a root-cause hypothesis?

- **Examiner is testing:** Evidence classification and causal reasoning.
- **Technically accurate answer:** Confirmed observations include the candidate implementation’s exact segmentation/statistical rules, the local data counts and sampling representation reported in the audit, and the existence of comparison residuals under the current pairings. Different original segmentation, time weighting, formula conventions, or preprocessing are plausible mechanisms, not proven explanations for any specific feature error.
- **Short spoken answer:** “We can reproduce the residuals under our declared candidates; we cannot attribute them to a confirmed cause without source formulas and identity.”
- **Possible follow-up:** Which suspected cause is most likely?
- **Strong honest response:** “I would not rank causes as established from these comparisons. Cycle identity and source conventions are unresolved confounders, so the responsible conclusion is that attribution remains open.”

#### 26. The loader zips profiles and sheets by order. Is that safe?

- **Examiner is testing:** Ability to identify a real provenance limitation in code.
- **Technically accurate answer:** The loader checks only that the MAT profile count equals the workbook sheet count. Validation and analysis iterate `zip(sheets.items(), profiles)`, so association is by enumeration order. The code does not verify that MAT battery ordinal and workbook sheet name identify the same physical battery, nor that cycle ordinals match workbook rows.
- **Short spoken answer:** “The implementation associates profiles and sheets by order after a count check; that is an operational convention, not a verified identity join.”
- **Possible follow-up:** Should you change it to capacity matching now?
- **Strong honest response:** “Not as ground truth. Capacity matching is not a unique identifier and changing alignment behavior would need new authoritative evidence and approval. The existing diagnostic behavior must remain clearly labeled.”

#### 27. What is a potentially subtle statistical assumption in disjoint intervals?

- **Examiner is testing:** Deep inspection of actual code.
- **Technically accurate answer:** `_interval_arrays` creates a 257-point grid separately for every interval. `_features_for_segment` concatenates these arrays, and the elapsed-time coordinate is reset to each interval’s own start. Consequently, simple means and moments give each interval 257 grid values regardless of its duration, rather than automatically weighting by duration. For duration features CCCT/CVCT, disjoint results are returned as unavailable.
- **Short spoken answer:** “For disjoint segments, the candidate concatenates equal-sized per-interval grids, so statistics are not duration-weighted; that is an implementation choice, not an original definition.”
- **Possible follow-up:** Does this affect every feature group?
- **Strong honest response:** “It matters when a selected phase is disjoint. The dV/dI candidate windows require a single parent interval; Charge is one full interval. CC can have multiple runs, so it is the clearest case.”

#### 28. Can your current results support a claim that one feature is scientifically valid?

- **Examiner is testing:** Whether you understand validation prerequisites.
- **Technically accurate answer:** They support statements about code behavior and diagnostic numerical comparisons, not source-level validity of a benchmark feature. To validate a formula, we need an authoritative equation/implementation tied to the exact column; to validate candidate outputs against Excel, we also need authoritative cycle-row identity and documented preprocessing.
- **Short spoken answer:** “No feature can currently be called verified; source formulas and cycle identity are both missing.”
- **Possible follow-up:** What is the concrete next research milestone?
- **Strong honest response:** “Obtain the original workbook generator or column-specific equations and a row-to-cycle mapping from the authors or maintainers, then implement an independent reference path and test it on verified pairs.”

#### 29. How do you separate your work from teammate contributions in a viva?

- **Examiner is testing:** Individual ownership and teamwork integrity.
- **Technically accurate answer:** I should describe my assigned Member 4 scope—XJTU candidate feature extraction, feature-level transparency, comparisons/error analysis, and provenance investigation. Formula Explorer is integrated with the project frontend/backend, but the shared route, API host, and other application/model components are not evidence of exclusive authorship. Exact attribution should follow the team’s assignment or contribution record.
- **Short spoken answer:** “I’ll explain my Member 4 feature-engineering and validation scope, and credit shared application integration and other modules to the team.”
- **Possible follow-up:** Did you implement the complete application?
- **Strong honest response:** “No. My contribution is a subsystem integrated into VoltTwin. I can explain its contracts and boundaries, but I won’t claim the whole frontend, backend, or prediction model.”

#### 30. What would change your conclusion from “candidate/unverified” to “verified”?

- **Examiner is testing:** Falsifiability and a rigorous verification plan.
- **Technically accurate answer:** A pinned authoritative source explicitly tied to the exact 67 workbook columns, specifying signals, preprocessing, segment boundaries, units, numerical/integration/statistical/entropy conventions, plus an authoritative mapping from workbook rows to raw/prepared cycles. Then we would implement the reference independently, test edge cases, retain missing/ambiguous counts, and compare on verified pairs without tuning to the workbook.
- **Short spoken answer:** “We need the original column-specific generator and an authoritative cycle mapping; numerical fit alone is insufficient.”
- **Possible follow-up:** What if you find the original code but no cycle mapping?
- **Strong honest response:** “Then formula provenance may be verified, but validation against workbook values remains inconclusive for any rows without verified identity. Those two evidence questions are separate.”

## Demo talking points

1. Start with the provenance banner: state that every displayed calculation is a candidate.
2. Show one conventional candidate such as `CC_energy`; explain the equation, stored-time integration, unit conversion, candidate interval, and what the UI’s intermediates demonstrate.
3. Choose a batch/profile/cycle as a prepared MAT ordinal. Explicitly say it does not identify the corresponding workbook row.
4. Show the trace, candidate shading, raw sample markers, observed nonuniform time steps, and calculation details.
5. Select an entropy feature and explain that the histogram is a diagnostic proxy, not the original estimator.
6. Open validation/error analysis only after explaining the cohort labels and counts; do not call the residuals accuracy.
7. Close with the two key evidence gaps: original feature generator and authoritative cycle-to-row mapping.

## Technical concepts to revise

- Composite trapezoidal integration for nonuniform time steps; units when time is in minutes.
- Linear interpolation at threshold crossings and interval endpoints.
- Difference between sample and population standard deviation; biased versus adjusted skewness; Pearson versus excess kurtosis.
- Degenerate/constant-signal moments and why standardized moments are undefined at zero variance.
- Shannon entropy, histogram estimator dependence, probability normalization, and nats versus bits.
- Relative MAE versus MAPE; near-zero denominators; valid/invalid observation counts.
- Why row position, profile count, and capacity labels are not authoritative physical cycle identifiers.
- Difference between a software unit test, numerical agreement, formula provenance, and scientific validation.
- Evidence classes: verified implementation behavior, candidate assumption, diagnostic association, and unresolved cause.

## Common mistakes to avoid

- Calling any candidate equation “the original formula” or “verified.”
- Saying that the supplement or related author helper generated the 67 Excel columns.
- Calling positional or capacity-label pairings “matched cycles” without the diagnostic qualifier.
- Reporting an MAE/RMSE without naming feature, cohort/alignment method, valid count, and candidate status.
- Claiming all 27,535 cycles or every workbook row was identity-validated.
- Saying the loader resamples raw 1 Hz data; it reads already-prepared MAT arrays.
- Treating 257-point statistics or 16-bin entropy as benchmark-author settings.
- Claiming sensitivity analysis selected or discovered the original formula.
- Treating 95 passing tests as evidence that the candidate formulas are scientifically correct.
- Claiming sole ownership of shared backend/frontend/model code without team contribution evidence.

## Final revision checklist

- [ ] Rehearse the 30 answers, especially the follow-ups for questions 20–30.
- [ ] Be able to explain `load_batch` → `CycleTrace.validate` → `segment_cycle` → `extract_cycle_with_details` without notes.
- [ ] Memorize the exact candidate thresholds and the two different CC modes.
- [ ] Explain which operations use native timestamps and which use the 257-point grid.
- [ ] Explain the entropy proxy, its units, and its unknown original definition.
- [ ] State the alignment cohorts and counts accurately; do not infer cycle identity.
- [ ] Open the provenance warning before showing a result in the live demo.
- [ ] Keep the candidate validation, identity, formula recovery, and audit reports ready as backup.
- [ ] Verify frontend, backend, local MAT/workbook files, and one usable candidate cycle before the evaluation.
- [ ] Do not modify code or scientific results during the demo.
- [ ] Confirm project/team contribution attribution with the group before describing other members’ work.
- [ ] If asked for evidence not present in the repository, say it is unresolved and name the evidence needed.
