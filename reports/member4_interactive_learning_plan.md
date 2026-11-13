# Member 4 Interactive Code Learning Plan

## Purpose and scientific boundary

This is a hands-on learning plan for understanding the Member 4 XJTU feature work from beginner level through viva practice. It is a plan for **you to perform**; reading it does not mean the exercises, browser demo, or rehearsal have already been completed.

The code implements candidate definitions for 67 workbook feature names. Research so far found **0/67 original formulas source-verified**, 63 candidate/unverified calculations, four original entropy definitions unavailable, and **0 authoritative cycle-to-workbook identity pairs**. Candidate-to-Excel comparisons are diagnostics. Passing software tests demonstrates covered software behavior, not scientific correctness. Keep these distinctions in every explanation.

## How to study

- Follow the modules in order. Each builds on the previous one.
- Keep this plan and the referenced source file open side by side in VS Code.
- Read a function once without trying to memorize it. On a second pass, write down its inputs, outputs, and assumptions in your own words.
- Run only small, targeted, non-destructive checks while learning. The default CLI scripts can write into existing report paths, so do not rerun them until you understand their outputs and have chosen a safe destination or are prepared for those outputs to be regenerated.
- Use synthetic test fixtures to understand code paths; do not treat them as physical battery evidence.
- At the end of each session, explain the module aloud without reading. Mark a checklist complete only when you can do the task and answer the question unaided.

## Learning journey

### Module 1 — Project architecture and complete data flow

**Goal:** Be able to narrate how data moves through the Member 4 contribution and how that subsystem connects to VoltTwin.

**What you must understand**

- The difference between the offline extraction/validation pipeline and the interactive Formula Explorer request path.
- Which files define schema, load data, segment cycles, compute candidates, compare outputs, provide API endpoints, and render the UI.
- That the live API calculation uses a selected prepared-MAT ordinal; it does not identify a matching Excel row.

**Study these files**

- [`member4_code_mastery_guide.md`](./member4_code_mastery_guide.md)
- [`member4_demo_walkthrough.md`](./member4_demo_walkthrough.md)
- [`feature_definitions.py`](../scripts/member4_xjtu/feature_definitions.py)
- [`loader.py`](../scripts/member4_xjtu/loader.py)
- [`segments.py`](../scripts/member4_xjtu/segments.py)
- [`extractor.py`](../scripts/member4_xjtu/extractor.py)
- [`validation.py`](../scripts/member4_xjtu/validation.py)
- [`analysis.py`](../scripts/member4_xjtu/error_analysis/analysis.py)
- [`formula_explorer_api.py`](../backend/formula_explorer_api.py)
- [`FormulaExplorer.tsx`](../frontend/src/components/FormulaExplorer.tsx)

**Beginner concepts**

- A module is a Python source file that other files can import.
- A function takes inputs and returns outputs; a pipeline is a sequence of function calls.
- The backend is the server-side code; the frontend is the browser interface.
- A data flow diagram shows transformations and dependencies, not scientific proof of the data's origin.

**Important functions/classes and responsibilities**

- `load_batch`: reads MAT profiles and Excel sheets.
- `CycleTrace`: stores one prepared cycle's signals and local ordinals.
- `segment_cycle`: finds candidate intervals.
- `extract_cycle_with_details`: returns feature values, segments, and calculation evidence.
- `validate_batches` and `run_analysis`: compare and summarize candidate values.
- Formula Explorer endpoints: expose feature catalog, profiles, and a candidate calculation.
- `FormulaExplorer`: fetches that data and renders controls/details/charts.

**Math, units, and variables**

At this architectural level, identify what the signals mean: `time_min`, `voltage_v`, `current_a`, `temperature_c`, and `capacity_label`. No new equation is introduced in this module.

**Exercises**

1. Draw the pipeline from MAT/XLSX input to a candidate feature value and to an error report.
2. Draw a separate sequence for a browser request from the React component through FastAPI to the extractor and back.
3. Explain why the live calculation flow and the workbook-validation flow are separate.

**VS Code practical task**

Use Explorer to open the files in the order above. Use “Go to Definition” on `extract_cycle_with_details`, `load_batch`, and `calculate_candidate_features`. Follow imports; do not edit files. Add a private diagram to your own notes if useful, not to the repository.

**Examiner may ask**

- “What is the difference between the candidate extraction pipeline and Formula Explorer?”
- “Does the UI calculate the formula itself?”
- “At what point is a workbook row matched to a selected UI cycle?”

**Completion checklist**

- [ ] I can explain both flows without mixing them.
- [ ] I can name each major module's responsibility.
- [ ] I can state that the UI calculation does not establish Excel row identity.
- [ ] I can distinguish code flow from scientific provenance.

### Module 2 — Dataset structure and preprocessing

**Goal:** Understand what the local loader actually reads and what upstream preprocessing remains unknown.

**Study these files**

- [`loader.py`](../scripts/member4_xjtu/loader.py)
- [`models.py`](../scripts/member4_xjtu/models.py)
- [`scripts/member4_xjtu/README.md`](../scripts/member4_xjtu/README.md)
- [`member4_cycle_identity_investigation.md`](./member4_cycle_identity_investigation.md)
- [`member4_final_contribution_audit.md`](./member4_final_contribution_audit.md)

**What you must understand**

- Each batch has a prepared MAT file and a feature workbook with sheets.
- `load_batch` reads a top-level `battery` structure, a sequence of profiles and cycles, and Excel sheets.
- The loader creates `SheetN` and cycle ordinals by enumeration. These are local labels, not author-provided physical IDs.
- `CycleTrace.validate()` enforces matching channel lengths (at least two), finite values, strictly increasing time, and finite capacity.
- The inspected prepared cycles have 128 samples with nonuniform relative times; the transformation from the release's stated 1 Hz acquisition to this prepared representation is not documented in the inspected sources.

