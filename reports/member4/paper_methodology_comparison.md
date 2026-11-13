# Paper-Based Scientific Validation — Phase 2

## Executive result

The 2024 Nature Communications paper defines its own 16-feature method. It does
**not** define or claim to generate the 67 feature columns in the
SOHbenchmark XJTU workbooks. Comparison by feature names alone would be
misleading.

- Exact paper-to-VoltTwin feature equivalences: **0/16**.
- Partial mathematical similarities: statistical moments, charge integrals,
  durations, slope-like quantities, and entropy; none has a fully matching
  signal window and calculation convention in the current 67-feature
  implementation.
- Paper feature values were **not** compared with VoltTwin candidate values.
  Such a comparison would not be scientifically fair because the windows,
  statistical conventions, and data lineage do not match.
- A reproducible **window-coverage-only** audit was run on all six local
  prepared batches. Its output is not feature validation and is explicitly
  labelled as such in the CSV.
- No original 67-feature formula was verified or changed.

## Sources and evidence scope

1. Wang et al., “Physics-informed neural network for lithium-ion battery
   degradation stable modeling and prognosis,” *Nature Communications* 15,
   4332 (2024), [DOI: 10.1038/s41467-024-48779-z](https://doi.org/10.1038/s41467-024-48779-z).
   I read the publisher-hosted full article, including “Feature extraction,”
   “SOH estimation,” “Discussion,” and “Methods,” and inspected Fig. 3 for the
   visible 1–16 feature labels.
2. The publisher’s [Supplementary Information PDF](https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-024-48779-z/MediaObjects/41467_2024_48779_MOESM1_ESM.pdf),
   Supplementary Notes 1–3, especially Note 2, printed p. 6. The existing
   [supplement inspection record](../member4_supplementary_pdf_inspection.md)
   records its page-by-page examination and the equations.
3. The paper’s linked [PINN4SOH author repository](https://github.com/wang-fujin/PINN4SOH)
   and its prepared XJTU CSV schema, as recorded in the existing supplementary
   inspection. The CSV schema is a separate 16-input-feature schema plus
   capacity; it is not the 67-column SOHbenchmark workbook schema.
4. Local project evidence: [candidate feature registry](../../scripts/member4_xjtu/feature_definitions.py),
   [segment policy](../../scripts/member4_xjtu/segments.py),
   [candidate extractor](../../scripts/member4_xjtu/extractor.py),
   [cycle/data validation](../../scripts/member4_xjtu/models.py),
   [loader](../../scripts/member4_xjtu/loader.py), and the earlier
   [67-feature provenance audit](../member4_scientific_provenance_audit.md).

The uploaded/local article PDFs previously found in `C:\Users\acer\Downloads`
were truncated and not page-renderable. The paper’s full publisher article and
the publisher supplement provide the evidence used here; the invalid local
copies were not treated as page evidence.

## Paper evidence matrix

| Paper claim / method | Evidence in the paper | Classification | Scope or uncertainty |
|---|---|---|---|
| The method uses 16 charging features, numbered 1–16 | Main text, “Feature extraction”; Fig. 3 labels | **SUPPORTED BY PAPER** | This is the paper’s schema, not the 67-column benchmark schema. |
| Voltage samples are selected from `[V_end − 0.2, V_end]` | Main text, “Feature extraction” | **SUPPORTED BY PAPER** | For XJTU the stated charge cutoff is 4.2 V, hence the value band `[4.0, 4.2] V`. |
| Current samples are selected between 0.5 A and 0.1 A during CV charging | Main text, “Feature extraction”; Supplementary Note 2 | **SUPPORTED BY PAPER** | The supplement prints the bounds in descending order `[0.5, 0.1] A`; it does not specify endpoint inclusion or a machine-readable phase boundary. |
| Mean is arithmetic mean of the selected samples | Supplementary Note 2, Eq. (1) | **SUPPORTED BY PAPER** | The selected samples and paper window must match for equivalence. |
| Standard deviation uses denominator `n−1` | Supplementary Note 2, Eq. (2) | **SUPPORTED BY PAPER** | This is sample standard deviation; VoltTwin’s candidate moments use population `ddof=0`. |
| Skewness and kurtosis use the printed central-moment expressions | Supplementary Note 2, Eqs. (3)–(4) | **SUPPORTED BY PAPER** | The equations use `(n−1)` with the defined sample σ; do not silently replace them with a library default or common corrected estimator. |
| Selected-window duration is `t_end−t_start` | Supplementary Note 2, Eq. (5) | **SUPPORTED BY PAPER** | Time unit and endpoint inclusion are not specified there. |
| Accumulated charge is `∫ I dt` over the selected interval | Supplementary Note 2, Eq. (6) | **SUPPORTED BY PAPER** | Numerical integration method, time unit, and output unit are not specified. |
| Voltage slope is endpoint voltage difference divided by duration | Supplementary Note 2, Eq. (7) | **SUPPORTED BY PAPER** | The printed equation is for voltage; the paper names a current-slope feature too, but does not print its equation. |
| Curve entropy has form `−Σ p_i log(p_i)` | Supplementary Note 2, Eq. (8) | **SUPPORTED BY PAPER** | The text calls `p_i` a “normalized value of a curve” but does not define probability construction, binning, zero handling, or log base. |
| A current slope is one of the 16 inputs | Main text and Fig. 3, feature 15 | **SUPPORTED BY PAPER** | Its exact formula and sampling convention are **NOT SPECIFIED**. |
| Feature inputs are min–max scaled to `[−1, 1]` | Main text, “SOH estimation” | **SUPPORTED BY PAPER** | Whether scaling parameters are fit on training batteries only, and whether cycle/time is scaled identically, is **NOT SPECIFIED**. |
| Paper’s SOH target is `Q^k / Q^0` | Main text, Methods, Eq. (5) | **SUPPORTED BY PAPER** | `Q^0` is nominal capacity. The paper reports XJTU nominal capacity as 2 Ah. |
| Paper’s XJTU experiment has 55 LISHEN NCM cells, 2 Ah nominal capacity, 3.6 V nominal voltage, room-temperature operation, and six protocol batches | Main text, “Data generation”; Supplementary Note 1 | **SUPPORTED BY PAPER** | These are paper dataset facts; matching profile counts in a local prepared release do not establish cycle-level identity or preprocessing equivalence. |
| Model evaluation uses four datasets; about 6:2:2 battery-level train/validation/test splits and 10 repetitions | Main text, “SOH estimation” and results | **SUPPORTED BY PAPER** | This validates the paper’s model evaluation, not VoltTwin’s feature equations. |
| The abstract reports 0.87% MAPE | Paper abstract | **SUPPORTED BY PAPER** | Paper-only result; it is not a VoltTwin score and is not used in any comparison here. |
| Exact missing-value behavior, statistical endpoint handling, source sample rate for these feature calculations, and feature normalization fit scope | No complete specification found in the article/supplement | **NOT SPECIFIED** | Required for exact independent reproduction. |
| Exact mapping of these 16 fields to the SOHbenchmark 67 workbook fields | No mapping in paper, supplement, or author CSV schema | **NOT APPLICABLE** | They are separate schemas. Name similarity is not evidence of shared feature provenance. |
| Exact paper feature extraction is already implemented in VoltTwin | Current Member 4 code implements its own candidate windows and formulas | **NEEDS IMPLEMENTATION** | No separate Paper-16 extractor exists. It was intentionally not added because it cannot validate the original 67 features. |

### Numbering and feature definitions

The numbered mapping below follows the labels visibly printed in Fig. 3. The
supplementary prose lists “charging time” before “accumulated charge,” whereas
Fig. 3 labels feature 5 as `CC Q` and feature 6 as `CC charge time`; the figure
resolves that numbering for this table. The original source formula for current
slope remains unspecified, and the entropy equations remain incomplete.

| # | Paper feature | Paper’s signal and selected data | Formula evidence and units |
|---:|---|---|---|
| 1 | Voltage mean | Voltage values with `V ∈ [V_end−0.2, V_end]`; XJTU `[4.0,4.2] V` | Arithmetic mean; output V before normalization. |
| 2 | Voltage std | Same voltage values | Sample standard deviation, denominator `n−1`; output V before normalization. |
| 3 | Voltage kurtosis | Same voltage values | Supplementary Note 2 Eq. (3); dimensionless. |
| 4 | Voltage skewness | Same voltage values | Supplementary Note 2 Eq. (4); dimensionless. |
| 5 | CC Q | Current integrated over the selected voltage-window times | `∫I dt`; unit depends on time base, not stated. |
| 6 | CC charge time | Selected voltage-window duration | `t_end−t_start`; time unit not stated. |
| 7 | Voltage slope | Voltage endpoints over the selected voltage window | `(V_end−V_start)/(t_end−t_start)`; time unit not stated. |
| 8 | Voltage entropy | Selected voltage curve | `−Σp_i log(p_i)`; dimensionless form, estimator/log base not specified. |
| 9 | Current mean | Current values between 0.5 A and 0.1 A during CV | Arithmetic mean; output A before normalization. |
| 10 | Current std | Same current values | Sample standard deviation, denominator `n−1`; output A before normalization. |
| 11 | Current kurtosis | Same current values | Supplementary Note 2 Eq. (3); dimensionless. |
| 12 | Current skewness | Same current values | Supplementary Note 2 Eq. (4); dimensionless. |
| 13 | CV Q | Current integrated over the selected current-window times | `∫I dt`; unit depends on time base, not stated. |
| 14 | CV charge time | Selected current-window duration | `t_end−t_start`; time unit not stated. |
| 15 | Current slope | Selected current curve | Feature is named/shown; exact equation is not provided. A voltage-slope equation must not be silently repurposed. |
| 16 | Current entropy | Selected current curve | `−Σp_i log(p_i)`; estimator/log base not specified. |

The sixteenth-feature entropy operation is not equivalent to VoltTwin’s
16-bin histogram proxy: the paper does not specify a histogram or those bins.

## Comparison with VoltTwin’s 67 candidates

The [16-row mapping CSV](./paper_feature_mapping.csv) records the current
candidate names, candidate formulas/windows, units, missing-data behavior,
window coverage, and the reason each relationship is not an equivalence.

The closest overlaps are:

- **Means and moments:** VoltTwin has signal-statistic candidates, but they use
  group-specific candidate segments and 257-point uniform-time interpolations.
  The paper uses selected curve samples and specifies sample standard
  deviation; the current extractor uses population standard deviation,
  biased standardized skewness, and Pearson kurtosis.
- **Charge and duration:** both methods include integrals/durations, but the
  paper’s voltage-value window and current-value-within-CV window are not
  VoltTwin’s adaptive CC, CV-to-trace-end, 3.9–4.0 V dV, or 1.0–0.9 A dI
  segments. Paper integration time base and numerical quadrature are also
  unspecified.
- **Slope:** the voltage-rate candidate uses a 3.9–4.0 V window; the paper
  uses the selected 4.0–4.2 V voltage window. The dI rate candidate uses
  1.0–0.9 A, unlike the paper’s 0.5–0.1 A current band. The paper’s current
  slope equation is not explicit.
- **Entropy:** VoltTwin computes a 16-bin histogram entropy in nats. The paper
  gives only a generic `p_i` expression, so its entropy cannot be reproduced
  exactly from the text.
- **No paper counterpart located:** candidate energy, time-mean, temperature
  statistics, and other features remain outside this 16-feature method.

Thus, **no candidate is an exact equivalent**, and this paper does not upgrade
any original 67-feature status from the prior audit.

## Implementation and data audit

### Current implementation facts

- The registry and extractor define the existing 67 candidate names and
  candidate units; formulas were not modified.
- The default CC segment is an adaptive current plateau intersected with
  `V ≤ 4.199 V`; the optional author-helper-style CC selector is also not a
  Paper-16 window.
- Candidate CV begins at a rising 4.199 V crossing and continues to the stored
  trace end. Candidate dV is 3.9–4.0 V within candidate CC; candidate dI is a
  falling 1.0–0.9 A interval within candidate CV.
- Statistics and entropy use 257-point uniform-time interpolation grids.
  Candidate standard deviation is population `ddof=0`; candidate skewness is
  the biased standardized third central moment; candidate kurtosis is Pearson
  fourth standardized central moment.
- `CycleTrace.validate()` rejects non-finite channels, mismatched lengths,
  fewer than two channel samples, non-increasing time, and non-finite capacity.
  If a candidate segment is unavailable, the extractor returns `None` for its
  67 feature values rather than inventing a value. The paper does not specify
  equivalent missing-data behavior.

### Prepared-data coverage

The available local `charge/batch-*.mat` files have 128 samples per prepared
cycle. A new coverage-only script tested inclusive value bands:

- Voltage: `[4.0,4.2] V`, using the paper’s stated XJTU cutoff of 4.2 V.
- Current: `[0.1,0.5] A`, ordering the paper’s printed descending bounds for
  the purpose of counting samples. **No CV phase mask was applied**, because
  an authoritative current-window phase boundary is not supplied in the local
  prepared traces.

All 27,535 prepared cycles contain at least one sample in each value band.
For the voltage band, 27,485 have at least two samples; the remaining 50 are
from batch 6 and have one. All 27,535 have at least two current-band samples,
but that count is an upper bound on the paper’s current window because it does
not enforce “during CV.” See
[paper_validation_results.csv](./paper_validation_results.csv) and run:

```powershell
.\.venv\Scripts\python.exe -m scripts.member4_xjtu.paper_window_coverage
```

The coverage result establishes that the bands occur in the prepared arrays;
it does **not** establish exact paper sample membership, 1 Hz input fidelity,
paper-to-local cycle identity, matching phase boundaries, or feature values.
The existing dataset audit found 128-point prepared traces and no documented
transformation lineage from the release’s original acquisition samples.
There is no unique workbook-row-to-cycle identity established for the 67
feature values.

### Is a fair feature-value comparison possible?

**No, not against the current 67 candidates.** A fair comparison would require
the same input samples, same interval, same statistic/integration conventions,
and independently known expected values. The paper descriptions do not match
the candidate segments, and no paper-generated per-cycle 16-feature targets
are joined to the local cycle traces. Recomputing the paper’s equations on
these prepared traces would be a new Paper-16 extraction, not validation of
any of the benchmark’s 67 columns.

For that reason, the results CSV contains only sample-window coverage; there
are no fabricated MAE, relative-error, or unit-difference results. No test
can establish scientific equivalence where reference values and identity
mapping are absent.

## Dataset, SOH, validation, and paper conclusions

- **Datasets and chemistries stated in the paper:**

  | Dataset | Paper-reported cells / chemistry | Experiment details reported |
  |---|---|---|
  | XJTU (study-generated) | 55 LISHEN NCM cells; 2 Ah, 3.6 V nominal | Room temperature; charge/discharge cutoffs 4.2/2.5 V; six protocol batches (8 cells each except batch 2 with 15). |
  | TJU | NCA 3.5 Ah; NCM 3.5 Ah; mixed NCM+NCA 2.5 Ah | Cutoff ranges stated as 2.65–4.2 V for NCA and 2.5–4.2 V for NCM and NCM+NCA; temperature sets 25, 35, 45 °C; rates 0.25 C–4 C. |
  | HUST | 77 A123 LFP/graphite cells; 1.1 Ah, 3.3 V nominal | 30 °C; identical charge protocol with multi-stage discharge protocols. |
  | MIT | LFP chemistry, described as the same chemistry as HUST | Fast charge with one- or two-step policies, 4 C discharge, and 30 °C. |

  The paper reports 387 batteries and 310,705 samples across its four datasets.
  These are the paper’s dataset descriptions; local file counts or matching
  chemistry labels alone do not prove record-level identity.
- **Paper SOH:** `Q^k/Q^0`, with cycle capacity divided by nominal capacity.
  This is conceptually consistent with capacity normalization only if the
  local capacity units/identity are established; it does not validate any
  handcrafted feature.
- **Paper feature scaling:** min–max to `[-1,1]`. Exact scaler fit scope and
  feature handling for missing values are not specified in the reviewed text.
- **Paper evaluation:** four datasets, 387 batteries and 310,705 samples;
  approximately 6:2:2 battery-level train/validation/test splits and 10
  repeated experiments, plus small-sample and transfer experiments. The
  abstract’s 0.87% MAPE and the paper’s model results belong to the paper only.
- **Conclusions/limitations:** authors report that feature correlations vary
  with chemistry. They describe their PINN as an empirical-degradation/state
  space approach rather than a complete electrochemical model; only readily
  available voltage/current data are used. They identify seamless integration
  of detailed battery governing equations with neural networks as unresolved.
  These conclusions do not establish the 67 Excel formulas.

## What this paper supports—and does not support

**Supports:** an independent, explicitly described 16-feature charging
methodology; its voltage and current value bands; the stated moment equations;
the charge, duration, voltage-slope, and generic entropy expressions; the
paper’s SOH definition and reported experimental setup.

**Does not support:** the original 67-feature workbook formulas, VoltTwin’s
candidate phase rules, candidate 257-point interpolation, the candidate
population-moment conventions, the 16-bin entropy proxy, an authoritative
cycle mapping, or any VoltTwin validation score.

## Remaining blockers and next scientific task

1. Obtain the source/generator that created the SOHbenchmark 67-feature
   workbooks and a unique cycle-to-row key.
2. Obtain the exact preprocessing lineage from the paper’s source XJTU records
   to the local 128-point SOHbenchmark MAT traces, including signal/time
   transformations and cycle IDs.
3. If separately reproducing the paper’s 16 features is useful, recover or
   confirm its complete feature-generation code, including CV phase masking,
   current-slope formula, entropy estimator, endpoint conventions, time units,
   and normalization-fit scope. Keep this as a separate method; it cannot
   verify the 67-feature schema.
4. After the first two blockers are resolved, validate one identity-mapped
   original 67-feature value (recommended: `CC_Q`) against its author
   generator before scaling to other features.

No existing feature formula, API, metadata, or teammate source was modified.
