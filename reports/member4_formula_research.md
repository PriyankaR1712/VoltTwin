# Member 4: XJTU Handcrafted Feature Formula Research

## Executive summary

The original mathematical definitions and generator for the 67 XJTU workbook columns were **not located** in the repository or in the author-controlled preprocessing sources examined. No feature can be marked **Verified** or **original-source verified** from the available evidence.

The strongest source evidence is limited to the XJTU authors' helper code for selecting CC/CV portions of a charge cycle and calculating incremental-capacity (dQ/dV) curves. That code does not calculate the workbook's 67 features, and there is no evidence it generated the benchmark Excel files. The SOHbenchmark loader reads the Excel columns; it does not calculate them. The supplied appendix text extraction contains an “Appendix B. Feature engineering” heading, immediately followed by “Appendix C. Results”; no feature equations appear in that extraction. This does not substitute for visual inspection of the original PDF.

The table below lists every workbook feature and the corresponding current *candidate* interpretation. Those expressions describe the Member 4 candidate extractor, not recovered source formulas. Statistical estimators, integration conventions, timing, boundaries, and entropy definitions remain unverified. In particular:

- The meanings of `CC_energy` and `CC_Q` are physically plausible integral interpretations, not source-confirmed workbook definitions.
- `CC_CCCT` and `CV_CVCT` resemble phase-duration features by name, but no source identifies their exact boundary rules.
- `dV_dV_devide_dt` and `dI_dI_devide_dt` have no located source equation or estimator.
- All four entropy definitions remain unknown; the implemented histogram values are diagnostics only.
- Conventional mean/std/skewness/kurtosis formulas still leave important choices (sampling weights, sample versus population variance, skewness bias correction, Pearson versus excess kurtosis) unresolved.

Candidate-to-Excel numerical agreement is reported separately from formula provenance. For example, the candidate validation report gives aggregate relative errors of 1.21% for `CC_energy`, 1.13% for `CC_Q`, 1.93% for `CC_CCCT`, 0.42% for `CV_CVCT`, and 48–72% for the four entropy proxies. These figures do not establish that the candidate formulas or intervals are the originals.

## Search scope and method

Local repository searches covered the XJTU benchmark data and source material, Python source, documentation, notebooks, JSON metadata, and the existing candidate/validation materials. The three local XJTU analysis notebooks inspected each contain 65 cells; none contains the searched feature names or relevant formula/statistics terms. All six reference feature workbooks were inspected for embedded formulas, comments, and defined names; none supplied formula provenance. The feature metadata describes the feature set but supplies no original equations.

Exact-name and related-term searches included:

- `CC_energy`, `CC_Q`, `CC_CCCT`, `CV_CVCT`, `dV_dV_devide_dt`, `dI_dI_devide_dt`, `Charge_energy`
- `CC_entropy`, `dV_entropy`, `CV_entropy`, `dI_entropy`
- `handcraft_features`, `feature engineering`, `feature extraction`, `skewness`, `kurtosis`, and `dQ/dV`

GitHub code searches included the exact misspelled derivative name, `CC_CCCT`, and combinations of `Charge_energy`/`CC_energy`, as well as searches constrained to the XJTU authors' preprocessing repository. Exact derivative-name search returned no result. Searches for names such as `CC_CCCT` also return downstream datasets and copied feature-value CSVs; such data mirrors do not establish formulas or provenance. In the author preprocessing repository, `CC_energy` was not found, while `get_CC_value` identified the documented reader/helper implementation described below.

This search cannot prove that no private, unindexed, deleted, or inaccessible implementation exists. Findings are limited to the sources and versions listed here.

## Sources and evidence