**Important functions/classes and responsibilities**

- `_as_items`: makes MATLAB scalar/array structures easier to iterate.
- `_array_field`: fetches a signal field and converts it to a flattened float64 NumPy array.
- `_capacity_label`: extracts the first finite capacity value.
- `load_batch`: reads, checks, structures, and returns profiles plus workbook sheets.
- `CycleTrace.validate`: checks numeric and time-series invariants.
- `TimeInterval.__post_init__`: prevents non-finite or non-increasing boundaries.
- `PhaseSegment.is_disjoint`: reports whether a segment contains more than one interval.

**Beginner concepts**

- A path is a structured filename location; `Path / "folder" / "file"` joins path parts.
- `enumerate(items, start=1)` adds a counter to iteration.
- `np.asarray(..., dtype=np.float64).reshape(-1)` converts and flattens data.
- Exceptions such as `ValueError` and `FileNotFoundError` report invalid inputs instead of making up values.
- A pandas DataFrame is a table; `frame.columns` lists column names.

**Math, units, and variables**

Know the data fields and units: time in minutes, voltage in volts, current in amperes, temperature in °C, capacity label in Ah. The loader does not perform signal resampling, smoothing, or conversion from original 1 Hz data.

**Exercises**

1. Trace how `load_batch` builds one `CycleTrace` from `raw_cycle`.
2. Explain why strictly increasing time is required by interpolation and integration.
3. Given arrays with mismatched lengths or duplicate time, state which validation guard should reject them.
4. Explain in one sentence why equal profile/sheet counts do not prove battery identity.

**VS Code practical task**

Set a breakpoint in a unit test at the `CycleTrace` construction or use the debugger to inspect a synthetic test trace. Do not edit the dataset. Use Find All References for `load_batch` to see its callers in validation, error analysis, and API code.

**Examiner may ask**

- “Does your loader downsample the 1 Hz source?”
- “What does `cycle_index` identify?”
- “Why do you validate monotonic time and equal array lengths?”
- “What is unknown about the 128-sample traces?”

**Completion checklist**

- [ ] I can list every field stored in `CycleTrace`.
- [ ] I can explain each validation invariant.
- [ ] I can distinguish an ordinal from an authoritative identifier.
- [ ] I do not invent the preprocessing history of the MAT files.

### Module 3 — Feature engineering and mathematical operations

**Goal:** Understand the 67-name schema, candidate regions, equations in the code, and their units.

**Study these files**

- [`feature_definitions.py`](../scripts/member4_xjtu/feature_definitions.py)
- [`segments.py`](../scripts/member4_xjtu/segments.py)
- [`extractor.py`](../scripts/member4_xjtu/extractor.py)
- [`test_candidate_extraction.py`](../tests/member4_xjtu/test_candidate_extraction.py)
- [`member4_original_formula_recovery.md`](./member4_original_formula_recovery.md)

**What you must understand**

- The groups have 13 CC, 13 dV, 13 CV, 13 dI, and 15 Charge features.
- Group names and candidate signal/segment meanings are not proof of the original workbook's formula.
- Candidate segmentation uses thresholds and interpolation; candidate calculations use two distinct time grids/conventions.
- Missing candidate intervals can produce unavailable (`None`) values.

**Important functions/classes and responsibilities**

- `FeatureDefinition` and `feature_definitions`: store candidate descriptions and statuses.
- `SegmentationPolicy`: holds candidate threshold choices and validates configuration.
- `_crossing_time`: detects rising/falling crossings and linearly interpolates time.
- `_mask_runs` / `_mask_intervals`: convert Boolean sample selections into separate time intervals.
- `_threshold_window`: detects a sub-window only within a single parent interval.
- `segment_cycle`: creates CC/CV/dV/dI/Charge `PhaseSegment`s.
- `_interval_arrays`, `_moments`, `_trapezoid_details`, `_entropy_proxy`: numerical helpers.
- `_features_for_segment`: calculates a group's features; `extract_cycle_with_details` applies it to all groups.

**Beginner concepts**

- A Boolean mask is an array of `True`/`False` decisions, one per sample.
- Linear interpolation estimates a value between known samples.
- `np.diff` calculates differences between neighboring values.
- A loop applies the same operation repeatedly; a dictionary stores each result by feature name.
- A threshold rule is a programming choice; it is not automatically a scientific ground truth.

**Math, units, and variables (candidate code only)**

| Candidate operation | What the code does | Output unit |
|---|---|---|
| Energy | Trapezoidal integral of `V × I` over native timestamps plus interpolated boundaries; divide minute-integral by 60. | Wh |
| `Q` | Trapezoidal integral of `I` over the same time points; divide by 60. | Ah |
| `t_mean` | Mean elapsed time on 257 equally spaced points per interval, resetting origin for each interval. | min |
| Signal mean/std | Linear interpolation to the 257-point grid; population standard deviation (`ddof=0`). | V, A, or °C |
| Skewness | Biased third standardized central moment. | Dimensionless |
| Kurtosis | Pearson fourth standardized central moment; not excess kurtosis. | Dimensionless |
| `CCCT` / `CVCT` | Sum interval durations in details; feature output only for one contiguous interval. | min |
| dV/dt, dI/dt names | Difference between candidate interval endpoint signal values divided by interval duration. | V/min, A/min |
| Entropy | 16-bin equal-width histogram Shannon proxy with natural logarithm. | nats |

