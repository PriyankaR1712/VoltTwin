# Original Benchmark Formula Verification — Deep Research Phase 2

## Result

No authoritative generator, equation table, or workbook-row/cycle crosswalk for the 67 SOHbenchmark XJTU columns was recovered. The candidate equations and Formula Explorer provenance warning were left unchanged.

The Phase 2 evidence taxonomy separates related-method evidence from original-formula provenance:

| Evidence status | Features | Interpretation |
|---|---:|---|
| `SOURCE_VERIFIED` | 0 | Exact original workbook definition tied to an authoritative source |
| `PARTIALLY_VERIFIED` | 0 | Source-backed partial definition with an explicit workbook mapping |
| `RELATED_METHOD_ONLY` | 32 | Similar operation/window in a separate author method; not a workbook mapping |
| `CANDIDATE_UNVERIFIED` | 31 | No feature-specific original equation or related method correspondence located |
| `ORIGINAL_FORMULA_UNKNOWN` | 4 | Entropy estimator/signal/conventions remain unidentified |

The original-provenance status used by the existing Formula Explorer remains `SOURCE_VERIFIED=0`, `PARTIALLY_VERIFIED=0`, `CANDIDATE_UNVERIFIED=63`, and `ORIGINAL_FORMULA_UNKNOWN=4`. `RELATED_METHOD_ONLY` is a Phase 2 evidence label and does not promote a candidate to verified.

## Sources investigated

- [SOHbenchmark at pinned commit](https://github.com/wang-fujin/SOHbenchmark/tree/62230dd9a857f5c05ac641227b52ec2ffbeb9e15) and [workbook upload commit](https://github.com/wang-fujin/SOHbenchmark/commit/611bb5948fe4a7914486ded7be238db24faabb23): the loader reads precomputed `handcraft_features` workbooks; the inspected history contains no feature generator.
- The public SOHbenchmark navigation exposed one `main` branch and no releases/tags; the six-commit history was checked as a bounded public history search.
- [Current XJTU preprocessing class](https://github.com/wang-fujin/Battery-dataset-preprocessing-code-library/blob/e986a74054fb64c0f5134f2cc97f4643cd7699d2/XJTUBatteryClass.py) and [XJTU analysis notebook](https://github.com/wang-fujin/Battery-dataset-preprocessing-code-library/blob/e986a74054fb64c0f5134f2cc97f4643cd7699d2/XJTU%E6%95%B0%E6%8D%AE%E9%9B%86%E5%88%86%E6%9E%90.ipynb): the notebook uses CC `[3.8, 4.0] V` and CV `[1.0, 0.5] A` selectors for plots, and the class provides CC/CV helpers and dQ/dV routines. Neither maps helper output to any of the 67 workbook columns or exports feature sheets.
- Author `PINN4SOH`, the linked CSV schema, the official XJTU/Zenodo documentation, and the supplied SOHbenchmark appendix were checked. PINN4SOH exposes a separate 16-feature paper schema plus capacity; no 67-column generator is present.
- Author repository inventory and forks `rosyeeBen/SOHbenchmark2`, `armand00000/SOHbenchmarkT`, and `Yike-Lin/SOH-Baseline-test` were checked as discovery sources. Their trees retain the prepared-data benchmark layout and do not add a 67-feature generator.
- The Nature Communications supplementary PDF, Supplementary Note 2 p. 6, supplies equations for the separate 16-feature method (mean, sample standard deviation, skewness, kurtosis, duration, accumulated charge, voltage slope, and generic entropy). No equation is claimed as a SOHbenchmark workbook formula.

## Feature-level records

The machine-readable [Phase 2 CSV](./formula_verification_phase2.csv) contains exactly one row per registry feature with the original formula field intentionally blank when it was not recovered. Candidate implementation formulas are copied from the existing audit ledger and are not promoted by this report.

| Group | Features | Related-method evidence | Original formula recovered |
|---|---:|---:|---:|
| `CC` | 13 | 6 | 0 |
| `dV` | 13 | 6 | 0 |
| `CV` | 13 | 6 | 0 |
| `dI` | 13 | 5 | 0 |
| `Charge` | 15 | 9 | 0 |

## Scientific interpretation

- No candidate formula was edited. No source-backed regression test could be added because no original equation and no authoritative row/cycle identity were recovered.
- The notebook's `[3.8,4.0] V` and `[1.0,0.5] A` examples are useful provenance for related selectors, but they do not justify changing VoltTwin's candidate windows or declaring a workbook match.
- The 16-feature paper equations specify sample standard deviation (`n-1`) and a generic `-sum(p_i log p_i)` entropy, while VoltTwin candidates use different candidate windows/conventions. These differences are recorded rather than silently reconciled.
- The four entropy columns remain scientifically unresolved. The existing 16-bin histogram is explicitly diagnostic and not an original formula claim.

## Required next evidence

Obtain from the benchmark authors a versioned 67-feature generator or a source-authored table specifying each signal, phase/window, units, sampling/interpolation, integration/derivative estimator, statistical convention, entropy estimator, and workbook-row-to-cycle key. Until then, keep all 67 formulas candidate-only in the application.

## Verification

- Phase 2 rows: 67 (one per feature).
- Original formulas recovered: 0.
- Candidate implementation formulas modified: no.
- Formula Explorer modified: no.
- Existing formula recovery audit and Formula Explorer provenance tests remain applicable.
