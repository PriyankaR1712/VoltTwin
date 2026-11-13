# Member 4 Live Demo Checklist

## Before the session

- [ ] Confirm the current branch and ensure no demo step requires modifying files.
- [ ] Confirm the XJTU reference MAT files and six feature workbooks are present under `reference/SOHbenchmark/data/XJTU/`.
- [ ] Start the backend and frontend using the project's normal run procedure; verify the UI and API are available.
- [ ] Open the project at the Formula Explorer route (`#feature-explorer`).
- [ ] Check that the feature catalog loads and shows the provenance warning/status counts.
- [ ] Preselect or note a cycle known to return usable candidate results. Do not select based on presumed correspondence to an Excel row.
- [ ] Keep the candidate validation report, cycle identity report, and formula recovery report available in separate tabs/windows.
- [ ] Have the 5-minute script and this checklist available offline in case the browser or server fails.

## Live demonstration order

| Step | Page/control | What to click or show | What to explain | Avoid claiming |
|---:|---|---|---|---|
| 1 | Project home/navigation | Open **Formula Explorer**. | This is Member 4's interactive feature-explanation and candidate-calculation surface. | Do not say it displays recovered original formulas. |
| 2 | Formula Explorer status banner | Pause on the provenance warning and status counts. | 0 Source Verified, 0 Partially Verified, 63 Candidate/unverified, 4 Original formula unavailable. | Do not treat status colors or candidate values as verification. |
| 3 | Feature browser | Show group buttons and search. Select `CC_energy`. | Five groups; 67 total features. Search and group selection navigate the canonical workbook names. | Do not infer the original signal/segment solely from the name. |
| 4 | Candidate definition panel | Show notation, interpretation, units, implementation, variables, and steps. | The candidate uses V×I trapezoidal integration over its chosen interval and converts minutes to hours. The segment and convention are candidate assumptions. | Do not say the Excel used trapezoidal integration or this CC boundary. |
| 5 | Candidate calculation controls | Select Batch 1 (or another available batch), first available profile, cycle 1; click **Calculate candidate**. | Batch/profile/cycle select a prepared MAT trace by its stored ordinals. This is not a workbook row identity assertion. | Do not claim cycle 1 maps to workbook row 1. |
| 6 | Candidate result card | Point to the value and units. | It is output from the current candidate extractor. If unavailable, explain the segment may not be detected. | Do not quote as an original benchmark feature value or accuracy result. |
| 7 | Raw trace plot and sampling summary | Show shaded interval, selected sample markers, channel legend, and min/median/max time step. | Plot shows prepared MAT samples; interpolation is used inside candidate calculations. Prepared cycles are 128 points with nonuniform relative times. | Do not call these original acquisition samples or claim 1 Hz from the prepared trace. |
| 8 | Segment/calculation details | Expand segment evidence and selected raw sample details; show trapezoid panels if visible. | Shows what the candidate actually selected and how its result was produced. | Do not interpret transparency as source provenance. |
| 9 | Entropy feature | Search/select `CC_entropy`. | Original entropy formula is unavailable; 16-bin Shannon histogram is a diagnostic proxy. | Do not state that histogram entropy matches Excel or the 2024 paper's entropy formula. |
| 10 | Candidate validation/error report | Show feature/batch metrics with alignment method labels. | Candidate-to-workbook residuals are diagnostics. Positional and capacity cohorts are separate; ambiguous/unmatched rows are excluded. | Do not call MAE/RMSE benchmark accuracy or formula error ground truth. |
| 11 | Cycle identity report | Show summary counts. | 19,191 positional-unverified pairs; 7,129 capacity diagnostics; 0 identity-verified pairs; 617 unmatched workbook rows including 489 ambiguous; 1,215 unmatched raw cycles in batch-6 cohort. | Do not call capacity equality a unique cycle ID. |
| 12 | Formula recovery / supplement reports | Show status summary and supplement page 6 evidence/mapping conclusion. | Related methodology exists, but no direct mapping to these 67 columns; current formula counts remain 0/0/63/4. | Do not claim the 2024 supplement defines all 67 benchmark formulas. |
| 13 | Testing summary (if asked) | Show or cite current test run result. | 95 tests passed; this supports tested software behavior. | Do not present tests as scientific formula or identity validation. |

## Suggested fallback if the live demo fails

### Frontend or backend is unavailable

1. Do not spend the evaluation session changing code or restarting repeatedly.
2. State that the interactive demo is unavailable and continue with the report screenshots and code/report evidence.
3. Explain the API flow from the existing implementation: feature catalog, batch profile list, selected candidate calculation.
4. Use the supplementary PDF page render only to discuss the separate paper methodology; it is not an application screenshot.
5. Offer to demonstrate the app later after restoring the development environment.

### Candidate interval or value is unavailable

1. Explain that missing candidate windows are surfaced rather than fabricated.
2. Show the segment evidence and report's invalid-candidate counts.
3. Select another cycle only to demonstrate candidate behavior; do not choose a cycle to improve benchmark fit or imply alignment.

### Dataset files fail to load

1. Explain that the UI requires the local XJTU reference data path and a running backend.
2. Use the code, tests, and existing reports to explain the intended behavior.
3. Do not substitute invented or manually entered values.

### Examiner asks for exact original formula or cycle identity

Answer directly: “We have not located authoritative evidence for that. The candidate formula/alignment is explicitly labeled unverified. We need the original generator or a documented mapping before making that claim.”

## Final safety checklist

- [ ] Call every displayed extraction result a **candidate**.
- [ ] Show the provenance warning before showing equations or results.
- [ ] State comparison cohort and sample count whenever quoting metrics.
- [ ] State that there are zero identity-verified cycle/workbook pairs.
- [ ] Keep entropy proxy status visible.
- [ ] Do not modify code, formulas, data, or reports during the demo.
- [ ] Do not make claims of exact reproduction, verified accuracy, or causal root cause.