Candidate interval defaults: CC is an adaptive current plateau at 0.975 times the 95th-percentile current plus voltage ≤4.199 V; optional helper-style CC uses current ≥3.9 A plus voltage ≤4.199 V. CV starts at the first rising 4.199 V crossing and ends at trace end. dV is a rising 3.9-to-4.0 V window within one CC interval; dI is a falling 1.0-to-0.9 A window within one CV interval; Charge is the full stored trace. These are all candidate definitions.

**Exercises**

1. On paper, calculate one trapezoid panel for given `V`, `I`, and `Δt`, then convert minute integration to hours.
2. Explain why the implementation uses actual `np.diff(times)` for integration rather than assuming equal spacing.
3. Use a synthetic test to observe what happens when the voltage never crosses the CV threshold.
4. Compare the candidate definitions of population standard deviation and sample standard deviation in words.
5. Explain why a 16-bin entropy value depends on binning and cannot prove an original entropy method.

**VS Code practical task**

Run only the focused existing test file after confirming the project's Python environment. Step through a synthetic trace in the debugger. Inspect the returned `segments`, `values`, and `details`; do not run the all-batch generator unless you intentionally want to regenerate outputs.

**Examiner may ask**

- “Why use native times for integration and a uniform grid for statistics?”
- “Why do missing threshold crossings yield `None`?”
- “What is Pearson kurtosis?”
- “Are your thresholds and entropy bins original author settings?”

**Completion checklist**

- [ ] I can state all five group counts and describe the schema construction.
- [ ] I can explain every candidate operation and its units.
- [ ] I can explain the threshold rules as candidate assumptions.
- [ ] I can explain the missing-window and disjoint-interval behavior.
- [ ] I never call a candidate equation source verified.

### Module 4 — Python implementation and NumPy/pandas

**Goal:** Read the Python pipeline confidently and understand how data structures change at each step.

**Study these files**

- [`feature_definitions.py`](../scripts/member4_xjtu/feature_definitions.py)
- [`models.py`](../scripts/member4_xjtu/models.py)
- [`loader.py`](../scripts/member4_xjtu/loader.py)
- [`segments.py`](../scripts/member4_xjtu/segments.py)
- [`extractor.py`](../scripts/member4_xjtu/extractor.py)
- [`validation.py`](../scripts/member4_xjtu/validation.py)
- [`extract.py`](../scripts/member4_xjtu/extract.py)
- [`validate.py`](../scripts/member4_xjtu/validate.py)

**What you must understand**

- Python imports connect modules; relative imports such as `.models` refer to neighboring package files.
- Type annotations document expected inputs and outputs, but do not validate all values by themselves.
- The extractor returns a tuple of three related objects; the convenience function returns only two.
- The CLI entry points use `argparse` to choose batches, input roots, and output paths.

**Important functions/classes and responsibilities**

Review the named functions above and trace one call path from `validate.py:main` through `validate_batches`, `load_batch`, `extract_cycle`, and `_metric_rows`. Separately trace `extract.py:main` through `extract_batches`.

**Beginner concepts**

- `dict[str, float | None]` means keys are strings and values may be floats or `None`.
- `defaultdict(list)` creates a list automatically the first time a missing key is used.
- `zip(a, b)` iterates over corresponding items and stops when the shorter input ends.
- `float(...)`, `int(...)`, and `tuple(...)` convert values into specific Python types.
- `if __name__ == "__main__":` runs a CLI entry point only when the file is invoked directly as a module/script.
- Pandas `frame.iloc[row_index]` selects a row by integer position, not by an identity key.

**Math, units, and variables**

Focus on how `candidate - reference` defines signed error, how absolute errors form MAE, and how squared errors form RMSE. The scientific interpretation remains limited by the pairing method.

**Exercises**

1. Draw the return types of `load_batch`, `segment_cycle`, `extract_cycle`, and `extract_cycle_with_details`.
2. Explain one `for` loop and one dictionary update in `_features_for_segment`.
3. Explain the difference between `None`, `0.0`, and `NaN` in the candidate result path.
4. Read the CLI argument definitions and identify which defaults write into the repository.

**VS Code practical task**

Use “Go to Definition” and “Find All References” on `FEATURE_NAMES`, `load_batch`, `extract_cycle`, and `SegmentationPolicy`. Run a focused unit test and inspect a failed assertion message if any; do not alter source files to make a test pass.

**Examiner may ask**

- “Why return a dictionary keyed by feature name?”
- “What is the difference between `extract_cycle` and `extract_cycle_with_details`?”
- “What does `zip` assume in validation?”
- “Do type annotations validate a web request?”

**Completion checklist**

- [ ] I can follow the call path without skipping over function boundaries.
- [ ] I can describe the shape and purpose of the major lists/dictionaries.
- [ ] I understand `None` propagation for unavailable values.
- [ ] I can explain which scripts write files and where.

### Module 5 — Backend API integration

**Goal:** Explain how FastAPI turns browser selections into a candidate calculation and a JSON response.

**Study these files**

- [`formula_explorer_api.py`](../backend/formula_explorer_api.py)
- [`main.py`](../backend/main.py)
- [`models.py`](../scripts/member4_xjtu/models.py)
- [`extractor.py`](../scripts/member4_xjtu/extractor.py)
- [`test_formula_explorer_api.py`](../tests/test_formula_explorer_api.py)

**What you must understand**

- `APIRouter` groups related endpoints under `/formula-explorer`.
- Query/path constraints are checked by FastAPI/Pydantic; code also checks feature names and index bounds.
- The API transforms NumPy objects into JSON-friendly lists and scalar values.
- It explicitly marks output as candidate, not an original benchmark value.

