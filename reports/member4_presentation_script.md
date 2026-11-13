# Member 4 Presentation Script — 5 Minutes

## Spoken script

### 0:00–0:35 — Introduce my contribution

“I’m responsible for Member 4’s XJTU handcrafted-feature work. The benchmark workbooks contain 67 feature names, and my contribution is a candidate extraction pipeline, a Formula Explorer that explains each calculation, and research into how those workbook values were produced.

“Before I demonstrate it, I want to be clear about the scientific boundary: we have not found the original feature-generation code, and we do not have an authoritative mapping from each Excel row to a raw cycle. So I will show candidate calculations and diagnostic comparisons, not claim that these are verified original formulas.”

### 0:35–1:05 — Explain the feature groups

“The 67 names are organized into five groups: CC, dV, CV, dI, and Charge. There are 13 features each for CC, dV, CV, and dI, and 15 for Charge. They include energy and charge candidates, time and channel statistics, phase-duration or rate-like features, and four entropy columns.

“The names and groups come from the workbook schema. The candidate code assigns signal and segment meanings to them, but the names alone do not prove the original equations.”

### 1:05–2:10 — Demonstrate Formula Explorer

“I’ll open Formula Explorer. At the top, the status warning tells us that the original workbook formulas are unverified. The counts are zero source-verified, zero partially verified, 63 candidate/unverified, and four original entropy formulas unavailable.

“I’ll select `CC_energy`. The page shows the candidate equation, units, implementation notes, assumed segment, and variables. In this candidate, energy is trapezoidal integration of voltage times current over the selected interval, with the time converted from minutes to hours. This is a documented candidate convention—not a claim about the Excel generator.

“Now I’ll choose a batch, a profile, and a cycle, then click ‘Calculate candidate.’ The result comes from the prepared MAT trace selected by those ordinals. The plot shows raw prepared voltage, current, and temperature against relative time. The shaded region is the candidate interval, and markers show selected raw samples. The sampling summary reports the observed time steps. The calculation detail shows the actual operation and intermediate values.”

### 2:10–2:45 — Show an unknown entropy feature

“Next I’ll select `CC_entropy`. Its status is ‘Original Formula Unknown.’ The displayed 16-bin histogram entropy is only a diagnostic proxy. We do not know the original Excel signal, entropy estimator, binning, normalization, or logarithm base.

“This is why the interface separates a useful interactive calculation from an unsupported provenance claim.”

### 2:45–3:35 — Explain validation carefully

“I compared candidate outputs against the benchmark Excel values and computed metrics such as MAE, RMSE, bias, relative error, and correlation. The comparisons are split by alignment method.

“The audit records 19,191 equal-count positional pairs and 7,129 batch-6 capacity-label matches. Both are unverified or diagnostic; we have zero identity-verified cycle pairs. There are also 617 unmatched workbook rows, including 489 ambiguous rows, and 1,215 unmatched raw cycles in the batch-6 matching cohort.

“So the metrics are useful for finding numerical patterns in the current comparisons, but they do not establish formula accuracy.”

### 3:35–4:20 — Summarize research

“I investigated the benchmark loader and history, the XJTU author preprocessing helpers, papers and repositories, and the supplementary material for the 2024 paper. That supplement defines a related short-window statistical-feature method, but it does not say it generated these 67 Excel columns. The author-linked PINN4SOH CSV has a different schema of 16 input features plus capacity.

“Our formula ledger therefore remains at zero verified formulas. The cycle identity report likewise found no authoritative row-to-cycle mapping.”

### 4:20–5:00 — Close with limitations and next steps

“The current candidate extractor and reports are covered by tests; the full project suite passed 95 tests. That is software evidence, not scientific proof.

“The two most important missing pieces are an authoritative feature generator or formula specification and an authoritative cycle-to-row mapping. Without them, the correct next step is to request those materials from the authors or benchmark maintainers—not to tune candidate formulas until the errors look smaller.

“My contribution is a transparent, reproducible investigation that makes both the calculations and the evidence gaps visible. Thank you.”

## Demo timing at a glance

| Time | Action |
|---|---|
| 0:00–0:35 | State role and scientific caveat |
| 0:35–1:05 | Explain five groups and 67-feature count |
| 1:05–2:10 | Formula Explorer: warning, `CC_energy`, batch/profile/cycle calculation and plot |
| 2:10–2:45 | `CC_entropy`: unknown-original-formula status and proxy |
| 2:45–3:35 | Validation metrics and alignment counts |
| 3:35–4:20 | Formula and supplementary research findings |
| 4:20–5:00 | Test evidence, unresolved needs, conclusion |

## Delivery reminders

- Keep the candidate warning visible when showing an equation/result.
- Do not use “verified,” “exact reproduction,” or “ground-truth match” for candidates or aligned rows.
- If asked for a particular metric, state its cohort and sample count from the report; do not quote one number without its alignment caveat.
- The paper supplement is related methodology, not an identified source for this 67-column workbook.
