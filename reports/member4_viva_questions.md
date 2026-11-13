# Member 4 Guide/Viva Question Bank

Answers below distinguish the current project implementation from original benchmark facts. Candidate equations and comparison results must not be described as source-verified or ground truth.

## Contribution and system design

### 1. What was your responsibility in VoltTwin?

I worked on the XJTU 67-feature engineering contribution: defining a candidate extraction pipeline, exposing its assumptions and calculations in Formula Explorer, comparing candidate outputs with the supplied feature workbooks, and investigating formula provenance and cycle alignment. The central result is transparent and reproducible candidate analysis, not recovery of the original Excel generator.

### 2. What does “67 features” mean in this work?

It is the canonical ordered set of 67 named feature columns in the XJTU handcrafted-feature workbooks, grouped as CC, dV, CV, dI, and Charge. It describes the workbook schema and the features our candidate pipeline attempts to compute. It does not mean we know the benchmark authors' exact equations for those columns.

### 3. What are the five feature groups and their counts?

CC has 13, dV has 13, CV has 13, dI has 13, and Charge has 15, totaling 67. In the candidate implementation, those prefixes correspond to selected charge regions or the full stored charge trace. The exact original segment definitions remain unknown.

### 4. How is Formula Explorer connected to the rest of the application?

The frontend requests the 67-feature catalog, available batch profiles, and a candidate calculation from the Formula Explorer API. The backend loads the selected prepared MAT trace and calls the existing Python extractor. It returns feature values, candidate segment intervals, trace channels, sampling diagnostics, and calculation intermediates. The UI labels the result candidate-only.

### 5. Does Formula Explorer compare its live value to the workbook value?

No. The live calculation displays the candidate extractor's output for the selected prepared raw cycle. It does not establish a cycle-to-Excel-row match and does not display a verified benchmark value for that cycle.

## Feature engineering and mathematics

### 6. What signals are used by the candidate extractor?

The prepared traces provide relative time, voltage, current, and temperature. The candidate definitions use combinations of these channels depending on the feature. These signal assignments are candidate interpretations and are not all established as the workbook authors' original choices.

### 7. How do you segment CC, CV, dV, and dI?

By default, CC uses an adaptive current-plateau selector with a voltage ceiling. There is also an optional author-helper-style CC selector. CV starts at a candidate rising 4.199 V crossing. dV is a candidate rising 3.9–4.0 V window within CC, and dI is a candidate falling 1.0–0.9 A window within CV. Those rules make the candidate pipeline reproducible; they are not verified workbook rules.

### 8. Why include an “author-documented” CC option?

The XJTU authors' preprocessing helper documents a related CC selector using current at least 3.9 A and voltage at most 4.199 V. Keeping it as a separate option allows a transparent comparison of candidate segmentation assumptions. The helper does not state that this selector generated the 67 Excel features, so the option is not a recovered benchmark formula.

### 9. How are energy and charge computed in the candidate?

Candidate energy integrates voltage times current; candidate charge integrates current. Both use trapezoidal integration over stored relative-time timestamps, with interpolated interval boundaries, then convert minutes to hours. The benchmark's original integration, sign, segment endpoints, and units have not been independently verified.

### 10. Why do statistics use a 257-point grid?

That is an explicit numerical convention in the current candidate implementation: signals are linearly interpolated to a uniform-time grid within each interval before computing candidate statistics. It avoids treating the nonuniform recorded timestamps as if they were uniformly spaced. It is not evidence that the benchmark used 257 samples or this weighting.

### 11. Which standard-deviation, skewness, and kurtosis conventions does the candidate use?

It uses population standard deviation (`ddof=0`), biased standardized third central moment for skewness, and Pearson fourth standardized central moment for kurtosis. The original workbook estimator/library conventions remain unknown. The 2024 paper's supplement gives its own equations, but it does not establish these as the workbook conventions.

### 12. What exactly is `CC_CCCT` in your code?

In the candidate implementation it is the duration of the selected CC interval, returned only when the interval is not disjoint. The original meaning of the acronym and the workbook's boundary rule have not been verified from a source tied to the 67-column schema.

### 13. What does `dV_dV_devide_dt` mean in the candidate?

The candidate calculates the voltage difference between endpoints of its selected dV window divided by the window duration. The feature name suggests a rate, but the exact original signal, window, derivative estimator, and units are not source-verified.

### 14. What is the entropy implementation?