**Important functions/classes and responsibilities**

- `_load_batch`: one-entry LRU cache around `load_batch`.
- `_feature_provenance`: combines a `FeatureDefinition` with display status, notation, units, and research notes.
- `get_formula_features`: returns the 67-entry metadata catalog.
- `get_batch_profiles`: returns profile names and cycle counts.
- `calculate_candidate_features`: selects the prepared MAT cycle, calls the extractor, and builds the calculation response.
- `APIRouter`: holds the three route definitions.
- In `main.py`, `app.include_router(formula_explorer_router)` connects the router to the FastAPI app.

**Beginner concepts**

- An HTTP GET request asks the server for data.
- A path parameter is part of the URL path; a query parameter follows `?`.
- JSON represents objects, arrays, numbers, strings, booleans, and `null`.
- HTTP 404 means a requested profile/cycle is unavailable; 422 indicates invalid input; 503 indicates required local files are unavailable in the handled path.
- An LRU cache reuses a recent function result.

**Math, units, and variables**

The API does not introduce new mathematics. It sends `batch`, `profile`, `cycle`, and `feature_name` to existing Python code and returns units/diagnostics produced from the feature metadata and extractor.

**Exercises**

1. Write down the three endpoint paths and what each returns.
2. Follow `cycle=1` from request parameter to `cycles[cycle - 1]`; explain the one-based/zero-based conversion.
3. Read the API test and explain how `monkeypatch` substitutes a synthetic batch for disk loading.
4. Explain why `values_are_original_benchmark_values` is `False`.

**VS Code practical task**

Use the API tests as a safe offline exercise. Set breakpoints in `calculate_candidate_features` and step through the synthetic trace test. If the app is already running, inspect the browser network request read-only; do not alter shared workspace state or data.

**Examiner may ask**

- “What is a query parameter?”
- “How does the backend validate the cycle number?”
- “Why does the endpoint return trace arrays as lists?”
- “Does the API ever match the request to an Excel row?”

**Completion checklist**

- [ ] I can describe all three routes and their response purposes.
- [ ] I can trace one request into `extract_cycle_with_details`.
- [ ] I can name the important error cases and status codes.
- [ ] I can explain the candidate-status fields in the response.

### Module 6 — Frontend Formula Explorer

**Goal:** Understand the React component's types, state, effects, API calls, and visualized response.

**Study these files**

- [`FormulaExplorer.tsx`](../frontend/src/components/FormulaExplorer.tsx)
- [`FormulaExplorer.css`](../frontend/src/components/FormulaExplorer.css)
- [`vite.config.ts`](../frontend/vite.config.ts)
- [`formula_explorer_api.py`](../backend/formula_explorer_api.py)
- [`member4_live_demo_checklist.md`](./member4_live_demo_checklist.md)

**What you must understand**

- TypeScript types describe the expected response shape; most API payload fields are not fully runtime-validated.
- `useState` keeps interactive selections/data/errors; `useEffect` loads the feature catalog and profiles; `useMemo` derives selected/filtered information.
- The frontend requests `/api/formula-explorer/...`; Vite proxies `/api` to FastAPI and removes that prefix.
- The chart uses raw MAT trace arrays, shades candidate intervals, and marks selected stored samples. Interpolated calculation points are not plotted as raw acquisition samples.

**Important functions/classes and responsibilities**

- `FormulaFeature`, `CalculationResponse`, `Segment`, `CalculationDiagnostics`: expected API shapes.
- `fetchJson<T>`: fetches JSON and surfaces invalid JSON/HTTP errors.
- `isFeatureResponse`: checks for exactly 67 catalog entries.
- `plotLinesFor` / `makeSignalPoints`: prepare chart series and selected-sample markers.
- `DiagnosticRows`: renders operation-specific intermediates.
- `FormulaExplorer`: owns UI state, effects, selection handlers, request, and JSX.
- `ReferenceArea`, `Line`, `Scatter`: Recharts elements used for interval shading, signal lines, and selected raw samples.

**Beginner concepts**

- A React component is a function that returns UI.
- JSX looks like HTML but is JavaScript/TypeScript syntax.
- A state setter changes a value and triggers a render.
- `useEffect(..., [batch])` reruns when `batch` changes.
- `AbortController` cancels a pending fetch when an effect is cleaned up.
- `map` creates rendered UI for list items; `filter` selects matching entries.
- `URLSearchParams` safely encodes query parameters.
- A TypeScript generic like `fetchJson<FeatureResponse>` tells the type checker what shape the caller expects, but the cast alone does not validate server data.

**Math, units, and variables**

The frontend displays values and units from the API; it does not compute the feature equations. It formats numbers and displays diagnostic intermediates. Keep calculation and presentation responsibilities distinct.

**Exercises**

1. List all `useState` values and what user interaction or API request changes each one.
2. Explain why the profile effect depends on `[batch]`.
3. Follow a feature selection to the `feature_name` query parameter.
4. Explain the difference between the chart's `ReferenceArea` and selected-sample `Scatter` markers.
5. Identify which error states appear when catalog load, profile load, or calculation fails.

**VS Code practical task**

Use the TypeScript editor to hover `CalculationResponse`, `selectedValue`, and `selectedDiagnostic`. Use Find All References on `loadCandidateCalculation`. If you run the frontend, select a feature and inspect the network request; do not change source or use a feature value to imply workbook identity.

**Examiner may ask**

- “What is React state?”
- “Why clear the previous result when the batch changes?”
- “Does the browser calculate entropy?”
- “How are selected raw sample markers produced?”