| ID | Source and location | What it establishes | Authority for workbook formulas? |
|---|---|---|---|
| S1 | [XJTU authors' preprocessing repository](https://github.com/wang-fujin/Battery-dataset-preprocessing-code-library), [`XJTUBatteryClass.py`](https://github.com/wang-fujin/Battery-dataset-preprocessing-code-library/blob/e986a74054fb64c0f5134f2cc97f4643cd7699d2/XJTUBatteryClass.py#L165-L276); local copy [XJTUBatteryClass.py](../temp_preprocessing_source/XJTUBatteryClass.py) | `get_CC_value` selects charge-stage samples using current ≥3.9 A and voltage ≤4.199 V, or an optional voltage range intersected with current ≥3.9 A (roughly lines 165–185). `get_CV_value` selects voltage ≥4.199 V, or an optional current range (roughly lines 189–205). `get_IC_curve1` and `get_IC_curve2` calculate dQ/dV, including a resampling route and `I·dt/dV` (roughly lines 225–276). | Authoritative for what these helper methods do; **not** for the 67 workbook formulas or workbook generation. The inspected XJTU helper file does not implement the named energy/statistics/entropy columns. |
| S2 | [XJTU analysis notebook in the authors' preprocessing repository](https://github.com/wang-fujin/Battery-dataset-preprocessing-code-library/blob/e986a74054fb64c0f5134f2cc97f4643cd7699d2/XJTU%E6%95%B0%E6%8D%AE%E9%9B%86%E5%88%86%E6%9E%90.ipynb); local copies [XJTU_analysis.ipynb](../XJTU_analysis.ipynb), [author notebook](../temp_preprocessing_source/XJTU数据集分析.ipynb), and [copied author notebook](../temp_xjtu_source/XJTU数据集分析.ipynb) | Inspection of 65 cells in each local notebook found no target feature names or searched feature-engineering equations. | Not a feature-formula source. |
| S3 | Wang et al., “Physics-informed neural network for lithium-ion battery degradation stable modeling and prognosis,” *Nature Communications* 15, 4332 (2024), [DOI: 10.1038/s41467-024-48779-z](https://doi.org/10.1038/s41467-024-48779-z); citation and dataset link are also stated in S1 | The dataset paper/source is identified by the authors' code. No equation mapping was found there from this workbook schema to the 67 handcrafted columns. | Authoritative XJTU dataset research, but not an identified source for this Excel feature-generation recipe. |
| S4 | SOHbenchmark paper appendix text extraction, local [appendix_extracted.txt](../reference/SOHbenchmark/appendix_extracted.txt), 22 extracted pages; page 1 has “Appendix B. Feature engineering” followed immediately by “Appendix C. Results.” | No equations are present under Appendix B in the supplied text extraction. The original PDF was not visually inspected, so text extraction could omit non-text content. | It is benchmark-associated material, but the supplied extraction does not explain the XJTU workbook feature generation. |
| S5 | SOHbenchmark [XJTU_loader.py](../reference/SOHbenchmark/dataloader/XJTU_loader.py), `get_features` and `_parser_xlsx` (roughly lines 127–170) | Loads `batch-*_features.xlsx`, parses feature columns and labels, then normalizes them. It consumes prepared features rather than extracting the 67 columns from raw signals. | Authoritative for benchmark loading behavior; not a formula source. |
| S6 | Reference workbook set [handcraft_features/](../reference/SOHbenchmark/data/XJTU/handcraft_features/) and raw traces [charge/](../reference/SOHbenchmark/data/XJTU/charge/); metadata [feature_metadata.json](../feature_metadata.json) | Workbooks provide values, names, and labels. Workbook inspection found no formulas, comments, or defined names. Metadata does not provide the original equations. The raw traces expose cycle signals but cannot by themselves identify the workbook's choices. | Primary data, but no embedded formula provenance. |
| S7 | Member 4 candidate code [feature_definitions.py](../scripts/member4_xjtu/feature_definitions.py), [segments.py](../scripts/member4_xjtu/segments.py), and [extractor.py](../scripts/member4_xjtu/extractor.py) | Defines reproducible candidate segments, estimators, and diagnostic entropy proxies used in the existing validation. | **Not authoritative** for the workbook; these are the approximations being investigated. |
| S8 | Member 4 candidate validation [report](./member4_candidate_validation.md) and [CSV](./member4_candidate_validation.csv) | Reports comparisons against workbook values and alignment limitations across batches. | Numerical reproduction only; cannot establish source formulas or cycle identity. |
| S9 | XJTU authors' [papers summary repository](https://github.com/wang-fujin/XJTU-Battery-Dataset-Papers-Summary) | A bibliography/summary of research using XJTU. Exact-name/formula searches did not identify a source that documents this 67-column workbook schema or its generator. | Useful discovery aid; not itself an original feature-generation specification. |

### Source interpretation and limits

The author helper's `get_CC_value` and `get_CV_value` functions support the **existence of those selectors in that preprocessing library**, not the assumption that the Excel generator used identical selections. The helper also describes the charging/rest/discharge/rest stages and provides incremental-capacity code. Its dQ/dV calculations are distinct from the workbook columns named `dV_dV_devide_dt` and `dI_dI_devide_dt`; similar derivative notation is not evidence that these columns use the IC-curve code.

The XJTU benchmark loader's use of Excel input, combined with the absence of a generator in the inspected benchmark/source files, leaves the workbook-generation provenance unresolved. A feature-value copy found in another repository is a mirror of data, not a derivation source.

## Formula key and candidate segment assumptions

Every mathematical expression in the feature table is labeled a **candidate**. Notation:

- `g` denotes one candidate group interval; `t` is elapsed time in minutes; `V`, `I`, and `T` are voltage, current, and temperature.
- Candidate energy is `E_g = trapezoid-integral(V(t) I(t), t) / 60` in Wh. Candidate charge is `Q_g = trapezoid-integral(I(t), t) / 60` in Ah. The candidate implementation interpolates interval endpoints and applies trapezoids over stored timestamps. Sign convention, exact original limits, and integration method are not established.
- Candidate `t_mean` is the arithmetic mean of elapsed time from the group start on a 257-point uniform-time interpolation grid.
- For a signal `x` sampled on that grid, `μ_x = mean(x)`, `σ_x = sqrt(mean((x-μ_x)^2))`, `γ1_x = mean((x-μ_x)^3) / σ_x^3`, and `β2_x = mean((x-μ_x)^4) / σ_x^4`. These are respectively candidate mean, population standard deviation (`ddof=0`), biased standardized third central moment, and Pearson (not excess) kurtosis. They are not confirmed as the workbook conventions.
- Candidate entropy is a 16-bin equal-width histogram Shannon entropy, `-Σ p_i ln(p_i)`, in nats. The current diagnostic proxy uses voltage for CC/dV and current for CV/dI. The original entropy signal, estimator, binning, weighting, and logarithm base are unknown.
- Candidate duration is the sum of candidate interval lengths; derivative candidates are endpoint signal difference divided by candidate interval duration.

The groups currently used by the candidate extractor are not source-confirmed workbook boundaries:

| Group | Candidate interval only | Source evidence and unresolved choices |
|---|---|---|
| CC | Adaptive current plateau threshold `I ≥ 0.975 × percentile_95(I)` intersected with `V ≤ 4.199 V`. | S1 documents fixed `I ≥ 3.9 A` intersected with `V ≤ 4.199 V`; it does not document the adaptive threshold or confirm workbook use. |
| dV | Rising 3.9–4.0 V window within candidate CC. | Name/value-motivated approximation only; no source defines this window. |
| CV | First rising crossing of 4.199 V to the recorded charge endpoint. | S1 uses `V ≥ 4.199 V` as a selector, but not this first-crossing/endpoint interval rule for the workbook. |
| dI | Falling 1.0–0.9 A window within candidate CV. | Name/value-motivated approximation only; no source defines this window. |
| Charge | Entire stored charge trace. | Workbook's start/end event and whether rest data are excluded are not established. |

The prepared benchmark traces contain 128 samples per cycle and nonuniform `relative_time_min` spacing. Thus sample-wise statistics on the native trace would not be equal-time weighted; the candidate's 257-point interpolation makes its statistics approximately equal-time weighted by construction. This is a candidate choice, not a recovered workbook convention. Narrow-window feature values are also sensitive to downsampling, interpolation, event boundaries, and gaps. If a candidate CC mask is disjoint, the implementation may combine intervals for integrals/statistics, while single-interval features can be unavailable; this behavior is not known to match the original.

## All 67 workbook features

**Status meanings:** `Inferred candidate` means the feature name or common physical/statistical interpretation motivates the expression, but the workbook formula is unknown. `Unknown; proxy only` means even the original feature's entropy definition was not recovered; the listed expression is only the diagnostic proxy in S7. `None` means no feature in this table is source-verified.

| # | Exact workbook feature | Candidate expression (not recovered original) | Signal / candidate segment | Formula status |
|---:|---|---|---|---|
| 1 | `CC_energy` | `E_CC` | Voltage × current / time; CC | Inferred candidate; limits and method unknown |
| 2 | `CC_Q` | `Q_CC` | Current / time; CC | Inferred candidate; limits and method unknown |
| 3 | `CC_t_mean` | Candidate mean elapsed time | Time; CC | Inferred candidate; grid/time origin unknown |
| 4 | `CC_V_mean` | `μ_V` | Voltage; CC | Inferred candidate; weighting unknown |
| 5 | `CC_T_mean` | `μ_T` | Temperature; CC | Inferred candidate; weighting unknown |
| 6 | `CC_V_std` | `σ_V` (`ddof=0`) | Voltage; CC | Inferred candidate; estimator/weighting unknown |
| 7 | `CC_T_std` | `σ_T` (`ddof=0`) | Temperature; CC | Inferred candidate; estimator/weighting unknown |
| 8 | `CC_V_skewness` | `γ1_V` (biased moment) | Voltage; CC | Inferred candidate; convention/weighting unknown |
| 9 | `CC_T_skewness` | `γ1_T` (biased moment) | Temperature; CC | Inferred candidate; convention/weighting unknown |
| 10 | `CC_V_kurtosis` | `β2_V` (Pearson, not excess) | Voltage; CC | Inferred candidate; convention/weighting unknown |
| 11 | `CC_T_kurtosis` | `β2_T` (Pearson, not excess) | Temperature; CC | Inferred candidate; convention/weighting unknown |
| 12 | `CC_CCCT` | Candidate CC interval duration | Time; CC | Inferred from name only; exact rule unknown |
| 13 | `CC_entropy` | Diagnostic `H_16(V)` histogram proxy | Voltage proxy; CC | Unknown original definition; proxy only |
| 14 | `dV_energy` | `E_dV` | Voltage × current / time; rising 3.9–4.0 V within CC | Inferred candidate; interval unknown |
| 15 | `dV_Q` | `Q_dV` | Current / time; rising 3.9–4.0 V within CC | Inferred candidate; interval unknown |
| 16 | `dV_t_mean` | Candidate mean elapsed time | Time; rising 3.9–4.0 V within CC | Inferred candidate; grid/time origin unknown |
| 17 | `dV_V_mean` | `μ_V` | Voltage; rising 3.9–4.0 V within CC | Inferred candidate; weighting unknown |
| 18 | `dV_T_mean` | `μ_T` | Temperature; rising 3.9–4.0 V within CC | Inferred candidate; weighting unknown |
| 19 | `dV_V_std` | `σ_V` (`ddof=0`) | Voltage; rising 3.9–4.0 V within CC | Inferred candidate; estimator/weighting unknown |
| 20 | `dV_T_std` | `σ_T` (`ddof=0`) | Temperature; rising 3.9–4.0 V within CC | Inferred candidate; estimator/weighting unknown |
| 21 | `dV_V_skewness` | `γ1_V` (biased moment) | Voltage; rising 3.9–4.0 V within CC | Inferred candidate; convention/weighting unknown |
| 22 | `dV_T_skewness` | `γ1_T` (biased moment) | Temperature; rising 3.9–4.0 V within CC | Inferred candidate; convention/weighting unknown |
| 23 | `dV_V_kurtosis` | `β2_V` (Pearson, not excess) | Voltage; rising 3.9–4.0 V within CC | Inferred candidate; convention/weighting unknown |
| 24 | `dV_T_kurtosis` | `β2_T` (Pearson, not excess) | Temperature; rising 3.9–4.0 V within CC | Inferred candidate; convention/weighting unknown |
| 25 | `dV_dV_devide_dt` | Candidate `(V_end − V_start) / Δt` | Voltage / time; rising 3.9–4.0 V within CC | Inferred from name only; derivative estimator/window unknown |
| 26 | `dV_entropy` | Diagnostic `H_16(V)` histogram proxy | Voltage proxy; rising 3.9–4.0 V within CC | Unknown original definition; proxy only |
| 27 | `CV_energy` | `E_CV` | Voltage × current / time; CV | Inferred candidate; limits and method unknown |
| 28 | `CV_Q` | `Q_CV` | Current / time; CV | Inferred candidate; limits and method unknown |
| 29 | `CV_t_mean` | Candidate mean elapsed time | Time; CV | Inferred candidate; grid/time origin unknown |
| 30 | `CV_C_mean` | `μ_I` | Current; CV | Inferred candidate; weighting unknown |
| 31 | `CV_T_mean` | `μ_T` | Temperature; CV | Inferred candidate; weighting unknown |
| 32 | `CV_C_std` | `σ_I` (`ddof=0`) | Current; CV | Inferred candidate; estimator/weighting unknown |
| 33 | `CV_T_std` | `σ_T` (`ddof=0`) | Temperature; CV | Inferred candidate; estimator/weighting unknown |
| 34 | `CV_C_skewness` | `γ1_I` (biased moment) | Current; CV | Inferred candidate; convention/weighting unknown |
| 35 | `CV_T_skewness` | `γ1_T` (biased moment) | Temperature; CV | Inferred candidate; convention/weighting unknown |
| 36 | `CV_C_kurtosis` | `β2_I` (Pearson, not excess) | Current; CV | Inferred candidate; convention/weighting unknown |
| 37 | `CV_T_kurtosis` | `β2_T` (Pearson, not excess) | Temperature; CV | Inferred candidate; convention/weighting unknown |
| 38 | `CV_CVCT` | Candidate CV interval duration | Time; CV | Inferred from name only; exact rule unknown |
| 39 | `CV_entropy` | Diagnostic `H_16(I)` histogram proxy | Current proxy; CV | Unknown original definition; proxy only |
| 40 | `dI_energy` | `E_dI` | Voltage × current / time; falling 1.0–0.9 A within CV | Inferred candidate; interval unknown |
| 41 | `dI_Q` | `Q_dI` | Current / time; falling 1.0–0.9 A within CV | Inferred candidate; interval unknown |
| 42 | `dI_t_mean` | Candidate mean elapsed time | Time; falling 1.0–0.9 A within CV | Inferred candidate; grid/time origin unknown |
| 43 | `dI_C_mean` | `μ_I` | Current; falling 1.0–0.9 A within CV | Inferred candidate; weighting unknown |
| 44 | `dI_T_mean` | `μ_T` | Temperature; falling 1.0–0.9 A within CV | Inferred candidate; weighting unknown |
| 45 | `dI_C_std` | `σ_I` (`ddof=0`) | Current; falling 1.0–0.9 A within CV | Inferred candidate; estimator/weighting unknown |
| 46 | `dI_T_std` | `σ_T` (`ddof=0`) | Temperature; falling 1.0–0.9 A within CV | Inferred candidate; estimator/weighting unknown |
| 47 | `dI_C_skewness` | `γ1_I` (biased moment) | Current; falling 1.0–0.9 A within CV | Inferred candidate; convention/weighting unknown |
| 48 | `dI_T_skewness` | `γ1_T` (biased moment) | Temperature; falling 1.0–0.9 A within CV | Inferred candidate; convention/weighting unknown |
| 49 | `dI_C_kurtosis` | `β2_I` (Pearson, not excess) | Current; falling 1.0–0.9 A within CV | Inferred candidate; convention/weighting unknown |
| 50 | `dI_T_kurtosis` | `β2_T` (Pearson, not excess) | Temperature; falling 1.0–0.9 A within CV | Inferred candidate; convention/weighting unknown |
| 51 | `dI_dI_devide_dt` | Candidate `(I_end − I_start) / Δt` | Current / time; falling 1.0–0.9 A within CV | Inferred from name only; derivative estimator/window unknown |
| 52 | `dI_entropy` | Diagnostic `H_16(I)` histogram proxy | Current proxy; falling 1.0–0.9 A within CV | Unknown original definition; proxy only |
| 53 | `Charge_energy` | `E_Charge` | Voltage × current / time; entire stored charge trace | Inferred candidate; record bounds and method unknown |
| 54 | `Charge_Q` | `Q_Charge` | Current / time; entire stored charge trace | Inferred candidate; record bounds and method unknown |
| 55 | `Charge_t_mean` | Candidate mean elapsed time | Time; entire stored charge trace | Inferred candidate; grid/time origin unknown |
| 56 | `Charge_V_mean` | `μ_V` | Voltage; entire stored charge trace | Inferred candidate; weighting unknown |
| 57 | `Charge_C_mean` | `μ_I` | Current; entire stored charge trace | Inferred candidate; weighting unknown |
| 58 | `Charge_T_mean` | `μ_T` | Temperature; entire stored charge trace | Inferred candidate; weighting unknown |
| 59 | `Charge_C_std` | `σ_I` (`ddof=0`) | Current; entire stored charge trace | Inferred candidate; estimator/weighting unknown |
| 60 | `Charge_V_std` | `σ_V` (`ddof=0`) | Voltage; entire stored charge trace | Inferred candidate; estimator/weighting unknown |
| 61 | `Charge_T_std` | `σ_T` (`ddof=0`) | Temperature; entire stored charge trace | Inferred candidate; estimator/weighting unknown |
| 62 | `Charge_C_skewness` | `γ1_I` (biased moment) | Current; entire stored charge trace | Inferred candidate; convention/weighting unknown |
| 63 | `Charge_V_skewness` | `γ1_V` (biased moment) | Voltage; entire stored charge trace | Inferred candidate; convention/weighting unknown |
| 64 | `Charge_T_skewness` | `γ1_T` (biased moment) | Temperature; entire stored charge trace | Inferred candidate; convention/weighting unknown |
| 65 | `Charge_C_kurtosis` | `β2_I` (Pearson, not excess) | Current; entire stored charge trace | Inferred candidate; convention/weighting unknown |
| 66 | `Charge_V_kurtosis` | `β2_V` (Pearson, not excess) | Voltage; entire stored charge trace | Inferred candidate; convention/weighting unknown |
| 67 | `Charge_T_kurtosis` | `β2_T` (Pearson, not excess) | Temperature; entire stored charge trace | Inferred candidate; convention/weighting unknown |

## Focused findings

### CC_Q and CC_energy

The names and physical units are compatible with integrating current and electrical power, respectively:

- Candidate `CC_Q = ∫ I(t) dt`, converted from minutes to hours.
- Candidate `CC_energy = ∫ V(t) I(t) dt`, converted from minutes to hours.

No located source says these are the workbook equations. Unknowns include the exact CC boundary, whether the generator instead uses a capacity or power channel, current sign, sampling/integration convention, endpoint handling, unit conversion, and the meaning of any rests or gaps. The XJTU helper exposes `capacity_Ah` and `power_Wh`, but does not calculate these workbook columns.

### CC_CCCT and CV_CVCT

Duration is a plausible reading of the names, and S1 documents CC/CV sample selectors. No source was found that expands `CCCT`/`CVCT`, identifies which events bound the intervals, states whether disjoint intervals are summed, or specifies treatment of threshold crossings, missing samples, and rest periods. Candidate duration must therefore remain inferred.

### Derivative-named features

The misspelling `devide` is retained exactly as it appears in the workbook. No exact implementation or source formula was found for either derivative feature. The candidate endpoint slope is one possible interpretation, not a verified derivative estimator. Alternatives such as pointwise finite differences, regression slope, average rate over a selected window, or a derivative of a resampled curve have not been ruled out. S1's `dQ/dV` incremental-capacity calculation is a different quantity and must not be used as evidence for `dV_dV_devide_dt` or `dI_dI_devide_dt`.

### Entropy

The original signal, transform, estimator, bin count/edges, probability weighting, handling of repeated values, and log base were not located for `CC_entropy`, `dV_entropy`, `CV_entropy`, or `dI_entropy`. Differential entropy, histogram entropy, entropy of a derivative/distribution, and other estimators are not interchangeable. The 16-bin Shannon calculation is only a reproducible diagnostic proxy.

### Statistical definitions and nonuniform time

Feature suffixes identify likely signal families, but they do not specify statistical conventions. `std` can be sample or population standard deviation; skewness implementations can apply finite-sample corrections; kurtosis may be Pearson or excess kurtosis. A simple mean over 128 stored points weights each point equally, not each unit of elapsed time. The stored sample times are nonuniform, while the candidate statistics interpolate to a uniform-time grid. The Excel conventions remain unknown.

## Reproduction results are not formula verification

The current candidate validation compares approximations to workbook values across batches. It reports 26,320 valid comparisons for most features, 26,319 for features with one unavailable candidate, and 26,245 for the dI features with 75 unavailable candidates. Equal-length profiles are paired by row position; batch 6 uses capacity-label matching, which still leaves unmatched and ambiguous rows. These limitations affect interpretation of apparent agreement.

The small relative errors for several candidate integrals/durations and the much larger entropy-proxy errors are useful diagnostics for candidate quality. Neither favorable nor unfavorable error rates reveal what the original implementation did. In particular, low errors cannot resolve whether a statistic was uniformly sampled, how boundaries were set, or which of several entropy definitions was used.

## Remaining gaps and recommended authoritative next steps

1. Obtain the source script/notebook, archived project, or author-provided export that generated `batch-1_features.xlsx` through `batch-6_features.xlsx`, including its version and dependencies.
2. Ask the SOHbenchmark authors which upstream dataset and script produced the 67 columns, and request the exact feature-generation code or a formula specification. The loader and supplied appendix do not provide it.
3. Ask the XJTU dataset authors whether their preprocessing library or another private/released script generated these specific workbooks. Do not equate their CC/CV selectors or IC-curve routines with the workbook extractor absent confirmation.
4. If original code cannot be obtained, request a source-authored definition table specifying, for every column, signal, phase bounds, units, sample weighting, integration/derivative estimator, statistical convention, and entropy estimator.
5. Preserve candidate-only labels until such primary evidence is available. If definitions are later supplied, independently reproduce selected workbook cells from raw samples and verify row/cycle mapping before promoting any formula status.

**Final status: 67 features enumerated; original formula implementation not located for any feature; zero features marked Verified.**