The candidate creates a 16-bin equal-width histogram from interpolated signal values, normalizes nonzero bin counts into probabilities, and calculates Shannon entropy with natural logarithms, in nats. It is explicitly a diagnostic proxy. The original entropy signal, probability definition, binning, normalization, and log base are unknown for all four entropy columns.

### 15. Why not just use the entropy formula in the 2024 supplementary paper?

The supplement describes a separate method. It says \(H=-\sum p_i\log(p_i)\) and calls \(p_i\) a normalized curve value, but does not fully specify a probability estimator, bins, normalization details, or log base. More importantly, it does not map that method to the SOHbenchmark 67-feature workbook. Using it as the original would be an unsupported assumption.

## Validation and cycle identity

### 16. How did you compare candidate values with the Excel workbooks?

The scripts check the feature-column schema, calculate candidate values from prepared MAT traces, pair them with workbook rows using the existing alignment helper, and calculate error metrics. Equal-count profiles remain explicitly positional and unverified. Unequal-count matching uses unique monotone capacity-label matches only as diagnostics; ambiguous and unmatched workbook rows are not silently scored.

### 17. What metrics did you calculate?

The reports include MAE, RMSE, mean signed error/bias, median and maximum absolute error, error quantiles, MAPE with near-zero safeguards, relative MAE, Pearson and Spearman correlations when defined, and counts of valid/invalid observations. They are summaries of the declared candidate/alignment cohorts, not proof of original formula correctness.

### 18. How many comparisons were made and how trustworthy are they?

The current alignment audit records 26,320 comparison pairs: 19,191 positional-unverified pairs and 7,129 capacity-match diagnostics. None is identity-verified. They are useful for diagnosing numerical patterns under the current pairing rules, but they cannot be treated as ground-truth feature error measurements.

### 19. Why isn't equal row count enough to pair cycles by position?

Two sequences can have the same length and still differ because of omitted, merged, reordered, or differently sampled cycles. Equal counts do not prove a shared starting point or identical ordering. Without a common cycle identifier or authoritative generation rule, positional equality remains an assumption.

### 20. Why isn't an exact capacity match enough to prove cycle identity?

Capacity values can repeat and are measurements or labels, not guaranteed unique IDs. Labels may also differ through rounding, preprocessing, or a different capacity source. A capacity match can corroborate a possible pairing but cannot uniquely establish which physical cycle generated a workbook row.

### 21. What do the alignment counts say about missing or ambiguous data?

The audit records 27,535 prepared raw cycles and 26,937 workbook rows. It reports 617 unmatched workbook rows, of which 489 are ambiguous, and 1,215 unmatched raw cycles in the batch-6 capacity-match cohort. Those counts describe the existing audit algorithm; they do not identify the cause of the missing or ambiguous matches.

### 22. What root causes did you find for discrepancies?

I found evidence that candidate and possible original conventions could differ in phase segmentation, sampling/interpolation, time/statistical conventions, and entropy estimation. Those are evidence-supported mechanisms or hypotheses, not proven explanations for individual residuals. Unknown cycle identity is itself a confirmed limitation that affects interpretation of every comparison.

## Research, limitations, and difficult questions

### 23. Did you recover any original benchmark feature formula?

No. The current evidence ledger reports 0 Source Verified, 0 Partially Verified, 63 Candidate/unverified, and 4 Original formula unavailable. Related author helpers, the 2024 paper's supplementary equations, and numerical agreement do not directly tie formulas to the exact 67-column workbook.

### 24. If no formulas are verified, what is the value of your work?

The value is that the 67-name schema has a reproducible candidate implementation and an interactive explanation surface, while uncertainty is visible instead of hidden. The reports quantify candidate behavior, inspect alignment and sensitivity, document source searches, and identify exactly what primary evidence is missing. That is more scientifically useful than presenting a plausible formula as fact.

### 25. What would you need to call the benchmark reproducible or a formula verified?

At minimum, authoritative source code or equations explicitly tied to the exact workbook columns, including signals, segmentation, preprocessing, numerical conventions, and units. For validating outputs against Excel, I would also need an authoritative row-to-cycle mapping. Then I would implement the reference formulas separately, preserve the candidate extractor, compare them on verified pairs, and report missing/ambiguous observations and metrics.

## Quick reminder before the viva

- Say **candidate extraction**, not “the original formula.”
- Say **diagnostic candidate-to-workbook comparison**, not “verified accuracy.”
- Say **positional-unverified** or **capacity diagnostic**, not “matched cycle ground truth.”
- Say **the supplement contains related methodology**, not “the supplement defines all 67.”
- Say **the 95 tests verify tested software behavior**, not scientific validity.