**Completion checklist**

- [ ] I can narrate the component from initial render through calculation result.
- [ ] I understand the type/interface definitions and their runtime limitation.
- [ ] I can explain the Vite proxy and FastAPI route prefix.
- [ ] I can distinguish raw plotted points from interpolated calculation points.

### Module 7 — Validation and error analysis

**Goal:** Understand how comparisons are formed, what metrics mean, and why results remain diagnostic.

**Study these files**

- [`validation.py`](../scripts/member4_xjtu/validation.py)
- [`analysis.py`](../scripts/member4_xjtu/error_analysis/analysis.py)
- [`validate.py`](../scripts/member4_xjtu/validate.py)
- [`test_analysis.py`](../tests/member4_xjtu/error_analysis/test_analysis.py)
- [`member4_candidate_validation.md`](./member4_candidate_validation.md)
- [`member4_feature_error_analysis.md`](./member4_feature_error_analysis.md)
- [`member4_cycle_identity_investigation.md`](./member4_cycle_identity_investigation.md)

**What you must understand**

- Workbook feature columns are checked against the canonical 67 names and order.
- Equal counts lead to position-based pairs labeled unverified.
- When raw cycles outnumber workbook rows, a unique monotone capacity-label match within tolerance may be used diagnostically; ambiguous and unmatched rows are excluded.
- Basic validation reports MAE, RMSE, maximum absolute error, and relative MAE; error analysis adds bias, quantiles, MAPE with near-zero exclusion, correlations, scope/cohort tables, and sensitivity variants.
- A metric is only as scientifically interpretable as the compared observations and definitions.

**Important functions/classes and responsibilities**

- `_unique_monotone_capacity_pairs` / `_profile_pairs`: produce classified diagnostic pairs.
- `_metric_rows` / `validate_batches`: calculate and aggregate basic metrics.
- `ErrorAccumulator` / `PairedSensitivityAccumulator`: collect errors and common-valid baseline/variant data.
- `_metrics`: calculate expanded metrics and count valid/invalid values.
- `_segment_variant`: calculate predeclared candidate alternatives.
- `_variant_specs`, `_variant_arguments`, `_variant_features`: define sensitivity scenarios.
- `run_analysis`: orchestrates full diagnostic outputs, plots, and report.

**Beginner concepts**

- Signed error is candidate minus reference; absolute error ignores direction.
- MAE averages absolute errors; RMSE squares errors before averaging and square-rooting, so large errors weigh more.
- Correlation measures association, not equality or identity.
- A cohort is a subset grouped under one pairing rule.
- A sensitivity analysis compares specified alternatives; it is not necessarily optimization or validation.

**Math, units, and variables**

- `error_i = candidate_i - workbook_i`
- `MAE = mean(|error_i|)`
- `RMSE = sqrt(mean(error_i**2))`
- Basic relative MAE = `MAE / mean(|workbook_i|) × 100%`.
- Error-analysis MAPE averages per-observation percentage errors only for references above `max(1e-12, 0.01 × median(|reference|))`.

The reports use valid-observation counts and distinguish `positional_unverified` from `capacity_match_diagnostic`. Do not pool or describe these as verified.

**Exercises**

1. For a small hand-written set of reference/candidate numbers, calculate signed error, MAE, and RMSE.
2. Explain why MAE and MAPE treat denominators differently.
3. Read the near-zero MAPE test and explain why one value is excluded.
4. Explain why ambiguous capacity matches are left unmatched.
5. Pick one sensitivity variant and state exactly what changes and what stays fixed.

**VS Code practical task**

Run only `tests/member4_xjtu/error_analysis/test_analysis.py` after checking the environment. Step through `_metrics` with the test fixture. Avoid invoking the full report generator unless you intend to write its default report and artifact paths.

**Examiner may ask**

- “Why is equal-count positional alignment not verified?”
- “What does a lower relative MAE prove?”
- “How does the code protect MAPE near zero?”
- “Did sensitivity analysis tune thresholds to Excel?”

**Completion checklist**

- [ ] I can explain the two pairing methods and their labels.
- [ ] I can calculate MAE, RMSE, relative MAE, and MAPE.
- [ ] I can state the valid/invalid sample-count caveat.
- [ ] I can explain why results do not establish original formula accuracy.

### Module 8 — Scientific limitations and research findings

**Goal:** Practice separating implemented behavior, candidate assumptions, source evidence, and unknowns.

**Study these files**

- [`member4_final_contribution_audit.md`](./member4_final_contribution_audit.md)
- [`member4_original_formula_recovery.md`](./member4_original_formula_recovery.md)
- [`member4_cycle_identity_investigation.md`](./member4_cycle_identity_investigation.md)
- [`member4_supplementary_pdf_inspection.md`](./member4_supplementary_pdf_inspection.md)
- [`member4_final_viva_rehearsal.md`](./member4_final_viva_rehearsal.md)
- [`feature_definitions.py`](../scripts/member4_xjtu/feature_definitions.py)
- [`identity_investigation.py`](../scripts/member4_xjtu/cycle_identity/identity_investigation.py)

**What you must understand**

- A formula is source-verified only with direct evidence tying it to the exact workbook feature schema and implementation/conventions.
- Related paper equations, a related CC/CV helper, or numerical agreement do not by themselves establish provenance.
- Capacity is a measurement, not a guaranteed unique cycle ID; position is not a guaranteed identity either.
- Prepared-data lineage, all four original entropy definitions, and the original generator remain unresolved.
- Root-cause tables distinguish observed residual patterns from hypotheses; correlation or clustering does not prove causation.

**Important functions/classes and responsibilities**

- `feature_evidence_rows` / `generate_outputs` in `formula_recovery/recover.py`: generate the feature-level evidence ledger.
- `capacity_label_agreement` and related helpers in `cycle_identity/identity_investigation.py`: summarize diagnostic label agreement and identifiers without claiming identity.
- `_root_cause_rows` in `error_analysis/analysis.py`: structure observations/hypotheses and what cannot be established.

**Beginner concepts**

- Provenance means evidence about where a result or method came from.
- Verification requires an independent criterion; similarity is not proof.
- A confounder is an unresolved factor that makes causal attribution uncertain.
- A bounded search result means “not located in the inspected sources,” not “does not exist anywhere.”

**Math, units, and variables**

No new candidate equation is added here. The key distinction is logical: a small residual under an uncertain pairing does not imply the candidate equation equals the original equation for the same cycle.

**Exercises**

1. For three statements from the reports, label each as implemented fact, candidate assumption, diagnostic finding, or unresolved claim.
2. Explain why equal capacity values can recur and why this undermines capacity as a unique ID.
3. Give an example of a low residual that still cannot prove formula provenance.
4. Explain what evidence would be required to move a feature to “source verified.”

**VS Code practical task**

Open the evidence ledger and cycle mapping report. Trace one feature's status to its source row and one identity count to the audit method. Do not update statuses from numerical fit.

**Examiner may ask**

- “What did the supplementary paper establish?”
- “Can you claim there is no source anywhere?”
- “Which conclusion is strongest, and which remains a hypothesis?”
- “What primary evidence would change your conclusion?”

**Completion checklist**

- [ ] I can state the 0/0/63/4 formula status accurately.
- [ ] I can state that zero pairs are identity-verified.
- [ ] I can explain why paper similarity and capacity matching are insufficient.
- [ ] I can separate observations from causal hypotheses.

### Module 9 — Live demonstration preparation

**Goal:** Demonstrate one complete user journey while keeping provenance warnings visible.

**Study these files**

- [`member4_live_demo_checklist.md`](./member4_live_demo_checklist.md)
- [`member4_presentation_script.md`](./member4_presentation_script.md)
- [`FormulaExplorer.tsx`](../frontend/src/components/FormulaExplorer.tsx)
- [`formula_explorer_api.py`](../backend/formula_explorer_api.py)
- [`member4_demo_walkthrough.md`](./member4_demo_walkthrough.md)

**What you must understand**

- The app requires the frontend, backend, and local reference files.
- The initial view shows the provenance warning and feature-status counts.
- Feature selection changes what metadata/value is shown; the candidate calculation is executed by Python in the backend.
- A selected batch/profile/cycle is an ordinal selection, not an Excel identity assertion.
- Error and fallback handling should be calm and honest.

**Important functions/classes and responsibilities**

- `FormulaExplorer` handles selected controls and async API requests.
- `loadCandidateCalculation` constructs query parameters, stores response, and displays errors.
- `calculate_candidate_features` selects a trace and creates the candidate response.
- `DiagnosticRows` turns intermediate values into tables.
- Recharts `Line`, `ReferenceArea`, and `Scatter` display signals, intervals, and sample markers.

**Beginner concepts**

- A rehearsal is a repeatable sequence of actions.
- A stale result is data from a prior selection that could mislead if not cleared.
- A fallback plan is an explanation route that does not fabricate a live result.

**Math, units, and variables**

Use `CC_energy` to explain the candidate equation and units; use an entropy feature to explain proxy status. Never present either as the original workbook equation.

**Exercises**

1. Rehearse the checklist without quoting any metric.
2. Rehearse selecting a feature, batch, profile, cycle, and expanding one calculation detail.
3. Practice the fallback answer if the frontend, backend, or dataset fails.
4. Explain the plot's selected raw markers versus interpolated calculation points.

**VS Code practical task**

Before evaluation, personally verify the local setup and one usable cycle in the browser. Confirm that the status warning appears and the API response is candidate-only. This is a task for you to perform; it has not been executed as part of creating this plan.

**Examiner may ask**

- “What is this value, and where did it come from?”
- “Does this cycle correspond to workbook row one?”
- “What if the candidate segment is unavailable?”
- “What does the plot shade?”

**Completion checklist**

- [ ] I show the warning before an equation or result.
- [ ] I call the output a candidate.
- [ ] I do not infer workbook row identity from cycle ordinal.
- [ ] I can use a report/code explanation if the live demo fails.

### Module 10 — Final viva preparation

**Goal:** Answer detailed questions succinctly, accurately, and within your contribution boundary.

**Study these files**

- [`member4_code_mastery_guide.md`](./member4_code_mastery_guide.md)
- [`member4_viva_questions.md`](./member4_viva_questions.md)
- [`member4_final_viva_rehearsal.md`](./member4_final_viva_rehearsal.md)
- [`member4_presentation_script.md`](./member4_presentation_script.md)
- [`member4_final_contribution_audit.md`](./member4_final_contribution_audit.md)

**What you must understand**

- Your specific Member 4 responsibilities versus shared project/team modules.
- The data model, feature schema, segment rules, candidate mathematics, validation cohorts, and API/UI flow.
- How to admit uncertainty while still explaining implemented behavior precisely.
- The difference between unit tests, API tests, UI inspection, numerical comparisons, and scientific validation.

**Important functions/classes and responsibilities**

Rehearse `CycleTrace`, `SegmentationPolicy`, `segment_cycle`, `extract_cycle_with_details`, `_profile_pairs`, `_metrics`, `calculate_candidate_features`, and `FormulaExplorer`.

**Beginner concepts**

- A strong technical answer first addresses the question, then gives the evidence, then states the limit.
- If you do not know a source fact, state what is known and what evidence is missing.
- Avoid claiming ownership of teammate code unless supported by the contribution record.

**Math, units, and variables**

Review the Module 3/7 equations. Be ready to derive a simple trapezoid and explain why correlation is not equality, why capacity is not identity, and why the entropy proxy is estimator-dependent.

**Exercises**

1. Answer 10 random questions from the existing banks aloud, limiting the first response to 20–40 seconds.
2. Ask a friend to challenge each answer with “How do you know?” or “Does that prove the original formula?”
3. Give a two-minute code walkthrough without slides.
4. Practice saying: “That is not established by the evidence we have; the evidence needed is …”

**VS Code practical task**

Use Find All References for the main pipeline functions and rehearse navigating directly to the relevant code during a screen-share. Keep reports open as references; do not rely on memorized numerical rankings without their cohort/sample-count caveats.

**Examiner may ask**

- “What did you personally implement?”
- “What can you confidently claim?”
- “Why is the scientific question still open?”
- “What would you do next if the authors provide source code?”

**Completion checklist**

- [ ] I answer with implementation evidence before interpretation.
- [ ] I distinguish personal scope from team-owned integration.
- [ ] I can state limitations without sounding evasive.
- [ ] I do not claim verified formulas, authoritative mapping, or scientifically validated accuracy.

## Seven-day study schedule

Plan for approximately **2–3 hours per day**, with short breaks. If you have less time, preserve the order and shorten the exercises rather than skipping the scientific limitations.

| Day | Study blocks | Personal deliverable by end of day |
|---|---|---|
| **1 — Architecture and data** | 45 min: Module 1 diagram. 60 min: Module 2 loader/data model. 30 min: explain both flows aloud. | One-page handwritten data-flow diagram and a clear statement of what the loader does not establish. |
| **2 — Schema and segmentation** | 45 min: feature catalog construction. 60 min: `SegmentationPolicy` and `segment_cycle`. 30 min: inspect synthetic tests. | A short table of group counts, signal candidates, segment rules, and “verified vs candidate” labels. |
| **3 — Extraction math** | 45 min: native-time trapezoids. 45 min: 257-point statistics and moment conventions. 30 min: entropy/duration/rate details. 20 min: spoken explanation. | Work one trapezoid example by hand; explain units and all statistical conventions without notes. |
| **4 — Python and validation** | 45 min: Python data structures/control flow. 60 min: `validation.py` and metrics. 30 min: run focused tests or inspect results. | A call trace from CLI to metric row, plus hand calculations for MAE/RMSE/relative MAE. |
| **5 — Error analysis and evidence** | 60 min: accumulators, `_metrics`, sensitivity variants. 45 min: cycle/formula provenance reports. 30 min: distinguish observations/hypotheses. | A two-column evidence sheet: confirmed implementation/data observations versus unverified scientific conclusions. |
| **6 — API and UI** | 45 min: FastAPI endpoints and response. 60 min: React types/state/effects/request/rendering. 30 min: perform a personal browser demo if environment permits. | A sequence diagram for one calculation request and an annotated demo checklist. |
| **7 — Viva rehearsal and revision** | 45 min: answer questions from both banks. 30 min: five-minute script. 30 min: difficult follow-ups and contribution boundary. 20 min: review checklist and gaps. | A recorded or live five-minute explanation, with candidate caveats and no unsupported claims. |

### Daily revision loop

At the end of each day, close the source and answer three prompts from memory:

1. What does the file/module do?
2. What is one exact implementation detail I can point to?
3. What must I not conclude from that detail?

Start the next study day by correcting any answer that confused code behavior with formula provenance or cycle identity.

## Explain Every Line of My Contribution

This section gives a method for studying the real source line by line. It does not invent a separate explanation for each individual source line: code meaning depends on its surrounding block, and line numbers can change. Use the actual file and the navigation steps below.

### Correct source-study order

1. [`feature_definitions.py`](../scripts/member4_xjtu/feature_definitions.py) — names and candidate metadata.
2. [`models.py`](../scripts/member4_xjtu/models.py) — data structures used by the pipeline.
3. [`loader.py`](../scripts/member4_xjtu/loader.py) — files into structured data.
4. [`segments.py`](../scripts/member4_xjtu/segments.py) — candidate intervals.
5. [`extractor.py`](../scripts/member4_xjtu/extractor.py) — candidate values and derivation details.
6. [`validation.py`](../scripts/member4_xjtu/validation.py) — pairing labels and core metrics.
7. [`analysis.py`](../scripts/member4_xjtu/error_analysis/analysis.py) — expanded diagnostics and sensitivity analysis.
8. [`formula_explorer_api.py`](../backend/formula_explorer_api.py) — backend contract.
9. [`main.py`](../backend/main.py) and [`vite.config.ts`](../frontend/vite.config.ts) — application routing/proxy.
10. [`FormulaExplorer.tsx`](../frontend/src/components/FormulaExplorer.tsx) — UI state and rendering.

The module order adds `models.py` because it defines the objects passed between the requested files. It is a prerequisite for understanding, even though it was not one of the eight primary requested modules.

### A repeatable line-by-line method

For each file, study one logical block at a time:

1. **Orient:** Read imports, constants, and top-level types. Write down where each imported name comes from.
2. **State purpose:** Before reading implementation details, state what problem the file appears to solve. Mark guesses as questions.
3. **Read one function/class:** Identify parameters, local variables, branches/loops, side effects, and every return path.
4. **Track data shape:** For each variable, note whether it is a scalar, array, list, tuple, dictionary, dataclass, DataFrame, or response object.
5. **Translate operators:** Explain `>=`, `&`, `|`, `~`, `[]`, `.`, `*`, `/`, `**`, and comprehensions in that exact line's context.
6. **Trace calls:** Use VS Code “Go to Definition” for called functions and “Find All References” for callers.
7. **Check a test:** Find an existing test that exercises the block. Identify its fixture, assertion, and what it does **not** prove.
8. **Explain aloud:** Describe the block in plain language, then state one limitation.
9. **Return to uncertainty:** If the code cannot answer a scientific provenance question, write “not established by implementation” rather than infer an answer.

### Language and mathematics lookup method

- **Unfamiliar Python:** Hover a symbol, inspect its definition, and check the official Python documentation or a beginner reference. Reproduce the behavior only in a scratch REPL/test fixture, not in the project source.
- **Unfamiliar NumPy:** Check the exact function signature and argument meanings for the operation used (for example `np.interp`, `np.diff`, `np.percentile`, or `np.histogram`). Then explain what array goes in and what shape/value comes out.
- **Unfamiliar pandas:** Identify whether an object is a DataFrame, Series, or mapping. Distinguish label-based access (`frame["label"]`) from positional row selection (`frame.iloc[index]`).
- **Unfamiliar TypeScript:** Read the declared type before the value use. Distinguish a compile-time type assertion from runtime validation; `payload as T` does not inspect every property.
- **Unfamiliar React:** For each state hook, write “who changes this value?” For each effect, write its dependencies, asynchronous work, cleanup, and error path. For each mapped JSX block, identify the list and the rendered item.
- **Unfamiliar formula:** Define each symbol and unit, check dimensions, then find the exact implementation expression. Separate a mathematically reasonable formula from a formula proven to be the original benchmark definition.
- **Unfamiliar API value:** Trace the TypeScript request parameter → Vite proxy → FastAPI function parameter → Python call → response dictionary → React state → displayed element.

### Line-by-line note template

Use this in a personal notebook or private study notes:

```text
File / function:
Purpose:
Inputs and their shapes/units:
Important local variables:
Branch or loop:
Calls made:
Return value / side effect:
Test that covers it:
What the code proves:
What remains an assumption or unknown:
My 30-second spoken explanation:
```

Do not add personal study notes to the repository unless separately requested.

## Beginner to Expert Self-Assessment

### Beginner milestone

You are at beginner milestone when you can:

- Name the eight core files and their broad responsibilities.
- Explain what a function, class, list, tuple, dictionary, NumPy array, DataFrame, API endpoint, and React state are.
- Identify the five groups and their counts.
- Explain that all equations shown are candidates and that original formulas/mapping are unresolved.

**Honest test:** Can you describe one small function without reading every line, while correctly naming its input and output?

### Intermediate milestone

You are at intermediate milestone when you can:

- Trace a cycle from MAT fields into `CycleTrace`, through segmentation and candidate extraction.
- Explain why integration uses actual timestamps, why statistics use the candidate grid, and how one feature's unit is derived.
- Trace a UI selection into an API query and back to the displayed result.
- Calculate MAE/RMSE for a small example and explain alignment cohorts/invalid counts.
- Point to tests for a behavior and state what those tests do not establish.

**Honest test:** Can you answer “what happens if the threshold is not crossed?” or “what if the workbook row is ambiguous?” by following the real branch in code?

### Viva-ready milestone

You are viva-ready when you can:

- Explain the full architecture and a particular function call path without conflating validation and UI calculation.
- Explain the candidate equations, units, edge cases, and assumptions precisely.
- Answer a follow-up that challenges the source or alignment basis without becoming defensive or inventing evidence.
- Distinguish implementation facts, candidate assumptions, diagnostic comparisons, and unknowns.
- Describe your individual scope while crediting shared integration and teammate work accurately.
- State the next evidence required for original formula verification and authoritative cycle identity.

**Honest test:** Ask someone to interrupt with “How do you know?” after every claim. If your answer becomes “it seems likely” without labeling that as a hypothesis, revisit the source or downgrade the claim.

### Common misconceptions to correct

| Misconception | Correct understanding |
|---|---|
| “The feature name tells us its original equation.” | A name suggests an interpretation; the source formula remains unverified. |
| “The author helper threshold proves the workbook used it.” | It documents related selection behavior, not the exact Excel feature generator. |
| “Equal counts mean row order matches.” | Equal lengths are not an identity key. |
| “A unique capacity match is a cycle ID.” | Capacity is a label/measurement and may repeat or reflect different preprocessing. |
| “Low MAE proves a formula.” | It is agreement under the selected candidate and diagnostic pairing cohort. |
| “A test pass proves scientific correctness.” | Tests prove the covered code behavior for tested cases. |
| “The 257-point grid and 16 bins came from the dataset.” | They are candidate implementation choices. |
| “The browser recalculates the equation.” | The backend extractor calculates; the browser renders the response and diagnostics. |
| “The loader converts 1 Hz data to 128 samples.” | The loader reads prepared arrays; that upstream transformation is undocumented in the inspected evidence. |

## Final safety checklist

- [ ] I call all computed outputs candidates.
- [ ] I describe position and capacity matches as unverified/diagnostic.
- [ ] I do not say any original formula or cycle mapping is verified.
- [ ] I report metrics with cohort, sample count, and caveat.
- [ ] I distinguish software test evidence from scientific validation.
- [ ] I state when an explanation is a candidate assumption or unresolved.
- [ ] I credit teammate/shared work accurately.
- [ ] I do not claim to have performed study tasks merely because this plan exists.
