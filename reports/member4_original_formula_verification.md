# XJTU Original Formula Verification and Benchmark Reproduction

## Executive summary

No authoritative source was located that maps the 67 `handcraft_features` workbook columns to exact equations or a generating implementation. The author-provided XJTU helper code documents CC/CV selectors and incremental-capacity (`dQ/dV`) routines, but does not state that it generated these workbooks. The SOHbenchmark loader consumes the prepared Excel data rather than extracting the 67 features from raw traces.

Feature status counts: **0 Source Verified**, **0 Partially Verified**, **63 Candidate / Unverified**, **4 Original Formula Unknown**. No feature is promoted based on candidate-to-Excel numerical agreement.

**Genuine original benchmark reproduction is not currently possible.** There is no verified original equation/code against which an original-reference output can be generated. This report therefore keeps the existing candidate extractor comparison separate and labels every such metric candidate-only.

## Research methodology

- Inspected the existing Member 4 formula research, candidate validation, author-CC diagnostic reports, candidate definitions, segmentation and extractor code, and the SOHbenchmark loader and README.
- Inspected the pinned XJTU authors' preprocessing repository and the `XJTUBatteryClass.py` helper methods. The author's notebook/search work described in the prior report was treated as discovery evidence, not as a formula source.
- Inspected the complete supplied SOHbenchmark appendix PDF (22 pages), including a visual review of page 1. Page 1 prints the headings `Appendix A. Dataset`, `Appendix B. Feature engineering`, then immediately `Appendix C. Results`; the remaining pages are benchmark results. No feature equations are present in this supplied appendix.
- Scanned all six workbooks with formulas enabled for formula cells, comments, and defined names; none were found. Column headers and the 67 feature order were compared with the canonical schema.
- Searched exact feature spellings in local source and public GitHub code search. Exact-name hits that were recognizable as feature-value CSV mirrors were not treated as formula provenance. A search miss is not proof that private, deleted, unindexed, or inaccessible source code does not exist.
- Compared candidate values from the unchanged candidate extractor against workbook values using the existing `_profile_pairs` alignment rules without changing them. Equal-count profiles remain positional and explicitly unverified; batch-6 capacity matches remain diagnostic and ambiguous rows remain excluded.
- Consulted the 2024 Nature Communications article through its public PubMed Central full text (PMC11109204), and retrieved Zenodo record metadata and file listings through the Zenodo API. The article describes statistical features from a short pre-full-charge period, but does not establish that its feature set generated these 67 Excel columns.
- The Zenodo records are distinct: 10963339 is the XJTU dataset record, while 11046967 is the PINN4SOH software archive. The XJTU class docstring labels the latter as a dataset link; the Zenodo metadata identifies it as software. No feature formula is inferred from either record.
- Consulted OpenAlex records only to cross-check article titles, DOIs, publication dates, and the 2024 article's PMC identifier; no formula evidence is inferred from bibliographic metadata.

## Sources inspected

| Source | Evidence inspected | Authority for the 67 workbook formulas? |
|---|---|---|
| [XJTU author preprocessing repository at commit `e986a740`](https://github.com/wang-fujin/Battery-dataset-preprocessing-code-library/tree/e986a74054fb64c0f5134f2cc97f4643cd7699d2) and [`XJTUBatteryClass.py`](https://github.com/wang-fujin/Battery-dataset-preprocessing-code-library/blob/e986a74054fb64c0f5134f2cc97f4643cd7699d2/XJTUBatteryClass.py#L165-L276) | `get_CC_value` (lines 165–187) selects charging-stage values using current ≥3.9 A and voltage ≤4.199 V by default; `get_CV_value` (lines 189–205) selects voltage ≥4.199 V by default. `get_IC_curve1/2` (lines 225–276) implement dQ/dV using resampling and/or `I·dt/dV`. | Authoritative for those helper operations only. No link to these 67 columns or workbook generation was found. The dQ/dV helper is not the Excel column `dV_dV_devide_dt` or `dI_dI_devide_dt`. |
| [Author repository README at the same commit](https://github.com/wang-fujin/Battery-dataset-preprocessing-code-library/blob/e986a74054fb64c0f5134f2cc97f4643cd7699d2/README.md) | Identifies the code as a public-dataset reading/preprocessing library and cites Wang et al., *Nature Communications* 15, 4332 (2024), [DOI](https://doi.org/10.1038/s41467-024-48779-z). README links dataset record 10963339; the XJTU class docstring links 11046967 but labels it as a dataset. Zenodo metadata resolves the record types: 10963339 is the dataset, and 11046967 is the PINN4SOH software archive. The docstring's record type is mislabeled; this is not an unresolved Zenodo record conflict. | Dataset/code provenance, not a feature-generation specification. |
| [Zenodo XJTU dataset record 10963339](https://zenodo.org/records/10963339) and [record API metadata](https://zenodo.org/api/records/10963339) | The record identifies itself as a dataset, names the 55-cell experiment, refers to `Data Introduction.pdf` for further details, links the author preprocessing code, and states that the data sampling frequency is 1 Hz. Its file listing contains `Battery Dataset.zip`. | Authoritative for release metadata and the stated acquisition rate, not for the 67 workbook formulas or the transformation into the prepared MAT traces inspected here. |
| [Zenodo PINN4SOH software record 11046967](https://zenodo.org/records/11046967) and [record API metadata](https://zenodo.org/api/records/11046967) | The record identifies itself as software, describes `wang-fujin/PINN4SOH`, and archives `PINN4SOH-v1.zip`. | Authoritative for the software archive's identity, not for the 67 workbook formulas. |
| [Wang et al., *Nature Communications* 15, 4332 (2024)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11109204/) | The article describes extracting statistical features from a short period before full charge and reports a 55-cell XJTU dataset. It does not map that method to the 67-column SOHbenchmark workbooks. | Authoritative for the paper's described method and dataset; no evidence that its feature set is the Excel 67-feature schema or generator. |
| [OpenAlex record for the 2024 article](https://api.openalex.org/works/https://doi.org/10.1038/s41467-024-48779-z) and [OpenAlex record for the SOHbenchmark paper](https://api.openalex.org/works/https://doi.org/10.1016/j.est.2023.109884) | Cross-checks the article titles, publication dates, DOIs, and the 2024 article's PMCID. | Bibliographic metadata only; not formula or workbook-generation evidence. |
| [SOHbenchmark author repository at commit `62230dd`](https://github.com/wang-fujin/SOHbenchmark/tree/62230dd9a857f5c05ac641227b52ec2ffbeb9e15), [`XJTU_loader.py`](https://github.com/wang-fujin/SOHbenchmark/blob/62230dd9a857f5c05ac641227b52ec2ffbeb9e15/dataloader/XJTU_loader.py#L146-L170), and [README](https://github.com/wang-fujin/SOHbenchmark/blob/62230dd9a857f5c05ac641227b52ec2ffbeb9e15/README.md) | `get_features` reads `batch-*_features.xlsx`, parses feature columns and labels, then normalizes them. README describes the data under `data` as preprocessed and points to the XJTU dataset site/code. The paper is Wang et al., *Journal of Energy Storage* 77 (2024), 109884, [DOI](https://doi.org/10.1016/j.est.2023.109884). | Authoritative for consuming prepared features; not a raw-to-67 feature implementation. |
| [Supplied SOHbenchmark appendix PDF](../reference/SOHbenchmark/SOHbenchmark%20-%20Appendix.pdf), page 1 | Visually inspected; Appendix B appears as a heading only before Appendix C results. PDF text extraction covers 22 pages. | No equations or specific generator for the 67 columns in this supplied appendix. |
| Local XJTU workbooks and raw MAT traces under `reference/SOHbenchmark/data/XJTU/` | Six Excel workbooks, 55 sheets, 67 named feature columns plus `label`; formula/comment/name audit is summarized below. MAT traces contain raw time, voltage, current, temperature, and capacity labels. | Primary values/signals, but no embedded formula provenance. |
| [Member 4 candidate extractor](../scripts/member4_xjtu/extractor.py), [feature definitions](../scripts/member4_xjtu/feature_definitions.py), and existing [candidate validation report](./member4_candidate_validation.md) | Candidate intervals and calculations, prior candidate-vs-Excel errors, and explicit alignment caveats. | Not authoritative; metrics describe approximations only. |
| [XJTU author papers-summary repository](https://github.com/wang-fujin/XJTU-Battery-Dataset-Papers-Summary) | Bibliographic discovery resource. Exact target names and feature-workbook generator were not located. | Not a formula specification. |

### Exact-name source search findings

- The misspelled exact names `dV_dV_devide_dt` and `dI_dI_devide_dt` did not yield an authoritative implementation in the searched source/code indexes.
- Searches for `CC_energy`, `Charge_energy`, `CC_CCCT`, `CV_CVCT`, and entropy names produced no target implementation in the XJTU author preprocessing library. Some global hits were downstream CSV feature values; they document neither equations nor provenance.
- The checked-out author preprocessing source is pinned locally at commit `e986a74054fb64c0f5134f2cc97f4643cd7699d2`; SOHbenchmark source was checked at `62230dd9a857f5c05ac641227b52ec2ffbeb9e15`. These are explicit versions, not a claim that no later/private implementation exists.

## Original formula evidence and status rules

No exact original equation or generating implementation for any of the 67 Excel feature columns was found. The author helper's CC/CV selector and dQ/dV code are useful contextual evidence, but there is no authoritative mapping from those helpers to these workbook columns. Therefore no feature is marked Partially Verified: doing so would imply a feature-to-generator connection that the sources do not establish. The 63 non-entropy columns remain Candidate / Unverified; the four entropy columns are Original Formula Unknown because even their estimator and signal are not identified.

The 2024 Nature Communications paper and its XJTU dataset must not be used to silently substitute another feature set. No source was found that maps the paper's reported feature list to this 67-column Excel schema. Similar names or physical plausibility are not that mapping.

## Feature-by-feature verification table

All formulas below are the current candidate interpretation solely to describe what was compared. `Candidate input units`, `Candidate output unit`, and segment are not original-source-verified workbook attributes. For every row, the original benchmark equation remains not located.

| # | Feature | Candidate interpretation only | Candidate input signal | Candidate input units | Candidate output unit | Candidate segment | Status | Feature-specific source evidence | Original benchmark formula |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | CC_energy | Trapezoidal integral of V(t)*I(t), with minutes converted to hours. | voltage and current | V, A | Wh | constant-current-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CC sample selector (charging stage, I ≥ 3.9 A and V ≤ 4.199 V by default); no source links that selector to this Excel column. Candidate extractor instead uses an adaptive current threshold and V ceiling. | Not located; no original equation or implementation verified. |
| 2 | CC_Q | Trapezoidal integral of I(t), with minutes converted to hours. | current and time | A, min | Ah | constant-current-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CC sample selector (charging stage, I ≥ 3.9 A and V ≤ 4.199 V by default); no source links that selector to this Excel column. Candidate extractor instead uses an adaptive current threshold and V ceiling. | Not located; no original equation or implementation verified. |
| 3 | CC_t_mean | Arithmetic mean of elapsed time on a 257-point uniform-time interpolation grid. | elapsed time | min | min | constant-current-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CC sample selector (charging stage, I ≥ 3.9 A and V ≤ 4.199 V by default); no source links that selector to this Excel column. Candidate extractor instead uses an adaptive current threshold and V ceiling. | Not located; no original equation or implementation verified. |
| 4 | CC_V_mean | Arithmetic mean of voltage on a 257-point uniform-time interpolation grid. | voltage | V | V | constant-current-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CC sample selector (charging stage, I ≥ 3.9 A and V ≤ 4.199 V by default); no source links that selector to this Excel column. Candidate extractor instead uses an adaptive current threshold and V ceiling. | Not located; no original equation or implementation verified. |
| 5 | CC_T_mean | Arithmetic mean of temperature on a 257-point uniform-time interpolation grid. | temperature | °C | degC | constant-current-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CC sample selector (charging stage, I ≥ 3.9 A and V ≤ 4.199 V by default); no source links that selector to this Excel column. Candidate extractor instead uses an adaptive current threshold and V ceiling. | Not located; no original equation or implementation verified. |
| 6 | CC_V_std | Population standard deviation (ddof=0) of voltage on that grid. | voltage | V | V | constant-current-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CC sample selector (charging stage, I ≥ 3.9 A and V ≤ 4.199 V by default); no source links that selector to this Excel column. Candidate extractor instead uses an adaptive current threshold and V ceiling. | Not located; no original equation or implementation verified. |
| 7 | CC_T_std | Population standard deviation (ddof=0) of temperature on that grid. | temperature | °C | degC | constant-current-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CC sample selector (charging stage, I ≥ 3.9 A and V ≤ 4.199 V by default); no source links that selector to this Excel column. Candidate extractor instead uses an adaptive current threshold and V ceiling. | Not located; no original equation or implementation verified. |
| 8 | CC_V_skewness | Biased third standardized central moment of voltage. | voltage | V | dimensionless | constant-current-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CC sample selector (charging stage, I ≥ 3.9 A and V ≤ 4.199 V by default); no source links that selector to this Excel column. Candidate extractor instead uses an adaptive current threshold and V ceiling. | Not located; no original equation or implementation verified. |
| 9 | CC_T_skewness | Biased third standardized central moment of temperature. | temperature | °C | dimensionless | constant-current-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CC sample selector (charging stage, I ≥ 3.9 A and V ≤ 4.199 V by default); no source links that selector to this Excel column. Candidate extractor instead uses an adaptive current threshold and V ceiling. | Not located; no original equation or implementation verified. |
| 10 | CC_V_kurtosis | Pearson fourth standardized central moment of voltage. | voltage | V | dimensionless | constant-current-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CC sample selector (charging stage, I ≥ 3.9 A and V ≤ 4.199 V by default); no source links that selector to this Excel column. Candidate extractor instead uses an adaptive current threshold and V ceiling. | Not located; no original equation or implementation verified. |
| 11 | CC_T_kurtosis | Pearson fourth standardized central moment of temperature. | temperature | °C | dimensionless | constant-current-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CC sample selector (charging stage, I ≥ 3.9 A and V ≤ 4.199 V by default); no source links that selector to this Excel column. Candidate extractor instead uses an adaptive current threshold and V ceiling. | Not located; no original equation or implementation verified. |
| 12 | CC_CCCT | Candidate interval end minus start. | time | min | min | constant-current-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CC sample selector (charging stage, I ≥ 3.9 A and V ≤ 4.199 V by default); no source links that selector to this Excel column. Candidate extractor instead uses an adaptive current threshold and V ceiling. | Not located; no original equation or implementation verified. |
| 13 | CC_entropy | Diagnostic proxy: Shannon entropy in nats of a 16-bin equal-width histogram. | voltage proxy | V | nats | constant-current-like charge candidate | Original Formula Unknown | The XJTU author helper documents a CC sample selector (charging stage, I ≥ 3.9 A and V ≤ 4.199 V by default); no source links that selector to this Excel column. Candidate extractor instead uses an adaptive current threshold and V ceiling. | Not located; no original equation or implementation verified. |
| 14 | dV_energy | Trapezoidal integral of V(t)*I(t), with minutes converted to hours. | voltage and current | V, A | Wh | candidate rising 3.9-4.0 V window within CC | Candidate / Unverified | The author helper has CC-window dQ/dV incremental-capacity routines; they do not define this workbook column or its candidate voltage window. | Not located; no original equation or implementation verified. |
| 15 | dV_Q | Trapezoidal integral of I(t), with minutes converted to hours. | current and time | A, min | Ah | candidate rising 3.9-4.0 V window within CC | Candidate / Unverified | The author helper has CC-window dQ/dV incremental-capacity routines; they do not define this workbook column or its candidate voltage window. | Not located; no original equation or implementation verified. |
| 16 | dV_t_mean | Arithmetic mean of elapsed time on a 257-point uniform-time interpolation grid. | elapsed time | min | min | candidate rising 3.9-4.0 V window within CC | Candidate / Unverified | The author helper has CC-window dQ/dV incremental-capacity routines; they do not define this workbook column or its candidate voltage window. | Not located; no original equation or implementation verified. |
| 17 | dV_V_mean | Arithmetic mean of voltage on a 257-point uniform-time interpolation grid. | voltage | V | V | candidate rising 3.9-4.0 V window within CC | Candidate / Unverified | The author helper has CC-window dQ/dV incremental-capacity routines; they do not define this workbook column or its candidate voltage window. | Not located; no original equation or implementation verified. |
| 18 | dV_T_mean | Arithmetic mean of temperature on a 257-point uniform-time interpolation grid. | temperature | °C | degC | candidate rising 3.9-4.0 V window within CC | Candidate / Unverified | The author helper has CC-window dQ/dV incremental-capacity routines; they do not define this workbook column or its candidate voltage window. | Not located; no original equation or implementation verified. |
| 19 | dV_V_std | Population standard deviation (ddof=0) of voltage on that grid. | voltage | V | V | candidate rising 3.9-4.0 V window within CC | Candidate / Unverified | The author helper has CC-window dQ/dV incremental-capacity routines; they do not define this workbook column or its candidate voltage window. | Not located; no original equation or implementation verified. |
| 20 | dV_T_std | Population standard deviation (ddof=0) of temperature on that grid. | temperature | °C | degC | candidate rising 3.9-4.0 V window within CC | Candidate / Unverified | The author helper has CC-window dQ/dV incremental-capacity routines; they do not define this workbook column or its candidate voltage window. | Not located; no original equation or implementation verified. |
| 21 | dV_V_skewness | Biased third standardized central moment of voltage. | voltage | V | dimensionless | candidate rising 3.9-4.0 V window within CC | Candidate / Unverified | The author helper has CC-window dQ/dV incremental-capacity routines; they do not define this workbook column or its candidate voltage window. | Not located; no original equation or implementation verified. |
| 22 | dV_T_skewness | Biased third standardized central moment of temperature. | temperature | °C | dimensionless | candidate rising 3.9-4.0 V window within CC | Candidate / Unverified | The author helper has CC-window dQ/dV incremental-capacity routines; they do not define this workbook column or its candidate voltage window. | Not located; no original equation or implementation verified. |
| 23 | dV_V_kurtosis | Pearson fourth standardized central moment of voltage. | voltage | V | dimensionless | candidate rising 3.9-4.0 V window within CC | Candidate / Unverified | The author helper has CC-window dQ/dV incremental-capacity routines; they do not define this workbook column or its candidate voltage window. | Not located; no original equation or implementation verified. |
| 24 | dV_T_kurtosis | Pearson fourth standardized central moment of temperature. | temperature | °C | dimensionless | candidate rising 3.9-4.0 V window within CC | Candidate / Unverified | The author helper has CC-window dQ/dV incremental-capacity routines; they do not define this workbook column or its candidate voltage window. | Not located; no original equation or implementation verified. |
| 25 | dV_dV_devide_dt | Endpoint signal difference divided by candidate interval duration. | voltage and time | V, min | V/min | candidate rising 3.9-4.0 V window within CC | Candidate / Unverified | The author helper has CC-window dQ/dV incremental-capacity routines; they do not define this workbook column or its candidate voltage window. | Not located; no original equation or implementation verified. |
| 26 | dV_entropy | Diagnostic proxy: Shannon entropy in nats of a 16-bin equal-width histogram. | voltage proxy | V | nats | candidate rising 3.9-4.0 V window within CC | Original Formula Unknown | The author helper has CC-window dQ/dV incremental-capacity routines; they do not define this workbook column or its candidate voltage window. | Not located; no original equation or implementation verified. |
| 27 | CV_energy | Trapezoidal integral of V(t)*I(t), with minutes converted to hours. | voltage and current | V, A | Wh | constant-voltage-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CV selector (V ≥ 4.199 V by default); no source links it to this Excel column. Candidate extractor uses the first rising crossing through the recorded endpoint. | Not located; no original equation or implementation verified. |
| 28 | CV_Q | Trapezoidal integral of I(t), with minutes converted to hours. | current and time | A, min | Ah | constant-voltage-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CV selector (V ≥ 4.199 V by default); no source links it to this Excel column. Candidate extractor uses the first rising crossing through the recorded endpoint. | Not located; no original equation or implementation verified. |
| 29 | CV_t_mean | Arithmetic mean of elapsed time on a 257-point uniform-time interpolation grid. | elapsed time | min | min | constant-voltage-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CV selector (V ≥ 4.199 V by default); no source links it to this Excel column. Candidate extractor uses the first rising crossing through the recorded endpoint. | Not located; no original equation or implementation verified. |
| 30 | CV_C_mean | Arithmetic mean of current on a 257-point uniform-time interpolation grid. | current | not specified | A | constant-voltage-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CV selector (V ≥ 4.199 V by default); no source links it to this Excel column. Candidate extractor uses the first rising crossing through the recorded endpoint. | Not located; no original equation or implementation verified. |
| 31 | CV_T_mean | Arithmetic mean of temperature on a 257-point uniform-time interpolation grid. | temperature | °C | degC | constant-voltage-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CV selector (V ≥ 4.199 V by default); no source links it to this Excel column. Candidate extractor uses the first rising crossing through the recorded endpoint. | Not located; no original equation or implementation verified. |
| 32 | CV_C_std | Population standard deviation (ddof=0) of current on that grid. | current | not specified | A | constant-voltage-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CV selector (V ≥ 4.199 V by default); no source links it to this Excel column. Candidate extractor uses the first rising crossing through the recorded endpoint. | Not located; no original equation or implementation verified. |
| 33 | CV_T_std | Population standard deviation (ddof=0) of temperature on that grid. | temperature | °C | degC | constant-voltage-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CV selector (V ≥ 4.199 V by default); no source links it to this Excel column. Candidate extractor uses the first rising crossing through the recorded endpoint. | Not located; no original equation or implementation verified. |
| 34 | CV_C_skewness | Biased third standardized central moment of current. | current | not specified | dimensionless | constant-voltage-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CV selector (V ≥ 4.199 V by default); no source links it to this Excel column. Candidate extractor uses the first rising crossing through the recorded endpoint. | Not located; no original equation or implementation verified. |
| 35 | CV_T_skewness | Biased third standardized central moment of temperature. | temperature | °C | dimensionless | constant-voltage-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CV selector (V ≥ 4.199 V by default); no source links it to this Excel column. Candidate extractor uses the first rising crossing through the recorded endpoint. | Not located; no original equation or implementation verified. |
| 36 | CV_C_kurtosis | Pearson fourth standardized central moment of current. | current | not specified | dimensionless | constant-voltage-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CV selector (V ≥ 4.199 V by default); no source links it to this Excel column. Candidate extractor uses the first rising crossing through the recorded endpoint. | Not located; no original equation or implementation verified. |
| 37 | CV_T_kurtosis | Pearson fourth standardized central moment of temperature. | temperature | °C | dimensionless | constant-voltage-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CV selector (V ≥ 4.199 V by default); no source links it to this Excel column. Candidate extractor uses the first rising crossing through the recorded endpoint. | Not located; no original equation or implementation verified. |
| 38 | CV_CVCT | Candidate interval end minus start. | time | min | min | constant-voltage-like charge candidate | Candidate / Unverified | The XJTU author helper documents a CV selector (V ≥ 4.199 V by default); no source links it to this Excel column. Candidate extractor uses the first rising crossing through the recorded endpoint. | Not located; no original equation or implementation verified. |
| 39 | CV_entropy | Diagnostic proxy: Shannon entropy in nats of a 16-bin equal-width histogram. | current proxy | A | nats | constant-voltage-like charge candidate | Original Formula Unknown | The XJTU author helper documents a CV selector (V ≥ 4.199 V by default); no source links it to this Excel column. Candidate extractor uses the first rising crossing through the recorded endpoint. | Not located; no original equation or implementation verified. |
| 40 | dI_energy | Trapezoidal integral of V(t)*I(t), with minutes converted to hours. | voltage and current | V, A | Wh | candidate falling 1.0-0.9 A window within CV | Candidate / Unverified | No source definition for the workbook's dI interval or this column was located; the falling-current window is candidate-only. | Not located; no original equation or implementation verified. |
| 41 | dI_Q | Trapezoidal integral of I(t), with minutes converted to hours. | current and time | A, min | Ah | candidate falling 1.0-0.9 A window within CV | Candidate / Unverified | No source definition for the workbook's dI interval or this column was located; the falling-current window is candidate-only. | Not located; no original equation or implementation verified. |
| 42 | dI_t_mean | Arithmetic mean of elapsed time on a 257-point uniform-time interpolation grid. | elapsed time | min | min | candidate falling 1.0-0.9 A window within CV | Candidate / Unverified | No source definition for the workbook's dI interval or this column was located; the falling-current window is candidate-only. | Not located; no original equation or implementation verified. |
| 43 | dI_C_mean | Arithmetic mean of current on a 257-point uniform-time interpolation grid. | current | not specified | A | candidate falling 1.0-0.9 A window within CV | Candidate / Unverified | No source definition for the workbook's dI interval or this column was located; the falling-current window is candidate-only. | Not located; no original equation or implementation verified. |
| 44 | dI_T_mean | Arithmetic mean of temperature on a 257-point uniform-time interpolation grid. | temperature | °C | degC | candidate falling 1.0-0.9 A window within CV | Candidate / Unverified | No source definition for the workbook's dI interval or this column was located; the falling-current window is candidate-only. | Not located; no original equation or implementation verified. |
| 45 | dI_C_std | Population standard deviation (ddof=0) of current on that grid. | current | not specified | A | candidate falling 1.0-0.9 A window within CV | Candidate / Unverified | No source definition for the workbook's dI interval or this column was located; the falling-current window is candidate-only. | Not located; no original equation or implementation verified. |
| 46 | dI_T_std | Population standard deviation (ddof=0) of temperature on that grid. | temperature | °C | degC | candidate falling 1.0-0.9 A window within CV | Candidate / Unverified | No source definition for the workbook's dI interval or this column was located; the falling-current window is candidate-only. | Not located; no original equation or implementation verified. |
| 47 | dI_C_skewness | Biased third standardized central moment of current. | current | not specified | dimensionless | candidate falling 1.0-0.9 A window within CV | Candidate / Unverified | No source definition for the workbook's dI interval or this column was located; the falling-current window is candidate-only. | Not located; no original equation or implementation verified. |
| 48 | dI_T_skewness | Biased third standardized central moment of temperature. | temperature | °C | dimensionless | candidate falling 1.0-0.9 A window within CV | Candidate / Unverified | No source definition for the workbook's dI interval or this column was located; the falling-current window is candidate-only. | Not located; no original equation or implementation verified. |
| 49 | dI_C_kurtosis | Pearson fourth standardized central moment of current. | current | not specified | dimensionless | candidate falling 1.0-0.9 A window within CV | Candidate / Unverified | No source definition for the workbook's dI interval or this column was located; the falling-current window is candidate-only. | Not located; no original equation or implementation verified. |
| 50 | dI_T_kurtosis | Pearson fourth standardized central moment of temperature. | temperature | °C | dimensionless | candidate falling 1.0-0.9 A window within CV | Candidate / Unverified | No source definition for the workbook's dI interval or this column was located; the falling-current window is candidate-only. | Not located; no original equation or implementation verified. |
| 51 | dI_dI_devide_dt | Endpoint signal difference divided by candidate interval duration. | current and time | A, min | A/min | candidate falling 1.0-0.9 A window within CV | Candidate / Unverified | No source definition for the workbook's dI interval or this column was located; the falling-current window is candidate-only. | Not located; no original equation or implementation verified. |
| 52 | dI_entropy | Diagnostic proxy: Shannon entropy in nats of a 16-bin equal-width histogram. | current proxy | A | nats | candidate falling 1.0-0.9 A window within CV | Original Formula Unknown | No source definition for the workbook's dI interval or this column was located; the falling-current window is candidate-only. | Not located; no original equation or implementation verified. |
| 53 | Charge_energy | Trapezoidal integral of V(t)*I(t), with minutes converted to hours. | voltage and current | V, A | Wh | complete stored charge trace | Candidate / Unverified | No source defines the workbook's full-charge start/end limits; the candidate uses the full stored charge trace. | Not located; no original equation or implementation verified. |
| 54 | Charge_Q | Trapezoidal integral of I(t), with minutes converted to hours. | current and time | A, min | Ah | complete stored charge trace | Candidate / Unverified | No source defines the workbook's full-charge start/end limits; the candidate uses the full stored charge trace. | Not located; no original equation or implementation verified. |
| 55 | Charge_t_mean | Arithmetic mean of elapsed time on a 257-point uniform-time interpolation grid. | elapsed time | min | min | complete stored charge trace | Candidate / Unverified | No source defines the workbook's full-charge start/end limits; the candidate uses the full stored charge trace. | Not located; no original equation or implementation verified. |
| 56 | Charge_V_mean | Arithmetic mean of voltage on a 257-point uniform-time interpolation grid. | voltage | V | V | complete stored charge trace | Candidate / Unverified | No source defines the workbook's full-charge start/end limits; the candidate uses the full stored charge trace. | Not located; no original equation or implementation verified. |
| 57 | Charge_C_mean | Arithmetic mean of current on a 257-point uniform-time interpolation grid. | current | not specified | A | complete stored charge trace | Candidate / Unverified | No source defines the workbook's full-charge start/end limits; the candidate uses the full stored charge trace. | Not located; no original equation or implementation verified. |
| 58 | Charge_T_mean | Arithmetic mean of temperature on a 257-point uniform-time interpolation grid. | temperature | °C | degC | complete stored charge trace | Candidate / Unverified | No source defines the workbook's full-charge start/end limits; the candidate uses the full stored charge trace. | Not located; no original equation or implementation verified. |
| 59 | Charge_C_std | Population standard deviation (ddof=0) of current on that grid. | current | not specified | A | complete stored charge trace | Candidate / Unverified | No source defines the workbook's full-charge start/end limits; the candidate uses the full stored charge trace. | Not located; no original equation or implementation verified. |
| 60 | Charge_V_std | Population standard deviation (ddof=0) of voltage on that grid. | voltage | V | V | complete stored charge trace | Candidate / Unverified | No source defines the workbook's full-charge start/end limits; the candidate uses the full stored charge trace. | Not located; no original equation or implementation verified. |
| 61 | Charge_T_std | Population standard deviation (ddof=0) of temperature on that grid. | temperature | °C | degC | complete stored charge trace | Candidate / Unverified | No source defines the workbook's full-charge start/end limits; the candidate uses the full stored charge trace. | Not located; no original equation or implementation verified. |
| 62 | Charge_C_skewness | Biased third standardized central moment of current. | current | not specified | dimensionless | complete stored charge trace | Candidate / Unverified | No source defines the workbook's full-charge start/end limits; the candidate uses the full stored charge trace. | Not located; no original equation or implementation verified. |
| 63 | Charge_V_skewness | Biased third standardized central moment of voltage. | voltage | V | dimensionless | complete stored charge trace | Candidate / Unverified | No source defines the workbook's full-charge start/end limits; the candidate uses the full stored charge trace. | Not located; no original equation or implementation verified. |
| 64 | Charge_T_skewness | Biased third standardized central moment of temperature. | temperature | °C | dimensionless | complete stored charge trace | Candidate / Unverified | No source defines the workbook's full-charge start/end limits; the candidate uses the full stored charge trace. | Not located; no original equation or implementation verified. |
| 65 | Charge_C_kurtosis | Pearson fourth standardized central moment of current. | current | not specified | dimensionless | complete stored charge trace | Candidate / Unverified | No source defines the workbook's full-charge start/end limits; the candidate uses the full stored charge trace. | Not located; no original equation or implementation verified. |
| 66 | Charge_V_kurtosis | Pearson fourth standardized central moment of voltage. | voltage | V | dimensionless | complete stored charge trace | Candidate / Unverified | No source defines the workbook's full-charge start/end limits; the candidate uses the full stored charge trace. | Not located; no original equation or implementation verified. |
| 67 | Charge_T_kurtosis | Pearson fourth standardized central moment of temperature. | temperature | °C | dimensionless | complete stored charge trace | Candidate / Unverified | No source defines the workbook's full-charge start/end limits; the candidate uses the full stored charge trace. | Not located; no original equation or implementation verified. |

## Workbook formula audit

| Batch | Sheets | Feature columns (excluding label) | Formula cells | Commented cells | Defined names |
| --- | --- | --- | --- | --- | --- |
| 1 | 8 | 67 | 0 | 0 | 0 |
| 2 | 15 | 67 | 0 | 0 | 0 |
| 3 | 8 | 67 | 0 | 0 | 0 |
| 4 | 8 | 67 | 0 | 0 | 0 |
| 5 | 8 | 67 | 0 | 0 | 0 |
| 6 | 8 | 67 | 0 | 0 | 0 |

The workbooks contain values but no embedded formulas, comments, or defined names that expose their calculation provenance.

## Raw sampling and segmentation evidence

- Loaded 27,535 raw cycles; samples per cycle ranged from 128 to 128.
- Using `rtol=1e-6, atol=1e-9` against each cycle's median Δt, 0 cycles were classified nonuniform. The maximum relative Δt deviation from a cycle median was 1.08e-13; the median cycle step was 0.376976378 min (global interval range 0.0918661417–1.18486614 min).
- The XJTU dataset record states a 1 Hz sampling frequency ([Zenodo record 10963339](https://zenodo.org/records/10963339)). The MAT traces analyzed here have only 128 timestamped samples per cycle; measured intervals range from 0.0918661417 to 1.18486614 min (median per-cycle interval 0.376976378 min), much coarser than 1 s. The source-to-MAT transformation is not established by the available evidence; do not treat these prepared traces as a verified 1 Hz raw stream.
- This contradicts older Member 4 documentation that described these prepared 128-point traces as nonuniform. The new observation is for the exact loaded MAT files and tolerance stated above; prior reports were not edited.
- Candidate extraction defaults: adaptive CC current plateau with a 4.199 V ceiling; CV first rising 4.199 V crossing to trace end; dV rising 3.9–4.0 V within candidate CC; dI falling 1.0–0.9 A within candidate CV; Charge is the complete stored trace. None of these exact workbook boundary conventions is verified.
- Candidate integrals use trapezoids over stored timestamps and interpolated endpoints. Candidate moments use a 257-point uniform-time grid; candidate entropy is a 16-bin histogram proxy. These describe candidate code behavior only.

## Alignment limitations and coverage

Alignment decisions reuse `scripts.member4_xjtu.validation._profile_pairs` unchanged. Equal-count profiles are paired by row position and remain unverified. When counts differ, the existing unique monotone capacity match with tolerance 1e-6 is used; ambiguous rows are excluded. The ambiguous count is a subset of unmatched workbook rows and is not added again. Unmatched raw cycles are separately reported here.

| Batch | Profiles | Raw cycles | Workbook rows | Matched pairs | Unmatched workbook rows | Ambiguous rows (subset) | Unmatched raw cycles | Alignment method |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 8 | 3211 | 3211 | 3211 | 0 | 0 | 0 | positional_unverified_equal_counts |
| 2 | 15 | 3727 | 3727 | 3727 | 0 | 0 | 0 | positional_unverified_equal_counts |
| 3 | 8 | 4608 | 4608 | 4608 | 0 | 0 | 0 | positional_unverified_equal_counts |
| 4 | 8 | 5670 | 5670 | 5670 | 0 | 0 | 0 | positional_unverified_equal_counts |
| 5 | 8 | 1975 | 1975 | 1975 | 0 | 0 | 0 | positional_unverified_equal_counts |
| 6 | 8 | 8344 | 7746 | 7129 | 617 | 489 | 1215 | unique_monotone_capacity_diagnostic |

### Per-profile alignment accounting

| Batch | Profile | Raw cycles | Workbook rows | Matched pairs | Unmatched workbook rows | Ambiguous rows | Unmatched raw cycles | Method | Mean abs label Δ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Sheet1 | 389 | 389 | 389 | 0 | 0 | 0 | positional_unverified_equal_counts | 0 |
| 1 | Sheet2 | 406 | 406 | 406 | 0 | 0 | 0 | positional_unverified_equal_counts | 0 |
| 1 | Sheet3 | 392 | 392 | 392 | 0 | 0 | 0 | positional_unverified_equal_counts | 0 |
| 1 | Sheet4 | 395 | 395 | 395 | 0 | 0 | 0 | positional_unverified_equal_counts | 0 |
| 1 | Sheet5 | 402 | 402 | 402 | 0 | 0 | 0 | positional_unverified_equal_counts | 0 |
| 1 | Sheet6 | 407 | 407 | 407 | 0 | 0 | 0 | positional_unverified_equal_counts | 0 |
| 1 | Sheet7 | 401 | 401 | 401 | 0 | 0 | 0 | positional_unverified_equal_counts | 0 |
| 1 | Sheet8 | 419 | 419 | 419 | 0 | 0 | 0 | positional_unverified_equal_counts | 0 |
| 2 | Sheet1 | 298 | 298 | 298 | 0 | 0 | 0 | positional_unverified_equal_counts | 6.04026846e-05 |
| 2 | Sheet2 | 291 | 291 | 291 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.00035395189 |
| 2 | Sheet3 | 285 | 285 | 285 | 0 | 0 | 0 | positional_unverified_equal_counts | 0 |
| 2 | Sheet4 | 321 | 321 | 321 | 0 | 0 | 0 | positional_unverified_equal_counts | 0 |
| 2 | Sheet5 | 296 | 296 | 296 | 0 | 0 | 0 | positional_unverified_equal_counts | 0 |
| 2 | Sheet6 | 321 | 321 | 321 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.000190031153 |
| 2 | Sheet7 | 318 | 318 | 318 | 0 | 0 | 0 | positional_unverified_equal_counts | 0 |
| 2 | Sheet8 | 269 | 269 | 269 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.000661710037 |
| 2 | Sheet9 | 286 | 286 | 286 | 0 | 0 | 0 | positional_unverified_equal_counts | 0 |
| 2 | Sheet10 | 163 | 163 | 163 | 0 | 0 | 0 | positional_unverified_equal_counts | 6.13496933e-05 |
| 2 | Sheet11 | 130 | 130 | 130 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.000292307692 |
| 2 | Sheet12 | 211 | 211 | 211 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.000236966825 |
| 2 | Sheet13 | 225 | 225 | 225 | 0 | 0 | 0 | positional_unverified_equal_counts | 8.88888889e-05 |
| 2 | Sheet14 | 146 | 146 | 146 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.000205479452 |
| 2 | Sheet15 | 167 | 167 | 167 | 0 | 0 | 0 | positional_unverified_equal_counts | 0 |
| 3 | Sheet1 | 591 | 591 | 591 | 0 | 0 | 0 | positional_unverified_equal_counts | 2.01380555e-16 |
| 3 | Sheet2 | 551 | 551 | 551 | 0 | 0 | 0 | positional_unverified_equal_counts | 1.99477458e-16 |
| 3 | Sheet3 | 666 | 666 | 666 | 0 | 0 | 0 | positional_unverified_equal_counts | 3.78960437e-05 |
| 3 | Sheet4 | 556 | 556 | 556 | 0 | 0 | 0 | positional_unverified_equal_counts | 1.94089349e-16 |
| 3 | Sheet5 | 561 | 561 | 561 | 0 | 0 | 0 | positional_unverified_equal_counts | 1.96317512e-16 |
| 3 | Sheet6 | 541 | 541 | 541 | 0 | 0 | 0 | positional_unverified_equal_counts | 1.90441214e-16 |
| 3 | Sheet7 | 526 | 526 | 526 | 0 | 0 | 0 | positional_unverified_equal_counts | 3.98398709e-05 |
| 3 | Sheet8 | 616 | 616 | 616 | 0 | 0 | 0 | positional_unverified_equal_counts | 1.93207643e-16 |
| 4 | Sheet1 | 798 | 798 | 798 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.000708514219 |
| 4 | Sheet2 | 672 | 672 | 672 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.000895452856 |
| 4 | Sheet3 | 672 | 672 | 672 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.000821391133 |
| 4 | Sheet4 | 726 | 726 | 726 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.000777666727 |
| 4 | Sheet5 | 738 | 738 | 738 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.000738722442 |
| 4 | Sheet6 | 714 | 714 | 714 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.00112357838 |
| 4 | Sheet7 | 600 | 600 | 600 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.0010910507 |
| 4 | Sheet8 | 750 | 750 | 750 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.00073516105 |
| 5 | Sheet1 | 196 | 196 | 196 | 0 | 0 | 0 | positional_unverified_equal_counts | 2.36772053e-16 |
| 5 | Sheet2 | 306 | 306 | 306 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.000339109968 |
| 5 | Sheet3 | 339 | 339 | 339 | 0 | 0 | 0 | positional_unverified_equal_counts | 1.62366736e-05 |
| 5 | Sheet4 | 251 | 251 | 251 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.000593735148 |
| 5 | Sheet5 | 273 | 273 | 273 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.000297753479 |
| 5 | Sheet6 | 218 | 218 | 218 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.000292490102 |
| 5 | Sheet7 | 185 | 185 | 185 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.000319531838 |
| 5 | Sheet8 | 207 | 207 | 207 | 0 | 0 | 0 | positional_unverified_equal_counts | 0.000340932859 |
| 6 | Sheet1 | 948 | 874 | 807 | 67 | 60 | 141 | unique_monotone_capacity_diagnostic | 2.25621532e-16 |
| 6 | Sheet2 | 1225 | 1131 | 1036 | 95 | 75 | 189 | unique_monotone_capacity_diagnostic | 2.22044605e-16 |
| 6 | Sheet3 | 907 | 837 | 783 | 54 | 48 | 124 | unique_monotone_capacity_diagnostic | 2.14955058e-16 |
| 6 | Sheet4 | 939 | 868 | 810 | 58 | 54 | 129 | unique_monotone_capacity_diagnostic | 2.1080531e-16 |
| 6 | Sheet5 | 1287 | 1200 | 1107 | 93 | 82 | 180 | unique_monotone_capacity_diagnostic | 2.27861492e-16 |
| 6 | Sheet6 | 1062 | 992 | 909 | 83 | 61 | 153 | unique_monotone_capacity_diagnostic | 2.11052298e-16 |
| 6 | Sheet7 | 934 | 874 | 798 | 76 | 45 | 136 | unique_monotone_capacity_diagnostic | 1.98114986e-16 |
| 6 | Sheet8 | 1042 | 970 | 879 | 91 | 64 | 163 | unique_monotone_capacity_diagnostic | 6.14852488e-10 |

## Candidate comparison results (not original reproduction)

Metrics compare the existing default candidate extractor with workbook values under the preserved alignment rules. They are **not** original-reference results and do not establish formula provenance. Valid matched cycles require finite workbook and candidate values. Workbook invalid and candidate invalid counts are reported independently among aligned rows. Relative error is defined as `MAE / mean(abs(workbook values)) × 100`; it is unavailable when that denominator is zero. Pearson and Spearman are undefined for fewer than two valid pairs or constant input.

### Overall feature-wise candidate metrics (67 rows)

| Feature | Aligned | Valid | Workbook invalid | Candidate invalid | MAE | RMSE | Pearson r | Spearman ρ | Relative MAE (%) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CC_energy | 26320 | 26320 | 0 | 0 | 0.0582700025 | 0.083742078 | 0.999337177 | 0.997837346 | 1.21148577 |
| CC_Q | 26320 | 26320 | 0 | 0 | 0.0139619091 | 0.0204608009 | 0.999412423 | 0.998185969 | 1.13260167 |
| CC_t_mean | 26320 | 26320 | 0 | 0 | 0.170494615 | 1.39067771 | 0.953207966 | 0.9989314 | 1.93215107 |
| CC_V_mean | 26320 | 26320 | 0 | 0 | 0.00337889858 | 0.00448881187 | 0.998796876 | 0.996940097 | 0.0860544423 |
| CC_T_mean | 26320 | 26320 | 0 | 0 | 0.0186390264 | 0.0463517099 | 0.999877491 | 0.999895051 | 0.0682143801 |
| CC_V_std | 26320 | 26320 | 0 | 0 | 0.00172822535 | 0.00245684376 | 0.997086475 | 0.984549526 | 1.30360323 |
| CC_T_std | 26320 | 26320 | 0 | 0 | 0.00939201578 | 0.0357819144 | 0.999194085 | 0.999298444 | 0.743236743 |
| CC_V_skewness | 26320 | 26320 | 0 | 0 | 0.0662954033 | 0.0922407575 | 0.925362455 | 0.916142813 | 26.403264 |
| CC_T_skewness | 26320 | 26320 | 0 | 0 | 0.0358547737 | 0.25166574 | 0.939463199 | 0.984388879 | 6.83491296 |
| CC_V_kurtosis | 26320 | 26320 | 0 | 0 | 0.11919964 | 0.179649244 | 0.965902156 | 0.959474285 | 5.18060986 |
| CC_T_kurtosis | 26320 | 26320 | 0 | 0 | 0.108123728 | 1.36245738 | 0.768138617 | 0.972737252 | 4.50042036 |
| CC_CCCT | 26320 | 26319 | 0 | 1 | 0.340690911 | 2.78205942 | 0.953181999 | 0.998947211 | 1.93044544 |
| CC_entropy | 26320 | 26320 | 0 | 0 | 5.08988817 | 5.09048035 | 0.969874669 | 0.951107055 | 66.2488518 |
| dV_energy | 26320 | 26319 | 0 | 1 | 0.00938004474 | 0.0463554488 | 0.963780892 | 0.998687972 | 0.979686581 |
| dV_Q | 26320 | 26319 | 0 | 1 | 0.00237648976 | 0.0117647702 | 0.963746633 | 0.998696036 | 0.979530733 |
| dV_t_mean | 26320 | 26319 | 0 | 1 | 0.0193946756 | 0.174316669 | 0.902838905 | 0.998745288 | 1.13004593 |
| dV_V_mean | 26320 | 26319 | 0 | 1 | 0.000240161214 | 0.00111402501 | 0.752935016 | 0.976439743 | 0.00608541383 |
| dV_T_mean | 26320 | 26319 | 0 | 1 | 0.00661500766 | 0.0310675705 | 0.999953325 | 0.999984738 | 0.0238683318 |
| dV_V_std | 26320 | 26319 | 0 | 1 | 0.000124403864 | 0.000204794646 | 0.502382128 | 0.708826288 | 0.431355718 |
| dV_T_std | 26320 | 26319 | 0 | 1 | 0.00746680105 | 0.0184634833 | 0.995379069 | 0.995951244 | 3.08825627 |
| dV_V_skewness | 26320 | 26319 | 0 | 1 | 0.00718889697 | 0.0458258526 | 0.757905676 | 0.993823041 | 4.86225557 |
| dV_T_skewness | 26320 | 26319 | 0 | 1 | 0.147386931 | 0.479916884 | 0.639734115 | 0.86550544 | 53.1486796 |
| dV_V_kurtosis | 26320 | 26319 | 0 | 1 | 0.00430571662 | 0.0210236967 | 0.579150072 | 0.951974878 | 0.236127142 |
| dV_T_kurtosis | 26320 | 26319 | 0 | 1 | 0.460803815 | 4.69337651 | 0.159631266 | 0.799231438 | 20.6592244 |
| dV_dV_devide_dt | 26320 | 26319 | 0 | 1 | 0.000489833069 | 0.00515941627 | 0.625051258 | 0.998714454 | 1.66954496 |
| dV_entropy | 26320 | 26319 | 0 | 1 | 4.78006871 | 4.78173281 | 0.289179757 | 0.109551299 | 63.3644489 |
| CV_energy | 26320 | 26320 | 0 | 0 | 0.0318277057 | 0.0405480498 | 0.991981724 | 0.991161167 | 2.17362386 |
| CV_Q | 26320 | 26320 | 0 | 0 | 0.00757786847 | 0.00965441506 | 0.991979969 | 0.991160691 | 2.17355343 |
| CV_t_mean | 26320 | 26320 | 0 | 0 | 0.0631136023 | 0.130323073 | 0.998219726 | 0.999674238 | 0.448565202 |
| CV_C_mean | 26320 | 26320 | 0 | 0 | 0.0106935807 | 0.0177545324 | 0.987843409 | 0.98391655 | 1.42371186 |
| CV_T_mean | 26320 | 26320 | 0 | 0 | 0.015071462 | 0.0979952708 | 0.999314018 | 0.99975729 | 0.0612712725 |
| CV_C_std | 26320 | 26320 | 0 | 0 | 0.0186476791 | 0.0237060394 | 0.99443846 | 0.932214685 | 2.09117781 |
| CV_T_std | 26320 | 26320 | 0 | 0 | 0.00978819363 | 0.0387091407 | 0.998866595 | 0.999556771 | 0.442356255 |
| CV_C_skewness | 26320 | 26320 | 0 | 0 | 0.0160773357 | 0.0229721863 | 0.996647992 | 0.99566791 | 0.819270405 |
| CV_T_skewness | 26320 | 26320 | 0 | 0 | 0.0136273003 | 0.0825088951 | 0.846816421 | 0.980277705 | 1.95576384 |
| CV_C_kurtosis | 26320 | 26320 | 0 | 0 | 0.0775898987 | 0.102023893 | 0.997097848 | 0.99552183 | 1.21442147 |
| CV_T_kurtosis | 26320 | 26320 | 0 | 0 | 0.0180147552 | 0.127117539 | 0.849133075 | 0.994148645 | 0.85622837 |
| CV_CVCT | 26320 | 26320 | 0 | 0 | 0.118418294 | 0.255437485 | 0.998252499 | 0.999680362 | 0.420933631 |
| CV_entropy | 26320 | 26320 | 0 | 0 | 4.69811927 | 4.69892213 | 0.991974543 | 0.98694905 | 71.8324677 |
| dI_energy | 26320 | 26245 | 0 | 75 | 0.00120781183 | 0.00321231486 | 0.938226106 | 0.990451573 | 2.66032965 |
| dI_Q | 26320 | 26245 | 0 | 75 | 0.00028757776 | 0.000764846215 | 0.938223422 | 0.990451119 | 2.6603313 |
| dI_t_mean | 26320 | 26245 | 0 | 75 | 0.00907108836 | 0.0241701766 | 0.938338674 | 0.990310309 | 2.65276625 |
| dI_C_mean | 26320 | 26245 | 0 | 75 | 0.000565289144 | 0.00175746719 | 0.365081788 | 0.739271679 | 0.0596005078 |
| dI_T_mean | 26320 | 26245 | 0 | 75 | 0.0156943546 | 0.14460606 | 0.998604392 | 0.999691539 | 0.0594066478 |
| dI_C_std | 26320 | 26245 | 0 | 75 | 0.00032197513 | 0.00109549254 | -0.152981676 | 0.0851243209 | 1.11370184 |
| dI_T_std | 26320 | 26245 | 0 | 75 | 0.0122646652 | 0.0156038929 | 0.93266256 | 0.902866853 | 11.7917204 |
| dI_C_skewness | 26320 | 26245 | 0 | 75 | 0.00922420488 | 0.0193847087 | 0.871020924 | 0.90270259 | 14.8783916 |
| dI_T_skewness | 26320 | 26245 | 0 | 75 | 0.273947198 | 0.457013192 | 0.377236451 | 0.465355718 | 100.821174 |
| dI_C_kurtosis | 26320 | 26245 | 0 | 75 | 0.0110463538 | 0.0164892548 | 0.368775928 | 0.374106287 | 0.611907826 |
| dI_T_kurtosis | 26320 | 26245 | 0 | 75 | 0.447180647 | 2.99021992 | 0.0736281843 | 0.349161305 | 21.2894177 |
| dI_dI_devide_dt | 26320 | 26245 | 0 | 75 | 0.0012052474 | 0.00482652785 | 0.985143668 | 0.994381951 | 0.818598559 |
| dI_entropy | 26320 | 26245 | 0 | 75 | 2.56787697 | 2.58153552 | -0.210820305 | -0.0567003005 | 48.1058186 |
| Charge_energy | 26320 | 26320 | 0 | 0 | 0.00528029534 | 0.0332949208 | 0.99981228 | 0.999249144 | 0.0841218448 |
| Charge_Q | 26320 | 26320 | 0 | 0 | 0.00129092431 | 0.00814811528 | 0.999837223 | 0.999188151 | 0.0816021865 |
| Charge_t_mean | 26320 | 26320 | 0 | 0 | 0.128569306 | 1.92342072 | 0.932608995 | 0.999701428 | 0.562148687 |
| Charge_V_mean | 26320 | 26320 | 0 | 0 | 0.000927416811 | 0.00135476345 | 0.999754663 | 0.999790539 | 0.0226667303 |
| Charge_C_mean | 26320 | 26320 | 0 | 0 | 0.00181077141 | 0.00882279601 | 0.999837223 | 0.999804262 | 0.0877916851 |
| Charge_T_mean | 26320 | 26320 | 0 | 0 | 0.006907309 | 0.0710677431 | 0.999667904 | 0.999775259 | 0.0269861991 |
| Charge_C_std | 26320 | 26320 | 0 | 0 | 0.00115756997 | 0.0037101279 | 0.999966409 | 0.999853306 | 0.0633580851 |
| Charge_V_std | 26320 | 26320 | 0 | 0 | 0.00182831066 | 0.00251068904 | 0.999120763 | 0.999138981 | 1.18147511 |
| Charge_T_std | 26320 | 26320 | 0 | 0 | 0.0067424887 | 0.0668666038 | 0.996794259 | 0.998814497 | 0.284608547 |
| Charge_C_skewness | 26320 | 26320 | 0 | 0 | 0.00249676757 | 0.00977719483 | 0.999694393 | 0.999723501 | 0.675472168 |
| Charge_V_skewness | 26320 | 26320 | 0 | 0 | 0.0317812202 | 0.0605212889 | 0.994282733 | 0.997862249 | 2.52400897 |
| Charge_T_skewness | 26320 | 26320 | 0 | 0 | 0.00907192963 | 0.0651467661 | 0.967371378 | 0.990306162 | 4.75128387 |
| Charge_C_kurtosis | 26320 | 26320 | 0 | 0 | 0.00505621078 | 0.0306703938 | 0.99490684 | 0.999816269 | 0.370303423 |
| Charge_V_kurtosis | 26320 | 26320 | 0 | 0 | 0.183476512 | 0.483252468 | 0.956855018 | 0.992475566 | 5.42301609 |
| Charge_T_kurtosis | 26320 | 26320 | 0 | 0 | 0.0152726648 | 0.105186388 | 0.92555547 | 0.988295607 | 0.94700131 |

### Batch-wise feature candidate metrics (6 × 67 rows)

| Batch | Feature | Aligned | Valid | Workbook invalid | Candidate invalid | MAE | RMSE | Pearson r | Spearman ρ | Relative MAE (%) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | CC_energy | 3211 | 3211 | 0 | 0 | 0.055245591 | 0.0641518775 | 0.997807363 | 0.989044842 | 0.933297575 |
| 1 | CC_Q | 3211 | 3211 | 0 | 0 | 0.0129930345 | 0.0151384024 | 0.99832465 | 0.991119491 | 0.850452777 |
| 1 | CC_t_mean | 3211 | 3211 | 0 | 0 | 0.09736969 | 0.113510296 | 0.998316459 | 0.991111071 | 0.849793043 |
| 1 | CC_V_mean | 3211 | 3211 | 0 | 0 | 0.00340832259 | 0.00379936485 | 0.996785334 | 0.977946036 | 0.0879276055 |
| 1 | CC_T_mean | 3211 | 3211 | 0 | 0 | 0.0143238162 | 0.0171574758 | 0.999988781 | 0.999980733 | 0.0519661903 |
| 1 | CC_V_std | 3211 | 3211 | 0 | 0 | 0.00124466872 | 0.00145151332 | 0.980109568 | 0.966516394 | 0.833414735 |
| 1 | CC_T_std | 3211 | 3211 | 0 | 0 | 0.00592813304 | 0.024844124 | 0.989766891 | 0.997873516 | 0.509558702 |
| 1 | CC_V_skewness | 3211 | 3211 | 0 | 0 | 0.0834651039 | 0.0873359012 | 0.974300138 | 0.980334643 | 23.0590015 |
| 1 | CC_T_skewness | 3211 | 3211 | 0 | 0 | 0.0111914468 | 0.020195008 | 0.977112277 | 0.993048024 | 2.90620073 |
| 1 | CC_V_kurtosis | 3211 | 3211 | 0 | 0 | 0.134920445 | 0.147699078 | 0.822402572 | 0.853670974 | 5.58206384 |
| 1 | CC_T_kurtosis | 3211 | 3211 | 0 | 0 | 0.0154329855 | 0.0310651236 | 0.947706649 | 0.983892989 | 0.803439977 |
| 1 | CC_CCCT | 3211 | 3211 | 0 | 0 | 0.194855266 | 0.227038734 | 0.998324591 | 0.991130742 | 0.850291711 |
| 1 | CC_entropy | 3211 | 3211 | 0 | 0 | 5.06523635 | 5.06528957 | 0.853388186 | 0.910670441 | 66.7863795 |
| 1 | dV_energy | 3211 | 3211 | 0 | 0 | 0.00570468719 | 0.00648572879 | 0.997581591 | 0.991801084 | 0.619790553 |
| 1 | dV_Q | 3211 | 3211 | 0 | 0 | 0.00144693482 | 0.00164558324 | 0.997573461 | 0.991927119 | 0.620373162 |
| 1 | dV_t_mean | 3211 | 3211 | 0 | 0 | 0.01128383 | 0.013263871 | 0.99651488 | 0.990598761 | 0.644862563 |
| 1 | dV_V_mean | 3211 | 3211 | 0 | 0 | 0.000129618428 | 0.000182471482 | 0.920537596 | 0.909604785 | 0.00328450129 |
| 1 | dV_T_mean | 3211 | 3211 | 0 | 0 | 0.00660362409 | 0.00832998099 | 0.999992972 | 0.999986932 | 0.0232291296 |
| 1 | dV_V_std | 3211 | 3211 | 0 | 0 | 0.000145181189 | 0.000170231034 | 0.458949528 | 0.468258178 | 0.502777648 |
| 1 | dV_T_std | 3211 | 3211 | 0 | 0 | 0.00699288095 | 0.00910273943 | 0.986135078 | 0.98513512 | 4.62746216 |
| 1 | dV_V_skewness | 3211 | 3211 | 0 | 0 | 0.00296357261 | 0.00496576283 | 0.967885009 | 0.959528305 | 1.93390799 |
| 1 | dV_T_skewness | 3211 | 3211 | 0 | 0 | 0.133019152 | 0.214924545 | 0.856795126 | 0.883375941 | 47.0963997 |
| 1 | dV_V_kurtosis | 3211 | 3211 | 0 | 0 | 0.00341625566 | 0.00579744372 | 0.870169104 | 0.887450939 | 0.1876681 |
| 1 | dV_T_kurtosis | 3211 | 3211 | 0 | 0 | 0.222511302 | 0.471078262 | 0.65235701 | 0.825169559 | 10.6832317 |
| 1 | dV_dV_devide_dt | 3211 | 3211 | 0 | 0 | 7.98607558e-05 | 0.000145664219 | 0.997840066 | 0.994943013 | 0.280166823 |
| 1 | dV_entropy | 3211 | 3211 | 0 | 0 | 4.71264789 | 4.71504235 | 0.653923042 | 0.367124589 | 63.0333952 |
| 1 | CV_energy | 3211 | 3211 | 0 | 0 | 0.0339337323 | 0.041512242 | 0.982881474 | 0.979722966 | 2.40195836 |
| 1 | CV_Q | 3211 | 3211 | 0 | 0 | 0.00807927507 | 0.00988352964 | 0.982882426 | 0.97971549 | 2.40188223 |
| 1 | CV_t_mean | 3211 | 3211 | 0 | 0 | 0.0671875798 | 0.0779015446 | 0.999836527 | 0.998948689 | 0.47056027 |
| 1 | CV_C_mean | 3211 | 3211 | 0 | 0 | 0.0111412977 | 0.0145265938 | 0.963749601 | 0.957837088 | 1.56140891 |
| 1 | CV_T_mean | 3211 | 3211 | 0 | 0 | 0.0148734641 | 0.0178400968 | 0.999988914 | 0.999960448 | 0.0589447162 |
| 1 | CV_C_std | 3211 | 3211 | 0 | 0 | 0.0199296365 | 0.0234308479 | 0.815361745 | 0.80494938 | 2.41652112 |
| 1 | CV_T_std | 3211 | 3211 | 0 | 0 | 0.0106051789 | 0.0193328628 | 0.998410892 | 0.99933309 | 0.537007135 |
| 1 | CV_C_skewness | 3211 | 3211 | 0 | 0 | 0.0199816119 | 0.0300598931 | 0.987061025 | 0.98909683 | 1.01256833 |
| 1 | CV_T_skewness | 3211 | 3211 | 0 | 0 | 0.00827262336 | 0.0182915909 | 0.992376344 | 0.997132018 | 1.14625875 |
| 1 | CV_C_kurtosis | 3211 | 3211 | 0 | 0 | 0.0956486504 | 0.129183351 | 0.990240251 | 0.989147739 | 1.48532109 |
| 1 | CV_T_kurtosis | 3211 | 3211 | 0 | 0 | 0.0178521879 | 0.0219459251 | 0.997383536 | 0.995864512 | 0.830425382 |
| 1 | CV_CVCT | 3211 | 3211 | 0 | 0 | 0.12664274 | 0.148441252 | 0.999839749 | 0.998956255 | 0.443609429 |
| 1 | CV_entropy | 3211 | 3211 | 0 | 0 | 4.70939687 | 4.70956107 | 0.976901639 | 0.968326712 | 71.7424298 |
| 1 | dI_energy | 3211 | 3211 | 0 | 0 | 0.000956578028 | 0.00111538673 | 0.993109303 | 0.988948818 | 2.09389097 |
| 1 | dI_Q | 3211 | 3211 | 0 | 0 | 0.000227756133 | 0.000265567919 | 0.993108822 | 0.988932163 | 2.09386832 |
| 1 | dI_t_mean | 3211 | 3211 | 0 | 0 | 0.00719605977 | 0.0083992683 | 0.993118984 | 0.9890169 | 2.09074569 |
| 1 | dI_C_mean | 3211 | 3211 | 0 | 0 | 0.00048132146 | 0.000594476003 | 0.725128332 | 0.716281534 | 0.050764587 |
| 1 | dI_T_mean | 3211 | 3211 | 0 | 0 | 0.0178388031 | 0.149667758 | 0.997656119 | 0.999282335 | 0.0660148987 |
| 1 | dI_C_std | 3211 | 3211 | 0 | 0 | 0.000267364551 | 0.000331931306 | 0.0362624548 | 0.0324869599 | 0.924604999 |
| 1 | dI_T_std | 3211 | 3211 | 0 | 0 | 0.0125209889 | 0.0155355838 | 0.81621828 | 0.80278305 | 12.9941027 |
| 1 | dI_C_skewness | 3211 | 3211 | 0 | 0 | 0.0080074447 | 0.0104698719 | 0.930226205 | 0.924643359 | 10.4113057 |
| 1 | dI_T_skewness | 3211 | 3211 | 0 | 0 | 0.262737976 | 0.337435556 | 0.480749458 | 0.465233539 | 95.4107375 |
| 1 | dI_C_kurtosis | 3211 | 3211 | 0 | 0 | 0.0149698033 | 0.0182122959 | 0.200743501 | 0.177013774 | 0.828486657 |
| 1 | dI_T_kurtosis | 3211 | 3211 | 0 | 0 | 0.344652869 | 0.492471326 | 0.274232212 | 0.337735651 | 16.3506231 |
| 1 | dI_dI_devide_dt | 3211 | 3211 | 0 | 0 | 0.00103886446 | 0.00188466202 | 0.994354235 | 0.996785948 | 0.722959912 |
| 1 | dI_entropy | 3211 | 3211 | 0 | 0 | 2.59303462 | 2.59863639 | -0.441909546 | -0.395604466 | 48.3556244 |
| 1 | Charge_energy | 3211 | 3211 | 0 | 0 | 0.000979312012 | 0.00111373301 | 0.999998139 | 0.999982385 | 0.0133472898 |
| 1 | Charge_Q | 3211 | 3211 | 0 | 0 | 0.000137649403 | 0.00016056223 | 0.999998809 | 0.999987529 | 0.0073793028 |
| 1 | Charge_t_mean | 3211 | 3211 | 0 | 0 | 0.00730481062 | 0.101763065 | 0.996616079 | 0.999177947 | 0.0283720411 |
| 1 | Charge_V_mean | 3211 | 3211 | 0 | 0 | 0.00104547447 | 0.00105496205 | 0.999988918 | 0.999937882 | 0.0257901616 |
| 1 | Charge_C_mean | 3211 | 3211 | 0 | 0 | 0.000808535219 | 0.00124105696 | 0.999988115 | 0.999975297 | 0.0370283862 |
| 1 | Charge_T_mean | 3211 | 3211 | 0 | 0 | 0.00629916068 | 0.00687518397 | 0.999999305 | 0.9999973 | 0.0239950353 |
| 1 | Charge_C_std | 3211 | 3211 | 0 | 0 | 0.000642055826 | 0.00217131091 | 0.978550432 | 0.999559781 | 0.0370285004 |
| 1 | Charge_V_std | 3211 | 3211 | 0 | 0 | 0.00203393674 | 0.00206723736 | 0.999841494 | 0.998735257 | 1.0777115 |
| 1 | Charge_T_std | 3211 | 3211 | 0 | 0 | 0.00215192976 | 0.0159552605 | 0.999033581 | 0.999936686 | 0.106099349 |
| 1 | Charge_C_skewness | 3211 | 3211 | 0 | 0 | 0.000916972912 | 0.00152526062 | 0.999987878 | 0.999980259 | 0.437162354 |
| 1 | Charge_V_skewness | 3211 | 3211 | 0 | 0 | 0.0338759578 | 0.0353774982 | 0.999559318 | 0.998504689 | 3.98695678 |
| 1 | Charge_T_skewness | 3211 | 3211 | 0 | 0 | 0.0035669977 | 0.00522867564 | 0.999495575 | 0.999367533 | 2.10876964 |
| 1 | Charge_C_kurtosis | 3211 | 3211 | 0 | 0 | 0.000948060172 | 0.00384801267 | 0.996769222 | 0.999902217 | 0.0808919543 |
| 1 | Charge_V_kurtosis | 3211 | 3211 | 0 | 0 | 0.154021219 | 0.169211018 | 0.997301285 | 0.998451852 | 6.90675774 |
| 1 | Charge_T_kurtosis | 3211 | 3211 | 0 | 0 | 0.00285800763 | 0.0122602369 | 0.991055152 | 0.99835916 | 0.175215978 |
| 2 | CC_energy | 3727 | 3727 | 0 | 0 | 0.0662400461 | 0.0776242537 | 0.995908598 | 0.99172447 | 1.15287434 |
| 2 | CC_Q | 3727 | 3727 | 0 | 0 | 0.0155608448 | 0.0183021142 | 0.996782817 | 0.993399259 | 1.06013183 |
| 2 | CC_t_mean | 3727 | 3727 | 0 | 0 | 0.0778411076 | 0.0915273745 | 0.996779753 | 0.993381596 | 1.06064796 |
| 2 | CC_V_mean | 3727 | 3727 | 0 | 0 | 0.00390890587 | 0.00435306862 | 0.995256959 | 0.991795733 | 0.099824515 |
| 2 | CC_T_mean | 3727 | 3727 | 0 | 0 | 0.0429705705 | 0.0510933727 | 0.999929222 | 0.999844436 | 0.139959457 |
| 2 | CC_V_std | 3727 | 3727 | 0 | 0 | 0.00152892132 | 0.00192887131 | 0.975998868 | 0.970004835 | 1.12065954 |
| 2 | CC_T_std | 3727 | 3727 | 0 | 0 | 0.0132751708 | 0.0347782916 | 0.994061918 | 0.996314232 | 0.468833021 |
| 2 | CC_V_skewness | 3727 | 3727 | 0 | 0 | 0.129240559 | 0.13810527 | 0.994815775 | 0.993211522 | 54.9427747 |
| 2 | CC_T_skewness | 3727 | 3727 | 0 | 0 | 0.0101202656 | 0.0162689294 | 0.984543612 | 0.995135931 | 2.62399847 |
| 2 | CC_V_kurtosis | 3727 | 3727 | 0 | 0 | 0.276996304 | 0.31752951 | 0.983761412 | 0.964557643 | 10.3100137 |
| 2 | CC_T_kurtosis | 3727 | 3727 | 0 | 0 | 0.0118229316 | 0.0220348498 | 0.970173491 | 0.994544788 | 0.625404466 |
| 2 | CC_CCCT | 3727 | 3727 | 0 | 0 | 0.155584145 | 0.18299874 | 0.996782906 | 0.993401718 | 1.05998201 |
| 2 | CC_entropy | 3727 | 3727 | 0 | 0 | 5.0164867 | 5.0166242 | 0.957802821 | 0.982981184 | 67.1368352 |
| 2 | dV_energy | 3727 | 3727 | 0 | 0 | 0.0078612417 | 0.0153371775 | 0.992280446 | 0.999034812 | 0.640715359 |
| 2 | dV_Q | 3727 | 3727 | 0 | 0 | 0.00199052391 | 0.00388990157 | 0.992251396 | 0.999025765 | 0.640093434 |
| 2 | dV_t_mean | 3727 | 3727 | 0 | 0 | 0.00993025133 | 0.019458346 | 0.99221683 | 0.998987982 | 0.638651809 |
| 2 | dV_V_mean | 3727 | 3727 | 0 | 0 | 0.000117484061 | 0.000179108592 | 0.967543095 | 0.898316134 | 0.00297768147 |
| 2 | dV_T_mean | 3727 | 3727 | 0 | 0 | 0.00859594349 | 0.0257563796 | 0.99995688 | 0.999958223 | 0.0267204398 |
| 2 | dV_V_std | 3727 | 3727 | 0 | 0 | 0.000128390949 | 0.00014757305 | 0.724623898 | 0.695109862 | 0.44738152 |
| 2 | dV_T_std | 3727 | 3727 | 0 | 0 | 0.00864797742 | 0.0162065019 | 0.995516578 | 0.996545372 | 1.63582633 |
| 2 | dV_V_skewness | 3727 | 3727 | 0 | 0 | 0.00222250299 | 0.00568843606 | 0.982697314 | 0.982342837 | 1.16337259 |
| 2 | dV_T_skewness | 3727 | 3727 | 0 | 0 | 0.0391745953 | 0.0610228538 | 0.934121721 | 0.936635807 | 27.4352447 |
| 2 | dV_V_kurtosis | 3727 | 3727 | 0 | 0 | 0.00176042345 | 0.00225429574 | 0.939704824 | 0.919535258 | 0.0953307226 |
| 2 | dV_T_kurtosis | 3727 | 3727 | 0 | 0 | 0.0505752288 | 0.083048963 | 0.863190059 | 0.894299213 | 2.74536268 |
| 2 | dV_dV_devide_dt | 3727 | 3727 | 0 | 0 | 5.56446583e-05 | 0.000196330961 | 0.997225196 | 0.999674747 | 0.173012654 |
| 2 | dV_entropy | 3727 | 3727 | 0 | 0 | 4.70287351 | 4.70383013 | 0.444843355 | 0.501193482 | 63.0186388 |
| 2 | CV_energy | 3727 | 3727 | 0 | 0 | 0.0423142463 | 0.0494074515 | 0.983794794 | 0.979978556 | 2.52625193 |
| 2 | CV_Q | 3727 | 3727 | 0 | 0 | 0.0100746652 | 0.0117634122 | 0.983792558 | 0.97997249 | 2.52617134 |
| 2 | CV_t_mean | 3727 | 3727 | 0 | 0 | 0.0592106161 | 0.0803580737 | 0.999513047 | 0.999787076 | 0.437819846 |
| 2 | CV_C_mean | 3727 | 3727 | 0 | 0 | 0.0148897211 | 0.0177736855 | 0.982422799 | 0.979016641 | 1.66507574 |
| 2 | CV_T_mean | 3727 | 3727 | 0 | 0 | 0.0243107692 | 0.0346724009 | 0.999945907 | 0.999879472 | 0.0881764461 |
| 2 | CV_C_std | 3727 | 3727 | 0 | 0 | 0.0288560595 | 0.033674243 | 0.866682858 | 0.856057564 | 2.41531563 |
| 2 | CV_T_std | 3727 | 3727 | 0 | 0 | 0.0151511906 | 0.0222789424 | 0.998820066 | 0.999219264 | 0.419096173 |
| 2 | CV_C_skewness | 3727 | 3727 | 0 | 0 | 0.0144316424 | 0.0178184167 | 0.997387374 | 0.997295716 | 0.636475886 |
| 2 | CV_T_skewness | 3727 | 3727 | 0 | 0 | 0.00720103035 | 0.00943353669 | 0.998551827 | 0.998609114 | 1.00650446 |
| 2 | CV_C_kurtosis | 3727 | 3727 | 0 | 0 | 0.0754879252 | 0.0951559771 | 0.997113889 | 0.997384089 | 0.969961009 |
| 2 | CV_T_kurtosis | 3727 | 3727 | 0 | 0 | 0.0164438223 | 0.0219097832 | 0.997058347 | 0.996947741 | 0.768527679 |
| 2 | CV_CVCT | 3727 | 3727 | 0 | 0 | 0.110771797 | 0.155051632 | 0.99951776 | 0.999794164 | 0.409661417 |
| 2 | CV_entropy | 3727 | 3727 | 0 | 0 | 4.56870789 | 4.56911325 | 0.985081515 | 0.987087919 | 73.358803 |
| 2 | dI_energy | 3727 | 3727 | 0 | 0 | 0.00104141164 | 0.00127109196 | 0.996278071 | 0.996938535 | 2.54725197 |
| 2 | dI_Q | 3727 | 3727 | 0 | 0 | 0.000247960045 | 0.000302644936 | 0.9962781 | 0.996939196 | 2.54725813 |
| 2 | dI_t_mean | 3727 | 3727 | 0 | 0 | 0.00780613466 | 0.00953823217 | 0.996278459 | 0.996831259 | 2.53520425 |
| 2 | dI_C_mean | 3727 | 3727 | 0 | 0 | 0.000531630474 | 0.00066842064 | 0.80131329 | 0.761548865 | 0.0560494427 |
| 2 | dI_T_mean | 3727 | 3727 | 0 | 0 | 0.0170511516 | 0.0215786884 | 0.999950218 | 0.999908855 | 0.0565370485 |
| 2 | dI_C_std | 3727 | 3727 | 0 | 0 | 0.000311591326 | 0.000392570081 | 0.0834938236 | 0.100628436 | 1.07745688 |
| 2 | dI_T_std | 3727 | 3727 | 0 | 0 | 0.0140357352 | 0.0176927417 | 0.911656395 | 0.899617655 | 9.11859194 |
| 2 | dI_C_skewness | 3727 | 3727 | 0 | 0 | 0.00989751245 | 0.0138602028 | 0.940507379 | 0.917615884 | 16.4421914 |
| 2 | dI_T_skewness | 3727 | 3727 | 0 | 0 | 0.208039452 | 0.271993789 | 0.438436976 | 0.400923526 | 96.5315127 |
| 2 | dI_C_kurtosis | 3727 | 3727 | 0 | 0 | 0.0118898504 | 0.0161291982 | 0.428944267 | 0.399243224 | 0.658923085 |
| 2 | dI_T_kurtosis | 3727 | 3727 | 0 | 0 | 0.246824721 | 0.366973911 | 0.279416964 | 0.366506619 | 12.6131417 |
| 2 | dI_dI_devide_dt | 3727 | 3727 | 0 | 0 | 0.0011607936 | 0.00243820376 | 0.997969582 | 0.999203243 | 0.701404157 |
| 2 | dI_entropy | 3727 | 3727 | 0 | 0 | 2.40859404 | 2.42777957 | -0.137387017 | 0.0593222007 | 46.5094097 |
| 2 | Charge_energy | 3727 | 3727 | 0 | 0 | 0.0016603451 | 0.00696927132 | 0.999774431 | 0.999979963 | 0.0223525531 |
| 2 | Charge_Q | 3727 | 3727 | 0 | 0 | 0.000245431373 | 0.00152091063 | 0.999856879 | 0.999987076 | 0.0131360777 |
| 2 | Charge_t_mean | 3727 | 3727 | 0 | 0 | 0.00947590863 | 0.0669936581 | 0.998928113 | 0.999955027 | 0.0454045003 |
| 2 | Charge_V_mean | 3727 | 3727 | 0 | 0 | 0.00117574635 | 0.00119708347 | 0.999922242 | 0.99995297 | 0.0286894222 |
| 2 | Charge_C_mean | 3727 | 3727 | 0 | 0 | 0.00197466044 | 0.00491723463 | 0.999859024 | 0.999981556 | 0.0730340377 |
| 2 | Charge_T_mean | 3727 | 3727 | 0 | 0 | 0.0139946922 | 0.0214406342 | 0.999979934 | 0.999974537 | 0.0488193674 |
| 2 | Charge_C_std | 3727 | 3727 | 0 | 0 | 0.00124802607 | 0.00346893833 | 0.998233971 | 0.999828139 | 0.047789462 |
| 2 | Charge_V_std | 3727 | 3727 | 0 | 0 | 0.0027502784 | 0.00288595209 | 0.99868523 | 0.998727172 | 1.74046056 |
| 2 | Charge_T_std | 3727 | 3727 | 0 | 0 | 0.00300344144 | 0.0138101297 | 0.99945767 | 0.999801523 | 0.0816253598 |
| 2 | Charge_C_skewness | 3727 | 3727 | 0 | 0 | 0.0023939769 | 0.00490804483 | 0.999756022 | 0.999980913 | 0.67232901 |
| 2 | Charge_V_skewness | 3727 | 3727 | 0 | 0 | 0.0680125279 | 0.0808540909 | 0.997704414 | 0.998226897 | 5.29518768 |
| 2 | Charge_T_skewness | 3727 | 3727 | 0 | 0 | 0.00477436795 | 0.006606942 | 0.99932198 | 0.999842194 | 2.36054395 |
| 2 | Charge_C_kurtosis | 3727 | 3727 | 0 | 0 | 0.0040550292 | 0.0158453883 | 0.996982152 | 0.99995771 | 0.314117789 |
| 2 | Charge_V_kurtosis | 3727 | 3727 | 0 | 0 | 0.428906063 | 0.571870376 | 0.994866778 | 0.996455387 | 12.676098 |
| 2 | Charge_T_kurtosis | 3727 | 3727 | 0 | 0 | 0.00321126544 | 0.0102185479 | 0.99085113 | 0.998505994 | 0.19780091 |
| 3 | CC_energy | 4608 | 4608 | 0 | 0 | 0.0547102798 | 0.0639146872 | 0.997974629 | 0.995161806 | 0.9258069 |
| 3 | CC_Q | 4608 | 4608 | 0 | 0 | 0.0128555552 | 0.0150724671 | 0.998438392 | 0.996285782 | 0.840471735 |
| 3 | CC_t_mean | 4608 | 4608 | 0 | 0 | 0.096504024 | 0.113157095 | 0.998427285 | 0.996260869 | 0.841252455 |
| 3 | CC_V_mean | 4608 | 4608 | 0 | 0 | 0.00361740737 | 0.00403571458 | 0.996326155 | 0.994897158 | 0.093591088 |
| 3 | CC_T_mean | 4608 | 4608 | 0 | 0 | 0.0135180662 | 0.0173194411 | 0.999980077 | 0.999975119 | 0.0476710053 |
| 3 | CC_V_std | 4608 | 4608 | 0 | 0 | 0.00135983565 | 0.00164695367 | 0.988568868 | 0.985956622 | 0.842028999 |
| 3 | CC_T_std | 4608 | 4608 | 0 | 0 | 0.00951842526 | 0.0130024241 | 0.999771914 | 0.999670976 | 0.793107777 |
| 3 | CC_V_skewness | 4608 | 4608 | 0 | 0 | 0.0990388867 | 0.107318858 | 0.971146909 | 0.972326333 | 52.92872 |
| 3 | CC_T_skewness | 4608 | 4608 | 0 | 0 | 0.0215690897 | 0.0367120897 | 0.999426719 | 0.999417162 | 2.4874379 |
| 3 | CC_V_kurtosis | 4608 | 4608 | 0 | 0 | 0.205405188 | 0.23695352 | 0.934398451 | 0.950965141 | 7.90339593 |
| 3 | CC_T_kurtosis | 4608 | 4608 | 0 | 0 | 0.0730787591 | 0.255749919 | 0.991127367 | 0.997085508 | 2.22404067 |
| 3 | CC_CCCT | 4608 | 4608 | 0 | 0 | 0.192795176 | 0.226051722 | 0.998438482 | 0.996284282 | 0.840326291 |
| 3 | CC_entropy | 4608 | 4608 | 0 | 0 | 5.06007583 | 5.06017223 | 0.99694716 | 0.996610607 | 67.0501138 |
| 3 | dV_energy | 4608 | 4608 | 0 | 0 | 0.00519676571 | 0.00558271152 | 0.999077081 | 0.998422155 | 0.5816382 |
| 3 | dV_Q | 4608 | 4608 | 0 | 0 | 0.00131612879 | 0.00141398657 | 0.999079668 | 0.998463428 | 0.581354936 |
| 3 | dV_t_mean | 4608 | 4608 | 0 | 0 | 0.00986890106 | 0.0106392827 | 0.999025672 | 0.998385899 | 0.581245354 |
| 3 | dV_V_mean | 4608 | 4608 | 0 | 0 | 9.6206322e-05 | 0.000119679193 | 0.950215792 | 0.949669206 | 0.00243767978 |
| 3 | dV_T_mean | 4608 | 4608 | 0 | 0 | 0.00664348078 | 0.0195143957 | 0.999956861 | 0.999988151 | 0.0231958415 |
| 3 | dV_V_std | 4608 | 4608 | 0 | 0 | 0.000131479003 | 0.000146925783 | 0.593632791 | 0.588190815 | 0.455262299 |
| 3 | dV_T_std | 4608 | 4608 | 0 | 0 | 0.00819750058 | 0.0186230184 | 0.960310157 | 0.987495004 | 6.23256374 |
| 3 | dV_V_skewness | 4608 | 4608 | 0 | 0 | 0.0017263043 | 0.0022647167 | 0.989968617 | 0.990201612 | 1.22212327 |
| 3 | dV_T_skewness | 4608 | 4608 | 0 | 0 | 0.199024428 | 0.478558191 | 0.670771388 | 0.839767944 | 63.113361 |
| 3 | dV_V_kurtosis | 4608 | 4608 | 0 | 0 | 0.00169811277 | 0.00216434755 | 0.957800522 | 0.952942873 | 0.0934661489 |
| 3 | dV_T_kurtosis | 4608 | 4608 | 0 | 0 | 0.471522031 | 2.79676942 | 0.301497086 | 0.785273193 | 20.7753714 |
| 3 | dV_dV_devide_dt | 4608 | 4608 | 0 | 0 | 3.34365999e-05 | 5.55649445e-05 | 0.999342156 | 0.999510292 | 0.113886811 |
| 3 | dV_entropy | 4608 | 4608 | 0 | 0 | 4.80845645 | 4.80878895 | -0.780527886 | -0.803263312 | 63.48913 |
| 3 | CV_energy | 4608 | 4608 | 0 | 0 | 0.0353996937 | 0.0418649042 | 0.987230628 | 0.986535662 | 2.44410419 |
| 3 | CV_Q | 4608 | 4608 | 0 | 0 | 0.00842843082 | 0.00996770647 | 0.987229609 | 0.986536916 | 2.44402446 |
| 3 | CV_t_mean | 4608 | 4608 | 0 | 0 | 0.0697157621 | 0.0799822503 | 0.999820993 | 0.999503819 | 0.482427166 |
| 3 | CV_C_mean | 4608 | 4608 | 0 | 0 | 0.0113806917 | 0.0135144073 | 0.96387738 | 0.961303376 | 1.5776989 |
| 3 | CV_T_mean | 4608 | 4608 | 0 | 0 | 0.0170624743 | 0.02015912 | 0.999985207 | 0.999960145 | 0.0682198768 |
| 3 | CV_C_std | 4608 | 4608 | 0 | 0 | 0.0203597811 | 0.0238092427 | 0.762903637 | 0.74600284 | 2.4625562 |
| 3 | CV_T_std | 4608 | 4608 | 0 | 0 | 0.0124626764 | 0.0284814527 | 0.994985296 | 0.999133675 | 0.568915544 |
| 3 | CV_C_skewness | 4608 | 4608 | 0 | 0 | 0.0207050736 | 0.0241564923 | 0.992140678 | 0.991394255 | 1.06620672 |
| 3 | CV_T_skewness | 4608 | 4608 | 0 | 0 | 0.0136726322 | 0.0708894766 | 0.870235167 | 0.974134546 | 1.86429779 |
| 3 | CV_C_kurtosis | 4608 | 4608 | 0 | 0 | 0.0976192626 | 0.113218446 | 0.992114218 | 0.991395996 | 1.54718088 |
| 3 | CV_T_kurtosis | 4608 | 4608 | 0 | 0 | 0.0191730572 | 0.0315286459 | 0.990062617 | 0.99350467 | 0.886791819 |
| 3 | CV_CVCT | 4608 | 4608 | 0 | 0 | 0.131703052 | 0.152528522 | 0.999825515 | 0.999514117 | 0.455813748 |
| 3 | CV_entropy | 4608 | 4608 | 0 | 0 | 4.71624556 | 4.71635578 | 0.968758366 | 0.96815495 | 71.590417 |
| 3 | dI_energy | 4608 | 4608 | 0 | 0 | 0.00125100935 | 0.00445671992 | 0.886319832 | 0.989532218 | 2.52755751 |
| 3 | dI_Q | 4608 | 4608 | 0 | 0 | 0.000297865775 | 0.00106114124 | 0.886319855 | 0.989531788 | 2.52754854 |
| 3 | dI_t_mean | 4608 | 4608 | 0 | 0 | 0.0093533481 | 0.0332638703 | 0.888501187 | 0.989782849 | 2.50832239 |
| 3 | dI_C_mean | 4608 | 4608 | 0 | 0 | 0.000494926965 | 0.000717263086 | 0.806106418 | 0.830207408 | 0.0521920091 |
| 3 | dI_T_mean | 4608 | 4608 | 0 | 0 | 0.0144246249 | 0.0178538943 | 0.999962978 | 0.999941984 | 0.0536432599 |
| 3 | dI_C_std | 4608 | 4608 | 0 | 0 | 0.000259460733 | 0.000329769356 | 0.158836842 | 0.146311872 | 0.897714388 |
| 3 | dI_T_std | 4608 | 4608 | 0 | 0 | 0.0126587734 | 0.0158995041 | 0.831916363 | 0.812427831 | 11.365745 |
| 3 | dI_C_skewness | 4608 | 4608 | 0 | 0 | 0.00948560156 | 0.021885882 | 0.884363273 | 0.940493733 | 13.5609496 |
| 3 | dI_T_skewness | 4608 | 4608 | 0 | 0 | 0.241254761 | 0.378600416 | 0.35072346 | 0.434558891 | 97.2449863 |
| 3 | dI_C_kurtosis | 4608 | 4608 | 0 | 0 | 0.0125462532 | 0.0178273929 | 0.453152398 | 0.42812967 | 0.693875244 |
| 3 | dI_T_kurtosis | 4608 | 4608 | 0 | 0 | 0.336578076 | 3.73504758 | 0.00108298015 | 0.360379351 | 16.4704923 |
| 3 | dI_dI_devide_dt | 4608 | 4608 | 0 | 0 | 0.0011118816 | 0.00404276674 | 0.983520847 | 0.99531154 | 0.827048268 |
| 3 | dI_entropy | 4608 | 4608 | 0 | 0 | 2.69512488 | 2.70583684 | -0.295162241 | -0.208942291 | 49.3204566 |
| 3 | Charge_energy | 4608 | 4608 | 0 | 0 | 0.00186954312 | 0.0155820653 | 0.999174839 | 0.999958277 | 0.025387686 |
| 3 | Charge_Q | 4608 | 4608 | 0 | 0 | 0.00022506181 | 0.00184175529 | 0.99985476 | 0.999991037 | 0.0119983753 |
| 3 | Charge_t_mean | 4608 | 4608 | 0 | 0 | 0.0058060354 | 0.0108760905 | 0.999960278 | 0.999926323 | 0.0223903149 |
| 3 | Charge_V_mean | 4608 | 4608 | 0 | 0 | 0.00121291557 | 0.0012301687 | 0.999974844 | 0.999955402 | 0.0299494043 |
| 3 | Charge_C_mean | 4608 | 4608 | 0 | 0 | 0.000809894592 | 0.00131807196 | 0.999984948 | 0.999974155 | 0.0371781768 |
| 3 | Charge_T_mean | 4608 | 4608 | 0 | 0 | 0.00637974165 | 0.00757539209 | 0.999995002 | 0.999991699 | 0.0240948436 |
| 3 | Charge_C_std | 4608 | 4608 | 0 | 0 | 0.000999597988 | 0.00371114577 | 0.963101841 | 0.997874998 | 0.0577347098 |
| 3 | Charge_V_std | 4608 | 4608 | 0 | 0 | 0.00256254472 | 0.00264071834 | 0.999397426 | 0.999249091 | 1.2983062 |
| 3 | Charge_T_std | 4608 | 4608 | 0 | 0 | 0.0109686059 | 0.0642941401 | 0.993755907 | 0.999045683 | 0.436810437 |
| 3 | Charge_C_skewness | 4608 | 4608 | 0 | 0 | 0.000984332962 | 0.00160242028 | 0.999985447 | 0.999974809 | 0.510834077 |
| 3 | Charge_V_skewness | 4608 | 4608 | 0 | 0 | 0.0470309983 | 0.0515235953 | 0.997640033 | 0.997544243 | 5.00245935 |
| 3 | Charge_T_skewness | 4608 | 4608 | 0 | 0 | 0.00829714989 | 0.0124178025 | 0.999597351 | 0.999682471 | 3.35199721 |
| 3 | Charge_C_kurtosis | 4608 | 4608 | 0 | 0 | 0.00152080979 | 0.007310814 | 0.992360148 | 0.999912831 | 0.12978175 |
| 3 | Charge_V_kurtosis | 4608 | 4608 | 0 | 0 | 0.234073844 | 0.27579009 | 0.988096323 | 0.9923167 | 9.18520577 |
| 3 | Charge_T_kurtosis | 4608 | 4608 | 0 | 0 | 0.0205434224 | 0.115296817 | 0.957669254 | 0.995741395 | 1.1675916 |
| 4 | CC_energy | 5670 | 5670 | 0 | 0 | 0.0649022452 | 0.0771890983 | 0.9969662 | 0.996371762 | 1.14421878 |
| 4 | CC_Q | 5670 | 5670 | 0 | 0 | 0.0158011208 | 0.0188485015 | 0.997493134 | 0.996822591 | 1.07991256 |
| 4 | CC_t_mean | 5670 | 5670 | 0 | 0 | 0.118614258 | 0.141503316 | 0.997481058 | 0.99681383 | 1.08090332 |
| 4 | CC_V_mean | 5670 | 5670 | 0 | 0 | 0.00288955038 | 0.00337339901 | 0.99327927 | 0.98979731 | 0.0745074457 |
| 4 | CC_T_mean | 5670 | 5670 | 0 | 0 | 0.0117126972 | 0.0149229854 | 0.999982745 | 0.999973349 | 0.0441096341 |
| 4 | CC_V_std | 5670 | 5670 | 0 | 0 | 0.00210771583 | 0.00290334916 | 0.94706298 | 0.946289509 | 1.39963133 |
| 4 | CC_T_std | 5670 | 5670 | 0 | 0 | 0.00839226898 | 0.0107158405 | 0.999668387 | 0.999350936 | 0.797884334 |
| 4 | CC_V_skewness | 5670 | 5670 | 0 | 0 | 0.0488598287 | 0.0623710594 | 0.802799014 | 0.837957397 | 14.0956967 |
| 4 | CC_T_skewness | 5670 | 5670 | 0 | 0 | 0.0147164123 | 0.0240048189 | 0.999600438 | 0.999466939 | 2.37310099 |
| 4 | CC_V_kurtosis | 5670 | 5670 | 0 | 0 | 0.0677508318 | 0.101665365 | 0.753881981 | 0.914786883 | 2.89420823 |
| 4 | CC_T_kurtosis | 5670 | 5670 | 0 | 0 | 0.0492891247 | 0.294849287 | 0.97230404 | 0.982253258 | 1.95665343 |
| 4 | CC_CCCT | 5670 | 5670 | 0 | 0 | 0.236990036 | 0.282705939 | 0.997492933 | 0.996821705 | 1.07982352 |
| 4 | CC_entropy | 5670 | 5670 | 0 | 0 | 5.07996504 | 5.08068965 | 0.86064864 | 0.916117319 | 66.0366184 |
| 4 | dV_energy | 5670 | 5670 | 0 | 0 | 0.00470950646 | 0.00528037501 | 0.998695089 | 0.998665856 | 0.522411972 |
| 4 | dV_Q | 5670 | 5670 | 0 | 0 | 0.00119322336 | 0.00133796751 | 0.998698346 | 0.99867656 | 0.522366002 |
| 4 | dV_t_mean | 5670 | 5670 | 0 | 0 | 0.00892701287 | 0.0100686495 | 0.998605407 | 0.998579636 | 0.521073057 |
| 4 | dV_V_mean | 5670 | 5670 | 0 | 0 | 9.83738898e-05 | 0.000122768362 | 0.948132778 | 0.9461565 | 0.00249264531 |
| 4 | dV_T_mean | 5670 | 5670 | 0 | 0 | 0.00593096481 | 0.00758561221 | 0.999993248 | 0.999985583 | 0.0219928962 |
| 4 | dV_V_std | 5670 | 5670 | 0 | 0 | 0.000116362632 | 0.000133177522 | 0.591538608 | 0.569372068 | 0.402705746 |
| 4 | dV_T_std | 5670 | 5670 | 0 | 0 | 0.00670048387 | 0.00973255695 | 0.989221346 | 0.992002129 | 5.16675262 |
| 4 | dV_V_skewness | 5670 | 5670 | 0 | 0 | 0.00187906607 | 0.00266401442 | 0.986649848 | 0.986940392 | 1.30004341 |
| 4 | dV_T_skewness | 5670 | 5670 | 0 | 0 | 0.202831721 | 0.590676623 | 0.60883501 | 0.859341259 | 60.7271587 |
| 4 | dV_V_kurtosis | 5670 | 5670 | 0 | 0 | 0.00179491812 | 0.00231326254 | 0.953389368 | 0.944642966 | 0.0987408694 |
| 4 | dV_T_kurtosis | 5670 | 5670 | 0 | 0 | 0.563801812 | 4.72936973 | 0.244152758 | 0.803692773 | 24.5021534 |
| 4 | dV_dV_devide_dt | 5670 | 5670 | 0 | 0 | 3.76644525e-05 | 9.7874408e-05 | 0.998044953 | 0.999201207 | 0.129423042 |
| 4 | dV_entropy | 5670 | 5670 | 0 | 0 | 4.82183797 | 4.82218179 | -0.781547334 | -0.800015787 | 63.5563624 |
| 4 | CV_energy | 5670 | 5670 | 0 | 0 | 0.0337599632 | 0.0403487925 | 0.9860164 | 0.987420786 | 2.30441721 |
| 4 | CV_Q | 5670 | 5670 | 0 | 0 | 0.00803786921 | 0.00960653258 | 0.986015029 | 0.987421472 | 2.30434235 |
| 4 | CV_t_mean | 5670 | 5670 | 0 | 0 | 0.0664123896 | 0.0775044608 | 0.99976361 | 0.999653597 | 0.456198036 |
| 4 | CV_C_mean | 5670 | 5670 | 0 | 0 | 0.0107413127 | 0.0132720333 | 0.95016201 | 0.950836768 | 1.48544218 |
| 4 | CV_T_mean | 5670 | 5670 | 0 | 0 | 0.0133796947 | 0.0158736181 | 0.999989313 | 0.999966908 | 0.0557313189 |
| 4 | CV_C_std | 5670 | 5670 | 0 | 0 | 0.0188012986 | 0.0220332479 | 0.726809521 | 0.692531121 | 2.25864144 |
| 4 | CV_T_std | 5670 | 5670 | 0 | 0 | 0.00896124466 | 0.0116230684 | 0.999396526 | 0.999356244 | 0.482506992 |
| 4 | CV_C_skewness | 5670 | 5670 | 0 | 0 | 0.0191325449 | 0.0226517815 | 0.989062603 | 0.988322512 | 0.996035077 |
| 4 | CV_T_skewness | 5670 | 5670 | 0 | 0 | 0.0122093795 | 0.0630123095 | 0.883125057 | 0.983709884 | 1.67870405 |
| 4 | CV_C_kurtosis | 5670 | 5670 | 0 | 0 | 0.0913900001 | 0.107754104 | 0.988436391 | 0.987308314 | 1.47588596 |
| 4 | CV_T_kurtosis | 5670 | 5670 | 0 | 0 | 0.019561358 | 0.0380977024 | 0.982538897 | 0.994824084 | 0.912923082 |
| 4 | CV_CVCT | 5670 | 5670 | 0 | 0 | 0.125399868 | 0.148117701 | 0.999765802 | 0.999657375 | 0.430814593 |
| 4 | CV_entropy | 5670 | 5670 | 0 | 0 | 4.71351673 | 4.713642 | 0.952744462 | 0.960663372 | 71.6233672 |
| 4 | dI_energy | 5670 | 5670 | 0 | 0 | 0.00118256976 | 0.00335361953 | 0.916970098 | 0.992651171 | 2.4358726 |
| 4 | dI_Q | 5670 | 5670 | 0 | 0 | 0.000281566297 | 0.00079848342 | 0.916967189 | 0.992650898 | 2.43587753 |
| 4 | dI_t_mean | 5670 | 5670 | 0 | 0 | 0.00886672086 | 0.0251328774 | 0.917910478 | 0.992645804 | 2.42511528 |
| 4 | dI_C_mean | 5670 | 5670 | 0 | 0 | 0.000471426461 | 0.000622839556 | 0.821982244 | 0.75501299 | 0.0497014434 |
| 4 | dI_T_mean | 5670 | 5670 | 0 | 0 | 0.0143462294 | 0.0177018256 | 0.999962432 | 0.999887976 | 0.0561299612 |
| 4 | dI_C_std | 5670 | 5670 | 0 | 0 | 0.000259429813 | 0.000324476709 | 0.124113125 | 0.103932487 | 0.897945474 |
| 4 | dI_T_std | 5670 | 5670 | 0 | 0 | 0.0118473332 | 0.0149051497 | 0.804660147 | 0.795939593 | 12.7366675 |
| 4 | dI_C_skewness | 5670 | 5670 | 0 | 0 | 0.00785198568 | 0.0144965459 | 0.93575288 | 0.919685772 | 13.4192723 |
| 4 | dI_T_skewness | 5670 | 5670 | 0 | 0 | 0.249967427 | 0.352875542 | 0.452394377 | 0.496651099 | 95.421374 |
| 4 | dI_C_kurtosis | 5670 | 5670 | 0 | 0 | 0.0106393996 | 0.0152677167 | 0.450369627 | 0.415750532 | 0.589264057 |
| 4 | dI_T_kurtosis | 5670 | 5670 | 0 | 0 | 0.353982215 | 1.88026882 | 0.0523188001 | 0.351812452 | 16.8668882 |
| 4 | dI_dI_devide_dt | 5670 | 5670 | 0 | 0 | 0.00117886658 | 0.00420661933 | 0.978994918 | 0.996645607 | 0.865194901 |
| 4 | dI_entropy | 5670 | 5670 | 0 | 0 | 2.67508589 | 2.68382674 | -0.244727402 | -0.08176436 | 49.127137 |
| 4 | Charge_energy | 5670 | 5670 | 0 | 0 | 0.0139682485 | 0.0470998645 | 0.993950889 | 0.998673563 | 0.19547826 |
| 4 | Charge_Q | 5670 | 5670 | 0 | 0 | 0.00357263624 | 0.0112511789 | 0.995578641 | 0.998762333 | 0.196958265 |
| 4 | Charge_t_mean | 5670 | 5670 | 0 | 0 | 0.0271921607 | 0.0661290202 | 0.998254055 | 0.999073945 | 0.106477854 |
| 4 | Charge_V_mean | 5670 | 5670 | 0 | 0 | 0.000916748236 | 0.00109723238 | 0.999253817 | 0.998470133 | 0.0225795292 |
| 4 | Charge_C_mean | 5670 | 5670 | 0 | 0 | 0.00207002182 | 0.00392742372 | 0.999836776 | 0.999725353 | 0.0969049426 |
| 4 | Charge_T_mean | 5670 | 5670 | 0 | 0 | 0.00487493142 | 0.00584180041 | 0.999997089 | 0.999992523 | 0.019431654 |
| 4 | Charge_C_std | 5670 | 5670 | 0 | 0 | 0.00105555224 | 0.00374723801 | 0.974469282 | 0.998983803 | 0.06098661 |
| 4 | Charge_V_std | 5670 | 5670 | 0 | 0 | 0.0014269091 | 0.00162083903 | 0.996450449 | 0.994946322 | 0.76346201 |
| 4 | Charge_T_std | 5670 | 5670 | 0 | 0 | 0.0147941628 | 0.0978621631 | 0.975591411 | 0.99753575 | 0.724994286 |
| 4 | Charge_C_skewness | 5670 | 5670 | 0 | 0 | 0.00225377564 | 0.00416242719 | 0.999823158 | 0.999720779 | 1.31198094 |
| 4 | Charge_V_skewness | 5670 | 5670 | 0 | 0 | 0.0160581981 | 0.0199555485 | 0.997523256 | 0.995582736 | 1.74628064 |
| 4 | Charge_T_skewness | 5670 | 5670 | 0 | 0 | 0.00606070694 | 0.0113459344 | 0.999074112 | 0.999162332 | 3.2541768 |
| 4 | Charge_C_kurtosis | 5670 | 5670 | 0 | 0 | 0.00306742612 | 0.0150431286 | 0.979186341 | 0.99938586 | 0.262262696 |
| 4 | Charge_V_kurtosis | 5670 | 5670 | 0 | 0 | 0.0771350061 | 0.104860242 | 0.986088312 | 0.981023538 | 3.28120229 |
| 4 | Charge_T_kurtosis | 5670 | 5670 | 0 | 0 | 0.0210248518 | 0.100145932 | 0.916321362 | 0.991216445 | 1.26479994 |
| 5 | CC_energy | 1975 | 1975 | 0 | 0 | 0.0772242427 | 0.100830598 | 0.993275845 | 0.994410856 | 1.37745063 |
| 5 | CC_Q | 1975 | 1975 | 0 | 0 | 0.018790196 | 0.0246184715 | 0.994665036 | 0.995201449 | 1.30960541 |
| 5 | CC_t_mean | 1975 | 1975 | 0 | 0 | 1.1604553 | 5.06152484 | 0.91597378 | 0.99484037 | 10.9416103 |
| 5 | CC_V_mean | 1975 | 1975 | 0 | 0 | 0.00343899463 | 0.00409834579 | 0.997485475 | 0.988064479 | 0.0879454387 |
| 5 | CC_T_mean | 1975 | 1975 | 0 | 0 | 0.0342031573 | 0.0438749375 | 0.99993145 | 0.999718727 | 0.129474824 |
| 5 | CC_V_std | 1975 | 1975 | 0 | 0 | 0.00244226647 | 0.00375753908 | 0.980455651 | 0.969107214 | 1.74602308 |
| 5 | CC_T_std | 1975 | 1975 | 0 | 0 | 0.015493571 | 0.0230674039 | 0.999809577 | 0.999379927 | 0.708287908 |
| 5 | CC_V_skewness | 1975 | 1975 | 0 | 0 | 0.0788888921 | 0.10166842 | 0.919878041 | 0.931813278 | 28.7343896 |
| 5 | CC_T_skewness | 1975 | 1975 | 0 | 0 | 0.0599463924 | 0.275924578 | 0.602844071 | 0.9362946 | 18.4387796 |
| 5 | CC_V_kurtosis | 1975 | 1975 | 0 | 0 | 0.133167609 | 0.184138888 | 0.725677629 | 0.825503118 | 5.51156496 |
| 5 | CC_T_kurtosis | 1975 | 1975 | 0 | 0 | 0.154336706 | 0.828028757 | 0.390549976 | 0.919359852 | 8.06265133 |
| 5 | CC_CCCT | 1975 | 1975 | 0 | 0 | 2.3203665 | 10.1258102 | 0.915933094 | 0.994853996 | 10.9398252 |
| 5 | CC_entropy | 1975 | 1975 | 0 | 0 | 5.04110731 | 5.04181655 | 0.824736877 | 0.83916816 | 66.213703 |
| 5 | dV_energy | 1975 | 1975 | 0 | 0 | 0.00669961912 | 0.00785485797 | 0.99975326 | 0.996330133 | 0.574490335 |
| 5 | dV_Q | 1975 | 1975 | 0 | 0 | 0.00169747049 | 0.00199052881 | 0.99975301 | 0.99632575 | 0.574413312 |
| 5 | dV_t_mean | 1975 | 1975 | 0 | 0 | 0.155455769 | 0.63297937 | 0.851332962 | 0.994863495 | 8.42182248 |
| 5 | dV_V_mean | 1975 | 1975 | 0 | 0 | 0.000172684033 | 0.000405850978 | 0.970389291 | 0.973342155 | 0.00437566351 |
| 5 | dV_T_mean | 1975 | 1975 | 0 | 0 | 0.00720591096 | 0.00926218101 | 0.999994741 | 0.999980067 | 0.0263843873 |
| 5 | dV_V_std | 1975 | 1975 | 0 | 0 | 0.000147084223 | 0.000173368587 | 0.77500905 | 0.69709048 | 0.513326316 |
| 5 | dV_T_std | 1975 | 1975 | 0 | 0 | 0.00736658036 | 0.00929548631 | 0.999265134 | 0.997618027 | 1.57320741 |
| 5 | dV_V_skewness | 1975 | 1975 | 0 | 0 | 0.0051875568 | 0.0156907325 | 0.975920281 | 0.98648153 | 3.41967945 |
| 5 | dV_T_skewness | 1975 | 1975 | 0 | 0 | 0.172231093 | 0.83877603 | 0.427380144 | 0.830253827 | 68.1515566 |
| 5 | dV_V_kurtosis | 1975 | 1975 | 0 | 0 | 0.00380099209 | 0.00545602258 | 0.963549255 | 0.884446077 | 0.206604294 |
| 5 | dV_T_kurtosis | 1975 | 1975 | 0 | 0 | 1.33158459 | 12.2470435 | 0.0528399678 | 0.797515071 | 49.5012938 |
| 5 | dV_dV_devide_dt | 1975 | 1975 | 0 | 0 | 0.000246534548 | 0.00129582555 | 0.983442507 | 0.995950943 | 0.860241602 |
| 5 | dV_entropy | 1975 | 1975 | 0 | 0 | 4.67400975 | 4.67807436 | 0.37292676 | 0.24816115 | 62.8472631 |
| 5 | CV_energy | 1975 | 1975 | 0 | 0 | 0.0368398341 | 0.0440555985 | 0.997557174 | 0.987553722 | 2.38411325 |
| 5 | CV_Q | 1975 | 1975 | 0 | 0 | 0.00877099616 | 0.0104889282 | 0.997557151 | 0.98755192 | 2.38401854 |
| 5 | CV_t_mean | 1975 | 1975 | 0 | 0 | 0.111714527 | 0.397826915 | 0.987652411 | 0.99908552 | 0.785263704 |
| 5 | CV_C_mean | 1975 | 1975 | 0 | 0 | 0.0168302234 | 0.0383121477 | 0.985186195 | 0.9817782 | 2.0930869 |
| 5 | CV_T_mean | 1975 | 1975 | 0 | 0 | 0.0172245806 | 0.0216313335 | 0.999961758 | 0.9998893 | 0.0719752808 |
| 5 | CV_C_std | 1975 | 1975 | 0 | 0 | 0.0234820177 | 0.0286797726 | 0.997563131 | 0.890538517 | 2.23316832 |
| 5 | CV_T_std | 1975 | 1975 | 0 | 0 | 0.0108288253 | 0.013614308 | 0.999957112 | 0.999726092 | 0.376998576 |
| 5 | CV_C_skewness | 1975 | 1975 | 0 | 0 | 0.0152333533 | 0.0209157078 | 0.998906877 | 0.997137492 | 0.697483994 |
| 5 | CV_T_skewness | 1975 | 1975 | 0 | 0 | 0.0190574668 | 0.0744349968 | 0.864074201 | 0.943500837 | 2.70204204 |
| 5 | CV_C_kurtosis | 1975 | 1975 | 0 | 0 | 0.0771274784 | 0.102118637 | 0.998672785 | 0.996978582 | 1.03950876 |
| 5 | CV_T_kurtosis | 1975 | 1975 | 0 | 0 | 0.0306426124 | 0.115177504 | 0.892099689 | 0.977135686 | 1.44066832 |
| 5 | CV_CVCT | 1975 | 1975 | 0 | 0 | 0.214377977 | 0.788300135 | 0.987854173 | 0.999131273 | 0.753606773 |
| 5 | CV_entropy | 1975 | 1975 | 0 | 0 | 4.61101458 | 4.61269753 | 0.995852052 | 0.990794864 | 72.8701053 |
| 5 | dI_energy | 1975 | 1900 | 0 | 75 | 0.00177813545 | 0.00501539154 | 0.890927485 | 0.946473346 | 4.35281921 |
| 5 | dI_Q | 1975 | 1900 | 0 | 75 | 0.00042337154 | 0.00119418726 | 0.890903442 | 0.946476628 | 4.35291852 |
| 5 | dI_t_mean | 1975 | 1900 | 0 | 75 | 0.0135179974 | 0.0384764339 | 0.886918115 | 0.945654548 | 4.39174911 |
| 5 | dI_C_mean | 1975 | 1900 | 0 | 75 | 0.0015310876 | 0.00610609746 | 0.0583106336 | 0.734869631 | 0.161483061 |
| 5 | dI_T_mean | 1975 | 1900 | 0 | 75 | 0.0151153117 | 0.0190430977 | 0.99995885 | 0.999825507 | 0.0571365743 |
| 5 | dI_C_std | 1975 | 1900 | 0 | 75 | 0.000962849663 | 0.00388388633 | -0.347460745 | 0.0349941824 | 3.32400091 |
| 5 | dI_T_std | 1975 | 1900 | 0 | 75 | 0.0125537135 | 0.015714013 | 0.966060839 | 0.963687626 | 9.87352637 |
| 5 | dI_C_skewness | 1975 | 1900 | 0 | 75 | 0.0190629576 | 0.044701225 | 0.652339213 | 0.815883813 | 23.2455837 |
| 5 | dI_T_skewness | 1975 | 1900 | 0 | 75 | 0.270938073 | 0.521419243 | 0.207639522 | 0.373242408 | 102.097007 |
| 5 | dI_C_kurtosis | 1975 | 1900 | 0 | 75 | 0.0185727002 | 0.0303268598 | 0.220083458 | 0.342272101 | 1.02710339 |
| 5 | dI_T_kurtosis | 1975 | 1900 | 0 | 75 | 0.486898539 | 3.55674766 | 0.0125901362 | 0.291803637 | 23.6942275 |
| 5 | dI_dI_devide_dt | 1975 | 1900 | 0 | 75 | 0.00341598205 | 0.0130376519 | 0.951503864 | 0.961663535 | 2.04247158 |
| 5 | dI_entropy | 1975 | 1900 | 0 | 75 | 2.37544718 | 2.40408297 | -0.152614728 | 0.0228986783 | 46.1740395 |
| 5 | Charge_energy | 1975 | 1975 | 0 | 0 | 0.0173104741 | 0.0540507969 | 0.991583035 | 0.992904883 | 0.241810646 |
| 5 | Charge_Q | 1975 | 1975 | 0 | 0 | 0.00480408161 | 0.0148585539 | 0.990901672 | 0.990522393 | 0.266203241 |
| 5 | Charge_t_mean | 1975 | 1975 | 0 | 0 | 1.54737869 | 7.01361677 | 0.875733387 | 0.998112055 | 6.33029971 |
| 5 | Charge_V_mean | 1975 | 1975 | 0 | 0 | 0.00126005929 | 0.00215379883 | 0.999547638 | 0.999028582 | 0.0308755129 |
| 5 | Charge_C_mean | 1975 | 1975 | 0 | 0 | 0.00324252113 | 0.00463082482 | 0.999973134 | 0.999764482 | 0.136620285 |
| 5 | Charge_T_mean | 1975 | 1975 | 0 | 0 | 0.0101764603 | 0.0119159634 | 0.999994391 | 0.999989359 | 0.0410283454 |
| 5 | Charge_C_std | 1975 | 1975 | 0 | 0 | 0.00122742842 | 0.00161961874 | 0.999998497 | 0.999770132 | 0.054103298 |
| 5 | Charge_V_std | 1975 | 1975 | 0 | 0 | 0.00205703107 | 0.00262307041 | 0.997846691 | 0.993595217 | 1.2645148 |
| 5 | Charge_T_std | 1975 | 1975 | 0 | 0 | 0.00299380372 | 0.00616402115 | 0.999986724 | 0.999965329 | 0.102926718 |
| 5 | Charge_C_skewness | 1975 | 1975 | 0 | 0 | 0.00422450032 | 0.00740586497 | 0.999944561 | 0.999809859 | 0.832946876 |
| 5 | Charge_V_skewness | 1975 | 1975 | 0 | 0 | 0.0338364329 | 0.0437291653 | 0.998060832 | 0.996621241 | 2.87969451 |
| 5 | Charge_T_skewness | 1975 | 1975 | 0 | 0 | 0.0337074607 | 0.168062799 | 0.911248674 | 0.981045821 | 11.5586663 |
| 5 | Charge_C_kurtosis | 1975 | 1975 | 0 | 0 | 0.0129943672 | 0.0667541707 | 0.983206596 | 0.998749915 | 0.896527323 |
| 5 | Charge_V_kurtosis | 1975 | 1975 | 0 | 0 | 0.257142806 | 0.660535242 | 0.913621996 | 0.987100363 | 8.05227862 |
| 5 | Charge_T_kurtosis | 1975 | 1975 | 0 | 0 | 0.0425826007 | 0.223949572 | 0.823271039 | 0.933225688 | 2.40871253 |
| 6 | CC_energy | 7129 | 7129 | 0 | 0 | 0.0472405163 | 0.103397902 | 0.855711033 | 0.96666171 | 2.14398374 |
| 6 | CC_Q | 7129 | 7129 | 0 | 0 | 0.0114770872 | 0.0258838454 | 0.854467051 | 0.968636245 | 2.10283775 |
| 6 | CC_t_mean | 7129 | 7129 | 0 | 0 | 0.0667018922 | 0.0915499577 | 0.998218734 | 0.977025532 | 1.48238187 |
| 6 | CC_V_mean | 7129 | 7129 | 0 | 0 | 0.00330694578 | 0.00580956263 | 0.649779689 | 0.913725582 | 0.0819127924 |
| 6 | CC_T_mean | 7129 | 7129 | 0 | 0 | 0.0123692815 | 0.074366927 | 0.999470079 | 0.999468422 | 0.0482289817 |
| 6 | CC_V_std | 7129 | 7129 | 0 | 0 | 0.00178869722 | 0.00264987916 | 0.534808066 | 0.620290499 | 2.03368468 |
| 6 | CC_T_std | 7129 | 7129 | 0 | 0 | 0.00794517985 | 0.0588950189 | 0.974484742 | 0.998682841 | 1.79438623 |
| 6 | CC_V_skewness | 7129 | 7129 | 0 | 0 | 0.0148684275 | 0.0678497651 | 0.672151726 | 0.972800117 | 8.83438204 |
| 6 | CC_T_skewness | 7129 | 7129 | 0 | 0 | 0.0797891894 | 0.459444457 | 0.689840562 | 0.94929227 | 19.0934723 |
| 6 | CC_V_kurtosis | 7129 | 7129 | 0 | 0 | 0.0109523643 | 0.0520702324 | 0.462468721 | 0.962088054 | 0.611714217 |
| 6 | CC_T_kurtosis | 7129 | 7129 | 0 | 0 | 0.256861536 | 2.55955018 | 0.684013386 | 0.949873429 | 10.889395 |
| 6 | CC_CCCT | 7129 | 7128 | 0 | 1 | 0.13275031 | 0.177870335 | 0.998414027 | 0.977715017 | 1.47515478 |
| 6 | CC_entropy | 7129 | 7129 | 0 | 0 | 5.18004189 | 5.18007044 | 0.425142717 | 0.80308928 | 65.2610134 |
| 6 | dV_energy | 7129 | 7128 | 0 | 1 | 0.018992067 | 0.087936551 | 0.766592337 | 0.985563676 | 2.20512702 |
| 6 | dV_Q | 7129 | 7128 | 0 | 1 | 0.00481190259 | 0.0223183832 | 0.766944451 | 0.985630745 | 2.20511142 |
| 6 | dV_t_mean | 7129 | 7128 | 0 | 1 | 0.00478238498 | 0.0274101827 | 0.997855842 | 0.999135123 | 0.27111328 |
| 6 | dV_V_mean | 7129 | 7128 | 0 | 1 | 0.000578645549 | 0.00211748089 | 0.665847942 | 0.979552147 | 0.0146604577 |
| 6 | dV_T_mean | 7129 | 7128 | 0 | 1 | 0.00594636141 | 0.0535721742 | 0.999735588 | 0.999798104 | 0.0236241647 |
| 6 | dV_V_std | 7129 | 7128 | 0 | 1 | 0.000108497856 | 0.00030663829 | 0.45033843 | 0.733803517 | 0.375674675 |
| 6 | dV_T_std | 7129 | 7128 | 0 | 1 | 0.00722766019 | 0.0275783987 | 0.977914346 | 0.993262768 | 3.13817744 |
| 6 | dV_V_skewness | 7129 | 7128 | 0 | 1 | 0.0199987008 | 0.087457088 | 0.665497403 | 0.98699237 | 15.5421498 |
| 6 | dV_T_skewness | 7129 | 7128 | 0 | 1 | 0.126070649 | 0.455130649 | 0.689479188 | 0.867099335 | 44.6322213 |
| 6 | dV_V_kurtosis | 7129 | 7128 | 0 | 1 | 0.00986004655 | 0.0399833476 | 0.350737105 | 0.910813843 | 0.542638999 |
| 6 | dV_T_kurtosis | 7129 | 7128 | 0 | 1 | 0.452512429 | 4.10162375 | 0.30036587 | 0.794056363 | 19.7487674 |
| 6 | dV_dV_devide_dt | 7129 | 7128 | 0 | 1 | 0.00162367522 | 0.00988857639 | 0.543420759 | 0.997289256 | 5.67644479 |
| 6 | dV_entropy | 7129 | 7128 | 0 | 1 | 4.82861233 | 4.83027863 | 0.22532662 | -0.152696638 | 63.5964425 |
| 6 | CV_energy | 7129 | 7129 | 0 | 0 | 0.0201626248 | 0.0324395701 | 0.991180454 | 0.993988872 | 1.47757699 |
| 6 | CV_Q | 7129 | 7129 | 0 | 0 | 0.00480053635 | 0.00772527016 | 0.991174104 | 0.993988136 | 1.47753224 |
| 6 | CV_t_mean | 7129 | 7129 | 0 | 0 | 0.0429636777 | 0.0619447247 | 0.999570751 | 0.999519513 | 0.316270047 |
| 6 | CV_C_mean | 7129 | 7129 | 0 | 0 | 0.00611603096 | 0.0154532003 | 0.984118681 | 0.981988668 | 0.849420218 |
| 6 | CV_T_mean | 7129 | 7129 | 0 | 0 | 0.00979248886 | 0.184633767 | 0.995756462 | 0.999162908 | 0.0423090935 |
| 6 | CV_C_std | 7129 | 7129 | 0 | 0 | 0.0101652544 | 0.015946563 | 0.993628022 | 0.919031043 | 1.25743543 |
| 6 | CV_T_std | 7129 | 7129 | 0 | 0 | 0.00525716643 | 0.0664910609 | 0.990948578 | 0.999013503 | 0.309063243 |
| 6 | CV_C_skewness | 7129 | 7129 | 0 | 0 | 0.00999178117 | 0.0216536228 | 0.992853948 | 0.994727304 | 0.560442865 |
| 6 | CV_T_skewness | 7129 | 7129 | 0 | 0 | 0.01899281 | 0.130366728 | 0.629994969 | 0.962897226 | 3.03655804 |
| 6 | CV_C_kurtosis | 7129 | 7129 | 0 | 0 | 0.0467607221 | 0.0759579499 | 0.99511685 | 0.994859472 | 0.840989528 |
| 6 | CV_T_kurtosis | 7129 | 7129 | 0 | 0 | 0.013432087 | 0.231771407 | 0.535920814 | 0.994705048 | 0.675002611 |
| 6 | CV_CVCT | 7129 | 7129 | 0 | 0 | 0.0779873419 | 0.117296377 | 0.999586028 | 0.999530381 | 0.287131837 |
| 6 | CV_entropy | 7129 | 7129 | 0 | 0 | 4.76086386 | 4.76128988 | 0.996114922 | 0.984063592 | 71.1750804 |
| 6 | dI_energy | 7129 | 7129 | 0 | 0 | 0.00124811747 | 0.00284536564 | 0.93391229 | 0.991716981 | 2.85622554 |
| 6 | dI_Q | 7129 | 7129 | 0 | 0 | 0.000297174074 | 0.000677464086 | 0.933907561 | 0.991713361 | 2.8562252 |
| 6 | dI_t_mean | 7129 | 7129 | 0 | 0 | 0.00937185745 | 0.0214289175 | 0.933745314 | 0.99155605 | 2.84853493 |
| 6 | dI_C_mean | 7129 | 7129 | 0 | 0 | 0.000483437461 | 0.000632513148 | 0.545216356 | 0.454356627 | 0.0509552619 |
| 6 | dI_T_mean | 7129 | 7129 | 0 | 0 | 0.0160664068 | 0.257094338 | 0.991901858 | 0.999099748 | 0.0654164518 |
| 6 | dI_C_std | 7129 | 7129 | 0 | 0 | 0.000271349752 | 0.000337035956 | 0.0732353108 | 0.0548625678 | 0.938663187 |
| 6 | dI_T_std | 7129 | 7129 | 0 | 0 | 0.0112234528 | 0.0147680332 | 0.877788464 | 0.873957951 | 14.1746928 |
| 6 | dI_C_skewness | 7129 | 7129 | 0 | 0 | 0.00772047878 | 0.0149751735 | 0.773361975 | 0.71776943 | 15.9115233 |
| 6 | dI_T_skewness | 7129 | 7129 | 0 | 0 | 0.354457842 | 0.64405015 | 0.376909965 | 0.501057351 | 109.343485 |
| 6 | dI_C_kurtosis | 7129 | 7129 | 0 | 0 | 0.00618647569 | 0.0089229962 | 0.419093188 | 0.361513727 | 0.343317652 |
| 6 | dI_T_kurtosis | 7129 | 7129 | 0 | 0 | 0.733135339 | 4.1877131 | 0.0977125062 | 0.347493571 | 32.9852774 |
| 6 | dI_dI_devide_dt | 7129 | 7129 | 0 | 0 | 0.000795561343 | 0.0033334214 | 0.987319099 | 0.99689444 | 0.527052697 |
| 6 | dI_entropy | 7129 | 7129 | 0 | 0 | 2.52358603 | 2.53173691 | -0.137857305 | 0.123357607 | 47.6627416 |
| 6 | Charge_energy | 7129 | 7129 | 0 | 0 | 0.0010719156 | 0.036552588 | 0.993826659 | 0.99839811 | 0.0301111458 |
| 6 | Charge_Q | 7129 | 7129 | 0 | 0 | 0.000257878991 | 0.00893629763 | 0.993812656 | 0.998401039 | 0.0296909118 |
| 6 | Charge_t_mean | 7129 | 7129 | 0 | 0 | 0.012367093 | 0.142564348 | 0.997192332 | 0.999401957 | 0.0683741565 |
| 6 | Charge_V_mean | 7129 | 7129 | 0 | 0 | 0.00047620855 | 0.00151818424 | 0.978866891 | 0.998748125 | 0.0114476298 |
| 6 | Charge_C_mean | 7129 | 7129 | 0 | 0 | 0.00222061162 | 0.0159600273 | 0.995700082 | 0.999149102 | 0.15278726 |
| 6 | Charge_T_mean | 7129 | 7129 | 0 | 0 | 0.00452775006 | 0.135209182 | 0.997799115 | 0.999164693 | 0.0190654695 |
| 6 | Charge_C_std | 7129 | 7129 | 0 | 0 | 0.00150636938 | 0.00464848979 | 0.999842753 | 0.999758808 | 0.10213708 |
| 6 | Charge_V_std | 7129 | 7129 | 0 | 0 | 0.00103499243 | 0.00291383455 | 0.854615717 | 0.9977674 | 1.25587552 |
| 6 | Charge_T_std | 7129 | 7129 | 0 | 0 | 0.0026679238 | 0.0774174012 | 0.990144454 | 0.999047067 | 0.143641324 |
| 6 | Charge_C_skewness | 7129 | 7129 | 0 | 0 | 0.00395428086 | 0.017568496 | 0.996606321 | 0.999768642 | 0.579503237 |
| 6 | Charge_V_skewness | 7129 | 7129 | 0 | 0 | 0.0139749678 | 0.0835415127 | 0.95070375 | 0.999443195 | 0.724097476 |
| 6 | Charge_T_skewness | 7129 | 7129 | 0 | 0 | 0.00986895484 | 0.0872176504 | 0.898420347 | 0.982638038 | 7.35996739 |
| 6 | Charge_C_kurtosis | 7129 | 7129 | 0 | 0 | 0.00909778085 | 0.0434276053 | 0.983699837 | 0.999669853 | 0.52013883 |
| 6 | Charge_V_kurtosis | 7129 | 7129 | 0 | 0 | 0.099899278 | 0.70678433 | 0.812227665 | 0.998646595 | 1.87920454 |
| 6 | Charge_T_kurtosis | 7129 | 7129 | 0 | 0 | 0.0116223105 | 0.101305072 | 0.733802625 | 0.987723133 | 0.81755217 |

### Profile-wise feature candidate metrics (55 × 67 rows)

Each row below is one workbook profile × feature pair. The profile IDs are the workbook sheet names; equal-count positional identity is still not verified.

| Batch | Profile | Feature | Aligned | Valid | Workbook invalid | Candidate invalid | MAE | RMSE | Pearson r | Spearman ρ | Relative MAE (%) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Sheet1 | CC_energy | 389 | 389 | 0 | 0 | 0.0543844972 | 0.0634997702 | 0.997583476 | 0.986356158 | 0.910062917 |
| 1 | Sheet1 | CC_Q | 389 | 389 | 0 | 0 | 0.0127976107 | 0.0149881654 | 0.998151868 | 0.988548078 | 0.829124725 |
| 1 | Sheet1 | CC_t_mean | 389 | 389 | 0 | 0 | 0.0959468572 | 0.112339313 | 0.998156182 | 0.988586294 | 0.8288163 |
| 1 | Sheet1 | CC_V_mean | 389 | 389 | 0 | 0 | 0.00332771088 | 0.00373935193 | 0.996196023 | 0.961501563 | 0.0859173004 |
| 1 | Sheet1 | CC_T_mean | 389 | 389 | 0 | 0 | 0.0163513206 | 0.0196276055 | 0.999983048 | 0.999889915 | 0.0574171691 |
| 1 | Sheet1 | CC_V_std | 389 | 389 | 0 | 0 | 0.00123066364 | 0.00142603915 | 0.979003428 | 0.95407876 | 0.819020531 |
| 1 | Sheet1 | CC_T_std | 389 | 389 | 0 | 0 | 0.00660549961 | 0.0256468968 | 0.932593743 | 0.99660861 | 0.496786857 |
| 1 | Sheet1 | CC_V_skewness | 389 | 389 | 0 | 0 | 0.0786042065 | 0.0810304832 | 0.978964367 | 0.958700505 | 21.0087391 |
| 1 | Sheet1 | CC_T_skewness | 389 | 389 | 0 | 0 | 0.0100329117 | 0.0163527456 | 0.955432081 | 0.984577822 | 3.16977387 |
| 1 | Sheet1 | CC_V_kurtosis | 389 | 389 | 0 | 0 | 0.123265239 | 0.12862328 | 0.918354321 | 0.925226439 | 5.1026401 |
| 1 | Sheet1 | CC_T_kurtosis | 389 | 389 | 0 | 0 | 0.0114462152 | 0.0228121976 | 0.814674435 | 0.945140499 | 0.621147173 |
| 1 | Sheet1 | CC_CCCT | 389 | 389 | 0 | 0 | 0.191922535 | 0.224783993 | 0.998152003 | 0.988585665 | 0.828939615 |
| 1 | Sheet1 | CC_entropy | 389 | 389 | 0 | 0 | 5.06571572 | 5.06576183 | 0.846340207 | 0.928523754 | 66.7601392 |
| 1 | Sheet1 | dV_energy | 389 | 389 | 0 | 0 | 0.00607269492 | 0.00692521519 | 0.99592336 | 0.977796828 | 0.670588687 |
| 1 | Sheet1 | dV_Q | 389 | 389 | 0 | 0 | 0.00154326455 | 0.00176016828 | 0.995899238 | 0.977682613 | 0.672540526 |
| 1 | Sheet1 | dV_t_mean | 389 | 389 | 0 | 0 | 0.0124183882 | 0.0154438924 | 0.99268463 | 0.976723037 | 0.721132806 |
| 1 | Sheet1 | dV_V_mean | 389 | 389 | 0 | 0 | 0.000136944555 | 0.000189494551 | 0.925095712 | 0.911980378 | 0.00347003461 |
| 1 | Sheet1 | dV_T_mean | 389 | 389 | 0 | 0 | 0.00633827288 | 0.00791317691 | 0.999991952 | 0.999929362 | 0.0214916971 |
| 1 | Sheet1 | dV_V_std | 389 | 389 | 0 | 0 | 0.000146848134 | 0.000173159904 | 0.385001441 | 0.383829906 | 0.508374691 |
| 1 | Sheet1 | dV_T_std | 389 | 389 | 0 | 0 | 0.00606705569 | 0.00775676287 | 0.987141107 | 0.98075282 | 3.6001818 |
| 1 | Sheet1 | dV_V_skewness | 389 | 389 | 0 | 0 | 0.0031581372 | 0.00562148815 | 0.96137754 | 0.951357208 | 2.10905966 |
| 1 | Sheet1 | dV_T_skewness | 389 | 389 | 0 | 0 | 0.102782504 | 0.148314613 | 0.834272176 | 0.850424542 | 53.3133638 |
| 1 | Sheet1 | dV_V_kurtosis | 389 | 389 | 0 | 0 | 0.00364078504 | 0.00620164941 | 0.839873283 | 0.853653709 | 0.200223532 |
| 1 | Sheet1 | dV_T_kurtosis | 389 | 389 | 0 | 0 | 0.154369397 | 0.237788038 | 0.722230538 | 0.772602231 | 7.94305006 |
| 1 | Sheet1 | dV_dV_devide_dt | 389 | 389 | 0 | 0 | 8.97843985e-05 | 0.000171272734 | 0.996562427 | 0.985288527 | 0.310347354 |
| 1 | Sheet1 | dV_entropy | 389 | 389 | 0 | 0 | 4.69414818 | 4.6965548 | 0.700239964 | 0.465825311 | 62.9388037 |
| 1 | Sheet1 | CV_energy | 389 | 389 | 0 | 0 | 0.0343238029 | 0.0401224622 | 0.986656268 | 0.972522725 | 2.48115431 |
| 1 | Sheet1 | CV_Q | 389 | 389 | 0 | 0 | 0.0081725404 | 0.00955315746 | 0.986655309 | 0.972522725 | 2.48110932 |
| 1 | Sheet1 | CV_t_mean | 389 | 389 | 0 | 0 | 0.0690815442 | 0.0794611128 | 0.999822064 | 0.997489445 | 0.497530652 |
| 1 | Sheet1 | CV_C_mean | 389 | 389 | 0 | 0 | 0.0116179875 | 0.013984729 | 0.975351542 | 0.946702234 | 1.61612493 |
| 1 | Sheet1 | CV_T_mean | 389 | 389 | 0 | 0 | 0.0175991614 | 0.0209868303 | 0.999985793 | 0.999844658 | 0.0677797592 |
| 1 | Sheet1 | CV_C_std | 389 | 389 | 0 | 0 | 0.0208223338 | 0.0248119738 | 0.783656884 | 0.773653138 | 2.51817633 |
| 1 | Sheet1 | CV_T_std | 389 | 389 | 0 | 0 | 0.0107527616 | 0.0131077005 | 0.999351152 | 0.998016835 | 0.471293549 |
| 1 | Sheet1 | CV_C_skewness | 389 | 389 | 0 | 0 | 0.0210165357 | 0.0247813896 | 0.993504705 | 0.985412687 | 1.08071029 |
| 1 | Sheet1 | CV_T_skewness | 389 | 389 | 0 | 0 | 0.00748192294 | 0.00905638105 | 0.998638428 | 0.989905388 | 1.19377039 |
| 1 | Sheet1 | CV_C_kurtosis | 389 | 389 | 0 | 0 | 0.100539226 | 0.117372252 | 0.99339511 | 0.985183954 | 1.59307332 |
| 1 | Sheet1 | CV_T_kurtosis | 389 | 389 | 0 | 0 | 0.0153061831 | 0.0185958924 | 0.997037021 | 0.97894783 | 0.757315771 |
| 1 | Sheet1 | CV_CVCT | 389 | 389 | 0 | 0 | 0.1293353 | 0.150965402 | 0.999829732 | 0.99750351 | 0.465879761 |
| 1 | Sheet1 | CV_entropy | 389 | 389 | 0 | 0 | 4.70972229 | 4.70989941 | 0.986987871 | 0.966462133 | 71.6229668 |
| 1 | Sheet1 | dI_energy | 389 | 389 | 0 | 0 | 0.000985571205 | 0.00114542021 | 0.993396903 | 0.976944075 | 2.15920812 |
| 1 | Sheet1 | dI_Q | 389 | 389 | 0 | 0 | 0.000234673418 | 0.000272743843 | 0.99339553 | 0.976920834 | 2.15924022 |
| 1 | Sheet1 | dI_t_mean | 389 | 389 | 0 | 0 | 0.0074656022 | 0.0086583105 | 0.993304669 | 0.974767239 | 2.17110278 |
| 1 | Sheet1 | dI_C_mean | 389 | 389 | 0 | 0 | 0.000525320236 | 0.000648808394 | 0.658619336 | 0.622346417 | 0.0553953258 |
| 1 | Sheet1 | dI_T_mean | 389 | 389 | 0 | 0 | 0.0145932415 | 0.01788122 | 0.999961283 | 0.999814027 | 0.0520309118 |
| 1 | Sheet1 | dI_C_std | 389 | 389 | 0 | 0 | 0.000290625978 | 0.000368914123 | -0.0120509639 | 0.0157676712 | 1.00607727 |
| 1 | Sheet1 | dI_T_std | 389 | 389 | 0 | 0 | 0.0122755069 | 0.0152043734 | 0.817330805 | 0.807435505 | 11.5672067 |
| 1 | Sheet1 | dI_C_skewness | 389 | 389 | 0 | 0 | 0.00969127724 | 0.0121839769 | 0.881630488 | 0.866173458 | 13.2981073 |
| 1 | Sheet1 | dI_T_skewness | 389 | 389 | 0 | 0 | 0.22725722 | 0.287169571 | 0.380345107 | 0.341945125 | 102.474253 |
| 1 | Sheet1 | dI_C_kurtosis | 389 | 389 | 0 | 0 | 0.0137171592 | 0.0169247206 | 0.148176965 | 0.139452917 | 0.759416231 |
| 1 | Sheet1 | dI_T_kurtosis | 389 | 389 | 0 | 0 | 0.272627943 | 0.349856888 | 0.426725529 | 0.393541262 | 13.2790575 |
| 1 | Sheet1 | dI_dI_devide_dt | 389 | 389 | 0 | 0 | 0.00120253495 | 0.0018501974 | 0.995876232 | 0.991061805 | 0.836281759 |
| 1 | Sheet1 | dI_entropy | 389 | 389 | 0 | 0 | 2.58693017 | 2.59310691 | -0.440426841 | -0.413681414 | 48.2940718 |
| 1 | Sheet1 | Charge_energy | 389 | 389 | 0 | 0 | 0.000951435016 | 0.00109026895 | 0.999997763 | 0.999969828 | 0.0129199913 |
| 1 | Sheet1 | Charge_Q | 389 | 389 | 0 | 0 | 0.000140047124 | 0.00016272921 | 0.999998598 | 0.999974313 | 0.00747302813 |
| 1 | Sheet1 | Charge_t_mean | 389 | 389 | 0 | 0 | 0.00576967069 | 0.011482931 | 0.999961136 | 0.999829571 | 0.0226532341 |
| 1 | Sheet1 | Charge_V_mean | 389 | 389 | 0 | 0 | 0.00102355691 | 0.00103203898 | 0.999989246 | 0.999856481 | 0.0252772628 |
| 1 | Sheet1 | Charge_C_mean | 389 | 389 | 0 | 0 | 0.000828825099 | 0.00135703515 | 0.999983678 | 0.999946792 | 0.0373795792 |
| 1 | Sheet1 | Charge_T_mean | 389 | 389 | 0 | 0 | 0.00742103327 | 0.00798912165 | 0.999999103 | 0.999984099 | 0.0274024165 |
| 1 | Sheet1 | Charge_C_std | 389 | 389 | 0 | 0 | 0.000614227196 | 0.000987004427 | 0.996499883 | 0.999274558 | 0.0354363737 |
| 1 | Sheet1 | Charge_V_std | 389 | 389 | 0 | 0 | 0.00196056303 | 0.00198485548 | 0.999861648 | 0.998487755 | 1.02583966 |
| 1 | Sheet1 | Charge_T_std | 389 | 389 | 0 | 0 | 0.00197607253 | 0.00249024923 | 0.999979644 | 0.99979043 | 0.0864725609 |
| 1 | Sheet1 | Charge_C_skewness | 389 | 389 | 0 | 0 | 0.000866338839 | 0.00153807392 | 0.999983978 | 0.999953112 | 0.402916751 |
| 1 | Sheet1 | Charge_V_skewness | 389 | 389 | 0 | 0 | 0.0316381035 | 0.0325775524 | 0.999650366 | 0.99672843 | 3.89856753 |
| 1 | Sheet1 | Charge_T_skewness | 389 | 389 | 0 | 0 | 0.00333752278 | 0.00409411557 | 0.999668784 | 0.998198068 | 1.7666263 |
| 1 | Sheet1 | Charge_C_kurtosis | 389 | 389 | 0 | 0 | 0.000618439307 | 0.000943743274 | 0.999807786 | 0.999838134 | 0.0527035795 |
| 1 | Sheet1 | Charge_V_kurtosis | 389 | 389 | 0 | 0 | 0.138469441 | 0.146557454 | 0.998744635 | 0.997787287 | 6.42770552 |
| 1 | Sheet1 | Charge_T_kurtosis | 389 | 389 | 0 | 0 | 0.00245356637 | 0.00310224668 | 0.999601647 | 0.996868891 | 0.145160279 |
| 1 | Sheet2 | CC_energy | 406 | 406 | 0 | 0 | 0.0517321319 | 0.0610378998 | 0.997851268 | 0.991155688 | 0.874395377 |
| 1 | Sheet2 | CC_Q | 406 | 406 | 0 | 0 | 0.0121533667 | 0.0143953168 | 0.998351761 | 0.992541041 | 0.79576367 |
| 1 | Sheet2 | CC_t_mean | 406 | 406 | 0 | 0 | 0.0912829713 | 0.108174702 | 0.998341407 | 0.992583713 | 0.79691696 |
| 1 | Sheet2 | CC_V_mean | 406 | 406 | 0 | 0 | 0.00326650856 | 0.0036793029 | 0.99651984 | 0.972062703 | 0.0842859713 |
| 1 | Sheet2 | CC_T_mean | 406 | 406 | 0 | 0 | 0.015109908 | 0.0183049108 | 0.999986192 | 0.999915007 | 0.0539836315 |
| 1 | Sheet2 | CC_V_std | 406 | 406 | 0 | 0 | 0.00123063453 | 0.00144197146 | 0.978321603 | 0.95955167 | 0.819408465 |
| 1 | Sheet2 | CC_T_std | 406 | 406 | 0 | 0 | 0.00773038475 | 0.0435677822 | 0.904720265 | 0.996566158 | 0.611048589 |
| 1 | Sheet2 | CC_V_skewness | 406 | 406 | 0 | 0 | 0.0857064213 | 0.0927841974 | 0.939126944 | 0.971399613 | 24.5302025 |
| 1 | Sheet2 | CC_T_skewness | 406 | 406 | 0 | 0 | 0.00965851462 | 0.0164419362 | 0.982494796 | 0.992629575 | 2.76254962 |
| 1 | Sheet2 | CC_V_kurtosis | 406 | 406 | 0 | 0 | 0.14450082 | 0.175704968 | 0.65324812 | 0.880353798 | 5.95785536 |
| 1 | Sheet2 | CC_T_kurtosis | 406 | 406 | 0 | 0 | 0.0131676195 | 0.0284157326 | 0.898938551 | 0.970403855 | 0.695584903 |
| 1 | Sheet2 | CC_CCCT | 406 | 406 | 0 | 0 | 0.182260715 | 0.215896505 | 0.998351602 | 0.992563353 | 0.795594797 |
| 1 | Sheet2 | CC_entropy | 406 | 406 | 0 | 0 | 5.06278834 | 5.0628512 | 0.813070542 | 0.919375193 | 66.81945 |
| 1 | Sheet2 | dV_energy | 406 | 406 | 0 | 0 | 0.00642326782 | 0.00713214022 | 0.997393337 | 0.975732652 | 0.702122434 |
| 1 | Sheet2 | dV_Q | 406 | 406 | 0 | 0 | 0.00162781944 | 0.00180806896 | 0.997391137 | 0.976190969 | 0.702189052 |
| 1 | Sheet2 | dV_t_mean | 406 | 406 | 0 | 0 | 0.0126554981 | 0.0141269072 | 0.99641008 | 0.974539338 | 0.727660307 |
| 1 | Sheet2 | dV_V_mean | 406 | 406 | 0 | 0 | 0.000131341261 | 0.000185397016 | 0.91472499 | 0.88450394 | 0.00332815841 |
| 1 | Sheet2 | dV_T_mean | 406 | 406 | 0 | 0 | 0.0062344519 | 0.00794768578 | 0.999993046 | 0.999944055 | 0.021550605 |
| 1 | Sheet2 | dV_V_std | 406 | 406 | 0 | 0 | 0.000175075714 | 0.000199368096 | 0.384884981 | 0.430168009 | 0.606874938 |
| 1 | Sheet2 | dV_T_std | 406 | 406 | 0 | 0 | 0.00663144817 | 0.00857588827 | 0.985526483 | 0.984970371 | 4.02222941 |
| 1 | Sheet2 | dV_V_skewness | 406 | 406 | 0 | 0 | 0.0029745257 | 0.00488200599 | 0.969995921 | 0.951259813 | 1.94764344 |
| 1 | Sheet2 | dV_T_skewness | 406 | 406 | 0 | 0 | 0.11618812 | 0.194155533 | 0.836746005 | 0.873829763 | 48.0105234 |
| 1 | Sheet2 | dV_V_kurtosis | 406 | 406 | 0 | 0 | 0.00334876212 | 0.00546897715 | 0.867921116 | 0.88825135 | 0.183998528 |
| 1 | Sheet2 | dV_T_kurtosis | 406 | 406 | 0 | 0 | 0.171641978 | 0.283323432 | 0.753593022 | 0.837790321 | 8.5640673 |
| 1 | Sheet2 | dV_dV_devide_dt | 406 | 406 | 0 | 0 | 8.01215042e-05 | 0.000136563397 | 0.997911918 | 0.987060322 | 0.279810189 |
| 1 | Sheet2 | dV_entropy | 406 | 406 | 0 | 0 | 4.70945816 | 4.71168301 | 0.647524173 | 0.351278818 | 63.0175166 |
| 1 | Sheet2 | CV_energy | 406 | 406 | 0 | 0 | 0.0324348787 | 0.0500902858 | 0.954609373 | 0.980849277 | 2.31038606 |
| 1 | Sheet2 | CV_Q | 406 | 406 | 0 | 0 | 0.00772146875 | 0.0119247173 | 0.954601111 | 0.980855912 | 2.31024906 |
| 1 | Sheet2 | CV_t_mean | 406 | 406 | 0 | 0 | 0.0613490247 | 0.0702233822 | 0.999846092 | 0.99815364 | 0.436840755 |
| 1 | Sheet2 | CV_C_mean | 406 | 406 | 0 | 0 | 0.0107896374 | 0.0179181533 | 0.913220338 | 0.954203196 | 1.49896398 |
| 1 | Sheet2 | CV_T_mean | 406 | 406 | 0 | 0 | 0.0147964552 | 0.0174325355 | 0.999989721 | 0.999889724 | 0.0580369174 |
| 1 | Sheet2 | CV_C_std | 406 | 406 | 0 | 0 | 0.0184647979 | 0.021442526 | 0.783356233 | 0.792771903 | 2.22085182 |
| 1 | Sheet2 | CV_T_std | 406 | 406 | 0 | 0 | 0.0113249083 | 0.0379880527 | 0.984062177 | 0.997556894 | 0.520456151 |
| 1 | Sheet2 | CV_C_skewness | 406 | 406 | 0 | 0 | 0.0215590702 | 0.0588122146 | 0.927810392 | 0.976466749 | 1.0907266 |
| 1 | Sheet2 | CV_T_skewness | 406 | 406 | 0 | 0 | 0.0089925013 | 0.0443513927 | 0.926259274 | 0.981781154 | 1.31483117 |
| 1 | Sheet2 | CV_C_kurtosis | 406 | 406 | 0 | 0 | 0.10078194 | 0.218612231 | 0.954717631 | 0.975870721 | 1.55936754 |
| 1 | Sheet2 | CV_T_kurtosis | 406 | 406 | 0 | 0 | 0.0146191038 | 0.017312181 | 0.996969844 | 0.987311808 | 0.698919091 |
| 1 | Sheet2 | CV_CVCT | 406 | 406 | 0 | 0 | 0.114561332 | 0.132660262 | 0.999849346 | 0.998140055 | 0.407996516 |
| 1 | Sheet2 | CV_entropy | 406 | 406 | 0 | 0 | 4.71610706 | 4.71627724 | 0.948113426 | 0.962372194 | 71.7136109 |
| 1 | Sheet2 | dI_energy | 406 | 406 | 0 | 0 | 0.000957721979 | 0.00109711103 | 0.995463294 | 0.98183674 | 2.04351296 |
| 1 | Sheet2 | dI_Q | 406 | 406 | 0 | 0 | 0.000228020471 | 0.000261208683 | 0.995462001 | 0.981780258 | 2.04361308 |
| 1 | Sheet2 | dI_t_mean | 406 | 406 | 0 | 0 | 0.007110187 | 0.00817446088 | 0.995548445 | 0.981978036 | 2.01288626 |
| 1 | Sheet2 | dI_C_mean | 406 | 406 | 0 | 0 | 0.000517933247 | 0.000642073517 | 0.785015608 | 0.765229482 | 0.0546500057 |
| 1 | Sheet2 | dI_T_mean | 406 | 406 | 0 | 0 | 0.0356123943 | 0.417973985 | 0.980348177 | 0.994421738 | 0.129745333 |
| 1 | Sheet2 | dI_C_std | 406 | 406 | 0 | 0 | 0.000275294797 | 0.00033838838 | -0.024522797 | -0.0541210265 | 0.95277562 |
| 1 | Sheet2 | dI_T_std | 406 | 406 | 0 | 0 | 0.0119823619 | 0.0147629133 | 0.820461396 | 0.778816683 | 11.3615649 |
| 1 | Sheet2 | dI_C_skewness | 406 | 406 | 0 | 0 | 0.00797664565 | 0.010383454 | 0.953037378 | 0.929336771 | 9.15671021 |
| 1 | Sheet2 | dI_T_skewness | 406 | 406 | 0 | 0 | 0.252140502 | 0.314696844 | 0.439134226 | 0.439567646 | 96.70676 |
| 1 | Sheet2 | dI_C_kurtosis | 406 | 406 | 0 | 0 | 0.0147679059 | 0.0178724731 | 0.332768881 | 0.312858403 | 0.816390207 |
| 1 | Sheet2 | dI_T_kurtosis | 406 | 406 | 0 | 0 | 0.262010054 | 0.34448369 | 0.363894323 | 0.402305225 | 12.8612786 |
| 1 | Sheet2 | dI_dI_devide_dt | 406 | 406 | 0 | 0 | 0.00116483359 | 0.0023403869 | 0.994389396 | 0.994518638 | 0.829949288 |
| 1 | Sheet2 | dI_entropy | 406 | 406 | 0 | 0 | 2.62911372 | 2.63619531 | -0.536692002 | -0.513620968 | 48.7069045 |
| 1 | Sheet2 | Charge_energy | 406 | 406 | 0 | 0 | 0.000995818743 | 0.00112504509 | 0.999998275 | 0.999972565 | 0.013591339 |
| 1 | Sheet2 | Charge_Q | 406 | 406 | 0 | 0 | 0.000136165585 | 0.000157453305 | 0.999998877 | 0.999986014 | 0.00730866518 |
| 1 | Sheet2 | Charge_t_mean | 406 | 406 | 0 | 0 | 0.00521080984 | 0.00756722799 | 0.999980714 | 0.999908148 | 0.0204293425 |
| 1 | Sheet2 | Charge_V_mean | 406 | 406 | 0 | 0 | 0.00106226134 | 0.00107182429 | 0.999988066 | 0.999833421 | 0.0262116816 |
| 1 | Sheet2 | Charge_C_mean | 406 | 406 | 0 | 0 | 0.000780965521 | 0.00108035031 | 0.999990636 | 0.999937241 | 0.0355142545 |
| 1 | Sheet2 | Charge_T_mean | 406 | 406 | 0 | 0 | 0.00713877485 | 0.00754739253 | 0.99999945 | 0.999983324 | 0.0268397884 |
| 1 | Sheet2 | Charge_C_std | 406 | 406 | 0 | 0 | 0.000811356992 | 0.00494191478 | 0.889715452 | 0.999117971 | 0.0467824319 |
| 1 | Sheet2 | Charge_V_std | 406 | 406 | 0 | 0 | 0.00207988912 | 0.00211603288 | 0.999793047 | 0.998025612 | 1.09536666 |
| 1 | Sheet2 | Charge_T_std | 406 | 406 | 0 | 0 | 0.00400250863 | 0.0444373515 | 0.988013799 | 0.999573062 | 0.180924075 |
| 1 | Sheet2 | Charge_C_skewness | 406 | 406 | 0 | 0 | 0.000848928136 | 0.00135122687 | 0.999989333 | 0.999940469 | 0.422161692 |
| 1 | Sheet2 | Charge_V_skewness | 406 | 406 | 0 | 0 | 0.0352121309 | 0.0370637422 | 0.999240935 | 0.997752881 | 4.18961606 |
| 1 | Sheet2 | Charge_T_skewness | 406 | 406 | 0 | 0 | 0.00372173346 | 0.00929866635 | 0.997246578 | 0.999620938 | 2.15105056 |
| 1 | Sheet2 | Charge_C_kurtosis | 406 | 406 | 0 | 0 | 0.000817273147 | 0.00306896374 | 0.996713395 | 0.999806031 | 0.0700571302 |
| 1 | Sheet2 | Charge_V_kurtosis | 406 | 406 | 0 | 0 | 0.160984139 | 0.188151132 | 0.987728598 | 0.999327406 | 7.26607892 |
| 1 | Sheet2 | Charge_T_kurtosis | 406 | 406 | 0 | 0 | 0.00402423664 | 0.0332836787 | 0.935463562 | 0.989016334 | 0.242958817 |
| 1 | Sheet3 | CC_energy | 392 | 392 | 0 | 0 | 0.0586674512 | 0.06647071 | 0.998058468 | 0.98987182 | 0.99199891 |
| 1 | Sheet3 | CC_Q | 392 | 392 | 0 | 0 | 0.0138135094 | 0.0156963952 | 0.998509158 | 0.991320923 | 0.904875433 |
| 1 | Sheet3 | CC_t_mean | 392 | 392 | 0 | 0 | 0.103759355 | 0.117889624 | 0.998505623 | 0.991254579 | 0.906255523 |
| 1 | Sheet3 | CC_V_mean | 392 | 392 | 0 | 0 | 0.00355682106 | 0.00390135785 | 0.996829313 | 0.980415 | 0.0917689381 |
| 1 | Sheet3 | CC_T_mean | 392 | 392 | 0 | 0 | 0.0160655525 | 0.0185692606 | 0.999987584 | 0.999922903 | 0.057288884 |
| 1 | Sheet3 | CC_V_std | 392 | 392 | 0 | 0 | 0.00122549152 | 0.00140889063 | 0.980740141 | 0.940712893 | 0.824388219 |
| 1 | Sheet3 | CC_T_std | 392 | 392 | 0 | 0 | 0.00588907839 | 0.0230987578 | 0.961142025 | 0.997285921 | 0.472980856 |
| 1 | Sheet3 | CC_V_skewness | 392 | 392 | 0 | 0 | 0.0802536645 | 0.0826436927 | 0.982051371 | 0.967947418 | 21.0453244 |
| 1 | Sheet3 | CC_T_skewness | 392 | 392 | 0 | 0 | 0.011370633 | 0.0192784271 | 0.957004711 | 0.985497368 | 3.01468099 |
| 1 | Sheet3 | CC_V_kurtosis | 392 | 392 | 0 | 0 | 0.123948273 | 0.129390123 | 0.886680142 | 0.887985795 | 5.13792958 |
| 1 | Sheet3 | CC_T_kurtosis | 392 | 392 | 0 | 0 | 0.0147420867 | 0.0276178245 | 0.881695748 | 0.972193672 | 0.783128936 |
| 1 | Sheet3 | CC_CCCT | 392 | 392 | 0 | 0 | 0.207163426 | 0.235411168 | 0.998509248 | 0.991336396 | 0.904717656 |
| 1 | Sheet3 | CC_entropy | 392 | 392 | 0 | 0 | 5.06471298 | 5.06476553 | 0.77860836 | 0.868563845 | 66.7495709 |
| 1 | Sheet3 | dV_energy | 392 | 392 | 0 | 0 | 0.006241394 | 0.006873339 | 0.997349162 | 0.983067173 | 0.684150908 |
| 1 | Sheet3 | dV_Q | 392 | 392 | 0 | 0 | 0.00158163467 | 0.00174277875 | 0.997333252 | 0.983203188 | 0.684168013 |
| 1 | Sheet3 | dV_t_mean | 392 | 392 | 0 | 0 | 0.0123432973 | 0.0141239595 | 0.995792351 | 0.981461432 | 0.711649926 |
| 1 | Sheet3 | dV_V_mean | 392 | 392 | 0 | 0 | 0.000132188099 | 0.000195117712 | 0.923426341 | 0.901021932 | 0.00334964845 |
| 1 | Sheet3 | dV_T_mean | 392 | 392 | 0 | 0 | 0.00697643615 | 0.00876228472 | 0.999990422 | 0.999919516 | 0.0240692575 |
| 1 | Sheet3 | dV_V_std | 392 | 392 | 0 | 0 | 0.000163675704 | 0.000183754273 | 0.455364641 | 0.445025338 | 0.567087644 |
| 1 | Sheet3 | dV_T_std | 392 | 392 | 0 | 0 | 0.00738148013 | 0.00930697022 | 0.987538829 | 0.984052898 | 4.54982412 |
| 1 | Sheet3 | dV_V_skewness | 392 | 392 | 0 | 0 | 0.00287816055 | 0.00477573719 | 0.975575972 | 0.958626863 | 1.87989237 |
| 1 | Sheet3 | dV_T_skewness | 392 | 392 | 0 | 0 | 0.126910143 | 0.180814893 | 0.908720525 | 0.912741266 | 40.2939759 |
| 1 | Sheet3 | dV_V_kurtosis | 392 | 392 | 0 | 0 | 0.0036431535 | 0.00637881814 | 0.86482756 | 0.873389183 | 0.20016715 |
| 1 | Sheet3 | dV_T_kurtosis | 392 | 392 | 0 | 0 | 0.210388578 | 0.325252132 | 0.80221233 | 0.851392067 | 10.0343152 |
| 1 | Sheet3 | dV_dV_devide_dt | 392 | 392 | 0 | 0 | 8.3683839e-05 | 0.000155279111 | 0.997216594 | 0.987571186 | 0.291433547 |
| 1 | Sheet3 | dV_entropy | 392 | 392 | 0 | 0 | 4.70547061 | 4.7078175 | 0.679272218 | 0.424481339 | 62.998219 |
| 1 | Sheet3 | CV_energy | 392 | 392 | 0 | 0 | 0.0310331816 | 0.0372162715 | 0.985951329 | 0.970059912 | 2.23515475 |
| 1 | Sheet3 | CV_Q | 392 | 392 | 0 | 0 | 0.0073887377 | 0.00886084009 | 0.985951318 | 0.970072662 | 2.23511568 |
| 1 | Sheet3 | CV_t_mean | 392 | 392 | 0 | 0 | 0.0618242341 | 0.0728414155 | 0.999809587 | 0.997355198 | 0.445469843 |
| 1 | Sheet3 | CV_C_mean | 392 | 392 | 0 | 0 | 0.0109780034 | 0.0176584718 | 0.918161399 | 0.932451819 | 1.52479573 |
| 1 | Sheet3 | CV_T_mean | 392 | 392 | 0 | 0 | 0.0146454649 | 0.0180237088 | 0.999987709 | 0.999846404 | 0.0569860031 |
| 1 | Sheet3 | CV_C_std | 392 | 392 | 0 | 0 | 0.0186462561 | 0.0223256921 | 0.780028495 | 0.766826146 | 2.24032093 |
| 1 | Sheet3 | CV_T_std | 392 | 392 | 0 | 0 | 0.00950863798 | 0.0118397041 | 0.999208376 | 0.998561655 | 0.455726093 |
| 1 | Sheet3 | CV_C_skewness | 392 | 392 | 0 | 0 | 0.01776682 | 0.0211027664 | 0.992833227 | 0.982647623 | 0.914479324 |
| 1 | Sheet3 | CV_T_skewness | 392 | 392 | 0 | 0 | 0.00732319466 | 0.00902009667 | 0.998466115 | 0.993104112 | 1.1129435 |
| 1 | Sheet3 | CV_C_kurtosis | 392 | 392 | 0 | 0 | 0.0858642796 | 0.10164768 | 0.992480354 | 0.981566473 | 1.3693085 |
| 1 | Sheet3 | CV_T_kurtosis | 392 | 392 | 0 | 0 | 0.015643507 | 0.0193774864 | 0.996652354 | 0.988659387 | 0.760876948 |
| 1 | Sheet3 | CV_CVCT | 392 | 392 | 0 | 0 | 0.116604714 | 0.139375031 | 0.999810791 | 0.997397977 | 0.42020559 |
| 1 | Sheet3 | CV_entropy | 392 | 392 | 0 | 0 | 4.71250554 | 4.71270303 | 0.935049917 | 0.945214319 | 71.6690692 |
| 1 | Sheet3 | dI_energy | 392 | 392 | 0 | 0 | 0.000925118492 | 0.00106178266 | 0.993080601 | 0.968202216 | 2.12223492 |
| 1 | Sheet3 | dI_Q | 392 | 392 | 0 | 0 | 0.000220265825 | 0.000252804356 | 0.993080249 | 0.968188419 | 2.12222702 |
| 1 | Sheet3 | dI_t_mean | 392 | 392 | 0 | 0 | 0.0069501627 | 0.00797906284 | 0.993091351 | 0.968986922 | 2.1165018 |
| 1 | Sheet3 | dI_C_mean | 392 | 392 | 0 | 0 | 0.000489275201 | 0.000610833974 | 0.438288011 | 0.411418848 | 0.0515980963 |
| 1 | Sheet3 | dI_T_mean | 392 | 392 | 0 | 0 | 0.015306257 | 0.0185291997 | 0.999961104 | 0.999712231 | 0.0554935889 |
| 1 | Sheet3 | dI_C_std | 392 | 392 | 0 | 0 | 0.000283975656 | 0.000345351411 | 0.111258049 | 0.102491445 | 0.980644094 |
| 1 | Sheet3 | dI_T_std | 392 | 392 | 0 | 0 | 0.0136810007 | 0.017317647 | 0.799900629 | 0.806588637 | 14.3242505 |
| 1 | Sheet3 | dI_C_skewness | 392 | 392 | 0 | 0 | 0.00851750672 | 0.0109485732 | 0.763731082 | 0.712064881 | 12.0337242 |
| 1 | Sheet3 | dI_T_skewness | 392 | 392 | 0 | 0 | 0.271796373 | 0.353242244 | 0.576658727 | 0.540497779 | 88.0914896 |
| 1 | Sheet3 | dI_C_kurtosis | 392 | 392 | 0 | 0 | 0.0159968982 | 0.0186977075 | 0.058951004 | 0.0652506605 | 0.886002305 |
| 1 | Sheet3 | dI_T_kurtosis | 392 | 392 | 0 | 0 | 0.394330329 | 0.592389276 | 0.250457205 | 0.291714674 | 18.5535019 |
| 1 | Sheet3 | dI_dI_devide_dt | 392 | 392 | 0 | 0 | 0.000948823363 | 0.00127772765 | 0.996929274 | 0.988358615 | 0.630579533 |
| 1 | Sheet3 | dI_entropy | 392 | 392 | 0 | 0 | 2.52819268 | 2.53357523 | -0.455146017 | -0.320464764 | 47.7184745 |
| 1 | Sheet3 | Charge_energy | 392 | 392 | 0 | 0 | 0.000938279385 | 0.00105965295 | 0.999998378 | 0.999973703 | 0.0128403791 |
| 1 | Sheet3 | Charge_Q | 392 | 392 | 0 | 0 | 0.000132404329 | 0.000158934396 | 0.999998918 | 0.999985258 | 0.00712510858 |
| 1 | Sheet3 | Charge_t_mean | 392 | 392 | 0 | 0 | 0.0201242607 | 0.290113129 | 0.959782157 | 0.991294166 | 0.0793845296 |
| 1 | Sheet3 | Charge_V_mean | 392 | 392 | 0 | 0 | 0.00101234207 | 0.00102094743 | 0.999989448 | 0.999919516 | 0.0249859862 |
| 1 | Sheet3 | Charge_C_mean | 392 | 392 | 0 | 0 | 0.000835951181 | 0.00125818649 | 0.999986133 | 0.999928481 | 0.0378556708 |
| 1 | Sheet3 | Charge_T_mean | 392 | 392 | 0 | 0 | 0.00696247185 | 0.00751999106 | 0.99999922 | 0.999981274 | 0.0260419168 |
| 1 | Sheet3 | Charge_C_std | 392 | 392 | 0 | 0 | 0.00070380042 | 0.00278474019 | 0.952522734 | 0.999160301 | 0.0405807301 |
| 1 | Sheet3 | Charge_V_std | 392 | 392 | 0 | 0 | 0.00194493391 | 0.00197025293 | 0.999876142 | 0.997995481 | 1.02761085 |
| 1 | Sheet3 | Charge_T_std | 392 | 392 | 0 | 0 | 0.00190698408 | 0.00240320109 | 0.999972714 | 0.999867521 | 0.0902772667 |
| 1 | Sheet3 | Charge_C_skewness | 392 | 392 | 0 | 0 | 0.000833114353 | 0.00138984822 | 0.999986849 | 0.999944817 | 0.400432093 |
| 1 | Sheet3 | Charge_V_skewness | 392 | 392 | 0 | 0 | 0.0316020754 | 0.0326160458 | 0.999692432 | 0.997385878 | 3.86105241 |
| 1 | Sheet3 | Charge_T_skewness | 392 | 392 | 0 | 0 | 0.00350596485 | 0.00429612326 | 0.999668836 | 0.998244502 | 2.08126254 |
| 1 | Sheet3 | Charge_C_kurtosis | 392 | 392 | 0 | 0 | 0.000633427774 | 0.000994562441 | 0.99969672 | 0.999882661 | 0.0541439849 |
| 1 | Sheet3 | Charge_V_kurtosis | 392 | 392 | 0 | 0 | 0.139081924 | 0.148117654 | 0.99894942 | 0.998346899 | 6.43971238 |
| 1 | Sheet3 | Charge_T_kurtosis | 392 | 392 | 0 | 0 | 0.00261809582 | 0.00327849194 | 0.999366319 | 0.9977618 | 0.158484487 |
| 1 | Sheet4 | CC_energy | 395 | 395 | 0 | 0 | 0.0569252796 | 0.0664108598 | 0.997467819 | 0.981257801 | 0.960647499 |
| 1 | Sheet4 | CC_Q | 395 | 395 | 0 | 0 | 0.0133960194 | 0.0156800385 | 0.998068289 | 0.984011223 | 0.875947437 |
| 1 | Sheet4 | CC_t_mean | 395 | 395 | 0 | 0 | 0.100332083 | 0.117554436 | 0.998059261 | 0.984039303 | 0.874770296 |
| 1 | Sheet4 | CC_V_mean | 395 | 395 | 0 | 0 | 0.00349460317 | 0.00390547504 | 0.996532453 | 0.958638106 | 0.0901482669 |
| 1 | Sheet4 | CC_T_mean | 395 | 395 | 0 | 0 | 0.0155289999 | 0.0183782596 | 0.999984926 | 0.999904981 | 0.0554101981 |
| 1 | Sheet4 | CC_V_std | 395 | 395 | 0 | 0 | 0.00134645148 | 0.0015557184 | 0.975384576 | 0.953292872 | 0.898401638 |
| 1 | Sheet4 | CC_T_std | 395 | 395 | 0 | 0 | 0.00616860373 | 0.023173317 | 0.958449988 | 0.996372856 | 0.49605238 |
| 1 | Sheet4 | CC_V_skewness | 395 | 395 | 0 | 0 | 0.0856092957 | 0.0884984492 | 0.985667427 | 0.971837634 | 24.9824812 |
| 1 | Sheet4 | CC_T_skewness | 395 | 395 | 0 | 0 | 0.0104944245 | 0.016255888 | 0.978414778 | 0.989965175 | 2.77297966 |
| 1 | Sheet4 | CC_V_kurtosis | 395 | 395 | 0 | 0 | 0.141948272 | 0.149442095 | 0.889340868 | 0.880946456 | 5.85363964 |
| 1 | Sheet4 | CC_T_kurtosis | 395 | 395 | 0 | 0 | 0.0139145363 | 0.0255543575 | 0.914943014 | 0.970754693 | 0.727496738 |
| 1 | Sheet4 | CC_CCCT | 395 | 395 | 0 | 0 | 0.200899272 | 0.235157649 | 0.998067131 | 0.984047559 | 0.87578704 |
| 1 | Sheet4 | CC_entropy | 395 | 395 | 0 | 0 | 5.06096759 | 5.0610227 | 0.814184656 | 0.857407598 | 66.7970767 |
| 1 | Sheet4 | dV_energy | 395 | 395 | 0 | 0 | 0.00604904089 | 0.00668328222 | 0.997819425 | 0.982636556 | 0.653682856 |
| 1 | Sheet4 | dV_Q | 395 | 395 | 0 | 0 | 0.00153492219 | 0.00169640883 | 0.997807986 | 0.983069596 | 0.654575294 |
| 1 | Sheet4 | dV_t_mean | 395 | 395 | 0 | 0 | 0.0119519906 | 0.0134722525 | 0.996994233 | 0.981041865 | 0.679461173 |
| 1 | Sheet4 | dV_V_mean | 395 | 395 | 0 | 0 | 0.000135855025 | 0.000184206602 | 0.90974174 | 0.89718057 | 0.00344252632 |
| 1 | Sheet4 | dV_T_mean | 395 | 395 | 0 | 0 | 0.00669609537 | 0.00841176495 | 0.999991336 | 0.99991126 | 0.0231325019 |
| 1 | Sheet4 | dV_V_std | 395 | 395 | 0 | 0 | 0.000157807843 | 0.000180986453 | 0.522958252 | 0.551369896 | 0.546874231 |
| 1 | Sheet4 | dV_T_std | 395 | 395 | 0 | 0 | 0.00707235705 | 0.00878281355 | 0.987761179 | 0.985535039 | 4.31192225 |
| 1 | Sheet4 | dV_V_skewness | 395 | 395 | 0 | 0 | 0.00285208998 | 0.00471510311 | 0.966144231 | 0.960170295 | 1.86341448 |
| 1 | Sheet4 | dV_T_skewness | 395 | 395 | 0 | 0 | 0.117227309 | 0.203710316 | 0.850835356 | 0.896341361 | 44.5058928 |
| 1 | Sheet4 | dV_V_kurtosis | 395 | 395 | 0 | 0 | 0.00329836907 | 0.00562331797 | 0.876303778 | 0.886685593 | 0.18118226 |
| 1 | Sheet4 | dV_T_kurtosis | 395 | 395 | 0 | 0 | 0.193575935 | 0.362160395 | 0.660199845 | 0.828400694 | 9.53132764 |
| 1 | Sheet4 | dV_dV_devide_dt | 395 | 395 | 0 | 0 | 9.21189776e-05 | 0.000163028091 | 0.997620298 | 0.988899933 | 0.324841263 |
| 1 | Sheet4 | dV_entropy | 395 | 395 | 0 | 0 | 4.70949666 | 4.71212216 | 0.687323096 | 0.415165659 | 63.0176193 |
| 1 | Sheet4 | CV_energy | 395 | 395 | 0 | 0 | 0.0318552799 | 0.0383432298 | 0.985915146 | 0.97336437 | 2.26112597 |
| 1 | Sheet4 | CV_Q | 395 | 395 | 0 | 0 | 0.00758428586 | 0.00912890873 | 0.985917504 | 0.973357556 | 2.26101384 |
| 1 | Sheet4 | CV_t_mean | 395 | 395 | 0 | 0 | 0.0635758877 | 0.0755522554 | 0.999832312 | 0.997074452 | 0.443310284 |
| 1 | Sheet4 | CV_C_mean | 395 | 395 | 0 | 0 | 0.0102740661 | 0.0122410007 | 0.97799736 | 0.957348139 | 1.4499282 |
| 1 | Sheet4 | CV_T_mean | 395 | 395 | 0 | 0 | 0.0154635326 | 0.0185868376 | 0.999986367 | 0.999880836 | 0.060783492 |
| 1 | Sheet4 | CV_C_std | 395 | 395 | 0 | 0 | 0.01891824 | 0.0223890555 | 0.833715124 | 0.815645889 | 2.30901792 |
| 1 | Sheet4 | CV_T_std | 395 | 395 | 0 | 0 | 0.0108887213 | 0.013262608 | 0.998846642 | 0.996985858 | 0.512342833 |
| 1 | Sheet4 | CV_C_skewness | 395 | 395 | 0 | 0 | 0.0188201153 | 0.0220921351 | 0.99460406 | 0.990038144 | 0.944593546 |
| 1 | Sheet4 | CV_T_skewness | 395 | 395 | 0 | 0 | 0.00743516591 | 0.0090334236 | 0.998526365 | 0.991074596 | 1.01110317 |
| 1 | Sheet4 | CV_C_kurtosis | 395 | 395 | 0 | 0 | 0.0908919622 | 0.106247101 | 0.994607506 | 0.989970579 | 1.39043656 |
| 1 | Sheet4 | CV_T_kurtosis | 395 | 395 | 0 | 0 | 0.0173733713 | 0.0212456575 | 0.997126175 | 0.984014533 | 0.798639617 |
| 1 | Sheet4 | CV_CVCT | 395 | 395 | 0 | 0 | 0.119616402 | 0.143828715 | 0.999834849 | 0.997109401 | 0.417159655 |
| 1 | Sheet4 | CV_entropy | 395 | 395 | 0 | 0 | 4.7077486 | 4.70791244 | 0.987046787 | 0.971833354 | 71.8139214 |
| 1 | Sheet4 | dI_energy | 395 | 395 | 0 | 0 | 0.000989567373 | 0.00113921978 | 0.987417057 | 0.972321497 | 2.2130363 |
| 1 | Sheet4 | dI_Q | 395 | 395 | 0 | 0 | 0.000235602251 | 0.000271236555 | 0.987419092 | 0.972356351 | 2.21292989 |
| 1 | Sheet4 | dI_t_mean | 395 | 395 | 0 | 0 | 0.00741252737 | 0.00854874198 | 0.987727434 | 0.972990242 | 2.20030103 |
| 1 | Sheet4 | dI_C_mean | 395 | 395 | 0 | 0 | 0.000479152505 | 0.000584023005 | 0.660951405 | 0.644915353 | 0.0505357929 |
| 1 | Sheet4 | dI_T_mean | 395 | 395 | 0 | 0 | 0.0148311742 | 0.0184488545 | 0.999959202 | 0.999775789 | 0.0541320553 |
| 1 | Sheet4 | dI_C_std | 395 | 395 | 0 | 0 | 0.000269826677 | 0.000342904059 | -0.00186163784 | 0.017354293 | 0.933748378 |
| 1 | Sheet4 | dI_T_std | 395 | 395 | 0 | 0 | 0.0128582003 | 0.01589714 | 0.716677884 | 0.688006519 | 12.7616346 |
| 1 | Sheet4 | dI_C_skewness | 395 | 395 | 0 | 0 | 0.00916045477 | 0.0122432439 | 0.875997965 | 0.840294093 | 11.6255737 |
| 1 | Sheet4 | dI_T_skewness | 395 | 395 | 0 | 0 | 0.248671573 | 0.312771595 | 0.442444501 | 0.438655397 | 94.1705571 |
| 1 | Sheet4 | dI_C_kurtosis | 395 | 395 | 0 | 0 | 0.0168103895 | 0.0202661748 | 0.0279343363 | 0.0311469122 | 0.930476029 |
| 1 | Sheet4 | dI_T_kurtosis | 395 | 395 | 0 | 0 | 0.3066942 | 0.404715678 | 0.330142982 | 0.25687185 | 14.6937202 |
| 1 | Sheet4 | dI_dI_devide_dt | 395 | 395 | 0 | 0 | 0.00132419053 | 0.00261111578 | 0.988259853 | 0.992254794 | 0.906501456 |
| 1 | Sheet4 | dI_entropy | 395 | 395 | 0 | 0 | 2.56620886 | 2.56990536 | -0.343809618 | -0.408519655 | 48.0965842 |
| 1 | Sheet4 | Charge_energy | 395 | 395 | 0 | 0 | 0.000942701162 | 0.00109041545 | 0.999997924 | 0.999958916 | 0.0128445433 |
| 1 | Sheet4 | Charge_Q | 395 | 395 | 0 | 0 | 0.000143408194 | 0.000167444576 | 0.999998701 | 0.999967288 | 0.00768577622 |
| 1 | Sheet4 | Charge_t_mean | 395 | 395 | 0 | 0 | 0.0053527468 | 0.00822199784 | 0.99998392 | 0.999808257 | 0.0207313936 |
| 1 | Sheet4 | Charge_V_mean | 395 | 395 | 0 | 0 | 0.00106397657 | 0.00107267746 | 0.999991136 | 0.999874021 | 0.0262441435 |
| 1 | Sheet4 | Charge_C_mean | 395 | 395 | 0 | 0 | 0.000783502639 | 0.00104701848 | 0.999993279 | 0.999936329 | 0.0359756478 |
| 1 | Sheet4 | Charge_T_mean | 395 | 395 | 0 | 0 | 0.00648327371 | 0.00695792922 | 0.999999405 | 0.99998637 | 0.024403165 |
| 1 | Sheet4 | Charge_C_std | 395 | 395 | 0 | 0 | 0.000617081016 | 0.00104881708 | 0.996138051 | 0.999375705 | 0.0355690658 |
| 1 | Sheet4 | Charge_V_std | 395 | 395 | 0 | 0 | 0.00208389939 | 0.00211760608 | 0.999858518 | 0.998320414 | 1.10401406 |
| 1 | Sheet4 | Charge_T_std | 395 | 395 | 0 | 0 | 0.00198988297 | 0.00250070592 | 0.999971047 | 0.999843257 | 0.0903855334 |
| 1 | Sheet4 | Charge_C_skewness | 395 | 395 | 0 | 0 | 0.000922995203 | 0.00139292606 | 0.999993612 | 0.999954827 | 0.444584877 |
| 1 | Sheet4 | Charge_V_skewness | 395 | 395 | 0 | 0 | 0.0352356171 | 0.0366913351 | 0.999666656 | 0.996872341 | 4.09905793 |
| 1 | Sheet4 | Charge_T_skewness | 395 | 395 | 0 | 0 | 0.00313404919 | 0.0038092665 | 0.999810287 | 0.998962185 | 1.82916209 |
| 1 | Sheet4 | Charge_C_kurtosis | 395 | 395 | 0 | 0 | 0.000771173402 | 0.00150795898 | 0.999580949 | 0.999566376 | 0.065882982 |
| 1 | Sheet4 | Charge_V_kurtosis | 395 | 395 | 0 | 0 | 0.161875706 | 0.175635449 | 0.999056964 | 0.998744692 | 7.16482559 |
| 1 | Sheet4 | Charge_T_kurtosis | 395 | 395 | 0 | 0 | 0.0024588855 | 0.00312777404 | 0.99945402 | 0.997856026 | 0.150983967 |
| 1 | Sheet5 | CC_energy | 402 | 402 | 0 | 0 | 0.0578556602 | 0.0667267884 | 0.997859509 | 0.984551048 | 0.979143025 |
| 1 | Sheet5 | CC_Q | 402 | 402 | 0 | 0 | 0.0136154019 | 0.0157516419 | 0.998364257 | 0.987085127 | 0.892951097 |
| 1 | Sheet5 | CC_t_mean | 402 | 402 | 0 | 0 | 0.10191657 | 0.118055877 | 0.998350294 | 0.987192211 | 0.891254799 |
| 1 | Sheet5 | CC_V_mean | 402 | 402 | 0 | 0 | 0.00353948954 | 0.00392849048 | 0.996881969 | 0.976315646 | 0.0912914132 |
| 1 | Sheet5 | CC_T_mean | 402 | 402 | 0 | 0 | 0.0121240176 | 0.014455655 | 0.999991815 | 0.999943477 | 0.0456299312 |
| 1 | Sheet5 | CC_V_std | 402 | 402 | 0 | 0 | 0.00126528431 | 0.00147531375 | 0.981081826 | 0.931685914 | 0.851032375 |
| 1 | Sheet5 | CC_T_std | 402 | 402 | 0 | 0 | 0.00504873523 | 0.0191005446 | 0.917683146 | 0.990144864 | 0.524403764 |
| 1 | Sheet5 | CC_V_skewness | 402 | 402 | 0 | 0 | 0.0854166561 | 0.0877750377 | 0.979828375 | 0.963722411 | 23.6910864 |
| 1 | Sheet5 | CC_T_skewness | 402 | 402 | 0 | 0 | 0.0124546932 | 0.0213335726 | 0.963578635 | 0.984010183 | 3.05501729 |
| 1 | Sheet5 | CC_V_kurtosis | 402 | 402 | 0 | 0 | 0.13657718 | 0.144312512 | 0.849519797 | 0.887093998 | 5.64135919 |
| 1 | Sheet5 | CC_T_kurtosis | 402 | 402 | 0 | 0 | 0.0170726891 | 0.0297196124 | 0.942389233 | 0.981283963 | 0.880599501 |
| 1 | Sheet5 | CC_CCCT | 402 | 402 | 0 | 0 | 0.204190171 | 0.236236792 | 0.998364293 | 0.987030232 | 0.89279793 |
| 1 | Sheet5 | CC_entropy | 402 | 402 | 0 | 0 | 5.0664331 | 5.06646434 | 0.890430925 | 0.880410404 | 66.803239 |
| 1 | Sheet5 | dV_energy | 402 | 402 | 0 | 0 | 0.00481883117 | 0.00559356861 | 0.998089527 | 0.984234813 | 0.518637978 |
| 1 | Sheet5 | dV_Q | 402 | 402 | 0 | 0 | 0.00122015153 | 0.00141695565 | 0.998089623 | 0.984589053 | 0.518222748 |
| 1 | Sheet5 | dV_t_mean | 402 | 402 | 0 | 0 | 0.00929885258 | 0.0109396895 | 0.997747941 | 0.983663114 | 0.526448092 |
| 1 | Sheet5 | dV_V_mean | 402 | 402 | 0 | 0 | 0.000127868078 | 0.000183606202 | 0.926355146 | 0.901861296 | 0.00324022719 |
| 1 | Sheet5 | dV_T_mean | 402 | 402 | 0 | 0 | 0.0060572898 | 0.00759102771 | 0.999993659 | 0.999939044 | 0.0222015929 |
| 1 | Sheet5 | dV_V_std | 402 | 402 | 0 | 0 | 0.000121658994 | 0.000146606495 | 0.555440234 | 0.554335339 | 0.421018392 |
| 1 | Sheet5 | dV_T_std | 402 | 402 | 0 | 0 | 0.00648007367 | 0.00918165586 | 0.978097836 | 0.978107212 | 5.26650757 |
| 1 | Sheet5 | dV_V_skewness | 402 | 402 | 0 | 0 | 0.00315395971 | 0.00519120699 | 0.965979097 | 0.952598227 | 2.02205939 |
| 1 | Sheet5 | dV_T_skewness | 402 | 402 | 0 | 0 | 0.150943272 | 0.237424881 | 0.853398595 | 0.877357272 | 46.3120413 |
| 1 | Sheet5 | dV_V_kurtosis | 402 | 402 | 0 | 0 | 0.00335824106 | 0.00569337744 | 0.890450266 | 0.896645557 | 0.184346216 |
| 1 | Sheet5 | dV_T_kurtosis | 402 | 402 | 0 | 0 | 0.267945062 | 0.461304568 | 0.658972539 | 0.765591022 | 12.513202 |
| 1 | Sheet5 | dV_dV_devide_dt | 402 | 402 | 0 | 0 | 7.55620247e-05 | 0.000137634108 | 0.998398485 | 0.991451198 | 0.267227588 |
| 1 | Sheet5 | dV_entropy | 402 | 402 | 0 | 0 | 4.71904062 | 4.72142647 | 0.678264878 | 0.411101894 | 63.0673225 |
| 1 | Sheet5 | CV_energy | 402 | 402 | 0 | 0 | 0.0345401279 | 0.0410542329 | 0.985123359 | 0.969006782 | 2.43174058 |
| 1 | Sheet5 | CV_Q | 402 | 402 | 0 | 0 | 0.00822403941 | 0.00977502156 | 0.985123387 | 0.969025254 | 2.43168013 |
| 1 | Sheet5 | CV_t_mean | 402 | 402 | 0 | 0 | 0.0690564229 | 0.0810446174 | 0.999823149 | 0.997062084 | 0.47639924 |
| 1 | Sheet5 | CV_C_mean | 402 | 402 | 0 | 0 | 0.0110729547 | 0.0132406988 | 0.975502359 | 0.95860133 | 1.56624701 |
| 1 | Sheet5 | CV_T_mean | 402 | 402 | 0 | 0 | 0.0124242231 | 0.0150147882 | 0.999991349 | 0.999913737 | 0.0504731048 |
| 1 | Sheet5 | CV_C_std | 402 | 402 | 0 | 0 | 0.0201783323 | 0.0240520356 | 0.816594349 | 0.806372 | 2.45937557 |
| 1 | Sheet5 | CV_T_std | 402 | 402 | 0 | 0 | 0.00914571453 | 0.0127292675 | 0.997354668 | 0.994091287 | 0.564400275 |
| 1 | Sheet5 | CV_C_skewness | 402 | 402 | 0 | 0 | 0.0195780877 | 0.0231309835 | 0.994099064 | 0.9873713 | 0.985539895 |
| 1 | Sheet5 | CV_T_skewness | 402 | 402 | 0 | 0 | 0.00862266609 | 0.0106243221 | 0.998110258 | 0.991900734 | 1.1292433 |
| 1 | Sheet5 | CV_C_kurtosis | 402 | 402 | 0 | 0 | 0.0943419841 | 0.110812036 | 0.994080784 | 0.98748176 | 1.45252257 |
| 1 | Sheet5 | CV_T_kurtosis | 402 | 402 | 0 | 0 | 0.0193754298 | 0.0242369692 | 0.996421801 | 0.985917396 | 0.882444084 |
| 1 | Sheet5 | CV_CVCT | 402 | 402 | 0 | 0 | 0.130091094 | 0.154510516 | 0.999823233 | 0.997057741 | 0.44886801 |
| 1 | Sheet5 | CV_entropy | 402 | 402 | 0 | 0 | 4.70410317 | 4.70426503 | 0.986298114 | 0.964036028 | 71.829163 |
| 1 | Sheet5 | dI_energy | 402 | 402 | 0 | 0 | 0.00102082579 | 0.00114241622 | 0.990929963 | 0.975195525 | 2.26673467 |
| 1 | Sheet5 | dI_Q | 402 | 402 | 0 | 0 | 0.000243059643 | 0.00027199933 | 0.990933138 | 0.975149161 | 2.26667523 |
| 1 | Sheet5 | dI_t_mean | 402 | 402 | 0 | 0 | 0.0077381812 | 0.00865255176 | 0.990829436 | 0.975663727 | 2.28107025 |
| 1 | Sheet5 | dI_C_mean | 402 | 402 | 0 | 0 | 0.000458891447 | 0.000570883513 | 0.638697748 | 0.617020309 | 0.0483897544 |
| 1 | Sheet5 | dI_T_mean | 402 | 402 | 0 | 0 | 0.015358574 | 0.0190327949 | 0.999959026 | 0.999768042 | 0.0588262303 |
| 1 | Sheet5 | dI_C_std | 402 | 402 | 0 | 0 | 0.000258756056 | 0.000314075944 | 0.076307903 | 0.0420554296 | 0.895309298 |
| 1 | Sheet5 | dI_T_std | 402 | 402 | 0 | 0 | 0.0115552158 | 0.0144050372 | 0.728123043 | 0.704560228 | 13.9751594 |
| 1 | Sheet5 | dI_C_skewness | 402 | 402 | 0 | 0 | 0.00748405864 | 0.00972437177 | 0.894999395 | 0.876215723 | 9.99081647 |
| 1 | Sheet5 | dI_T_skewness | 402 | 402 | 0 | 0 | 0.262244608 | 0.338663008 | 0.505762887 | 0.553344175 | 93.8168705 |
| 1 | Sheet5 | dI_C_kurtosis | 402 | 402 | 0 | 0 | 0.0153816224 | 0.0184303962 | 0.0860066708 | 0.070416437 | 0.851626691 |
| 1 | Sheet5 | dI_T_kurtosis | 402 | 402 | 0 | 0 | 0.396963761 | 0.541678291 | 0.200405729 | 0.262876387 | 18.4871285 |
| 1 | Sheet5 | dI_dI_devide_dt | 402 | 402 | 0 | 0 | 0.000987333795 | 0.0016162538 | 0.993119 | 0.993544866 | 0.680871983 |
| 1 | Sheet5 | dI_entropy | 402 | 402 | 0 | 0 | 2.57611089 | 2.57982745 | -0.305182632 | -0.347545178 | 48.1896619 |
| 1 | Sheet5 | Charge_energy | 402 | 402 | 0 | 0 | 0.000962346847 | 0.0010963686 | 0.999998247 | 0.999967675 | 0.0131217823 |
| 1 | Sheet5 | Charge_Q | 402 | 402 | 0 | 0 | 0.000140855878 | 0.000165526397 | 0.999998851 | 0.999974324 | 0.00755622053 |
| 1 | Sheet5 | Charge_t_mean | 402 | 402 | 0 | 0 | 0.00594233501 | 0.0106508114 | 0.999968532 | 0.99981182 | 0.0229086868 |
| 1 | Sheet5 | Charge_V_mean | 402 | 402 | 0 | 0 | 0.00105044301 | 0.00105884144 | 0.999990548 | 0.999912814 | 0.0259027749 |
| 1 | Sheet5 | Charge_C_mean | 402 | 402 | 0 | 0 | 0.000831507481 | 0.00136796265 | 0.99998588 | 0.999930916 | 0.0383884749 |
| 1 | Sheet5 | Charge_T_mean | 402 | 402 | 0 | 0 | 0.00497134218 | 0.00552056215 | 0.999999396 | 0.999981713 | 0.0195249674 |
| 1 | Sheet5 | Charge_C_std | 402 | 402 | 0 | 0 | 0.000555477198 | 0.000599827118 | 0.999735987 | 0.999286994 | 0.0320199552 |
| 1 | Sheet5 | Charge_V_std | 402 | 402 | 0 | 0 | 0.00204948854 | 0.00207365297 | 0.999915905 | 0.998333303 | 1.09199592 |
| 1 | Sheet5 | Charge_T_std | 402 | 402 | 0 | 0 | 0.00177600532 | 0.00221078445 | 0.999949153 | 0.999447143 | 0.105811807 |
| 1 | Sheet5 | Charge_C_skewness | 402 | 402 | 0 | 0 | 0.000991255127 | 0.00169947362 | 0.99998581 | 0.999946986 | 0.46714746 |
| 1 | Sheet5 | Charge_V_skewness | 402 | 402 | 0 | 0 | 0.0342143649 | 0.0353000651 | 0.999758575 | 0.997305355 | 3.95915058 |
| 1 | Sheet5 | Charge_T_skewness | 402 | 402 | 0 | 0 | 0.00371928926 | 0.00463855005 | 0.999671384 | 0.998893363 | 2.4672332 |
| 1 | Sheet5 | Charge_C_kurtosis | 402 | 402 | 0 | 0 | 0.0007634075 | 0.00132762094 | 0.99976459 | 0.999791963 | 0.0650294277 |
| 1 | Sheet5 | Charge_V_kurtosis | 402 | 402 | 0 | 0 | 0.156193507 | 0.167263297 | 0.999246848 | 0.999433105 | 6.91746155 |
| 1 | Sheet5 | Charge_T_kurtosis | 402 | 402 | 0 | 0 | 0.00292778206 | 0.00370743253 | 0.999081833 | 0.997320871 | 0.182951999 |
| 1 | Sheet6 | CC_energy | 407 | 407 | 0 | 0 | 0.0533688148 | 0.0616180594 | 0.998148926 | 0.984203204 | 0.902143433 |
| 1 | Sheet6 | CC_Q | 407 | 407 | 0 | 0 | 0.012561516 | 0.0145484958 | 0.998584926 | 0.986681032 | 0.822753228 |
| 1 | Sheet6 | CC_t_mean | 407 | 407 | 0 | 0 | 0.0938242717 | 0.1088193 | 0.9985784 | 0.986693085 | 0.819424751 |
| 1 | Sheet6 | CC_V_mean | 407 | 407 | 0 | 0 | 0.00319380375 | 0.00355889005 | 0.997235358 | 0.971272081 | 0.0823874405 |
| 1 | Sheet6 | CC_T_mean | 407 | 407 | 0 | 0 | 0.0116097029 | 0.0137408813 | 0.999992461 | 0.999946958 | 0.0430525451 |
| 1 | Sheet6 | CC_V_std | 407 | 407 | 0 | 0 | 0.00118401424 | 0.00138755291 | 0.980736877 | 0.923143561 | 0.807125494 |
| 1 | Sheet6 | CC_T_std | 407 | 407 | 0 | 0 | 0.00497684776 | 0.0145660383 | 0.973974604 | 0.995292065 | 0.507318684 |
| 1 | Sheet6 | CC_V_skewness | 407 | 407 | 0 | 0 | 0.0675040806 | 0.069506123 | 0.984929895 | 0.981483308 | 15.6026207 |
| 1 | Sheet6 | CC_T_skewness | 407 | 407 | 0 | 0 | 0.0129385707 | 0.0304719404 | 0.936742669 | 0.986711957 | 3.18481811 |
| 1 | Sheet6 | CC_V_kurtosis | 407 | 407 | 0 | 0 | 0.0894500847 | 0.0937328742 | 0.897289386 | 0.926224069 | 3.76954915 |
| 1 | Sheet6 | CC_T_kurtosis | 407 | 407 | 0 | 0 | 0.0194778458 | 0.0480445575 | 0.876030073 | 0.976300222 | 0.999701799 |
| 1 | Sheet6 | CC_CCCT | 407 | 407 | 0 | 0 | 0.188383505 | 0.218190621 | 0.998585059 | 0.986691635 | 0.822605827 |
| 1 | Sheet6 | CC_entropy | 407 | 407 | 0 | 0 | 5.08366058 | 5.08369202 | 0.90196979 | 0.915782965 | 66.5966609 |
| 1 | Sheet6 | dV_energy | 407 | 407 | 0 | 0 | 0.00618232989 | 0.00675122067 | 0.997890322 | 0.981924906 | 0.675209568 |
| 1 | Sheet6 | dV_Q | 407 | 407 | 0 | 0 | 0.00156855195 | 0.00171319109 | 0.997885378 | 0.982193095 | 0.676046319 |
| 1 | Sheet6 | dV_t_mean | 407 | 407 | 0 | 0 | 0.0119723927 | 0.013292646 | 0.997434711 | 0.981192688 | 0.688008744 |
| 1 | Sheet6 | dV_V_mean | 407 | 407 | 0 | 0 | 0.000122630867 | 0.00017840873 | 0.931753674 | 0.915748209 | 0.00310744508 |
| 1 | Sheet6 | dV_T_mean | 407 | 407 | 0 | 0 | 0.00724969593 | 0.00907801089 | 0.999990737 | 0.999939082 | 0.0261646631 |
| 1 | Sheet6 | dV_V_std | 407 | 407 | 0 | 0 | 0.000157537188 | 0.000175280618 | 0.528264189 | 0.537631438 | 0.545858975 |
| 1 | Sheet6 | dV_T_std | 407 | 407 | 0 | 0 | 0.00803082096 | 0.0108798659 | 0.982824742 | 0.986690821 | 6.01201192 |
| 1 | Sheet6 | dV_V_skewness | 407 | 407 | 0 | 0 | 0.00274726503 | 0.00459156535 | 0.9744328 | 0.949397034 | 1.78033043 |
| 1 | Sheet6 | dV_T_skewness | 407 | 407 | 0 | 0 | 0.184714192 | 0.301211853 | 0.856004208 | 0.894437534 | 46.9901044 |
| 1 | Sheet6 | dV_V_kurtosis | 407 | 407 | 0 | 0 | 0.00336516559 | 0.00551960286 | 0.884298012 | 0.89338044 | 0.18485044 |
| 1 | Sheet6 | dV_T_kurtosis | 407 | 407 | 0 | 0 | 0.335125279 | 0.577177614 | 0.726612989 | 0.857848418 | 14.5650374 |
| 1 | Sheet6 | dV_dV_devide_dt | 407 | 407 | 0 | 0 | 7.3287971e-05 | 0.000132539998 | 0.998221721 | 0.989427364 | 0.255899273 |
| 1 | Sheet6 | dV_entropy | 407 | 407 | 0 | 0 | 4.70887021 | 4.71135571 | 0.628899816 | 0.338086486 | 63.0154226 |
| 1 | Sheet6 | CV_energy | 407 | 407 | 0 | 0 | 0.0374919496 | 0.0427925376 | 0.988654832 | 0.973880733 | 2.63693075 |
| 1 | Sheet6 | CV_Q | 407 | 407 | 0 | 0 | 0.0089267627 | 0.0101887624 | 0.988654402 | 0.97389426 | 2.63685506 |
| 1 | Sheet6 | CV_t_mean | 407 | 407 | 0 | 0 | 0.0744051238 | 0.0839639434 | 0.999853658 | 0.998633021 | 0.522625946 |
| 1 | Sheet6 | CV_C_mean | 407 | 407 | 0 | 0 | 0.0123094301 | 0.0143237858 | 0.977672973 | 0.937348751 | 1.70751725 |
| 1 | Sheet6 | CV_T_mean | 407 | 407 | 0 | 0 | 0.0147907152 | 0.0172259819 | 0.99999101 | 0.999883593 | 0.0595471851 |
| 1 | Sheet6 | CV_C_std | 407 | 407 | 0 | 0 | 0.0218497877 | 0.0252893976 | 0.826233764 | 0.790649828 | 2.63032646 |
| 1 | Sheet6 | CV_T_std | 407 | 407 | 0 | 0 | 0.0103621739 | 0.0126933783 | 0.998264892 | 0.998091213 | 0.607143784 |
| 1 | Sheet6 | CV_C_skewness | 407 | 407 | 0 | 0 | 0.0212421371 | 0.0243991945 | 0.994622707 | 0.981804405 | 1.09904909 |
| 1 | Sheet6 | CV_T_skewness | 407 | 407 | 0 | 0 | 0.0091585318 | 0.0110105558 | 0.998524978 | 0.995694372 | 1.21174339 |
| 1 | Sheet6 | CV_C_kurtosis | 407 | 407 | 0 | 0 | 0.102311007 | 0.11662089 | 0.994547893 | 0.981968336 | 1.63944287 |
| 1 | Sheet6 | CV_T_kurtosis | 407 | 407 | 0 | 0 | 0.0205872524 | 0.0250837261 | 0.997206032 | 0.993224554 | 0.934600485 |
| 1 | Sheet6 | CV_CVCT | 407 | 407 | 0 | 0 | 0.141151973 | 0.160768168 | 0.999856229 | 0.998656603 | 0.495865488 |
| 1 | Sheet6 | CV_entropy | 407 | 407 | 0 | 0 | 4.7123573 | 4.71250904 | 0.986660403 | 0.956635209 | 71.6231449 |
| 1 | Sheet6 | dI_energy | 407 | 407 | 0 | 0 | 0.000839747956 | 0.0009597426 | 0.996333913 | 0.976191959 | 1.83180511 |
| 1 | Sheet6 | dI_Q | 407 | 407 | 0 | 0 | 0.000199942785 | 0.000228509028 | 0.996333686 | 0.976122899 | 1.83175481 |
| 1 | Sheet6 | dI_t_mean | 407 | 407 | 0 | 0 | 0.00629175641 | 0.00719372816 | 0.99634584 | 0.974540008 | 1.82204583 |
| 1 | Sheet6 | dI_C_mean | 407 | 407 | 0 | 0 | 0.000468531072 | 0.000576982677 | 0.609930021 | 0.481354794 | 0.0494034788 |
| 1 | Sheet6 | dI_T_mean | 407 | 407 | 0 | 0 | 0.0161030521 | 0.0200447107 | 0.99995613 | 0.999745694 | 0.0612343634 |
| 1 | Sheet6 | dI_C_std | 407 | 407 | 0 | 0 | 0.000233017485 | 0.000290578354 | 0.0723385628 | 0.0571594816 | 0.804228219 |
| 1 | Sheet6 | dI_T_std | 407 | 407 | 0 | 0 | 0.0126336831 | 0.0157349522 | 0.852194263 | 0.854179238 | 14.347861 |
| 1 | Sheet6 | dI_C_skewness | 407 | 407 | 0 | 0 | 0.00608633307 | 0.00794835519 | 0.927996386 | 0.838383562 | 9.39384814 |
| 1 | Sheet6 | dI_T_skewness | 407 | 407 | 0 | 0 | 0.309563077 | 0.408415459 | 0.457428927 | 0.429972582 | 100.682562 |
| 1 | Sheet6 | dI_C_kurtosis | 407 | 407 | 0 | 0 | 0.012495026 | 0.0148851575 | 0.150592661 | 0.132443717 | 0.692602852 |
| 1 | Sheet6 | dI_T_kurtosis | 407 | 407 | 0 | 0 | 0.471204599 | 0.680175349 | 0.167679693 | 0.33665612 | 21.3044882 |
| 1 | Sheet6 | dI_dI_devide_dt | 407 | 407 | 0 | 0 | 0.000722832103 | 0.000883848439 | 0.998634514 | 0.992769725 | 0.502830391 |
| 1 | Sheet6 | dI_entropy | 407 | 407 | 0 | 0 | 2.59581369 | 2.60186235 | -0.451546594 | -0.313336714 | 48.3742622 |
| 1 | Sheet6 | Charge_energy | 407 | 407 | 0 | 0 | 0.000971758471 | 0.00108693083 | 0.999998396 | 0.99995924 | 0.0132349891 |
| 1 | Sheet6 | Charge_Q | 407 | 407 | 0 | 0 | 0.000133134266 | 0.000153690956 | 0.99999897 | 0.999966182 | 0.0071330653 |
| 1 | Sheet6 | Charge_t_mean | 407 | 407 | 0 | 0 | 0.005269485 | 0.00976595052 | 0.999974603 | 0.999852934 | 0.0205074658 |
| 1 | Sheet6 | Charge_V_mean | 407 | 407 | 0 | 0 | 0.000949219674 | 0.000959114603 | 0.999989802 | 0.999897477 | 0.023417299 |
| 1 | Sheet6 | Charge_C_mean | 407 | 407 | 0 | 0 | 0.000823054241 | 0.00125009726 | 0.999989162 | 0.999935389 | 0.0375834173 |
| 1 | Sheet6 | Charge_T_mean | 407 | 407 | 0 | 0 | 0.00535021529 | 0.00588749361 | 0.999999404 | 0.999987007 | 0.0207622014 |
| 1 | Sheet6 | Charge_C_std | 407 | 407 | 0 | 0 | 0.000550581544 | 0.000599222952 | 0.999668245 | 0.999204019 | 0.0318023821 |
| 1 | Sheet6 | Charge_V_std | 407 | 407 | 0 | 0 | 0.00173562126 | 0.00175702674 | 0.999932566 | 0.997464859 | 0.925119324 |
| 1 | Sheet6 | Charge_T_std | 407 | 407 | 0 | 0 | 0.00183712598 | 0.00231297052 | 0.99995433 | 0.999799225 | 0.103334022 |
| 1 | Sheet6 | Charge_C_skewness | 407 | 407 | 0 | 0 | 0.00088362846 | 0.00150313986 | 0.999989273 | 0.999949628 | 0.403223613 |
| 1 | Sheet6 | Charge_V_skewness | 407 | 407 | 0 | 0 | 0.0255424607 | 0.0263666073 | 0.999842137 | 0.998439722 | 3.10784052 |
| 1 | Sheet6 | Charge_T_skewness | 407 | 407 | 0 | 0 | 0.00333300816 | 0.00415413787 | 0.999738237 | 0.998782712 | 1.80977203 |
| 1 | Sheet6 | Charge_C_kurtosis | 407 | 407 | 0 | 0 | 0.000886230046 | 0.00248348336 | 0.998784858 | 0.99980007 | 0.0751250485 |
| 1 | Sheet6 | Charge_V_kurtosis | 407 | 407 | 0 | 0 | 0.110623842 | 0.118576635 | 0.999476911 | 0.998641031 | 5.1602358 |
| 1 | Sheet6 | Charge_T_kurtosis | 407 | 407 | 0 | 0 | 0.00295393109 | 0.00384345454 | 0.999369044 | 0.99793725 | 0.182731516 |
| 1 | Sheet7 | CC_energy | 401 | 401 | 0 | 0 | 0.0523518312 | 0.0618138696 | 0.997880494 | 0.990930137 | 0.884700605 |
| 1 | Sheet7 | CC_Q | 401 | 401 | 0 | 0 | 0.0122911811 | 0.0145734991 | 0.998387281 | 0.991924108 | 0.804460531 |
| 1 | Sheet7 | CC_t_mean | 401 | 401 | 0 | 0 | 0.0921111826 | 0.109409424 | 0.998369405 | 0.991915219 | 0.80384221 |
| 1 | Sheet7 | CC_V_mean | 401 | 401 | 0 | 0 | 0.00333962437 | 0.00374388795 | 0.997036412 | 0.971697249 | 0.0861864029 |
| 1 | Sheet7 | CC_T_mean | 401 | 401 | 0 | 0 | 0.0155294756 | 0.0185421141 | 0.999986696 | 0.999895225 | 0.0556422222 |
| 1 | Sheet7 | CC_V_std | 401 | 401 | 0 | 0 | 0.00125940853 | 0.00146493625 | 0.98320431 | 0.92372911 | 0.833338257 |
| 1 | Sheet7 | CC_T_std | 401 | 401 | 0 | 0 | 0.00618061996 | 0.0230215298 | 0.971202739 | 0.998112413 | 0.465357947 |
| 1 | Sheet7 | CC_V_skewness | 401 | 401 | 0 | 0 | 0.091943108 | 0.0966938891 | 0.901081583 | 0.944714005 | 28.1504893 |
| 1 | Sheet7 | CC_T_skewness | 401 | 401 | 0 | 0 | 0.0107304739 | 0.0182387914 | 0.969218041 | 0.990805216 | 2.16213671 |
| 1 | Sheet7 | CC_V_kurtosis | 401 | 401 | 0 | 0 | 0.159419628 | 0.171778629 | 0.813715655 | 0.898165449 | 6.49644321 |
| 1 | Sheet7 | CC_T_kurtosis | 401 | 401 | 0 | 0 | 0.0183560298 | 0.0306984442 | 0.92961976 | 0.977443063 | 0.89202212 |
| 1 | Sheet7 | CC_CCCT | 401 | 401 | 0 | 0 | 0.184324543 | 0.218564432 | 0.998387374 | 0.991910556 | 0.80428461 |
| 1 | Sheet7 | CC_entropy | 401 | 401 | 0 | 0 | 5.05825497 | 5.05828252 | 0.841884866 | 0.882546825 | 66.9377849 |
| 1 | Sheet7 | dV_energy | 401 | 401 | 0 | 0 | 0.00447570477 | 0.00549128839 | 0.99735697 | 0.985552909 | 0.488586115 |
| 1 | Sheet7 | dV_Q | 401 | 401 | 0 | 0 | 0.0011342115 | 0.00139273676 | 0.997352785 | 0.985874865 | 0.488616298 |
| 1 | Sheet7 | dV_t_mean | 401 | 401 | 0 | 0 | 0.00882164615 | 0.0112452763 | 0.996557764 | 0.984474959 | 0.506582286 |
| 1 | Sheet7 | dV_V_mean | 401 | 401 | 0 | 0 | 0.000127074376 | 0.000178911243 | 0.913244403 | 0.899366779 | 0.00322001498 |
| 1 | Sheet7 | dV_T_mean | 401 | 401 | 0 | 0 | 0.00640367869 | 0.00815860072 | 0.999992471 | 0.999911602 | 0.0221702756 |
| 1 | Sheet7 | dV_V_std | 401 | 401 | 0 | 0 | 0.000107727376 | 0.000133763062 | 0.453886697 | 0.420964566 | 0.372466451 |
| 1 | Sheet7 | dV_T_std | 401 | 401 | 0 | 0 | 0.00707107419 | 0.00904703784 | 0.98441726 | 0.976528827 | 4.50596095 |
| 1 | Sheet7 | dV_V_skewness | 401 | 401 | 0 | 0 | 0.00304770069 | 0.00510459995 | 0.962641143 | 0.954169613 | 2.00923084 |
| 1 | Sheet7 | dV_T_skewness | 401 | 401 | 0 | 0 | 0.112349598 | 0.157453192 | 0.848803592 | 0.850931812 | 50.8646473 |
| 1 | Sheet7 | dV_V_kurtosis | 401 | 401 | 0 | 0 | 0.00355409139 | 0.00592813333 | 0.860666767 | 0.866557301 | 0.19528853 |
| 1 | Sheet7 | dV_T_kurtosis | 401 | 401 | 0 | 0 | 0.171178992 | 0.23339582 | 0.793785477 | 0.82395969 | 8.52654163 |
| 1 | Sheet7 | dV_dV_devide_dt | 401 | 401 | 0 | 0 | 7.85992041e-05 | 0.000142927934 | 0.99802807 | 0.991575417 | 0.274230053 |
| 1 | Sheet7 | dV_entropy | 401 | 401 | 0 | 0 | 4.71321577 | 4.71570304 | 0.651467283 | 0.319052916 | 63.0345963 |
| 1 | Sheet7 | CV_energy | 401 | 401 | 0 | 0 | 0.0355141308 | 0.0410472379 | 0.985089586 | 0.97550843 | 2.5068893 |
| 1 | Sheet7 | CV_Q | 401 | 401 | 0 | 0 | 0.0084554707 | 0.00977270229 | 0.985092379 | 0.975486843 | 2.50678798 |
| 1 | Sheet7 | CV_t_mean | 401 | 401 | 0 | 0 | 0.070664568 | 0.0809651065 | 0.99983192 | 0.997854245 | 0.48859847 |
| 1 | Sheet7 | CV_C_mean | 401 | 401 | 0 | 0 | 0.0114384012 | 0.0133308658 | 0.978568232 | 0.951659471 | 1.61864695 |
| 1 | Sheet7 | CV_T_mean | 401 | 401 | 0 | 0 | 0.0171762666 | 0.0201769872 | 0.999986314 | 0.999896155 | 0.0679559989 |
| 1 | Sheet7 | CV_C_std | 401 | 401 | 0 | 0 | 0.0209747451 | 0.0242330377 | 0.82840938 | 0.81847415 | 2.56335075 |
| 1 | Sheet7 | CV_T_std | 401 | 401 | 0 | 0 | 0.0143693395 | 0.0248532858 | 0.990265268 | 0.996439123 | 0.669102623 |
| 1 | Sheet7 | CV_C_skewness | 401 | 401 | 0 | 0 | 0.0208959446 | 0.0241076458 | 0.995257726 | 0.98684855 | 1.04491706 |
| 1 | Sheet7 | CV_T_skewness | 401 | 401 | 0 | 0 | 0.00846007144 | 0.0100608783 | 0.998693431 | 0.992952879 | 1.0669938 |
| 1 | Sheet7 | CV_C_kurtosis | 401 | 401 | 0 | 0 | 0.100312836 | 0.11533616 | 0.995277686 | 0.986975286 | 1.52576654 |
| 1 | Sheet7 | CV_T_kurtosis | 401 | 401 | 0 | 0 | 0.020623159 | 0.0246596041 | 0.997537502 | 0.984017754 | 0.911963175 |
| 1 | Sheet7 | CV_CVCT | 401 | 401 | 0 | 0 | 0.133456758 | 0.1540011 | 0.999837275 | 0.997915006 | 0.461515496 |
| 1 | Sheet7 | CV_entropy | 401 | 401 | 0 | 0 | 4.70366302 | 4.70381666 | 0.987806454 | 0.960437888 | 71.8152276 |
| 1 | Sheet7 | dI_energy | 401 | 401 | 0 | 0 | 0.000971431819 | 0.00111194443 | 0.984524165 | 0.975133993 | 2.15605249 |
| 1 | Sheet7 | dI_Q | 401 | 401 | 0 | 0 | 0.000231289549 | 0.000264744112 | 0.984527433 | 0.975150929 | 2.15600058 |
| 1 | Sheet7 | dI_t_mean | 401 | 401 | 0 | 0 | 0.00731162639 | 0.00838528724 | 0.984505323 | 0.974951008 | 2.15408048 |
| 1 | Sheet7 | dI_C_mean | 401 | 401 | 0 | 0 | 0.000451825688 | 0.000552099909 | 0.736946326 | 0.730165106 | 0.047650379 |
| 1 | Sheet7 | dI_T_mean | 401 | 401 | 0 | 0 | 0.0158756459 | 0.01955969 | 0.999954892 | 0.999791845 | 0.0583223644 |
| 1 | Sheet7 | dI_C_std | 401 | 401 | 0 | 0 | 0.000274445864 | 0.000338928433 | 0.0479902965 | 0.0677697547 | 0.949594002 |
| 1 | Sheet7 | dI_T_std | 401 | 401 | 0 | 0 | 0.0120122167 | 0.0148016761 | 0.6335381 | 0.590502065 | 11.412238 |
| 1 | Sheet7 | dI_C_skewness | 401 | 401 | 0 | 0 | 0.00768031447 | 0.00983011465 | 0.934608476 | 0.916948859 | 10.1489089 |
| 1 | Sheet7 | dI_T_skewness | 401 | 401 | 0 | 0 | 0.240097963 | 0.299799343 | 0.405564215 | 0.364562847 | 94.5070392 |
| 1 | Sheet7 | dI_C_kurtosis | 401 | 401 | 0 | 0 | 0.0158985162 | 0.019637451 | 0.18368329 | 0.213043138 | 0.879987164 |
| 1 | Sheet7 | dI_T_kurtosis | 401 | 401 | 0 | 0 | 0.276434796 | 0.345199992 | 0.455245641 | 0.401031157 | 13.4446208 |
| 1 | Sheet7 | dI_dI_devide_dt | 401 | 401 | 0 | 0 | 0.00104424596 | 0.00178690768 | 0.988403207 | 0.991753665 | 0.721717779 |
| 1 | Sheet7 | dI_entropy | 401 | 401 | 0 | 0 | 2.5786802 | 2.58108406 | -0.344588172 | -0.370733893 | 48.2170426 |
| 1 | Sheet7 | Charge_energy | 401 | 401 | 0 | 0 | 0.00101620432 | 0.00115363717 | 0.999998395 | 0.999973387 | 0.0138468166 |
| 1 | Sheet7 | Charge_Q | 401 | 401 | 0 | 0 | 0.000136341913 | 0.000158522654 | 0.999998954 | 0.999979715 | 0.0073053896 |
| 1 | Sheet7 | Charge_t_mean | 401 | 401 | 0 | 0 | 0.0059199438 | 0.0108403554 | 0.999962003 | 0.999819016 | 0.0228306471 |
| 1 | Sheet7 | Charge_V_mean | 401 | 401 | 0 | 0 | 0.00110380952 | 0.00110966832 | 0.999990534 | 0.999921279 | 0.027226485 |
| 1 | Sheet7 | Charge_C_mean | 401 | 401 | 0 | 0 | 0.000823445405 | 0.0013567257 | 0.999984609 | 0.999943983 | 0.0379711693 |
| 1 | Sheet7 | Charge_T_mean | 401 | 401 | 0 | 0 | 0.0071331855 | 0.00762328595 | 0.99999926 | 0.99998902 | 0.0269973439 |
| 1 | Sheet7 | Charge_C_std | 401 | 401 | 0 | 0 | 0.000554786797 | 0.000619803983 | 0.999384714 | 0.999019429 | 0.031974423 |
| 1 | Sheet7 | Charge_V_std | 401 | 401 | 0 | 0 | 0.00220842138 | 0.00222733068 | 0.999925271 | 0.998942569 | 1.16424117 |
| 1 | Sheet7 | Charge_T_std | 401 | 401 | 0 | 0 | 0.00186141752 | 0.0023242084 | 0.999965198 | 0.999782261 | 0.0827566375 |
| 1 | Sheet7 | Charge_C_skewness | 401 | 401 | 0 | 0 | 0.000993236439 | 0.00169427105 | 0.99998304 | 0.999939517 | 0.476807385 |
| 1 | Sheet7 | Charge_V_skewness | 401 | 401 | 0 | 0 | 0.0385610739 | 0.0395147226 | 0.999741692 | 0.99946384 | 4.41177661 |
| 1 | Sheet7 | Charge_T_skewness | 401 | 401 | 0 | 0 | 0.00404837051 | 0.00468032043 | 0.999848748 | 0.998875386 | 2.59304134 |
| 1 | Sheet7 | Charge_C_kurtosis | 401 | 401 | 0 | 0 | 0.000825198885 | 0.00202820352 | 0.999152184 | 0.999788216 | 0.0704957201 |
| 1 | Sheet7 | Charge_V_kurtosis | 401 | 401 | 0 | 0 | 0.178441408 | 0.18895898 | 0.999178306 | 0.999637101 | 7.77309614 |
| 1 | Sheet7 | Charge_T_kurtosis | 401 | 401 | 0 | 0 | 0.00246972689 | 0.00299749041 | 0.999102193 | 0.997472364 | 0.155484938 |
| 1 | Sheet8 | CC_energy | 419 | 419 | 0 | 0 | 0.0567529458 | 0.0653999271 | 0.997652707 | 0.988137952 | 0.964454318 |
| 1 | Sheet8 | CC_Q | 419 | 419 | 0 | 0 | 0.0133343215 | 0.0154176897 | 0.998212575 | 0.989951541 | 0.878910335 |
| 1 | Sheet8 | CC_t_mean | 419 | 419 | 0 | 0 | 0.0999319736 | 0.115435296 | 0.998206881 | 0.990025031 | 0.878291872 |
| 1 | Sheet8 | CC_V_mean | 419 | 419 | 0 | 0 | 0.00354858571 | 0.00392194131 | 0.996906002 | 0.980634 | 0.0914493621 |
| 1 | Sheet8 | CC_T_mean | 419 | 419 | 0 | 0 | 0.0125071888 | 0.0148219937 | 0.9999909 | 0.999944372 | 0.0469831655 |
| 1 | Sheet8 | CC_V_std | 419 | 419 | 0 | 0 | 0.00121829018 | 0.00144652314 | 0.980487659 | 0.954468456 | 0.815763491 |
| 1 | Sheet8 | CC_T_std | 419 | 419 | 0 | 0 | 0.00488889075 | 0.0145413314 | 0.98370241 | 0.997677925 | 0.503789906 |
| 1 | Sheet8 | CC_V_skewness | 419 | 419 | 0 | 0 | 0.0923070505 | 0.0959696382 | 0.986477094 | 0.967780593 | 28.02091 |
| 1 | Sheet8 | CC_T_skewness | 419 | 419 | 0 | 0 | 0.0117739504 | 0.0190120068 | 0.977367643 | 0.989592404 | 3.382241 |
| 1 | Sheet8 | CC_V_kurtosis | 419 | 419 | 0 | 0 | 0.159229754 | 0.168620675 | 0.826071799 | 0.77516872 | 6.60512836 |
| 1 | Sheet8 | CC_T_kurtosis | 419 | 419 | 0 | 0 | 0.0151075735 | 0.0284487491 | 0.943694895 | 0.98493871 | 0.799732197 |
| 1 | Sheet8 | CC_CCCT | 419 | 419 | 0 | 0 | 0.199977543 | 0.231229004 | 0.998212728 | 0.989987777 | 0.878770767 |
| 1 | Sheet8 | CC_entropy | 419 | 419 | 0 | 0 | 5.05931398 | 5.05938708 | 0.763601927 | 0.818257322 | 66.8281259 |
| 1 | Sheet8 | dV_energy | 419 | 419 | 0 | 0 | 0.00540212863 | 0.00625225195 | 0.998178329 | 0.987468291 | 0.572835632 |
| 1 | Sheet8 | dV_Q | 419 | 419 | 0 | 0 | 0.00137199925 | 0.00158746993 | 0.998171766 | 0.987653038 | 0.574127404 |
| 1 | Sheet8 | dV_t_mean | 419 | 419 | 0 | 0 | 0.0108723187 | 0.0129695461 | 0.997092181 | 0.986208905 | 0.606367696 |
| 1 | Sheet8 | dV_V_mean | 419 | 419 | 0 | 0 | 0.000123765544 | 0.000164370089 | 0.92288282 | 0.915010551 | 0.00313619932 |
| 1 | Sheet8 | dV_T_mean | 419 | 419 | 0 | 0 | 0.00685968683 | 0.00865120689 | 0.999991334 | 0.999939315 | 0.0251200759 |
| 1 | Sheet8 | dV_V_std | 419 | 419 | 0 | 0 | 0.000131870954 | 0.000160208635 | 0.45237421 | 0.541309827 | 0.456711189 |
| 1 | Sheet8 | dV_T_std | 419 | 419 | 0 | 0 | 0.00717310828 | 0.00893968345 | 0.982511063 | 0.98115994 | 5.21769289 |
| 1 | Sheet8 | dV_V_skewness | 419 | 419 | 0 | 0 | 0.00290426665 | 0.00479281996 | 0.96263828 | 0.962309277 | 1.87215403 |
| 1 | Sheet8 | dV_T_skewness | 419 | 419 | 0 | 0 | 0.150372561 | 0.247787539 | 0.845528142 | 0.891675816 | 49.7772542 |
| 1 | Sheet8 | dV_V_kurtosis | 419 | 419 | 0 | 0 | 0.00314543255 | 0.00553897748 | 0.863394886 | 0.886945776 | 0.172650108 |
| 1 | Sheet8 | dV_T_kurtosis | 419 | 419 | 0 | 0 | 0.269832832 | 0.876270385 | 0.413261241 | 0.816852774 | 12.6784516 |
| 1 | Sheet8 | dV_dV_devide_dt | 419 | 419 | 0 | 0 | 6.69783892e-05 | 0.000122051486 | 0.998451762 | 0.991855074 | 0.240376033 |
| 1 | Sheet8 | dV_entropy | 419 | 419 | 0 | 0 | 4.73959198 | 4.7416755 | 0.627029187 | 0.334755465 | 63.1673657 |
| 1 | Sheet8 | CV_energy | 419 | 419 | 0 | 0 | 0.0341463732 | 0.0398794986 | 0.990340589 | 0.986922938 | 2.3464334 |
| 1 | Sheet8 | CV_Q | 419 | 419 | 0 | 0 | 0.00812992747 | 0.00949484558 | 0.990341034 | 0.986923101 | 2.34637502 |
| 1 | Sheet8 | CV_t_mean | 419 | 419 | 0 | 0 | 0.0673777076 | 0.0780899464 | 0.999860274 | 0.998639308 | 0.454016302 |
| 1 | Sheet8 | CV_C_mean | 419 | 419 | 0 | 0 | 0.0106563695 | 0.012406922 | 0.975176179 | 0.959040256 | 1.50745911 |
| 1 | Sheet8 | CV_T_mean | 419 | 419 | 0 | 0 | 0.012300953 | 0.0145573428 | 0.999992346 | 0.999951386 | 0.0500019338 |
| 1 | Sheet8 | CV_C_std | 419 | 419 | 0 | 0 | 0.019570415 | 0.0226508888 | 0.804188117 | 0.805308346 | 2.39038224 |
| 1 | Sheet8 | CV_T_std | 419 | 419 | 0 | 0 | 0.00856318447 | 0.0103144142 | 0.999122852 | 0.998962801 | 0.508397787 |
| 1 | Sheet8 | CV_C_skewness | 419 | 419 | 0 | 0 | 0.0189469862 | 0.0218733107 | 0.994036909 | 0.9861337 | 0.943123727 |
| 1 | Sheet8 | CV_T_skewness | 419 | 419 | 0 | 0 | 0.00861113209 | 0.0102920913 | 0.998498379 | 0.995813683 | 1.14543403 |
| 1 | Sheet8 | CV_C_kurtosis | 419 | 419 | 0 | 0 | 0.0900906032 | 0.103735859 | 0.994134761 | 0.985881497 | 1.36222418 |
| 1 | Sheet8 | CV_T_kurtosis | 419 | 419 | 0 | 0 | 0.0190963155 | 0.023364448 | 0.997134999 | 0.992980879 | 0.873286511 |
| 1 | Sheet8 | CV_CVCT | 419 | 419 | 0 | 0 | 0.127941162 | 0.149224382 | 0.99986359 | 0.998618182 | 0.431169046 |
| 1 | Sheet8 | CV_entropy | 419 | 419 | 0 | 0 | 4.70892904 | 4.70905606 | 0.986074075 | 0.963499148 | 71.8467115 |
| 1 | Sheet8 | dI_energy | 419 | 419 | 0 | 0 | 0.000964512216 | 0.00124148146 | 0.991828474 | 0.992466521 | 1.98801743 |
| 1 | Sheet8 | dI_Q | 419 | 419 | 0 | 0 | 0.000229641482 | 0.000295589252 | 0.991829202 | 0.992449229 | 1.9879712 |
| 1 | Sheet8 | dI_t_mean | 419 | 419 | 0 | 0 | 0.00730268441 | 0.0094046175 | 0.991802645 | 0.992210116 | 1.99746853 |
| 1 | Sheet8 | dI_C_mean | 419 | 419 | 0 | 0 | 0.000461773299 | 0.000565339336 | 0.841206908 | 0.803167259 | 0.0487185719 |
| 1 | Sheet8 | dI_T_mean | 419 | 419 | 0 | 0 | 0.0147790079 | 0.018455778 | 0.999960506 | 0.999849469 | 0.0564681014 |
| 1 | Sheet8 | dI_C_std | 419 | 419 | 0 | 0 | 0.00025506812 | 0.000313075686 | 0.00173075043 | -0.0097140769 | 0.882005649 |
| 1 | Sheet8 | dI_T_std | 419 | 419 | 0 | 0 | 0.0131716904 | 0.015991622 | 0.779755887 | 0.758465713 | 15.0031275 |
| 1 | Sheet8 | dI_C_skewness | 419 | 419 | 0 | 0 | 0.00759117533 | 0.00998671717 | 0.966989868 | 0.942892869 | 8.47176166 |
| 1 | Sheet8 | dI_T_skewness | 419 | 419 | 0 | 0 | 0.287389739 | 0.364714158 | 0.515583247 | 0.522787082 | 94.4655251 |
| 1 | Sheet8 | dI_C_kurtosis | 419 | 419 | 0 | 0 | 0.014752298 | 0.0184927199 | 0.332056347 | 0.298802931 | 0.814761587 |
| 1 | Sheet8 | dI_T_kurtosis | 419 | 419 | 0 | 0 | 0.373079366 | 0.549835048 | 0.306940312 | 0.361066011 | 17.4231127 |
| 1 | Sheet8 | dI_dI_devide_dt | 419 | 419 | 0 | 0 | 0.000931378855 | 0.00211162627 | 0.995152348 | 0.997683912 | 0.684842716 |
| 1 | Sheet8 | dI_entropy | 419 | 419 | 0 | 0 | 2.67697048 | 2.68432401 | -0.424735822 | -0.427574661 | 49.1624487 |
| 1 | Sheet8 | Charge_energy | 419 | 419 | 0 | 0 | 0.0010504074 | 0.00119574698 | 0.999997726 | 0.999933768 | 0.0143019958 |
| 1 | Sheet8 | Charge_Q | 419 | 419 | 0 | 0 | 0.000138900054 | 0.000160042165 | 0.999998566 | 0.999963132 | 0.00744865018 |
| 1 | Sheet8 | Charge_t_mean | 419 | 419 | 0 | 0 | 0.00521554774 | 0.0079540423 | 0.999988092 | 0.999948205 | 0.0198859399 |
| 1 | Sheet8 | Charge_V_mean | 419 | 419 | 0 | 0 | 0.00109601395 | 0.00110428923 | 0.999993074 | 0.999861663 | 0.0270017589 |
| 1 | Sheet8 | Charge_C_mean | 419 | 419 | 0 | 0 | 0.000763948749 | 0.00117189687 | 0.999990652 | 0.999953344 | 0.0356255468 |
| 1 | Sheet8 | Charge_T_mean | 419 | 419 | 0 | 0 | 0.0050474314 | 0.00554193059 | 0.999999425 | 0.999985971 | 0.0198237298 |
| 1 | Sheet8 | Charge_C_std | 419 | 419 | 0 | 0 | 0.000725062399 | 0.00148569058 | 0.994252685 | 0.999383519 | 0.0418224644 |
| 1 | Sheet8 | Charge_V_std | 419 | 419 | 0 | 0 | 0.0022015592 | 0.00224100272 | 0.999869575 | 0.997891833 | 1.18347001 |
| 1 | Sheet8 | Charge_T_std | 419 | 419 | 0 | 0 | 0.00184845192 | 0.00231794127 | 0.999957794 | 0.99981256 | 0.106452132 |
| 1 | Sheet8 | Charge_C_skewness | 419 | 419 | 0 | 0 | 0.000990826493 | 0.00158547501 | 0.999990129 | 0.999971615 | 0.479094107 |
| 1 | Sheet8 | Charge_V_skewness | 419 | 419 | 0 | 0 | 0.0387907491 | 0.0405635369 | 0.999744631 | 0.999448284 | 4.29312544 |
| 1 | Sheet8 | Charge_T_skewness | 419 | 419 | 0 | 0 | 0.00371583925 | 0.00456632798 | 0.999734048 | 0.999440943 | 2.30548103 |
| 1 | Sheet8 | Charge_C_kurtosis | 419 | 419 | 0 | 0 | 0.00219672565 | 0.0094251499 | 0.990780013 | 0.999748285 | 0.187528972 |
| 1 | Sheet8 | Charge_V_kurtosis | 419 | 419 | 0 | 0 | 0.184983875 | 0.202244348 | 0.9992688 | 0.999228218 | 7.88313111 |
| 1 | Sheet8 | Charge_T_kurtosis | 419 | 419 | 0 | 0 | 0.00291563952 | 0.00376077242 | 0.999206691 | 0.998719243 | 0.180043253 |
| 2 | Sheet1 | CC_energy | 298 | 298 | 0 | 0 | 0.061858706 | 0.0730703331 | 0.995851659 | 0.979419907 | 1.06671836 |
| 2 | Sheet1 | CC_Q | 298 | 298 | 0 | 0 | 0.0145366405 | 0.0172330024 | 0.99678598 | 0.980948288 | 0.979806316 |
| 2 | Sheet1 | CC_t_mean | 298 | 298 | 0 | 0 | 0.0726955473 | 0.0861206885 | 0.996795593 | 0.980984214 | 0.979983614 |
| 2 | Sheet1 | CC_V_mean | 298 | 298 | 0 | 0 | 0.00368355059 | 0.00411549077 | 0.996094728 | 0.97121084 | 0.0942054567 |
| 2 | Sheet1 | CC_T_mean | 298 | 298 | 0 | 0 | 0.0423158548 | 0.0505335853 | 0.99976843 | 0.99900738 | 0.130346094 |
| 2 | Sheet1 | CC_V_std | 298 | 298 | 0 | 0 | 0.0014229703 | 0.001680068 | 0.977733237 | 0.895924068 | 1.03220505 |
| 2 | Sheet1 | CC_T_std | 298 | 298 | 0 | 0 | 0.0139738995 | 0.0381706503 | 0.963734576 | 0.992473158 | 0.480543026 |
| 2 | Sheet1 | CC_V_skewness | 298 | 298 | 0 | 0 | 0.122806436 | 0.128328553 | 0.98769243 | 0.894764449 | 64.3206823 |
| 2 | Sheet1 | CC_T_skewness | 298 | 298 | 0 | 0 | 0.00859379674 | 0.0144590829 | 0.915698387 | 0.981725516 | 2.57755555 |
| 2 | Sheet1 | CC_V_kurtosis | 298 | 298 | 0 | 0 | 0.251079714 | 0.267758755 | 0.88628704 | 0.799667116 | 9.55668718 |
| 2 | Sheet1 | CC_T_kurtosis | 298 | 298 | 0 | 0 | 0.00906609837 | 0.0146505393 | 0.91674192 | 0.973929433 | 0.486735029 |
| 2 | Sheet1 | CC_CCCT | 298 | 298 | 0 | 0 | 0.145340142 | 0.17230616 | 0.996785992 | 0.980956726 | 0.979640632 |
| 2 | Sheet1 | CC_entropy | 298 | 298 | 0 | 0 | 5.0148017 | 5.01488421 | 0.810860942 | 0.949207986 | 67.1173161 |
| 2 | Sheet1 | dV_energy | 298 | 298 | 0 | 0 | 0.00684850646 | 0.00743105729 | 0.999450872 | 0.990744916 | 0.576163983 |
| 2 | Sheet1 | dV_Q | 298 | 298 | 0 | 0 | 0.00173209979 | 0.00187987551 | 0.999450459 | 0.990997493 | 0.574917693 |
| 2 | Sheet1 | dV_t_mean | 298 | 298 | 0 | 0 | 0.00864734689 | 0.00941692273 | 0.999429033 | 0.989700373 | 0.57404673 |
| 2 | Sheet1 | dV_V_mean | 298 | 298 | 0 | 0 | 0.000114196514 | 0.000152322769 | 0.893238169 | 0.670223629 | 0.00289448165 |
| 2 | Sheet1 | dV_T_mean | 298 | 298 | 0 | 0 | 0.00730572436 | 0.00918434799 | 0.999985643 | 0.99985614 | 0.0214616588 |
| 2 | Sheet1 | dV_V_std | 298 | 298 | 0 | 0 | 0.000126169242 | 0.000145269391 | 0.554087127 | 0.552811679 | 0.439128852 |
| 2 | Sheet1 | dV_T_std | 298 | 298 | 0 | 0 | 0.00895271957 | 0.01353374 | 0.997139808 | 0.990133502 | 1.67264561 |
| 2 | Sheet1 | dV_V_skewness | 298 | 298 | 0 | 0 | 0.00198959741 | 0.00361618658 | 0.966093288 | 0.865845597 | 1.00837687 |
| 2 | Sheet1 | dV_T_skewness | 298 | 298 | 0 | 0 | 0.0356248082 | 0.0549417817 | 0.902996801 | 0.914689985 | 30.0462684 |
| 2 | Sheet1 | dV_V_kurtosis | 298 | 298 | 0 | 0 | 0.0018044963 | 0.00227513905 | 0.816808927 | 0.803972567 | 0.0977458633 |
| 2 | Sheet1 | dV_T_kurtosis | 298 | 298 | 0 | 0 | 0.0449079476 | 0.0644605697 | 0.85985582 | 0.876571828 | 2.44860346 |
| 2 | Sheet1 | dV_dV_devide_dt | 298 | 298 | 0 | 0 | 4.3930296e-05 | 5.46264536e-05 | 0.999707835 | 0.99541959 | 0.132549242 |
| 2 | Sheet1 | dV_entropy | 298 | 298 | 0 | 0 | 4.66408605 | 4.6647763 | 0.834129084 | 0.536562962 | 62.8304497 |
| 2 | Sheet1 | CV_energy | 298 | 298 | 0 | 0 | 0.0394790428 | 0.0462040805 | 0.979427397 | 0.971772675 | 2.38994188 |
| 2 | Sheet1 | CV_Q | 298 | 298 | 0 | 0 | 0.0093994228 | 0.0110004791 | 0.979426682 | 0.971787186 | 2.38985194 |
| 2 | Sheet1 | CV_t_mean | 298 | 298 | 0 | 0 | 0.0530391903 | 0.0610912937 | 0.99983922 | 0.998653682 | 0.422048446 |
| 2 | Sheet1 | CV_C_mean | 298 | 298 | 0 | 0 | 0.0146373985 | 0.0170067866 | 0.974831112 | 0.847676106 | 1.54575785 |
| 2 | Sheet1 | CV_T_mean | 298 | 298 | 0 | 0 | 0.0232272997 | 0.0274289295 | 0.999954478 | 0.999699811 | 0.0782209202 |
| 2 | Sheet1 | CV_C_std | 298 | 298 | 0 | 0 | 0.0278303445 | 0.0321374653 | 0.809590995 | 0.647598065 | 2.27370615 |
| 2 | Sheet1 | CV_T_std | 298 | 298 | 0 | 0 | 0.0126926046 | 0.0150561171 | 0.999265572 | 0.998540318 | 0.334356782 |
| 2 | Sheet1 | CV_C_skewness | 298 | 298 | 0 | 0 | 0.0146068797 | 0.0167601603 | 0.996559305 | 0.98063189 | 0.683087902 |
| 2 | Sheet1 | CV_T_skewness | 298 | 298 | 0 | 0 | 0.00650247509 | 0.00766849506 | 0.998369507 | 0.992765526 | 1.12477918 |
| 2 | Sheet1 | CV_C_kurtosis | 298 | 298 | 0 | 0 | 0.071800795 | 0.0821133115 | 0.99688034 | 0.981073558 | 1.00362494 |
| 2 | Sheet1 | CV_T_kurtosis | 298 | 298 | 0 | 0 | 0.0126489049 | 0.0151158806 | 0.996658934 | 0.980123563 | 0.651439276 |
| 2 | Sheet1 | CV_CVCT | 298 | 298 | 0 | 0 | 0.0982440443 | 0.115004508 | 0.999837355 | 0.998630554 | 0.39101188 |
| 2 | Sheet1 | CV_entropy | 298 | 298 | 0 | 0 | 4.61426494 | 4.61445027 | 0.991675672 | 0.93742038 | 72.6331191 |
| 2 | Sheet1 | dI_energy | 298 | 298 | 0 | 0 | 0.00115861606 | 0.00156943916 | 0.990183331 | 0.978103406 | 2.75081134 |
| 2 | Sheet1 | dI_Q | 298 | 298 | 0 | 0 | 0.000275860763 | 0.0003736766 | 0.990183263 | 0.978103406 | 2.75080882 |
| 2 | Sheet1 | dI_t_mean | 298 | 298 | 0 | 0 | 0.00868948388 | 0.0118123031 | 0.990181006 | 0.977866132 | 2.7400995 |
| 2 | Sheet1 | dI_C_mean | 298 | 298 | 0 | 0 | 0.000544071614 | 0.000659458663 | 0.81969032 | 0.657878946 | 0.0573473498 |
| 2 | Sheet1 | dI_T_mean | 298 | 298 | 0 | 0 | 0.0174266157 | 0.0211908606 | 0.999849297 | 0.999393159 | 0.0543218151 |
| 2 | Sheet1 | dI_C_std | 298 | 298 | 0 | 0 | 0.000331514648 | 0.000400576713 | 0.182313739 | 0.143450849 | 1.14580075 |
| 2 | Sheet1 | dI_T_std | 298 | 298 | 0 | 0 | 0.0137512726 | 0.0171425823 | 0.884527741 | 0.830129991 | 8.63016582 |
| 2 | Sheet1 | dI_C_skewness | 298 | 298 | 0 | 0 | 0.0100693816 | 0.0145230752 | 0.944090577 | 0.888425228 | 21.1379869 |
| 2 | Sheet1 | dI_T_skewness | 298 | 298 | 0 | 0 | 0.198158572 | 0.247485723 | 0.435793277 | 0.370528249 | 104.46592 |
| 2 | Sheet1 | dI_C_kurtosis | 298 | 298 | 0 | 0 | 0.00874831377 | 0.0114567042 | 0.660460884 | 0.357477266 | 0.485284574 |
| 2 | Sheet1 | dI_T_kurtosis | 298 | 298 | 0 | 0 | 0.230196773 | 0.302238917 | 0.421455134 | 0.405645377 | 11.9726918 |
| 2 | Sheet1 | dI_dI_devide_dt | 298 | 298 | 0 | 0 | 0.00105264023 | 0.00130728711 | 0.998379201 | 0.993828748 | 0.671933994 |
| 2 | Sheet1 | dI_entropy | 298 | 298 | 0 | 0 | 2.46062928 | 2.46930492 | -0.437154254 | -0.0269828974 | 47.0371614 |
| 2 | Sheet1 | Charge_energy | 298 | 298 | 0 | 0 | 0.00142821514 | 0.00366676336 | 0.999944626 | 0.999967124 | 0.0191493956 |
| 2 | Sheet1 | Charge_Q | 298 | 298 | 0 | 0 | 0.000188619366 | 0.000574231246 | 0.999979715 | 0.999978687 | 0.0100400608 |
| 2 | Sheet1 | Charge_t_mean | 298 | 298 | 0 | 0 | 0.00468853626 | 0.00604488078 | 0.999992971 | 0.999825191 | 0.0234501419 |
| 2 | Sheet1 | Charge_V_mean | 298 | 298 | 0 | 0 | 0.00115674107 | 0.00116375151 | 0.999981628 | 0.999814536 | 0.0282772041 |
| 2 | Sheet1 | Charge_C_mean | 298 | 298 | 0 | 0 | 0.00138198802 | 0.00174907047 | 0.999995522 | 0.999942864 | 0.0487711338 |
| 2 | Sheet1 | Charge_T_mean | 298 | 298 | 0 | 0 | 0.0140926192 | 0.01437876 | 0.999998652 | 0.999973699 | 0.0458994499 |
| 2 | Sheet1 | Charge_C_std | 298 | 298 | 0 | 0 | 0.00130308143 | 0.00348785203 | 0.997786719 | 0.999867588 | 0.0497754452 |
| 2 | Sheet1 | Charge_V_std | 298 | 298 | 0 | 0 | 0.00259878405 | 0.00264589064 | 0.999725619 | 0.998356214 | 1.5909176 |
| 2 | Sheet1 | Charge_T_std | 298 | 298 | 0 | 0 | 0.00299607579 | 0.00358569006 | 0.999974668 | 0.999858068 | 0.080058976 |
| 2 | Sheet1 | Charge_C_skewness | 298 | 298 | 0 | 0 | 0.0018145565 | 0.00204424256 | 0.999996094 | 0.999945132 | 0.679601836 |
| 2 | Sheet1 | Charge_V_skewness | 298 | 298 | 0 | 0 | 0.0595762967 | 0.0643264555 | 0.999101713 | 0.998298731 | 5.02788367 |
| 2 | Sheet1 | Charge_T_skewness | 298 | 298 | 0 | 0 | 0.00448528105 | 0.00498287858 | 0.999700216 | 0.999086282 | 3.44746687 |
| 2 | Sheet1 | Charge_C_kurtosis | 298 | 298 | 0 | 0 | 0.00328517517 | 0.0122461623 | 0.997802012 | 0.999940596 | 0.266363711 |
| 2 | Sheet1 | Charge_V_kurtosis | 298 | 298 | 0 | 0 | 0.347311147 | 0.408059627 | 0.996083917 | 0.999316176 | 11.3852459 |
| 2 | Sheet1 | Charge_T_kurtosis | 298 | 298 | 0 | 0 | 0.00239907458 | 0.00557938921 | 0.989619272 | 0.993028891 | 0.147158759 |
| 2 | Sheet2 | CC_energy | 291 | 291 | 0 | 0 | 0.0636213631 | 0.0765550022 | 0.995972875 | 0.987786388 | 1.09769531 |
| 2 | Sheet2 | CC_Q | 291 | 291 | 0 | 0 | 0.0149474138 | 0.0180646755 | 0.996833888 | 0.990377589 | 1.008615 |
| 2 | Sheet2 | CC_t_mean | 291 | 291 | 0 | 0 | 0.0746988917 | 0.0903431151 | 0.996812997 | 0.990229908 | 1.00811326 |
| 2 | Sheet2 | CC_V_mean | 291 | 291 | 0 | 0 | 0.00381991797 | 0.00432514778 | 0.995115981 | 0.974528667 | 0.0976337844 |
| 2 | Sheet2 | CC_T_mean | 291 | 291 | 0 | 0 | 0.0431681677 | 0.053196495 | 0.999814206 | 0.999132209 | 0.133065648 |
| 2 | Sheet2 | CC_V_std | 291 | 291 | 0 | 0 | 0.00150849707 | 0.00183499378 | 0.974341602 | 0.886010158 | 1.08649219 |
| 2 | Sheet2 | CC_T_std | 291 | 291 | 0 | 0 | 0.0132093793 | 0.0317746542 | 0.949850102 | 0.989215797 | 0.446871415 |
| 2 | Sheet2 | CC_V_skewness | 291 | 291 | 0 | 0 | 0.135108628 | 0.143579717 | 0.992574205 | 0.963949379 | 86.7441966 |
| 2 | Sheet2 | CC_T_skewness | 291 | 291 | 0 | 0 | 0.00916089865 | 0.0146790909 | 0.972984902 | 0.993797997 | 2.38748984 |
| 2 | Sheet2 | CC_V_kurtosis | 291 | 291 | 0 | 0 | 0.291109262 | 0.316715329 | 0.905847017 | 0.695918169 | 10.8912622 |
| 2 | Sheet2 | CC_T_kurtosis | 291 | 291 | 0 | 0 | 0.0108196751 | 0.017865671 | 0.962445871 | 0.991291166 | 0.566696655 |
| 2 | Sheet2 | CC_CCCT | 291 | 291 | 0 | 0 | 0.149440593 | 0.180616949 | 0.99683392 | 0.990365269 | 1.00839305 |
| 2 | Sheet2 | CC_entropy | 291 | 291 | 0 | 0 | 5.010251 | 5.01033082 | 0.842368072 | 0.86797744 | 67.1493384 |
| 2 | Sheet2 | dV_energy | 291 | 291 | 0 | 0 | 0.00663478358 | 0.00733348214 | 0.999245688 | 0.992194264 | 0.549060297 |
| 2 | Sheet2 | dV_Q | 291 | 291 | 0 | 0 | 0.00168260811 | 0.00185977906 | 0.999240658 | 0.991780335 | 0.54940204 |
| 2 | Sheet2 | dV_t_mean | 291 | 291 | 0 | 0 | 0.0084063036 | 0.00928448443 | 0.999237909 | 0.99197695 | 0.548956784 |
| 2 | Sheet2 | dV_V_mean | 291 | 291 | 0 | 0 | 0.00012683785 | 0.000240201825 | 0.955852514 | 0.85319076 | 0.0032146957 |
| 2 | Sheet2 | dV_T_mean | 291 | 291 | 0 | 0 | 0.00790480608 | 0.00983793044 | 0.999989072 | 0.999815436 | 0.0232533862 |
| 2 | Sheet2 | dV_V_std | 291 | 291 | 0 | 0 | 0.000113599501 | 0.00013332845 | 0.72744503 | 0.583190375 | 0.395569574 |
| 2 | Sheet2 | dV_T_std | 291 | 291 | 0 | 0 | 0.00910108717 | 0.0162704876 | 0.996117686 | 0.990893795 | 1.69427855 |
| 2 | Sheet2 | dV_V_skewness | 291 | 291 | 0 | 0 | 0.0028478995 | 0.00888973923 | 0.970920991 | 0.965374714 | 1.49933184 |
| 2 | Sheet2 | dV_T_skewness | 291 | 291 | 0 | 0 | 0.0369421429 | 0.0529287277 | 0.919543667 | 0.914026852 | 29.5507374 |
| 2 | Sheet2 | dV_V_kurtosis | 291 | 291 | 0 | 0 | 0.0017007386 | 0.0021183561 | 0.803423438 | 0.727819955 | 0.0921375287 |
| 2 | Sheet2 | dV_T_kurtosis | 291 | 291 | 0 | 0 | 0.0509774336 | 0.08061181 | 0.742303544 | 0.797096163 | 2.7696943 |
| 2 | Sheet2 | dV_dV_devide_dt | 291 | 291 | 0 | 0 | 3.81117427e-05 | 4.6629752e-05 | 0.999748352 | 0.997790219 | 0.116953512 |
| 2 | Sheet2 | dV_entropy | 291 | 291 | 0 | 0 | 4.68248097 | 4.68302724 | 0.852228391 | 0.668279104 | 62.9151559 |
| 2 | Sheet2 | CV_energy | 291 | 291 | 0 | 0 | 0.042230034 | 0.0484398935 | 0.989031124 | 0.979829461 | 2.45704011 |
| 2 | Sheet2 | CV_Q | 291 | 291 | 0 | 0 | 0.0100538573 | 0.0115321399 | 0.989029844 | 0.979825565 | 2.45691064 |
| 2 | Sheet2 | CV_t_mean | 291 | 291 | 0 | 0 | 0.0579952477 | 0.0674176447 | 0.999800455 | 0.998365831 | 0.416968167 |
| 2 | Sheet2 | CV_C_mean | 291 | 291 | 0 | 0 | 0.0140356919 | 0.0162174182 | 0.965835746 | 0.905198954 | 1.57834105 |
| 2 | Sheet2 | CV_T_mean | 291 | 291 | 0 | 0 | 0.023579246 | 0.0276343334 | 0.999958452 | 0.99959094 | 0.081338416 |
| 2 | Sheet2 | CV_C_std | 291 | 291 | 0 | 0 | 0.0280573293 | 0.032226466 | 0.720228839 | 0.670471733 | 2.36296509 |
| 2 | Sheet2 | CV_T_std | 291 | 291 | 0 | 0 | 0.0158166844 | 0.0182806709 | 0.993987559 | 0.993390277 | 0.414247549 |
| 2 | Sheet2 | CV_C_skewness | 291 | 291 | 0 | 0 | 0.0156131972 | 0.0180661014 | 0.995173256 | 0.959186556 | 0.683134909 |
| 2 | Sheet2 | CV_T_skewness | 291 | 291 | 0 | 0 | 0.00669272239 | 0.00843925647 | 0.998051858 | 0.993764761 | 0.894745078 |
| 2 | Sheet2 | CV_C_kurtosis | 291 | 291 | 0 | 0 | 0.0806454233 | 0.093665973 | 0.995584999 | 0.961932612 | 1.01952758 |
| 2 | Sheet2 | CV_T_kurtosis | 291 | 291 | 0 | 0 | 0.0159149252 | 0.0199090844 | 0.996620417 | 0.98249955 | 0.727995655 |
| 2 | Sheet2 | CV_CVCT | 291 | 291 | 0 | 0 | 0.108076149 | 0.127851284 | 0.999803281 | 0.998399917 | 0.388640599 |
| 2 | Sheet2 | CV_entropy | 291 | 291 | 0 | 0 | 4.56671193 | 4.56683384 | 0.985037022 | 0.902997885 | 73.2926667 |
| 2 | Sheet2 | dI_energy | 291 | 291 | 0 | 0 | 0.00105926669 | 0.00152943426 | 0.987852298 | 0.989665886 | 2.27445944 |
| 2 | Sheet2 | dI_Q | 291 | 291 | 0 | 0 | 0.00025219899 | 0.000364139083 | 0.987852206 | 0.989658581 | 2.27447756 |
| 2 | Sheet2 | dI_t_mean | 291 | 291 | 0 | 0 | 0.00794889186 | 0.0115111816 | 0.987818019 | 0.990332917 | 2.26701049 |
| 2 | Sheet2 | dI_C_mean | 291 | 291 | 0 | 0 | 0.000459323938 | 0.000564624959 | 0.865300968 | 0.80141223 | 0.0484135908 |
| 2 | Sheet2 | dI_T_mean | 291 | 291 | 0 | 0 | 0.0144222764 | 0.0181120962 | 0.999929868 | 0.999638177 | 0.045749122 |
| 2 | Sheet2 | dI_C_std | 291 | 291 | 0 | 0 | 0.000250949183 | 0.000316281818 | 0.275396 | 0.182485914 | 0.865851742 |
| 2 | Sheet2 | dI_T_std | 291 | 291 | 0 | 0 | 0.0147109174 | 0.0182268171 | 0.834958542 | 0.791629859 | 8.40292942 |
| 2 | Sheet2 | dI_C_skewness | 291 | 291 | 0 | 0 | 0.00865806221 | 0.0118905822 | 0.960604231 | 0.946887494 | 16.75488 |
| 2 | Sheet2 | dI_T_skewness | 291 | 291 | 0 | 0 | 0.159377726 | 0.203047667 | 0.369706179 | 0.331812183 | 116.478467 |
| 2 | Sheet2 | dI_C_kurtosis | 291 | 291 | 0 | 0 | 0.00826837705 | 0.01137746 | 0.624637243 | 0.518524074 | 0.458142468 |
| 2 | Sheet2 | dI_T_kurtosis | 291 | 291 | 0 | 0 | 0.20822771 | 0.254381848 | 0.352475706 | 0.233414147 | 11.0363997 |
| 2 | Sheet2 | dI_dI_devide_dt | 291 | 291 | 0 | 0 | 0.00119832774 | 0.00319806582 | 0.990257615 | 0.996561278 | 0.847013258 |
| 2 | Sheet2 | dI_entropy | 291 | 291 | 0 | 0 | 2.60952759 | 2.6165414 | -0.26682208 | -0.170085783 | 48.5036099 |
| 2 | Sheet2 | Charge_energy | 291 | 291 | 0 | 0 | 0.00205268562 | 0.00802085385 | 0.999688704 | 0.999968346 | 0.0272891248 |
| 2 | Sheet2 | Charge_Q | 291 | 291 | 0 | 0 | 0.000365325978 | 0.00209093403 | 0.999724738 | 0.999975651 | 0.0192993983 |
| 2 | Sheet2 | Charge_t_mean | 291 | 291 | 0 | 0 | 0.00755690852 | 0.0290447055 | 0.999807794 | 0.999896396 | 0.0354331681 |
| 2 | Sheet2 | Charge_V_mean | 291 | 291 | 0 | 0 | 0.00122047351 | 0.00122944719 | 0.999978746 | 0.999864621 | 0.0297798738 |
| 2 | Sheet2 | Charge_C_mean | 291 | 291 | 0 | 0 | 0.00185014457 | 0.00260052466 | 0.999985515 | 0.999950815 | 0.0690341374 |
| 2 | Sheet2 | Charge_T_mean | 291 | 291 | 0 | 0 | 0.0135872266 | 0.0138177447 | 0.999998699 | 0.999971755 | 0.0450148884 |
| 2 | Sheet2 | Charge_C_std | 291 | 291 | 0 | 0 | 0.00170739275 | 0.00519346982 | 0.997718027 | 0.999764298 | 0.065488811 |
| 2 | Sheet2 | Charge_V_std | 291 | 291 | 0 | 0 | 0.00287039314 | 0.00294067222 | 0.999616576 | 0.997969797 | 1.79729464 |
| 2 | Sheet2 | Charge_T_std | 291 | 291 | 0 | 0 | 0.00225496273 | 0.00273076831 | 0.999904651 | 0.999682492 | 0.0577962657 |
| 2 | Sheet2 | Charge_C_skewness | 291 | 291 | 0 | 0 | 0.00231008817 | 0.00295426389 | 0.999967374 | 0.999957998 | 0.614021569 |
| 2 | Sheet2 | Charge_V_skewness | 291 | 291 | 0 | 0 | 0.0715866933 | 0.0819614316 | 0.998319922 | 0.998701709 | 5.46810253 |
| 2 | Sheet2 | Charge_T_skewness | 291 | 291 | 0 | 0 | 0.00523522823 | 0.00856367457 | 0.998512272 | 0.999467248 | 2.429494 |
| 2 | Sheet2 | Charge_C_kurtosis | 291 | 291 | 0 | 0 | 0.00547848751 | 0.0196656581 | 0.997353173 | 0.999937666 | 0.419710994 |
| 2 | Sheet2 | Charge_V_kurtosis | 291 | 291 | 0 | 0 | 0.457776917 | 0.59911101 | 0.991633065 | 0.999397108 | 13.3301233 |
| 2 | Sheet2 | Charge_T_kurtosis | 291 | 291 | 0 | 0 | 0.00379349011 | 0.0128450664 | 0.992140357 | 0.997278292 | 0.232707637 |
| 2 | Sheet3 | CC_energy | 285 | 285 | 0 | 0 | 0.0670304517 | 0.0767999253 | 0.996668123 | 0.983781822 | 1.13739281 |
| 2 | Sheet3 | CC_Q | 285 | 285 | 0 | 0 | 0.0157674574 | 0.0181180554 | 0.99743323 | 0.986321906 | 1.04442479 |
| 2 | Sheet3 | CC_t_mean | 285 | 285 | 0 | 0 | 0.0787524065 | 0.0905373432 | 0.99742712 | 0.986407557 | 1.04332596 |
| 2 | Sheet3 | CC_V_mean | 285 | 285 | 0 | 0 | 0.00384044107 | 0.00424467443 | 0.996567134 | 0.968289383 | 0.0983364646 |
| 2 | Sheet3 | CC_T_mean | 285 | 285 | 0 | 0 | 0.0520889609 | 0.0600105183 | 0.999757172 | 0.999247306 | 0.152687029 |
| 2 | Sheet3 | CC_V_std | 285 | 285 | 0 | 0 | 0.00131181087 | 0.00154947057 | 0.976622524 | 0.883089779 | 0.973701948 |
| 2 | Sheet3 | CC_T_std | 285 | 285 | 0 | 0 | 0.0136980773 | 0.0351776525 | 0.981609693 | 0.99441324 | 0.390038946 |
| 2 | Sheet3 | CC_V_skewness | 285 | 285 | 0 | 0 | 0.110304096 | 0.117599528 | 0.993859139 | 0.983499303 | 31.2239031 |
| 2 | Sheet3 | CC_T_skewness | 285 | 285 | 0 | 0 | 0.0082865736 | 0.00967242598 | 0.990644233 | 0.989209308 | 1.80636481 |
| 2 | Sheet3 | CC_V_kurtosis | 285 | 285 | 0 | 0 | 0.19090528 | 0.210898272 | 0.836568283 | 0.777805886 | 7.53881842 |
| 2 | Sheet3 | CC_T_kurtosis | 285 | 285 | 0 | 0 | 0.0124522587 | 0.0151071591 | 0.975208896 | 0.985997007 | 0.628345579 |
| 2 | Sheet3 | CC_CCCT | 285 | 285 | 0 | 0 | 0.157645807 | 0.181153601 | 0.997433338 | 0.986324195 | 1.0442488 |
| 2 | Sheet3 | CC_entropy | 285 | 285 | 0 | 0 | 5.02542594 | 5.0254936 | 0.887062156 | 0.922932571 | 67.0237935 |
| 2 | Sheet3 | dV_energy | 285 | 285 | 0 | 0 | 0.00611866202 | 0.00672159737 | 0.999626659 | 0.995278424 | 0.541155559 |
| 2 | Sheet3 | dV_Q | 285 | 285 | 0 | 0 | 0.00154607064 | 0.0016989543 | 0.999627335 | 0.995150768 | 0.539481627 |
| 2 | Sheet3 | dV_t_mean | 285 | 285 | 0 | 0 | 0.00769582023 | 0.00848609426 | 0.999612368 | 0.995012491 | 0.537063126 |
| 2 | Sheet3 | dV_V_mean | 285 | 285 | 0 | 0 | 0.000118221295 | 0.000145748785 | 0.609369206 | 0.520565677 | 0.00299647532 |
| 2 | Sheet3 | dV_T_mean | 285 | 285 | 0 | 0 | 0.00796583684 | 0.00971589166 | 0.999987161 | 0.999903969 | 0.0219595604 |
| 2 | Sheet3 | dV_V_std | 285 | 285 | 0 | 0 | 0.000107091981 | 0.000126811825 | 0.562829342 | 0.555344803 | 0.371496893 |
| 2 | Sheet3 | dV_T_std | 285 | 285 | 0 | 0 | 0.0107718062 | 0.0236443451 | 0.993103315 | 0.99147977 | 2.0179156 |
| 2 | Sheet3 | dV_V_skewness | 285 | 285 | 0 | 0 | 0.00159646378 | 0.0019594408 | 0.935926535 | 0.913519986 | 0.81969102 |
| 2 | Sheet3 | dV_T_skewness | 285 | 285 | 0 | 0 | 0.043608812 | 0.0674241075 | 0.925083171 | 0.943487276 | 29.8219111 |
| 2 | Sheet3 | dV_V_kurtosis | 285 | 285 | 0 | 0 | 0.00166813373 | 0.00209318654 | 0.93482917 | 0.92679685 | 0.0906718159 |
| 2 | Sheet3 | dV_T_kurtosis | 285 | 285 | 0 | 0 | 0.0515546441 | 0.0692674296 | 0.901631599 | 0.914964206 | 2.7973826 |
| 2 | Sheet3 | dV_dV_devide_dt | 285 | 285 | 0 | 0 | 4.16279551e-05 | 5.27750507e-05 | 0.999858459 | 0.998716344 | 0.119154958 |
| 2 | Sheet3 | dV_entropy | 285 | 285 | 0 | 0 | 4.60634982 | 4.60741059 | -0.0872712766 | -0.35951037 | 62.5379552 |
| 2 | Sheet3 | CV_energy | 285 | 285 | 0 | 0 | 0.0416382709 | 0.0485015535 | 0.991446242 | 0.980601015 | 2.52267311 |
| 2 | Sheet3 | CV_Q | 285 | 285 | 0 | 0 | 0.00991369645 | 0.0115477586 | 0.991445911 | 0.980631081 | 2.52258317 |
| 2 | Sheet3 | CV_t_mean | 285 | 285 | 0 | 0 | 0.0560521513 | 0.0644898913 | 0.999917584 | 0.99947384 | 0.42913681 |
| 2 | Sheet3 | CV_C_mean | 285 | 285 | 0 | 0 | 0.0147513342 | 0.0172729986 | 0.986537266 | 0.93128917 | 1.60975498 |
| 2 | Sheet3 | CV_T_mean | 285 | 285 | 0 | 0 | 0.0276028834 | 0.0325654862 | 0.999959002 | 0.999767764 | 0.0897317729 |
| 2 | Sheet3 | CV_C_std | 285 | 285 | 0 | 0 | 0.028539555 | 0.033186755 | 0.906827314 | 0.837400405 | 2.36618998 |
| 2 | Sheet3 | CV_T_std | 285 | 285 | 0 | 0 | 0.0164534589 | 0.0201511796 | 0.998941046 | 0.997943569 | 0.384202585 |
| 2 | Sheet3 | CV_C_skewness | 285 | 285 | 0 | 0 | 0.0171893028 | 0.0200543537 | 0.997340425 | 0.974327007 | 0.792474463 |
| 2 | Sheet3 | CV_T_skewness | 285 | 285 | 0 | 0 | 0.00736297293 | 0.0114396538 | 0.99839443 | 0.997708222 | 1.17174469 |
| 2 | Sheet3 | CV_C_kurtosis | 285 | 285 | 0 | 0 | 0.090449509 | 0.105683607 | 0.997438695 | 0.970257171 | 1.23162511 |
| 2 | Sheet3 | CV_T_kurtosis | 285 | 285 | 0 | 0 | 0.0134872222 | 0.0164045404 | 0.998699151 | 0.993815673 | 0.660263215 |
| 2 | Sheet3 | CV_CVCT | 285 | 285 | 0 | 0 | 0.10458995 | 0.121675964 | 0.999919081 | 0.999442348 | 0.400498467 |
| 2 | Sheet3 | CV_entropy | 285 | 285 | 0 | 0 | 4.56532617 | 4.56576447 | 0.990703547 | 0.966110153 | 72.9312652 |
| 2 | Sheet3 | dI_energy | 285 | 285 | 0 | 0 | 0.00114288607 | 0.0015361583 | 0.985016789 | 0.954824864 | 3.01949299 |
| 2 | Sheet3 | dI_Q | 285 | 285 | 0 | 0 | 0.000272125013 | 0.000365756756 | 0.985015908 | 0.95466066 | 3.01954197 |
| 2 | Sheet3 | dI_t_mean | 285 | 285 | 0 | 0 | 0.00855947726 | 0.0114780187 | 0.985281391 | 0.951680318 | 3.00353435 |
| 2 | Sheet3 | dI_C_mean | 285 | 285 | 0 | 0 | 0.000568425277 | 0.000704671572 | 0.612506391 | 0.49804083 | 0.0599071893 |
| 2 | Sheet3 | dI_T_mean | 285 | 285 | 0 | 0 | 0.0190680027 | 0.0235410491 | 0.999912601 | 0.999732773 | 0.0568370062 |
| 2 | Sheet3 | dI_C_std | 285 | 285 | 0 | 0 | 0.000305196996 | 0.000380791437 | 0.0945816539 | 0.119234139 | 1.05466266 |
| 2 | Sheet3 | dI_T_std | 285 | 285 | 0 | 0 | 0.0147545653 | 0.0189301015 | 0.897729996 | 0.863058477 | 9.0532708 |
| 2 | Sheet3 | dI_C_skewness | 285 | 285 | 0 | 0 | 0.00904818131 | 0.0114695501 | 0.900445309 | 0.746408891 | 20.3975901 |
| 2 | Sheet3 | dI_T_skewness | 285 | 285 | 0 | 0 | 0.219904053 | 0.295498109 | 0.378166466 | 0.370243174 | 98.1910055 |
| 2 | Sheet3 | dI_C_kurtosis | 285 | 285 | 0 | 0 | 0.010669159 | 0.0139664852 | 0.227393366 | 0.198847631 | 0.592475608 |
| 2 | Sheet3 | dI_T_kurtosis | 285 | 285 | 0 | 0 | 0.252876556 | 0.353500088 | 0.382137491 | 0.436188649 | 12.8324928 |
| 2 | Sheet3 | dI_dI_devide_dt | 285 | 285 | 0 | 0 | 0.00113424144 | 0.0016388994 | 0.99702015 | 0.988971666 | 0.654549277 |
| 2 | Sheet3 | dI_entropy | 285 | 285 | 0 | 0 | 2.31461205 | 2.32196225 | -0.326538698 | -0.177538401 | 45.5119341 |
| 2 | Sheet3 | Charge_energy | 285 | 285 | 0 | 0 | 0.00119727456 | 0.00138456523 | 0.9999976 | 0.999846558 | 0.0158555884 |
| 2 | Sheet3 | Charge_Q | 285 | 285 | 0 | 0 | 0.000155423407 | 0.000179450464 | 0.999998518 | 0.999885437 | 0.00816130096 |
| 2 | Sheet3 | Charge_t_mean | 285 | 285 | 0 | 0 | 0.00427427455 | 0.00515519047 | 0.999998632 | 0.999967471 | 0.0207304493 |
| 2 | Sheet3 | Charge_V_mean | 285 | 285 | 0 | 0 | 0.00106777914 | 0.00107973041 | 0.999987091 | 0.999893731 | 0.0261106094 |
| 2 | Sheet3 | Charge_C_mean | 285 | 285 | 0 | 0 | 0.00148558283 | 0.00184490302 | 0.999997914 | 0.999952309 | 0.0530337279 |
| 2 | Sheet3 | Charge_T_mean | 285 | 285 | 0 | 0 | 0.0170716274 | 0.0173692944 | 0.999999032 | 0.999979265 | 0.0533549713 |
| 2 | Sheet3 | Charge_C_std | 285 | 285 | 0 | 0 | 0.000837796908 | 0.000978154335 | 0.999979961 | 0.999080904 | 0.0320300423 |
| 2 | Sheet3 | Charge_V_std | 285 | 285 | 0 | 0 | 0.0022762178 | 0.00234860061 | 0.999738534 | 0.99845003 | 1.39116668 |
| 2 | Sheet3 | Charge_T_std | 285 | 285 | 0 | 0 | 0.00397072386 | 0.00479279686 | 0.999962026 | 0.999851224 | 0.0914510301 |
| 2 | Sheet3 | Charge_C_skewness | 285 | 285 | 0 | 0 | 0.00188908991 | 0.00215505083 | 0.999998439 | 0.999960603 | 0.660502184 |
| 2 | Sheet3 | Charge_V_skewness | 285 | 285 | 0 | 0 | 0.0470079154 | 0.0513288092 | 0.999806353 | 0.999715407 | 4.12383987 |
| 2 | Sheet3 | Charge_T_skewness | 285 | 285 | 0 | 0 | 0.00419976401 | 0.00446578612 | 0.999926706 | 0.999740289 | 2.8693242 |
| 2 | Sheet3 | Charge_C_kurtosis | 285 | 285 | 0 | 0 | 0.00201248091 | 0.00282217599 | 0.999998702 | 0.999934684 | 0.158390896 |
| 2 | Sheet3 | Charge_V_kurtosis | 285 | 285 | 0 | 0 | 0.26600344 | 0.308740905 | 0.999612342 | 0.999532936 | 9.26461643 |
| 2 | Sheet3 | Charge_T_kurtosis | 285 | 285 | 0 | 0 | 0.00215595964 | 0.00570340892 | 0.993423079 | 0.997371789 | 0.133869061 |
| 2 | Sheet4 | CC_energy | 321 | 321 | 0 | 0 | 0.0643533718 | 0.0745743307 | 0.99667805 | 0.990850482 | 1.12575357 |
| 2 | Sheet4 | CC_Q | 321 | 321 | 0 | 0 | 0.0151244413 | 0.0175880934 | 0.997420458 | 0.992186684 | 1.03541382 |
| 2 | Sheet4 | CC_t_mean | 321 | 321 | 0 | 0 | 0.0755956525 | 0.0878887434 | 0.997425836 | 0.992111582 | 1.03507722 |
| 2 | Sheet4 | CC_V_mean | 321 | 321 | 0 | 0 | 0.00377010814 | 0.00416974631 | 0.996793434 | 0.980381451 | 0.0962935104 |
| 2 | Sheet4 | CC_T_mean | 321 | 321 | 0 | 0 | 0.0389008537 | 0.0457651826 | 0.999909913 | 0.999587856 | 0.124453519 |
| 2 | Sheet4 | CC_V_std | 321 | 321 | 0 | 0 | 0.0013215677 | 0.00154671627 | 0.980158494 | 0.910861946 | 0.989324882 |
| 2 | Sheet4 | CC_T_std | 321 | 321 | 0 | 0 | 0.0151727239 | 0.0443950708 | 0.953614334 | 0.993052981 | 0.591785496 |
| 2 | Sheet4 | CC_V_skewness | 321 | 321 | 0 | 0 | 0.118758337 | 0.124596321 | 0.989793273 | 0.932420038 | 46.3569137 |
| 2 | Sheet4 | CC_T_skewness | 321 | 321 | 0 | 0 | 0.00896140867 | 0.0125430996 | 0.983386415 | 0.99307564 | 2.42399285 |
| 2 | Sheet4 | CC_V_kurtosis | 321 | 321 | 0 | 0 | 0.223683043 | 0.240291414 | 0.790980252 | 0.634823243 | 8.80135036 |
| 2 | Sheet4 | CC_T_kurtosis | 321 | 321 | 0 | 0 | 0.0105029527 | 0.0158870492 | 0.967200812 | 0.986273998 | 0.558518957 |
| 2 | Sheet4 | CC_CCCT | 321 | 321 | 0 | 0 | 0.15122192 | 0.175859413 | 0.997420761 | 0.992150656 | 1.03528191 |
| 2 | Sheet4 | CC_entropy | 321 | 321 | 0 | 0 | 5.02547165 | 5.02554148 | 0.773432764 | 0.903321623 | 67.0045289 |
| 2 | Sheet4 | dV_energy | 321 | 321 | 0 | 0 | 0.00729876405 | 0.00796358565 | 0.999558889 | 0.994218015 | 0.599362796 |
| 2 | Sheet4 | dV_Q | 321 | 321 | 0 | 0 | 0.00184548637 | 0.00201404121 | 0.999558995 | 0.994328307 | 0.597896484 |
| 2 | Sheet4 | dV_t_mean | 321 | 321 | 0 | 0 | 0.00924737125 | 0.0100980444 | 0.999554252 | 0.993710816 | 0.599209597 |
| 2 | Sheet4 | dV_V_mean | 321 | 321 | 0 | 0 | 0.000121949612 | 0.000169957515 | 0.900436133 | 0.70685008 | 0.00309105923 |
| 2 | Sheet4 | dV_T_mean | 321 | 321 | 0 | 0 | 0.00789624508 | 0.00946589009 | 0.999990891 | 0.999907485 | 0.0242189873 |
| 2 | Sheet4 | dV_V_std | 321 | 321 | 0 | 0 | 0.000138005895 | 0.000158796228 | 0.667944334 | 0.621912913 | 0.480900619 |
| 2 | Sheet4 | dV_T_std | 321 | 321 | 0 | 0 | 0.00721356445 | 0.00991808523 | 0.998087428 | 0.990986533 | 1.50856948 |
| 2 | Sheet4 | dV_V_skewness | 321 | 321 | 0 | 0 | 0.00196429728 | 0.00388859287 | 0.968675843 | 0.902197755 | 0.982151218 |
| 2 | Sheet4 | dV_T_skewness | 321 | 321 | 0 | 0 | 0.0419423602 | 0.0576506123 | 0.886723212 | 0.899271855 | 39.2461656 |
| 2 | Sheet4 | dV_V_kurtosis | 321 | 321 | 0 | 0 | 0.00173208779 | 0.00216352669 | 0.850898388 | 0.817943127 | 0.0936876157 |
| 2 | Sheet4 | dV_T_kurtosis | 321 | 321 | 0 | 0 | 0.0482142418 | 0.0647137937 | 0.836922106 | 0.818398081 | 2.6309689 |
| 2 | Sheet4 | dV_dV_devide_dt | 321 | 321 | 0 | 0 | 4.91452496e-05 | 5.98818323e-05 | 0.999769954 | 0.998175371 | 0.151644814 |
| 2 | Sheet4 | dV_entropy | 321 | 321 | 0 | 0 | 4.68952608 | 4.69045846 | 0.821088331 | 0.629174468 | 62.9615055 |
| 2 | Sheet4 | CV_energy | 321 | 321 | 0 | 0 | 0.0409972656 | 0.0477856909 | 0.984549419 | 0.980770375 | 2.45496018 |
| 2 | Sheet4 | CV_Q | 321 | 321 | 0 | 0 | 0.00976133495 | 0.0113774919 | 0.984544488 | 0.980763482 | 2.45490859 |
| 2 | Sheet4 | CV_t_mean | 321 | 321 | 0 | 0 | 0.0555342691 | 0.0638759533 | 0.999835792 | 0.998782797 | 0.433473239 |
| 2 | Sheet4 | CV_C_mean | 321 | 321 | 0 | 0 | 0.0147467553 | 0.0174934183 | 0.963266055 | 0.856748854 | 1.57174006 |
| 2 | Sheet4 | CV_T_mean | 321 | 321 | 0 | 0 | 0.0212294877 | 0.0251716585 | 0.999973993 | 0.999808077 | 0.0744810377 |
| 2 | Sheet4 | CV_C_std | 321 | 321 | 0 | 0 | 0.0279923276 | 0.0329848817 | 0.724345284 | 0.626266907 | 2.28635448 |
| 2 | Sheet4 | CV_T_std | 321 | 321 | 0 | 0 | 0.0128442714 | 0.0151961779 | 0.99862054 | 0.996242817 | 0.37937145 |
| 2 | Sheet4 | CV_C_skewness | 321 | 321 | 0 | 0 | 0.0140912837 | 0.0165356454 | 0.99552653 | 0.962540634 | 0.657496316 |
| 2 | Sheet4 | CV_T_skewness | 321 | 321 | 0 | 0 | 0.00707907536 | 0.0088064613 | 0.998047869 | 0.992753019 | 1.09461073 |
| 2 | Sheet4 | CV_C_kurtosis | 321 | 321 | 0 | 0 | 0.0697997035 | 0.081410852 | 0.995907071 | 0.959148793 | 0.976216115 |
| 2 | Sheet4 | CV_T_kurtosis | 321 | 321 | 0 | 0 | 0.0157771524 | 0.0228195772 | 0.99330555 | 0.979566596 | 0.780538464 |
| 2 | Sheet4 | CV_CVCT | 321 | 321 | 0 | 0 | 0.102352119 | 0.11916504 | 0.999842611 | 0.99879241 | 0.399597354 |
| 2 | Sheet4 | CV_entropy | 321 | 321 | 0 | 0 | 4.6057919 | 4.60591409 | 0.987742675 | 0.925430058 | 72.7544552 |
| 2 | Sheet4 | dI_energy | 321 | 321 | 0 | 0 | 0.000934599623 | 0.00105760906 | 0.997072737 | 0.979021304 | 2.19143026 |
| 2 | Sheet4 | dI_Q | 321 | 321 | 0 | 0 | 0.000222530253 | 0.000251819997 | 0.997072153 | 0.979016225 | 2.19142885 |
| 2 | Sheet4 | dI_t_mean | 321 | 321 | 0 | 0 | 0.0069959799 | 0.00792755034 | 0.997062553 | 0.978639358 | 2.17846554 |
| 2 | Sheet4 | dI_C_mean | 321 | 321 | 0 | 0 | 0.000493128625 | 0.000619072578 | 0.631700843 | 0.470549906 | 0.051980478 |
| 2 | Sheet4 | dI_T_mean | 321 | 321 | 0 | 0 | 0.0155997201 | 0.0188134863 | 0.999946934 | 0.999720551 | 0.050970892 |
| 2 | Sheet4 | dI_C_std | 321 | 321 | 0 | 0 | 0.000285042172 | 0.000345290938 | 0.125457761 | 0.09927132 | 0.984531847 |
| 2 | Sheet4 | dI_T_std | 321 | 321 | 0 | 0 | 0.0137758563 | 0.0168303248 | 0.793966855 | 0.738341406 | 9.21049741 |
| 2 | Sheet4 | dI_C_skewness | 321 | 321 | 0 | 0 | 0.00777499725 | 0.0100270184 | 0.912581336 | 0.804303456 | 15.816439 |
| 2 | Sheet4 | dI_T_skewness | 321 | 321 | 0 | 0 | 0.229500644 | 0.285312691 | 0.327946915 | 0.288767269 | 106.33923 |
| 2 | Sheet4 | dI_C_kurtosis | 321 | 321 | 0 | 0 | 0.0080464189 | 0.0101170977 | 0.480412054 | 0.428936408 | 0.446386117 |
| 2 | Sheet4 | dI_T_kurtosis | 321 | 321 | 0 | 0 | 0.232677605 | 0.304832798 | 0.376336914 | 0.354255311 | 12.009376 |
| 2 | Sheet4 | dI_dI_devide_dt | 321 | 321 | 0 | 0 | 0.000889999608 | 0.00114676518 | 0.998641619 | 0.99314272 | 0.57293877 |
| 2 | Sheet4 | dI_entropy | 321 | 321 | 0 | 0 | 2.4797049 | 2.48912575 | -0.413670663 | -0.131231476 | 47.2261549 |
| 2 | Sheet4 | Charge_energy | 321 | 321 | 0 | 0 | 0.00111621562 | 0.00127264376 | 0.999997689 | 0.999982585 | 0.015096966 |
| 2 | Sheet4 | Charge_Q | 321 | 321 | 0 | 0 | 0.000132722516 | 0.000155037318 | 0.999998536 | 0.99998186 | 0.00713541479 |
| 2 | Sheet4 | Charge_t_mean | 321 | 321 | 0 | 0 | 0.00493308775 | 0.0070215631 | 0.999988982 | 0.999914923 | 0.0245143115 |
| 2 | Sheet4 | Charge_V_mean | 321 | 321 | 0 | 0 | 0.00109953531 | 0.00110664293 | 0.999985752 | 0.999927077 | 0.026852697 |
| 2 | Sheet4 | Charge_C_mean | 321 | 321 | 0 | 0 | 0.0015198464 | 0.00193077894 | 0.999994573 | 0.999942677 | 0.0545065051 |
| 2 | Sheet4 | Charge_T_mean | 321 | 321 | 0 | 0 | 0.0120026089 | 0.012316872 | 0.999999222 | 0.999985125 | 0.0406981525 |
| 2 | Sheet4 | Charge_C_std | 321 | 321 | 0 | 0 | 0.00105584122 | 0.00191848035 | 0.999452558 | 0.999849073 | 0.0404099918 |
| 2 | Sheet4 | Charge_V_std | 321 | 321 | 0 | 0 | 0.00242337661 | 0.00247061573 | 0.999820101 | 0.998110161 | 1.52547667 |
| 2 | Sheet4 | Charge_T_std | 321 | 321 | 0 | 0 | 0.00231153191 | 0.0028329443 | 0.999951447 | 0.999695971 | 0.0683003756 |
| 2 | Sheet4 | Charge_C_skewness | 321 | 321 | 0 | 0 | 0.00192244142 | 0.00218588464 | 0.999994747 | 0.999944491 | 0.646035147 |
| 2 | Sheet4 | Charge_V_skewness | 321 | 321 | 0 | 0 | 0.0537430156 | 0.0574948207 | 0.999706239 | 0.999756559 | 4.49492428 |
| 2 | Sheet4 | Charge_T_skewness | 321 | 321 | 0 | 0 | 0.00517348765 | 0.00915119018 | 0.997596696 | 0.99938904 | 3.46363379 |
| 2 | Sheet4 | Charge_C_kurtosis | 321 | 321 | 0 | 0 | 0.00311267478 | 0.0098826468 | 0.998661761 | 0.9999405 | 0.247910615 |
| 2 | Sheet4 | Charge_V_kurtosis | 321 | 321 | 0 | 0 | 0.312962762 | 0.361544769 | 0.998662962 | 0.999829844 | 10.3108731 |
| 2 | Sheet4 | Charge_T_kurtosis | 321 | 321 | 0 | 0 | 0.00266030051 | 0.00829240718 | 0.988853499 | 0.995776569 | 0.164697573 |
| 2 | Sheet5 | CC_energy | 296 | 296 | 0 | 0 | 0.0656927067 | 0.0765887323 | 0.996260436 | 0.987881564 | 1.13529111 |
| 2 | Sheet5 | CC_Q | 296 | 296 | 0 | 0 | 0.0154351852 | 0.0180579898 | 0.997097295 | 0.990192927 | 1.04302344 |
| 2 | Sheet5 | CC_t_mean | 296 | 296 | 0 | 0 | 0.077191174 | 0.0902602276 | 0.997104415 | 0.990359616 | 1.04324636 |
| 2 | Sheet5 | CC_V_mean | 296 | 296 | 0 | 0 | 0.00388320892 | 0.00431864006 | 0.996258223 | 0.970261016 | 0.0992693624 |
| 2 | Sheet5 | CC_T_mean | 296 | 296 | 0 | 0 | 0.0435282963 | 0.0513002151 | 0.999818726 | 0.998916328 | 0.136069785 |
| 2 | Sheet5 | CC_V_std | 296 | 296 | 0 | 0 | 0.00130017299 | 0.00156968205 | 0.981169379 | 0.910957953 | 0.95775151 |
| 2 | Sheet5 | CC_T_std | 296 | 296 | 0 | 0 | 0.0127361196 | 0.0334147371 | 0.954769812 | 0.990903653 | 0.440533477 |
| 2 | Sheet5 | CC_V_skewness | 296 | 296 | 0 | 0 | 0.127400722 | 0.133775496 | 0.989392681 | 0.914441212 | 54.9534875 |
| 2 | Sheet5 | CC_T_skewness | 296 | 296 | 0 | 0 | 0.00918643392 | 0.0127948479 | 0.976514016 | 0.990130461 | 2.19716565 |
| 2 | Sheet5 | CC_V_kurtosis | 296 | 296 | 0 | 0 | 0.253211992 | 0.271312171 | 0.8769287 | 0.784649056 | 9.71205774 |
| 2 | Sheet5 | CC_T_kurtosis | 296 | 296 | 0 | 0 | 0.011851843 | 0.0168307827 | 0.96132738 | 0.987298429 | 0.618965505 |
| 2 | Sheet5 | CC_CCCT | 296 | 296 | 0 | 0 | 0.154331108 | 0.18056095 | 0.997097248 | 0.990168488 | 1.04290083 |
| 2 | Sheet5 | CC_entropy | 296 | 296 | 0 | 0 | 5.01315231 | 5.01323932 | 0.801625965 | 0.918493917 | 67.1424736 |
| 2 | Sheet5 | dV_energy | 296 | 296 | 0 | 0 | 0.00595192957 | 0.00658220237 | 0.999602603 | 0.992224582 | 0.499724274 |
| 2 | Sheet5 | dV_Q | 296 | 296 | 0 | 0 | 0.00150686723 | 0.0016661143 | 0.999603914 | 0.993011439 | 0.499143442 |
| 2 | Sheet5 | dV_t_mean | 296 | 296 | 0 | 0 | 0.00750076073 | 0.00832857767 | 0.999594112 | 0.993099223 | 0.496919859 |
| 2 | Sheet5 | dV_V_mean | 296 | 296 | 0 | 0 | 0.000110938574 | 0.000140936202 | 0.815725814 | 0.472053216 | 0.00281192924 |
| 2 | Sheet5 | dV_T_mean | 296 | 296 | 0 | 0 | 0.00775187192 | 0.00955038738 | 0.999987349 | 0.999806702 | 0.0230673205 |
| 2 | Sheet5 | dV_V_std | 296 | 296 | 0 | 0 | 0.000104192875 | 0.000123258321 | 0.563636838 | 0.537760102 | 0.362211775 |
| 2 | Sheet5 | dV_T_std | 296 | 296 | 0 | 0 | 0.0102050313 | 0.0234774584 | 0.993226755 | 0.994445524 | 2.0076541 |
| 2 | Sheet5 | dV_V_skewness | 296 | 296 | 0 | 0 | 0.00178808505 | 0.00296203446 | 0.952940461 | 0.882579924 | 0.89466772 |
| 2 | Sheet5 | dV_T_skewness | 296 | 296 | 0 | 0 | 0.0434655237 | 0.0889577278 | 0.910848515 | 0.928389252 | 25.246977 |
| 2 | Sheet5 | dV_V_kurtosis | 296 | 296 | 0 | 0 | 0.00178229378 | 0.00219819523 | 0.837775619 | 0.850419449 | 0.096526314 |
| 2 | Sheet5 | dV_T_kurtosis | 296 | 296 | 0 | 0 | 0.0541184928 | 0.0975522601 | 0.897770624 | 0.945684976 | 2.9197385 |
| 2 | Sheet5 | dV_dV_devide_dt | 296 | 296 | 0 | 0 | 4.70183913e-05 | 5.79851952e-05 | 0.999846795 | 0.998144049 | 0.141902281 |
| 2 | Sheet5 | dV_entropy | 296 | 296 | 0 | 0 | 4.66763868 | 4.66846148 | 0.754307449 | 0.377678978 | 62.8514297 |
| 2 | Sheet5 | CV_energy | 296 | 296 | 0 | 0 | 0.038870778 | 0.0456743513 | 0.980609731 | 0.976924536 | 2.35410533 |
| 2 | Sheet5 | CV_Q | 296 | 296 | 0 | 0 | 0.0092546113 | 0.0108743145 | 0.980607671 | 0.976919909 | 2.35400573 |
| 2 | Sheet5 | CV_t_mean | 296 | 296 | 0 | 0 | 0.0530907583 | 0.063757018 | 0.999777615 | 0.998645062 | 0.409481798 |
| 2 | Sheet5 | CV_C_mean | 296 | 296 | 0 | 0 | 0.0140309369 | 0.0164293935 | 0.977212079 | 0.89175169 | 1.52755414 |
| 2 | Sheet5 | CV_T_mean | 296 | 296 | 0 | 0 | 0.0223190395 | 0.0264440071 | 0.999960075 | 0.999562737 | 0.0773617671 |
| 2 | Sheet5 | CV_C_std | 296 | 296 | 0 | 0 | 0.0271656114 | 0.0316201278 | 0.832213999 | 0.734443843 | 2.24186588 |
| 2 | Sheet5 | CV_T_std | 296 | 296 | 0 | 0 | 0.0139393521 | 0.016528793 | 0.998062544 | 0.994875461 | 0.378677587 |
| 2 | Sheet5 | CV_C_skewness | 296 | 296 | 0 | 0 | 0.0138271173 | 0.0160354932 | 0.99711677 | 0.971216517 | 0.63086697 |
| 2 | Sheet5 | CV_T_skewness | 296 | 296 | 0 | 0 | 0.00663182946 | 0.00795689892 | 0.998921603 | 0.990969706 | 0.932872403 |
| 2 | Sheet5 | CV_C_kurtosis | 296 | 296 | 0 | 0 | 0.0704617954 | 0.0814555657 | 0.997360124 | 0.971735217 | 0.952449514 |
| 2 | Sheet5 | CV_T_kurtosis | 296 | 296 | 0 | 0 | 0.0152235054 | 0.0192752784 | 0.997554695 | 0.97892875 | 0.721203667 |
| 2 | Sheet5 | CV_CVCT | 296 | 296 | 0 | 0 | 0.0986931287 | 0.120374929 | 0.999785206 | 0.998649226 | 0.380721871 |
| 2 | Sheet5 | CV_entropy | 296 | 296 | 0 | 0 | 4.58604256 | 4.58625865 | 0.991591523 | 0.865524357 | 72.9914362 |
| 2 | Sheet5 | dI_energy | 296 | 296 | 0 | 0 | 0.0011942136 | 0.00149366972 | 0.98464692 | 0.980324084 | 2.96277515 |
| 2 | Sheet5 | dI_Q | 296 | 296 | 0 | 0 | 0.000284341806 | 0.000355639778 | 0.984646307 | 0.980371743 | 2.96279989 |
| 2 | Sheet5 | dI_t_mean | 296 | 296 | 0 | 0 | 0.00892865241 | 0.0111821751 | 0.984702433 | 0.97874716 | 2.94166579 |
| 2 | Sheet5 | dI_C_mean | 296 | 296 | 0 | 0 | 0.000511364267 | 0.000632413227 | 0.731460807 | 0.627476148 | 0.0539095824 |
| 2 | Sheet5 | dI_T_mean | 296 | 296 | 0 | 0 | 0.0176506185 | 0.0213211155 | 0.999885147 | 0.999279556 | 0.0565237223 |
| 2 | Sheet5 | dI_C_std | 296 | 296 | 0 | 0 | 0.000293797253 | 0.000362358739 | 0.0737427388 | 0.0624800455 | 1.01695935 |
| 2 | Sheet5 | dI_T_std | 296 | 296 | 0 | 0 | 0.0142958707 | 0.0175815835 | 0.844854579 | 0.816074121 | 8.92660532 |
| 2 | Sheet5 | dI_C_skewness | 296 | 296 | 0 | 0 | 0.0062567918 | 0.00807353869 | 0.956846138 | 0.921498077 | 12.3885562 |
| 2 | Sheet5 | dI_T_skewness | 296 | 296 | 0 | 0 | 0.192056527 | 0.248399694 | 0.423216863 | 0.422543162 | 100.17776 |
| 2 | Sheet5 | dI_C_kurtosis | 296 | 296 | 0 | 0 | 0.00809771477 | 0.0109928813 | 0.425189374 | 0.371829148 | 0.449201576 |
| 2 | Sheet5 | dI_T_kurtosis | 296 | 296 | 0 | 0 | 0.239004927 | 0.301279117 | 0.489592997 | 0.376740001 | 12.3399944 |
| 2 | Sheet5 | dI_dI_devide_dt | 296 | 296 | 0 | 0 | 0.000678606659 | 0.000977211917 | 0.998384734 | 0.997383108 | 0.419489593 |
| 2 | Sheet5 | dI_entropy | 296 | 296 | 0 | 0 | 2.40921681 | 2.41404579 | -0.206436938 | 0.0191711379 | 46.5094136 |
| 2 | Sheet5 | Charge_energy | 296 | 296 | 0 | 0 | 0.00114121472 | 0.00132503883 | 0.999997261 | 0.999962983 | 0.0153290058 |
| 2 | Sheet5 | Charge_Q | 296 | 296 | 0 | 0 | 0.000153206525 | 0.000174022303 | 0.999998199 | 0.999970386 | 0.00817229206 |
| 2 | Sheet5 | Charge_t_mean | 296 | 296 | 0 | 0 | 0.00610851042 | 0.0283758439 | 0.999759079 | 0.999851353 | 0.02998349 |
| 2 | Sheet5 | Charge_V_mean | 296 | 296 | 0 | 0 | 0.00114694712 | 0.00115313799 | 0.999985164 | 0.99986859 | 0.0280196301 |
| 2 | Sheet5 | Charge_C_mean | 296 | 296 | 0 | 0 | 0.00147967072 | 0.00182220248 | 0.999996924 | 0.999931981 | 0.0532696791 |
| 2 | Sheet5 | Charge_T_mean | 296 | 296 | 0 | 0 | 0.0135777032 | 0.0138637633 | 0.999999026 | 0.999968073 | 0.0452981121 |
| 2 | Sheet5 | Charge_C_std | 296 | 296 | 0 | 0 | 0.00124787078 | 0.00340352505 | 0.998322924 | 0.999795942 | 0.0476623656 |
| 2 | Sheet5 | Charge_V_std | 296 | 296 | 0 | 0 | 0.00258018349 | 0.00262797652 | 0.999767533 | 0.998088073 | 1.60213397 |
| 2 | Sheet5 | Charge_T_std | 296 | 296 | 0 | 0 | 0.00234508603 | 0.00298071894 | 0.999959891 | 0.999761703 | 0.0628229549 |
| 2 | Sheet5 | Charge_C_skewness | 296 | 296 | 0 | 0 | 0.00198890742 | 0.00272855125 | 0.999953697 | 0.999939269 | 0.655248531 |
| 2 | Sheet5 | Charge_V_skewness | 296 | 296 | 0 | 0 | 0.0597122268 | 0.0650414342 | 0.99905169 | 0.998409191 | 4.96979783 |
| 2 | Sheet5 | Charge_T_skewness | 296 | 296 | 0 | 0 | 0.00486156884 | 0.00660061903 | 0.999356012 | 0.99919164 | 2.61559286 |
| 2 | Sheet5 | Charge_C_kurtosis | 296 | 296 | 0 | 0 | 0.00347667362 | 0.0133344056 | 0.998012494 | 0.999936145 | 0.276401054 |
| 2 | Sheet5 | Charge_V_kurtosis | 296 | 296 | 0 | 0 | 0.35081113 | 0.41524262 | 0.996562119 | 0.999189783 | 11.4109622 |
| 2 | Sheet5 | Charge_T_kurtosis | 296 | 296 | 0 | 0 | 0.00337176184 | 0.0109363494 | 0.989912004 | 0.996994511 | 0.210609061 |
| 2 | Sheet6 | CC_energy | 321 | 321 | 0 | 0 | 0.0666620965 | 0.0788176208 | 0.995892874 | 0.989263579 | 1.15546075 |
| 2 | Sheet6 | CC_Q | 321 | 321 | 0 | 0 | 0.015578777 | 0.0184045861 | 0.996913781 | 0.990805403 | 1.05657002 |
| 2 | Sheet6 | CC_t_mean | 321 | 321 | 0 | 0 | 0.0779049594 | 0.0920667692 | 0.99690511 | 0.990775102 | 1.05672404 |
| 2 | Sheet6 | CC_V_mean | 321 | 321 | 0 | 0 | 0.00394201779 | 0.004416276 | 0.996280826 | 0.968998157 | 0.100709045 |
| 2 | Sheet6 | CC_T_mean | 321 | 321 | 0 | 0 | 0.0419424983 | 0.0511208155 | 0.999846479 | 0.999290721 | 0.133356013 |
| 2 | Sheet6 | CC_V_std | 321 | 321 | 0 | 0 | 0.00138557547 | 0.00167725003 | 0.980816259 | 0.898914132 | 1.01947552 |
| 2 | Sheet6 | CC_T_std | 321 | 321 | 0 | 0 | 0.0121306129 | 0.0276290856 | 0.987477219 | 0.998023452 | 0.44706097 |
| 2 | Sheet6 | CC_V_skewness | 321 | 321 | 0 | 0 | 0.134765902 | 0.144660058 | 0.988323162 | 0.958289219 | 69.2772507 |
| 2 | Sheet6 | CC_T_skewness | 321 | 321 | 0 | 0 | 0.0101548494 | 0.0156433656 | 0.954490511 | 0.979873979 | 2.53345188 |
| 2 | Sheet6 | CC_V_kurtosis | 321 | 321 | 0 | 0 | 0.277707339 | 0.307459636 | 0.871225643 | 0.729985633 | 10.6156382 |
| 2 | Sheet6 | CC_T_kurtosis | 321 | 321 | 0 | 0 | 0.0125271355 | 0.0204999338 | 0.927524541 | 0.977815074 | 0.652019001 |
| 2 | Sheet6 | CC_CCCT | 321 | 321 | 0 | 0 | 0.155755979 | 0.184016512 | 0.996914042 | 0.99081554 | 1.05636318 |
| 2 | Sheet6 | CC_entropy | 321 | 321 | 0 | 0 | 5.01789661 | 5.0179693 | 0.912006206 | 0.945421316 | 67.1240032 |
| 2 | Sheet6 | dV_energy | 321 | 321 | 0 | 0 | 0.00830090283 | 0.00878760359 | 0.999622744 | 0.994319963 | 0.676930663 |
| 2 | Sheet6 | dV_Q | 321 | 321 | 0 | 0 | 0.00210550529 | 0.00222856331 | 0.999622579 | 0.994385085 | 0.677440197 |
| 2 | Sheet6 | dV_t_mean | 321 | 321 | 0 | 0 | 0.0105647287 | 0.0111880011 | 0.999616422 | 0.993787095 | 0.679856519 |
| 2 | Sheet6 | dV_V_mean | 321 | 321 | 0 | 0 | 0.000121482277 | 0.000197185351 | 0.896717146 | 0.800250298 | 0.00307907226 |
| 2 | Sheet6 | dV_T_mean | 321 | 321 | 0 | 0 | 0.00762004079 | 0.00957727398 | 0.999989638 | 0.999903857 | 0.0231914485 |
| 2 | Sheet6 | dV_V_std | 321 | 321 | 0 | 0 | 0.000145846508 | 0.000162697373 | 0.658315819 | 0.565414725 | 0.5085307 |
| 2 | Sheet6 | dV_T_std | 321 | 321 | 0 | 0 | 0.00976382313 | 0.020815768 | 0.994502676 | 0.993040427 | 1.93072918 |
| 2 | Sheet6 | dV_V_skewness | 321 | 321 | 0 | 0 | 0.00246768866 | 0.00695722016 | 0.925972139 | 0.965021265 | 1.25803822 |
| 2 | Sheet6 | dV_T_skewness | 321 | 321 | 0 | 0 | 0.0363264204 | 0.046076139 | 0.971375165 | 0.962516689 | 22.9749299 |
| 2 | Sheet6 | dV_V_kurtosis | 321 | 321 | 0 | 0 | 0.00177423456 | 0.00227821837 | 0.736300082 | 0.735698752 | 0.0960325691 |
| 2 | Sheet6 | dV_T_kurtosis | 321 | 321 | 0 | 0 | 0.0541464348 | 0.0784919859 | 0.90596054 | 0.925605518 | 2.90742127 |
| 2 | Sheet6 | dV_dV_devide_dt | 321 | 321 | 0 | 0 | 3.47912933e-05 | 4.47686954e-05 | 0.999843942 | 0.997760049 | 0.108176669 |
| 2 | Sheet6 | dV_entropy | 321 | 321 | 0 | 0 | 4.6998806 | 4.70074497 | 0.811848683 | 0.690337801 | 63.0075726 |
| 2 | Sheet6 | CV_energy | 321 | 321 | 0 | 0 | 0.0442493308 | 0.0519661318 | 0.984287718 | 0.976437424 | 2.61134465 |
| 2 | Sheet6 | CV_Q | 321 | 321 | 0 | 0 | 0.0105359781 | 0.0123732707 | 0.984285268 | 0.976424 | 2.61129008 |
| 2 | Sheet6 | CV_t_mean | 321 | 321 | 0 | 0 | 0.0588227578 | 0.0683895487 | 0.99983741 | 0.998389519 | 0.439328824 |
| 2 | Sheet6 | CV_C_mean | 321 | 321 | 0 | 0 | 0.016022372 | 0.0186707109 | 0.964940639 | 0.920508141 | 1.75726161 |
| 2 | Sheet6 | CV_T_mean | 321 | 321 | 0 | 0 | 0.0249179171 | 0.029394122 | 0.999957721 | 0.999594387 | 0.0885071951 |
| 2 | Sheet6 | CV_C_std | 321 | 321 | 0 | 0 | 0.0312616087 | 0.0361855949 | 0.748801929 | 0.748446117 | 2.59778879 |
| 2 | Sheet6 | CV_T_std | 321 | 321 | 0 | 0 | 0.0197958286 | 0.0445009702 | 0.984766665 | 0.997291316 | 0.56163497 |
| 2 | Sheet6 | CV_C_skewness | 321 | 321 | 0 | 0 | 0.0155769563 | 0.018017557 | 0.995483742 | 0.979792985 | 0.702756398 |
| 2 | Sheet6 | CV_T_skewness | 321 | 321 | 0 | 0 | 0.0076507479 | 0.00895953368 | 0.998376504 | 0.99518561 | 1.00954827 |
| 2 | Sheet6 | CV_C_kurtosis | 321 | 321 | 0 | 0 | 0.0773107079 | 0.0890358527 | 0.995827574 | 0.981365734 | 1.02716916 |
| 2 | Sheet6 | CV_T_kurtosis | 321 | 321 | 0 | 0 | 0.0183617421 | 0.0217666664 | 0.996938475 | 0.988562649 | 0.834236005 |
| 2 | Sheet6 | CV_CVCT | 321 | 321 | 0 | 0 | 0.110730275 | 0.129980618 | 0.999839947 | 0.99842081 | 0.413623516 |
| 2 | Sheet6 | CV_entropy | 321 | 321 | 0 | 0 | 4.58926775 | 4.58941779 | 0.985606603 | 0.905786284 | 73.0591048 |
| 2 | Sheet6 | dI_energy | 321 | 321 | 0 | 0 | 0.00106879237 | 0.00124097382 | 0.993620087 | 0.991455999 | 2.45331899 |
| 2 | Sheet6 | dI_Q | 321 | 321 | 0 | 0 | 0.000254491113 | 0.000295487244 | 0.993619689 | 0.991455274 | 2.45332641 |
| 2 | Sheet6 | dI_t_mean | 321 | 321 | 0 | 0 | 0.00804604961 | 0.00933377381 | 0.993713899 | 0.991545883 | 2.45277556 |
| 2 | Sheet6 | dI_C_mean | 321 | 321 | 0 | 0 | 0.000507793137 | 0.000607064705 | 0.842047622 | 0.713528856 | 0.0535186032 |
| 2 | Sheet6 | dI_T_mean | 321 | 321 | 0 | 0 | 0.0171331967 | 0.0208733004 | 0.999920469 | 0.999667491 | 0.0564409711 |
| 2 | Sheet6 | dI_C_std | 321 | 321 | 0 | 0 | 0.000259923536 | 0.00032645609 | 0.123960107 | 0.0609058455 | 0.899653792 |
| 2 | Sheet6 | dI_T_std | 321 | 321 | 0 | 0 | 0.0133575899 | 0.0170469079 | 0.857655751 | 0.833691299 | 8.4228702 |
| 2 | Sheet6 | dI_C_skewness | 321 | 321 | 0 | 0 | 0.00658032 | 0.00860013727 | 0.976136428 | 0.899208365 | 12.5519706 |
| 2 | Sheet6 | dI_T_skewness | 321 | 321 | 0 | 0 | 0.194411339 | 0.245592748 | 0.51701349 | 0.487636051 | 93.7048034 |
| 2 | Sheet6 | dI_C_kurtosis | 321 | 321 | 0 | 0 | 0.00732182399 | 0.00946361179 | 0.594807914 | 0.533837871 | 0.405904285 |
| 2 | Sheet6 | dI_T_kurtosis | 321 | 321 | 0 | 0 | 0.2177174 | 0.286506848 | 0.395806187 | 0.354021731 | 11.2345807 |
| 2 | Sheet6 | dI_dI_devide_dt | 321 | 321 | 0 | 0 | 0.00120711551 | 0.00361671293 | 0.987415066 | 0.998439924 | 0.801094297 |
| 2 | Sheet6 | dI_entropy | 321 | 321 | 0 | 0 | 2.51763063 | 2.5245636 | -0.530408672 | -0.346822587 | 47.6087944 |
| 2 | Sheet6 | Charge_energy | 321 | 321 | 0 | 0 | 0.00195876814 | 0.00773243613 | 0.999692485 | 0.999974241 | 0.026217287 |
| 2 | Sheet6 | Charge_Q | 321 | 321 | 0 | 0 | 0.000241299664 | 0.0012246289 | 0.999896429 | 0.999977325 | 0.0128370491 |
| 2 | Sheet6 | Charge_t_mean | 321 | 321 | 0 | 0 | 0.00436409225 | 0.00540589094 | 0.999996098 | 0.999907213 | 0.0210116827 |
| 2 | Sheet6 | Charge_V_mean | 321 | 321 | 0 | 0 | 0.00117008114 | 0.00117797771 | 0.999984794 | 0.999857056 | 0.0285638043 |
| 2 | Sheet6 | Charge_C_mean | 321 | 321 | 0 | 0 | 0.00160277141 | 0.00193926888 | 0.999996448 | 0.999910025 | 0.0586425413 |
| 2 | Sheet6 | Charge_T_mean | 321 | 321 | 0 | 0 | 0.0124098867 | 0.0126668877 | 0.999999254 | 0.999985488 | 0.0423375132 |
| 2 | Sheet6 | Charge_C_std | 321 | 321 | 0 | 0 | 0.00127094946 | 0.00370015378 | 0.998246063 | 0.999807352 | 0.0486960342 |
| 2 | Sheet6 | Charge_V_std | 321 | 321 | 0 | 0 | 0.00270414599 | 0.0027737502 | 0.999744672 | 0.99814499 | 1.70109461 |
| 2 | Sheet6 | Charge_T_std | 321 | 321 | 0 | 0 | 0.00483249905 | 0.0347421468 | 0.993460424 | 0.999860684 | 0.133589576 |
| 2 | Sheet6 | Charge_C_skewness | 321 | 321 | 0 | 0 | 0.00202665249 | 0.00225957386 | 0.999996802 | 0.999908574 | 0.600385011 |
| 2 | Sheet6 | Charge_V_skewness | 321 | 321 | 0 | 0 | 0.0653859402 | 0.0731734323 | 0.999062221 | 0.998362309 | 5.2181272 |
| 2 | Sheet6 | Charge_T_skewness | 321 | 321 | 0 | 0 | 0.00431393609 | 0.00457378689 | 0.999920547 | 0.999438382 | 2.14417657 |
| 2 | Sheet6 | Charge_C_kurtosis | 321 | 321 | 0 | 0 | 0.0035063751 | 0.0142566473 | 0.997714897 | 0.999905308 | 0.273732881 |
| 2 | Sheet6 | Charge_V_kurtosis | 321 | 321 | 0 | 0 | 0.398290942 | 0.486318789 | 0.996668892 | 0.999130361 | 12.296823 |
| 2 | Sheet6 | Charge_T_kurtosis | 321 | 321 | 0 | 0 | 0.00344307189 | 0.0102035802 | 0.992639337 | 0.996022594 | 0.21264737 |
| 2 | Sheet7 | CC_energy | 318 | 318 | 0 | 0 | 0.064112704 | 0.0746636482 | 0.997313653 | 0.983123486 | 1.09921214 |
| 2 | Sheet7 | CC_Q | 318 | 318 | 0 | 0 | 0.0150921405 | 0.017631253 | 0.99792477 | 0.986444025 | 1.01132238 |
| 2 | Sheet7 | CC_t_mean | 318 | 318 | 0 | 0 | 0.0753639506 | 0.0880536987 | 0.997926676 | 0.986438415 | 1.01005575 |
| 2 | Sheet7 | CC_V_mean | 318 | 318 | 0 | 0 | 0.00357805549 | 0.00401391375 | 0.997431239 | 0.970385402 | 0.091494853 |
| 2 | Sheet7 | CC_T_mean | 318 | 318 | 0 | 0 | 0.0405806088 | 0.0482024217 | 0.999896008 | 0.999464131 | 0.127525465 |
| 2 | Sheet7 | CC_V_std | 318 | 318 | 0 | 0 | 0.00132825721 | 0.00157545856 | 0.979921244 | 0.882118526 | 1.01750529 |
| 2 | Sheet7 | CC_T_std | 318 | 318 | 0 | 0 | 0.0107083529 | 0.0284745876 | 0.972474443 | 0.993413867 | 0.375294267 |
| 2 | Sheet7 | CC_V_skewness | 318 | 318 | 0 | 0 | 0.0923120196 | 0.0991208619 | 0.994215295 | 0.987741746 | 22.0458837 |
| 2 | Sheet7 | CC_T_skewness | 318 | 318 | 0 | 0 | 0.0104275792 | 0.0136682677 | 0.985806957 | 0.991340639 | 2.16077427 |
| 2 | Sheet7 | CC_V_kurtosis | 318 | 318 | 0 | 0 | 0.132824249 | 0.149655662 | 0.509542032 | 0.594333745 | 5.44608335 |
| 2 | Sheet7 | CC_T_kurtosis | 318 | 318 | 0 | 0 | 0.0143860483 | 0.0188592863 | 0.97904971 | 0.986168808 | 0.722348134 |
| 2 | Sheet7 | CC_CCCT | 318 | 318 | 0 | 0 | 0.150900163 | 0.176293075 | 0.99792482 | 0.986429118 | 1.01119699 |
| 2 | Sheet7 | CC_entropy | 318 | 318 | 0 | 0 | 5.0520944 | 5.05213542 | 0.988506002 | 0.947321578 | 66.7358422 |
| 2 | Sheet7 | dV_energy | 318 | 318 | 0 | 0 | 0.00796095258 | 0.00844422329 | 0.999744002 | 0.994427485 | 0.679182432 |
| 2 | Sheet7 | dV_Q | 318 | 318 | 0 | 0 | 0.00201407467 | 0.00213650461 | 0.999744437 | 0.994586583 | 0.677889561 |
| 2 | Sheet7 | dV_t_mean | 318 | 318 | 0 | 0 | 0.0100267306 | 0.0106703717 | 0.999733353 | 0.99478134 | 0.674943727 |
| 2 | Sheet7 | dV_V_mean | 318 | 318 | 0 | 0 | 0.000107132368 | 0.00013278939 | 0.854494758 | 0.727173227 | 0.00271554957 |
| 2 | Sheet7 | dV_T_mean | 318 | 318 | 0 | 0 | 0.00694454009 | 0.00847158463 | 0.999992912 | 0.999896166 | 0.0207208009 |
| 2 | Sheet7 | dV_V_std | 318 | 318 | 0 | 0 | 0.000150640522 | 0.000167519757 | 0.6585433 | 0.629960823 | 0.52405587 |
| 2 | Sheet7 | dV_T_std | 318 | 318 | 0 | 0 | 0.00753409484 | 0.0111206303 | 0.998502719 | 0.988531899 | 1.59695041 |
| 2 | Sheet7 | dV_V_skewness | 318 | 318 | 0 | 0 | 0.00171715071 | 0.00246721361 | 0.969996946 | 0.963622292 | 0.842045204 |
| 2 | Sheet7 | dV_T_skewness | 318 | 318 | 0 | 0 | 0.0403784399 | 0.0519705312 | 0.888468201 | 0.863674707 | 30.0645021 |
| 2 | Sheet7 | dV_V_kurtosis | 318 | 318 | 0 | 0 | 0.00180282168 | 0.00220554776 | 0.916449609 | 0.919836836 | 0.0976694511 |
| 2 | Sheet7 | dV_T_kurtosis | 318 | 318 | 0 | 0 | 0.0535543323 | 0.0847990185 | 0.676394415 | 0.765988328 | 2.90992634 |
| 2 | Sheet7 | dV_dV_devide_dt | 318 | 318 | 0 | 0 | 4.73893037e-05 | 5.6859763e-05 | 0.999865299 | 0.997551548 | 0.140439344 |
| 2 | Sheet7 | dV_entropy | 318 | 318 | 0 | 0 | 4.64626861 | 4.64773272 | 0.639369146 | 0.168898185 | 62.7506633 |
| 2 | Sheet7 | CV_energy | 318 | 318 | 0 | 0 | 0.044573586 | 0.0515981282 | 0.984351932 | 0.968421047 | 2.72715761 |
| 2 | Sheet7 | CV_Q | 318 | 318 | 0 | 0 | 0.0106130217 | 0.0122854854 | 0.984350564 | 0.968422539 | 2.72709756 |
| 2 | Sheet7 | CV_t_mean | 318 | 318 | 0 | 0 | 0.0599948036 | 0.0685533097 | 0.999912729 | 0.999110741 | 0.463970511 |
| 2 | Sheet7 | CV_C_mean | 318 | 318 | 0 | 0 | 0.0163309475 | 0.0191857635 | 0.986826099 | 0.866878725 | 1.7756835 |
| 2 | Sheet7 | CV_T_mean | 318 | 318 | 0 | 0 | 0.0267434694 | 0.0312474775 | 0.99996745 | 0.99969139 | 0.0944850666 |
| 2 | Sheet7 | CV_C_std | 318 | 318 | 0 | 0 | 0.0310232202 | 0.0361536411 | 0.912108241 | 0.762908948 | 2.54197039 |
| 2 | Sheet7 | CV_T_std | 318 | 318 | 0 | 0 | 0.0177031982 | 0.0208720316 | 0.997567212 | 0.996232871 | 0.482484614 |
| 2 | Sheet7 | CV_C_skewness | 318 | 318 | 0 | 0 | 0.0154769353 | 0.0178523972 | 0.998479789 | 0.968634499 | 0.71700675 |
| 2 | Sheet7 | CV_T_skewness | 318 | 318 | 0 | 0 | 0.00799542928 | 0.00935449524 | 0.999309098 | 0.994432709 | 1.06267215 |
| 2 | Sheet7 | CV_C_kurtosis | 318 | 318 | 0 | 0 | 0.0808488169 | 0.0927271788 | 0.998584879 | 0.96504761 | 1.11750359 |
| 2 | Sheet7 | CV_T_kurtosis | 318 | 318 | 0 | 0 | 0.0187970168 | 0.0223443093 | 0.99868361 | 0.986333475 | 0.853456008 |
| 2 | Sheet7 | CV_CVCT | 318 | 318 | 0 | 0 | 0.11193472 | 0.129373269 | 0.999914292 | 0.999123148 | 0.432966867 |
| 2 | Sheet7 | CV_entropy | 318 | 318 | 0 | 0 | 4.56586074 | 4.56625011 | 0.995044726 | 0.941677691 | 73.0077155 |
| 2 | Sheet7 | dI_energy | 318 | 318 | 0 | 0 | 0.000956460053 | 0.00108655032 | 0.992637501 | 0.951701263 | 2.62226007 |
| 2 | Sheet7 | dI_Q | 318 | 318 | 0 | 0 | 0.000227737393 | 0.000258711259 | 0.992637541 | 0.951791196 | 2.6222361 |
| 2 | Sheet7 | dI_t_mean | 318 | 318 | 0 | 0 | 0.00716852652 | 0.0081563106 | 0.992654958 | 0.951977478 | 2.6099669 |
| 2 | Sheet7 | dI_C_mean | 318 | 318 | 0 | 0 | 0.000520215678 | 0.000650630611 | 0.381538598 | 0.338304799 | 0.0548357489 |
| 2 | Sheet7 | dI_T_mean | 318 | 318 | 0 | 0 | 0.0173829241 | 0.0219756147 | 0.999921695 | 0.999490252 | 0.0567507477 |
| 2 | Sheet7 | dI_C_std | 318 | 318 | 0 | 0 | 0.000344045336 | 0.000410390219 | 0.0415942398 | 0.0374639963 | 1.18710371 |
| 2 | Sheet7 | dI_T_std | 318 | 318 | 0 | 0 | 0.0145325194 | 0.0178447278 | 0.702176553 | 0.62862879 | 9.95594576 |
| 2 | Sheet7 | dI_C_skewness | 318 | 318 | 0 | 0 | 0.00679653447 | 0.00850497426 | 0.854307616 | 0.786066623 | 13.3534941 |
| 2 | Sheet7 | dI_T_skewness | 318 | 318 | 0 | 0 | 0.213345906 | 0.263517155 | 0.313161336 | 0.260889294 | 99.5733044 |
| 2 | Sheet7 | dI_C_kurtosis | 318 | 318 | 0 | 0 | 0.0113088035 | 0.0137612353 | 0.134215704 | 0.117349523 | 0.628471574 |
| 2 | Sheet7 | dI_T_kurtosis | 318 | 318 | 0 | 0 | 0.217347299 | 0.280487806 | 0.45718801 | 0.391079558 | 11.2921877 |
| 2 | Sheet7 | dI_dI_devide_dt | 318 | 318 | 0 | 0 | 0.00100015703 | 0.00121694311 | 0.998031437 | 0.991909006 | 0.557712502 |
| 2 | Sheet7 | dI_entropy | 318 | 318 | 0 | 0 | 2.26750002 | 2.27322469 | -0.593278699 | -0.462188496 | 45.0036504 |
| 2 | Sheet7 | Charge_energy | 318 | 318 | 0 | 0 | 0.00110874115 | 0.00126833765 | 0.999997827 | 0.999937681 | 0.0148341462 |
| 2 | Sheet7 | Charge_Q | 318 | 318 | 0 | 0 | 0.000146513657 | 0.000171242058 | 0.999998673 | 0.999968654 | 0.00778002107 |
| 2 | Sheet7 | Charge_t_mean | 318 | 318 | 0 | 0 | 0.00471401003 | 0.00683781081 | 0.99999564 | 0.999944771 | 0.023107045 |
| 2 | Sheet7 | Charge_V_mean | 318 | 318 | 0 | 0 | 0.000968499121 | 0.000975430729 | 0.999993665 | 0.99992462 | 0.0236743952 |
| 2 | Sheet7 | Charge_C_mean | 318 | 318 | 0 | 0 | 0.0014788359 | 0.00200114118 | 0.999997687 | 0.999943278 | 0.0527783757 |
| 2 | Sheet7 | Charge_T_mean | 318 | 318 | 0 | 0 | 0.0131646775 | 0.0135060539 | 0.999999369 | 0.999980595 | 0.0445211536 |
| 2 | Sheet7 | Charge_C_std | 318 | 318 | 0 | 0 | 0.000919967461 | 0.0012045997 | 0.999918506 | 0.999568618 | 0.0351749905 |
| 2 | Sheet7 | Charge_V_std | 318 | 318 | 0 | 0 | 0.00194156997 | 0.00199593711 | 0.999922191 | 0.998925277 | 1.21217072 |
| 2 | Sheet7 | Charge_T_std | 318 | 318 | 0 | 0 | 0.00269446035 | 0.00334240057 | 0.999963291 | 0.99972908 | 0.0711574649 |
| 2 | Sheet7 | Charge_C_skewness | 318 | 318 | 0 | 0 | 0.00189977014 | 0.00230568925 | 0.999997692 | 0.999940293 | 0.667474315 |
| 2 | Sheet7 | Charge_V_skewness | 318 | 318 | 0 | 0 | 0.036173264 | 0.0402870638 | 0.999836239 | 0.99853345 | 3.21844122 |
| 2 | Sheet7 | Charge_T_skewness | 318 | 318 | 0 | 0 | 0.00450505619 | 0.00475471312 | 0.999959338 | 0.999350688 | 2.65986656 |
| 2 | Sheet7 | Charge_C_kurtosis | 318 | 318 | 0 | 0 | 0.00256805446 | 0.00594871596 | 0.9997312 | 0.99992462 | 0.200536418 |
| 2 | Sheet7 | Charge_V_kurtosis | 318 | 318 | 0 | 0 | 0.202247783 | 0.250621972 | 0.999463722 | 0.996595496 | 7.21093606 |
| 2 | Sheet7 | Charge_T_kurtosis | 318 | 318 | 0 | 0 | 0.0028653065 | 0.00730638827 | 0.997386331 | 0.996988583 | 0.179179905 |
| 2 | Sheet8 | CC_energy | 269 | 269 | 0 | 0 | 0.0700688359 | 0.0824757412 | 0.994420482 | 0.985547556 | 1.20430591 |
| 2 | Sheet8 | CC_Q | 269 | 269 | 0 | 0 | 0.0165252561 | 0.0196246266 | 0.995422711 | 0.987342802 | 1.11009508 |
| 2 | Sheet8 | CC_t_mean | 269 | 269 | 0 | 0 | 0.0825191152 | 0.098066409 | 0.995419995 | 0.987365609 | 1.10868629 |
| 2 | Sheet8 | CC_V_mean | 269 | 269 | 0 | 0 | 0.00405363799 | 0.00447718426 | 0.990875908 | 0.95223669 | 0.103692805 |
| 2 | Sheet8 | CC_T_mean | 269 | 269 | 0 | 0 | 0.0376542558 | 0.0440961943 | 0.99977045 | 0.998681931 | 0.121763892 |
| 2 | Sheet8 | CC_V_std | 269 | 269 | 0 | 0 | 0.00149524828 | 0.00182488116 | 0.959452124 | 0.872754085 | 1.04882766 |
| 2 | Sheet8 | CC_T_std | 269 | 269 | 0 | 0 | 0.0123515214 | 0.0314315566 | 0.961800086 | 0.993200498 | 0.497203081 |
| 2 | Sheet8 | CC_V_skewness | 269 | 269 | 0 | 0 | 0.13591098 | 0.143892938 | 0.996489748 | 0.990456016 | 107.209075 |
| 2 | Sheet8 | CC_T_skewness | 269 | 269 | 0 | 0 | 0.00947324329 | 0.013264989 | 0.979734408 | 0.991395099 | 2.49248616 |
| 2 | Sheet8 | CC_V_kurtosis | 269 | 269 | 0 | 0 | 0.313010771 | 0.343844302 | 0.983369672 | 0.94188089 | 11.3186525 |
| 2 | Sheet8 | CC_T_kurtosis | 269 | 269 | 0 | 0 | 0.0121126202 | 0.017922247 | 0.965544093 | 0.989864015 | 0.64567298 |
| 2 | Sheet8 | CC_CCCT | 269 | 269 | 0 | 0 | 0.165228873 | 0.196225388 | 0.995422843 | 0.987385612 | 1.10995709 |
| 2 | Sheet8 | CC_entropy | 269 | 269 | 0 | 0 | 5.00538666 | 5.00548868 | 0.921311233 | 0.96173147 | 67.2386336 |
| 2 | Sheet8 | dV_energy | 269 | 269 | 0 | 0 | 0.00854527506 | 0.00904336824 | 0.998399146 | 0.991370286 | 0.72234954 |
| 2 | Sheet8 | dV_Q | 269 | 269 | 0 | 0 | 0.00216725552 | 0.0022932635 | 0.9983905 | 0.991318653 | 0.722858673 |
| 2 | Sheet8 | dV_t_mean | 269 | 269 | 0 | 0 | 0.0107903927 | 0.0114176342 | 0.998396146 | 0.991275346 | 0.719789859 |
| 2 | Sheet8 | dV_V_mean | 269 | 269 | 0 | 0 | 0.000130898105 | 0.000246000909 | 0.93836226 | 0.866593128 | 0.00331752708 |
| 2 | Sheet8 | dV_T_mean | 269 | 269 | 0 | 0 | 0.0206138205 | 0.0893707381 | 0.998457658 | 0.999725654 | 0.0638410611 |
| 2 | Sheet8 | dV_V_std | 269 | 269 | 0 | 0 | 0.000155385767 | 0.000171704413 | 0.641289214 | 0.505008415 | 0.54167609 |
| 2 | Sheet8 | dV_T_std | 269 | 269 | 0 | 0 | 0.0105188663 | 0.0251567941 | 0.985437804 | 0.988597804 | 2.43102797 |
| 2 | Sheet8 | dV_V_skewness | 269 | 269 | 0 | 0 | 0.00292278943 | 0.00949086455 | 0.955833085 | 0.980908609 | 1.5693056 |
| 2 | Sheet8 | dV_T_skewness | 269 | 269 | 0 | 0 | 0.0504337298 | 0.0815994618 | 0.904584726 | 0.928402597 | 31.9591753 |
| 2 | Sheet8 | dV_V_kurtosis | 269 | 269 | 0 | 0 | 0.00173433536 | 0.00217636806 | 0.880085637 | 0.849198863 | 0.094090974 |
| 2 | Sheet8 | dV_T_kurtosis | 269 | 269 | 0 | 0 | 0.0624918518 | 0.094071568 | 0.845564941 | 0.882785576 | 3.38391426 |
| 2 | Sheet8 | dV_dV_devide_dt | 269 | 269 | 0 | 0 | 4.3253315e-05 | 5.6389499e-05 | 0.99925106 | 0.995975489 | 0.13047697 |
| 2 | Sheet8 | dV_entropy | 269 | 269 | 0 | 0 | 4.66756627 | 4.66787947 | 0.810183013 | 0.55791847 | 62.836372 |
| 2 | Sheet8 | CV_energy | 269 | 269 | 0 | 0 | 0.0431858406 | 0.0503621081 | 0.982118259 | 0.973158372 | 2.57703163 |
| 2 | Sheet8 | CV_Q | 269 | 269 | 0 | 0 | 0.0102825853 | 0.0119911483 | 0.982116932 | 0.973158372 | 2.57697343 |
| 2 | Sheet8 | CV_t_mean | 269 | 269 | 0 | 0 | 0.0771237004 | 0.161057708 | 0.996519895 | 0.998405111 | 0.575727678 |
| 2 | Sheet8 | CV_C_mean | 269 | 269 | 0 | 0 | 0.015229781 | 0.0177111454 | 0.963950345 | 0.883737418 | 1.6953286 |
| 2 | Sheet8 | CV_T_mean | 269 | 269 | 0 | 0 | 0.0277504128 | 0.0562644931 | 0.999418264 | 0.999580162 | 0.0984515423 |
| 2 | Sheet8 | CV_C_std | 269 | 269 | 0 | 0 | 0.0296568611 | 0.0343521221 | 0.729202362 | 0.661778042 | 2.50080976 |
| 2 | Sheet8 | CV_T_std | 269 | 269 | 0 | 0 | 0.0139089219 | 0.0165807196 | 0.99590707 | 0.994782276 | 0.440091413 |
| 2 | Sheet8 | CV_C_skewness | 269 | 269 | 0 | 0 | 0.0154948584 | 0.0189989943 | 0.991490329 | 0.97743851 | 0.679231225 |
| 2 | Sheet8 | CV_T_skewness | 269 | 269 | 0 | 0 | 0.00872978857 | 0.0126069723 | 0.995407722 | 0.99206382 | 1.17713021 |
| 2 | Sheet8 | CV_C_kurtosis | 269 | 269 | 0 | 0 | 0.0777445458 | 0.097383488 | 0.991047856 | 0.980609178 | 0.988664036 |
| 2 | Sheet8 | CV_T_kurtosis | 269 | 269 | 0 | 0 | 0.0198855481 | 0.0281893957 | 0.993657016 | 0.983562928 | 0.918628993 |
| 2 | Sheet8 | CV_CVCT | 269 | 269 | 0 | 0 | 0.147300072 | 0.320495196 | 0.996513798 | 0.998431002 | 0.54996478 |
| 2 | Sheet8 | CV_entropy | 269 | 269 | 0 | 0 | 4.58911664 | 4.58924039 | 0.972256557 | 0.881851326 | 73.2027942 |
| 2 | Sheet8 | dI_energy | 269 | 269 | 0 | 0 | 0.000999078468 | 0.00112599911 | 0.998416068 | 0.997138225 | 1.9866351 |
| 2 | Sheet8 | dI_Q | 269 | 269 | 0 | 0 | 0.000237884836 | 0.000268105695 | 0.998416075 | 0.997138225 | 1.98661715 |
| 2 | Sheet8 | dI_t_mean | 269 | 269 | 0 | 0 | 0.00749979627 | 0.00845104833 | 0.998420819 | 0.997299591 | 1.98080846 |
| 2 | Sheet8 | dI_C_mean | 269 | 269 | 0 | 0 | 0.000400622485 | 0.000511835843 | 0.939556003 | 0.940517364 | 0.0422247233 |
| 2 | Sheet8 | dI_T_mean | 269 | 269 | 0 | 0 | 0.0148372223 | 0.0182777646 | 0.999859028 | 0.999636113 | 0.0489813577 |
| 2 | Sheet8 | dI_C_std | 269 | 269 | 0 | 0 | 0.00026986552 | 0.000331767731 | 0.305111958 | 0.309627205 | 0.935291958 |
| 2 | Sheet8 | dI_T_std | 269 | 269 | 0 | 0 | 0.0124567527 | 0.0163759673 | 0.89799412 | 0.888219374 | 7.67098043 |
| 2 | Sheet8 | dI_C_skewness | 269 | 269 | 0 | 0 | 0.00728962401 | 0.00984378916 | 0.987810604 | 0.986245353 | 11.5006274 |
| 2 | Sheet8 | dI_T_skewness | 269 | 269 | 0 | 0 | 0.172014816 | 0.217361489 | 0.535490869 | 0.479599524 | 94.2299733 |
| 2 | Sheet8 | dI_C_kurtosis | 269 | 269 | 0 | 0 | 0.00935320834 | 0.0127899669 | 0.7268683 | 0.725661655 | 0.517006515 |
| 2 | Sheet8 | dI_T_kurtosis | 269 | 269 | 0 | 0 | 0.203222909 | 0.282393701 | 0.369245835 | 0.398094533 | 10.5608022 |
| 2 | Sheet8 | dI_dI_devide_dt | 269 | 269 | 0 | 0 | 0.000958970047 | 0.00204706151 | 0.998196914 | 0.999011434 | 0.709732704 |
| 2 | Sheet8 | dI_entropy | 269 | 269 | 0 | 0 | 2.69458994 | 2.71218979 | -0.110990977 | -0.148196372 | 49.311205 |
| 2 | Sheet8 | Charge_energy | 269 | 269 | 0 | 0 | 0.00413480355 | 0.0205002222 | 0.997721083 | 0.999943898 | 0.0551170511 |
| 2 | Sheet8 | Charge_Q | 269 | 269 | 0 | 0 | 0.000710566859 | 0.00436623638 | 0.998642861 | 0.999962393 | 0.0376092468 |
| 2 | Sheet8 | Charge_t_mean | 269 | 269 | 0 | 0 | 0.0236720647 | 0.127657588 | 0.995829953 | 0.999899818 | 0.113544769 |
| 2 | Sheet8 | Charge_V_mean | 269 | 269 | 0 | 0 | 0.00127188878 | 0.00131568495 | 0.99942744 | 0.999810272 | 0.031061061 |
| 2 | Sheet8 | Charge_C_mean | 269 | 269 | 0 | 0 | 0.00349766534 | 0.0146279578 | 0.998363759 | 0.99992417 | 0.128068265 |
| 2 | Sheet8 | Charge_T_mean | 269 | 269 | 0 | 0 | 0.0182636616 | 0.0520612099 | 0.999466646 | 0.999939582 | 0.0626274072 |
| 2 | Sheet8 | Charge_C_std | 269 | 269 | 0 | 0 | 0.0019119679 | 0.00746501551 | 0.993041937 | 0.99978114 | 0.0730812546 |
| 2 | Sheet8 | Charge_V_std | 269 | 269 | 0 | 0 | 0.00294949089 | 0.00304597472 | 0.996362859 | 0.995702942 | 1.80635917 |
| 2 | Sheet8 | Charge_T_std | 269 | 269 | 0 | 0 | 0.00368477145 | 0.014407343 | 0.996804649 | 0.999702385 | 0.11462783 |
| 2 | Sheet8 | Charge_C_skewness | 269 | 269 | 0 | 0 | 0.0037125726 | 0.0128432723 | 0.997833384 | 0.999909991 | 1.09177921 |
| 2 | Sheet8 | Charge_V_skewness | 269 | 269 | 0 | 0 | 0.0775790884 | 0.0950420017 | 0.994858674 | 0.998202274 | 5.98940349 |
| 2 | Sheet8 | Charge_T_skewness | 269 | 269 | 0 | 0 | 0.00540910758 | 0.00901959441 | 0.998167813 | 0.99925527 | 2.52685632 |
| 2 | Sheet8 | Charge_C_kurtosis | 269 | 269 | 0 | 0 | 0.00717303178 | 0.034569754 | 0.988640975 | 0.999928485 | 0.567586901 |
| 2 | Sheet8 | Charge_V_kurtosis | 269 | 269 | 0 | 0 | 0.489041827 | 0.671017366 | 0.984676781 | 0.999389041 | 14.1946986 |
| 2 | Sheet8 | Charge_T_kurtosis | 269 | 269 | 0 | 0 | 0.00392630441 | 0.014243499 | 0.985874565 | 0.997325616 | 0.2422888 |
| 2 | Sheet9 | CC_energy | 286 | 286 | 0 | 0 | 0.0617700234 | 0.0731076292 | 0.995645474 | 0.986279702 | 1.09651807 |
| 2 | Sheet9 | CC_Q | 286 | 286 | 0 | 0 | 0.0144992176 | 0.0172307138 | 0.996453425 | 0.987717546 | 1.00953745 |
| 2 | Sheet9 | CC_t_mean | 286 | 286 | 0 | 0 | 0.072881526 | 0.0864902966 | 0.996450948 | 0.987638799 | 1.01486136 |
| 2 | Sheet9 | CC_V_mean | 286 | 286 | 0 | 0 | 0.00373968206 | 0.00417412476 | 0.990495788 | 0.967355366 | 0.0953232065 |
| 2 | Sheet9 | CC_T_mean | 286 | 286 | 0 | 0 | 0.0424346251 | 0.0507582213 | 0.997465619 | 0.994542556 | 0.148142407 |
| 2 | Sheet9 | CC_V_std | 286 | 286 | 0 | 0 | 0.00156785556 | 0.00209058668 | 0.920024102 | 0.899934006 | 1.17234694 |
| 2 | Sheet9 | CC_T_std | 286 | 286 | 0 | 0 | 0.014906746 | 0.0336675208 | 0.941040391 | 0.978665363 | 0.523774805 |
| 2 | Sheet9 | CC_V_skewness | 286 | 286 | 0 | 0 | 0.134553504 | 0.141860518 | 0.996068171 | 0.993213846 | 77.0359033 |
| 2 | Sheet9 | CC_T_skewness | 286 | 286 | 0 | 0 | 0.00922685123 | 0.0164610693 | 0.976024608 | 0.993414028 | 3.05538696 |
| 2 | Sheet9 | CC_V_kurtosis | 286 | 286 | 0 | 0 | 0.297068198 | 0.326218786 | 0.992020881 | 0.968478248 | 11.0730657 |
| 2 | Sheet9 | CC_T_kurtosis | 286 | 286 | 0 | 0 | 0.00967160167 | 0.0228288961 | 0.908481625 | 0.98821448 | 0.532825686 |
| 2 | Sheet9 | CC_CCCT | 286 | 286 | 0 | 0 | 0.144971422 | 0.172288521 | 0.996453382 | 0.987765606 | 1.00940553 |
| 2 | Sheet9 | CC_entropy | 286 | 286 | 0 | 0 | 5.01586686 | 5.01597794 | 0.997262869 | 0.982675953 | 67.1875566 |
| 2 | Sheet9 | dV_energy | 286 | 286 | 0 | 0 | 0.00841898031 | 0.0197836014 | 0.940476991 | 0.990617274 | 0.652912821 |
| 2 | Sheet9 | dV_Q | 286 | 286 | 0 | 0 | 0.00213058367 | 0.00502005635 | 0.940279715 | 0.990658825 | 0.651897646 |
| 2 | Sheet9 | dV_t_mean | 286 | 286 | 0 | 0 | 0.0106112028 | 0.0252179544 | 0.939381371 | 0.991065862 | 0.649334584 |
| 2 | Sheet9 | dV_V_mean | 286 | 286 | 0 | 0 | 0.000104824404 | 0.000139603825 | 0.980212057 | 0.963929515 | 0.00265690672 |
| 2 | Sheet9 | dV_T_mean | 286 | 286 | 0 | 0 | 0.00748466135 | 0.0092097532 | 0.999804891 | 0.999720818 | 0.0249932401 |
| 2 | Sheet9 | dV_V_std | 286 | 286 | 0 | 0 | 0.000122451903 | 0.00013978704 | 0.515827872 | 0.381321167 | 0.427541734 |
| 2 | Sheet9 | dV_T_std | 286 | 286 | 0 | 0 | 0.00817030928 | 0.0115848074 | 0.996019745 | 0.995219799 | 1.39085405 |
| 2 | Sheet9 | dV_V_skewness | 286 | 286 | 0 | 0 | 0.00220599266 | 0.00387380409 | 0.991019841 | 0.992368423 | 1.12414158 |
| 2 | Sheet9 | dV_T_skewness | 286 | 286 | 0 | 0 | 0.040375362 | 0.0787948399 | 0.90227515 | 0.942233376 | 25.9756023 |
| 2 | Sheet9 | dV_V_kurtosis | 286 | 286 | 0 | 0 | 0.00197479177 | 0.00266473079 | 0.93242498 | 0.913217324 | 0.106546042 |
| 2 | Sheet9 | dV_T_kurtosis | 286 | 286 | 0 | 0 | 0.0462721444 | 0.0881204238 | 0.870344107 | 0.929340493 | 2.48208361 |
| 2 | Sheet9 | dV_dV_devide_dt | 286 | 286 | 0 | 0 | 6.78970527e-05 | 0.000299098104 | 0.964522549 | 0.996826757 | 0.222948307 |
| 2 | Sheet9 | dV_entropy | 286 | 286 | 0 | 0 | 4.76714499 | 4.76737824 | 0.356630911 | 0.417725997 | 63.3395778 |
| 2 | Sheet9 | CV_energy | 286 | 286 | 0 | 0 | 0.0433408263 | 0.0500408109 | 0.980907665 | 0.979513683 | 2.55191553 |
| 2 | Sheet9 | CV_Q | 286 | 286 | 0 | 0 | 0.0103189294 | 0.0119139909 | 0.980907141 | 0.979513683 | 2.55183389 |
| 2 | Sheet9 | CV_t_mean | 286 | 286 | 0 | 0 | 0.0575122486 | 0.0655790921 | 0.999557222 | 0.997913768 | 0.431159405 |
| 2 | Sheet9 | CV_C_mean | 286 | 286 | 0 | 0 | 0.0164113 | 0.0206271723 | 0.937357958 | 0.865288477 | 1.79668089 |
| 2 | Sheet9 | CV_T_mean | 286 | 286 | 0 | 0 | 0.0318301421 | 0.0636020471 | 0.994162265 | 0.998684233 | 0.12298333 |
| 2 | Sheet9 | CV_C_std | 286 | 286 | 0 | 0 | 0.0296545713 | 0.0343624379 | 0.715332071 | 0.58480297 | 2.44599726 |
| 2 | Sheet9 | CV_T_std | 286 | 286 | 0 | 0 | 0.0132065761 | 0.0154997359 | 0.999047432 | 0.998563183 | 0.351615439 |
| 2 | Sheet9 | CV_C_skewness | 286 | 286 | 0 | 0 | 0.0155089487 | 0.0235836035 | 0.978198883 | 0.974011724 | 0.699505423 |
| 2 | Sheet9 | CV_T_skewness | 286 | 286 | 0 | 0 | 0.00769245833 | 0.0111719644 | 0.981583725 | 0.985026764 | 1.27950232 |
| 2 | Sheet9 | CV_C_kurtosis | 286 | 286 | 0 | 0 | 0.0773459066 | 0.118318639 | 0.977538934 | 0.974849526 | 1.03290731 |
| 2 | Sheet9 | CV_T_kurtosis | 286 | 286 | 0 | 0 | 0.0151878359 | 0.0210388911 | 0.973966882 | 0.974322692 | 0.776145931 |
| 2 | Sheet9 | CV_CVCT | 286 | 286 | 0 | 0 | 0.107811699 | 0.124427895 | 0.999594043 | 0.998336576 | 0.404216103 |
| 2 | Sheet9 | CV_entropy | 286 | 286 | 0 | 0 | 4.5922144 | 4.59229901 | 0.940105178 | 0.938116385 | 73.1588608 |
| 2 | Sheet9 | dI_energy | 286 | 286 | 0 | 0 | 0.000984835132 | 0.0011397335 | 0.995030806 | 0.972287847 | 2.18528318 |
| 2 | Sheet9 | dI_Q | 286 | 286 | 0 | 0 | 0.000234486973 | 0.000271368295 | 0.995030791 | 0.972287847 | 2.18530327 |
| 2 | Sheet9 | dI_t_mean | 286 | 286 | 0 | 0 | 0.00737248188 | 0.00855591212 | 0.99492544 | 0.971067873 | 2.17308158 |
| 2 | Sheet9 | dI_C_mean | 286 | 286 | 0 | 0 | 0.00049174014 | 0.00062191233 | 0.796962237 | 0.761112828 | 0.0518249496 |
| 2 | Sheet9 | dI_T_mean | 286 | 286 | 0 | 0 | 0.0170713166 | 0.0260422889 | 0.997686795 | 0.998189486 | 0.0598043581 |
| 2 | Sheet9 | dI_C_std | 286 | 286 | 0 | 0 | 0.00031064424 | 0.000391965786 | 0.0105891041 | 0.0589513183 | 1.07450297 |
| 2 | Sheet9 | dI_T_std | 286 | 286 | 0 | 0 | 0.0143181146 | 0.0189083557 | 0.883131213 | 0.864509781 | 8.23857432 |
| 2 | Sheet9 | dI_C_skewness | 286 | 286 | 0 | 0 | 0.0102339111 | 0.0134813191 | 0.924258619 | 0.868896187 | 23.8470908 |
| 2 | Sheet9 | dI_T_skewness | 286 | 286 | 0 | 0 | 0.175318054 | 0.250441258 | 0.547859443 | 0.529387685 | 86.69736 |
| 2 | Sheet9 | dI_C_kurtosis | 286 | 286 | 0 | 0 | 0.00882381965 | 0.0124501222 | 0.350356961 | 0.442104494 | 0.489496344 |
| 2 | Sheet9 | dI_T_kurtosis | 286 | 286 | 0 | 0 | 0.211544846 | 0.399179453 | 0.21553828 | 0.313805106 | 11.1232075 |
| 2 | Sheet9 | dI_dI_devide_dt | 286 | 286 | 0 | 0 | 0.00198153149 | 0.00546615262 | 0.992374582 | 0.992930671 | 1.34548766 |
| 2 | Sheet9 | dI_entropy | 286 | 286 | 0 | 0 | 2.57144166 | 2.58130929 | 0.31738679 | 0.240183016 | 48.1320011 |
| 2 | Sheet9 | Charge_energy | 286 | 286 | 0 | 0 | 0.00118805304 | 0.00133807064 | 0.999997179 | 0.999968196 | 0.0161886981 |
| 2 | Sheet9 | Charge_Q | 286 | 286 | 0 | 0 | 0.000135283156 | 0.000159306085 | 0.999998085 | 0.999966657 | 0.00734318837 |
| 2 | Sheet9 | Charge_t_mean | 286 | 286 | 0 | 0 | 0.0105482546 | 0.0673486199 | 0.994014943 | 0.998221157 | 0.0513946588 |
| 2 | Sheet9 | Charge_V_mean | 286 | 286 | 0 | 0 | 0.00116968873 | 0.00118573409 | 0.999905676 | 0.999389058 | 0.0285126813 |
| 2 | Sheet9 | Charge_C_mean | 286 | 286 | 0 | 0 | 0.00195041422 | 0.0030820688 | 0.999898828 | 0.999160275 | 0.0722900347 |
| 2 | Sheet9 | Charge_T_mean | 286 | 286 | 0 | 0 | 0.0179276717 | 0.0355943014 | 0.997953702 | 0.999889199 | 0.0667812405 |
| 2 | Sheet9 | Charge_C_std | 286 | 286 | 0 | 0 | 0.000940611697 | 0.00126415284 | 0.999789111 | 0.999791992 | 0.0360285708 |
| 2 | Sheet9 | Charge_V_std | 286 | 286 | 0 | 0 | 0.00277907253 | 0.00286805722 | 0.998590849 | 0.997574697 | 1.80679726 |
| 2 | Sheet9 | Charge_T_std | 286 | 286 | 0 | 0 | 0.00224503576 | 0.00273749297 | 0.999945556 | 0.999846623 | 0.0604779707 |
| 2 | Sheet9 | Charge_C_skewness | 286 | 286 | 0 | 0 | 0.00217217773 | 0.00270080171 | 0.999911801 | 0.999142834 | 0.605056462 |
| 2 | Sheet9 | Charge_V_skewness | 286 | 286 | 0 | 0 | 0.0699082077 | 0.0766340675 | 0.998854349 | 0.995416648 | 5.37664248 |
| 2 | Sheet9 | Charge_T_skewness | 286 | 286 | 0 | 0 | 0.00463296516 | 0.00577369134 | 0.997855059 | 0.998606785 | 2.81321284 |
| 2 | Sheet9 | Charge_C_kurtosis | 286 | 286 | 0 | 0 | 0.00322487529 | 0.00941086104 | 0.997809587 | 0.999431628 | 0.253197962 |
| 2 | Sheet9 | Charge_V_kurtosis | 286 | 286 | 0 | 0 | 0.432247066 | 0.50527884 | 0.997953432 | 0.996501035 | 12.7395632 |
| 2 | Sheet9 | Charge_T_kurtosis | 286 | 286 | 0 | 0 | 0.00171778369 | 0.00266007986 | 0.994394272 | 0.994887269 | 0.105403168 |
| 2 | Sheet10 | CC_energy | 163 | 163 | 0 | 0 | 0.0790714624 | 0.0889695952 | 0.994722132 | 0.977191991 | 1.40628311 |
| 2 | Sheet10 | CC_Q | 163 | 163 | 0 | 0 | 0.018582969 | 0.0209775117 | 0.995610313 | 0.982406992 | 1.29750639 |
| 2 | Sheet10 | CC_t_mean | 163 | 163 | 0 | 0 | 0.0929393159 | 0.105096659 | 0.995541913 | 0.981741249 | 1.29784945 |
| 2 | Sheet10 | CC_V_mean | 163 | 163 | 0 | 0 | 0.00460642836 | 0.00498339965 | 0.986812245 | 0.965645185 | 0.117319033 |
| 2 | Sheet10 | CC_T_mean | 163 | 163 | 0 | 0 | 0.0500995584 | 0.056945617 | 0.997831723 | 0.997284431 | 0.178058677 |
| 2 | Sheet10 | CC_V_std | 163 | 163 | 0 | 0 | 0.0018196259 | 0.00236539041 | 0.981578957 | 0.839442252 | 1.31399969 |
| 2 | Sheet10 | CC_T_std | 163 | 163 | 0 | 0 | 0.0136118917 | 0.0168097146 | 0.995812178 | 0.995763158 | 0.503595245 |
| 2 | Sheet10 | CC_V_skewness | 163 | 163 | 0 | 0 | 0.151209879 | 0.159564609 | 0.998072878 | 0.997677911 | 66.1209999 |
| 2 | Sheet10 | CC_T_skewness | 163 | 163 | 0 | 0 | 0.0128863765 | 0.0193823016 | 0.980596535 | 0.99386849 | 3.93380774 |
| 2 | Sheet10 | CC_V_kurtosis | 163 | 163 | 0 | 0 | 0.376049658 | 0.422619416 | 0.997635804 | 0.99683276 | 12.8152322 |
| 2 | Sheet10 | CC_T_kurtosis | 163 | 163 | 0 | 0 | 0.0125723208 | 0.0329301269 | 0.897399877 | 0.992097827 | 0.692276387 |
| 2 | Sheet10 | CC_CCCT | 163 | 163 | 0 | 0 | 0.185796966 | 0.209745216 | 0.995610083 | 0.982454026 | 1.29728755 |
| 2 | Sheet10 | CC_entropy | 163 | 163 | 0 | 0 | 5.00602995 | 5.00625829 | 0.998274203 | 0.99405199 | 67.2984255 |
| 2 | Sheet10 | dV_energy | 163 | 163 | 0 | 0 | 0.0095097962 | 0.0267694254 | 0.957058769 | 0.978691272 | 0.722187327 |
| 2 | Sheet10 | dV_Q | 163 | 163 | 0 | 0 | 0.00241289311 | 0.00679418162 | 0.957056271 | 0.979320302 | 0.723064104 |
| 2 | Sheet10 | dV_t_mean | 163 | 163 | 0 | 0 | 0.012011372 | 0.0339446094 | 0.95710428 | 0.977258605 | 0.71984497 |
| 2 | Sheet10 | dV_V_mean | 163 | 163 | 0 | 0 | 0.000124359289 | 0.000209423101 | 0.979100049 | 0.940248412 | 0.0031515018 |
| 2 | Sheet10 | dV_T_mean | 163 | 163 | 0 | 0 | 0.00839150363 | 0.0107029694 | 0.999736635 | 0.999301711 | 0.0286915913 |
| 2 | Sheet10 | dV_V_std | 163 | 163 | 0 | 0 | 0.000110884522 | 0.000128495962 | 0.600582485 | 0.523406543 | 0.387185481 |
| 2 | Sheet10 | dV_T_std | 163 | 163 | 0 | 0 | 0.00779702021 | 0.00987052403 | 0.99672717 | 0.993945389 | 1.31675869 |
| 2 | Sheet10 | dV_V_skewness | 163 | 163 | 0 | 0 | 0.00218027094 | 0.00510761659 | 0.993218187 | 0.990257068 | 1.28306667 |
| 2 | Sheet10 | dV_T_skewness | 163 | 163 | 0 | 0 | 0.0356658557 | 0.0447610543 | 0.965857112 | 0.962802246 | 21.3023726 |
| 2 | Sheet10 | dV_V_kurtosis | 163 | 163 | 0 | 0 | 0.00184217717 | 0.00230263126 | 0.951479923 | 0.912808065 | 0.0997994072 |
| 2 | Sheet10 | dV_T_kurtosis | 163 | 163 | 0 | 0 | 0.051588156 | 0.117291942 | 0.833024338 | 0.911018006 | 2.80492264 |
| 2 | Sheet10 | dV_dV_devide_dt | 163 | 163 | 0 | 0 | 8.65543456e-05 | 0.000362031627 | 0.976140927 | 0.993787177 | 0.289856766 |
| 2 | Sheet10 | dV_entropy | 163 | 163 | 0 | 0 | 4.7826563 | 4.78288536 | -0.371615317 | -0.376366047 | 63.389803 |
| 2 | Sheet10 | CV_energy | 163 | 163 | 0 | 0 | 0.0390123478 | 0.047014418 | 0.976476893 | 0.965930692 | 2.2624139 |
| 2 | Sheet10 | CV_Q | 163 | 163 | 0 | 0 | 0.00928795945 | 0.0111928135 | 0.976476518 | 0.965930692 | 2.26234705 |
| 2 | Sheet10 | CV_t_mean | 163 | 163 | 0 | 0 | 0.0612872539 | 0.100147552 | 0.997759535 | 0.998566003 | 0.405473609 |
| 2 | Sheet10 | CV_C_mean | 163 | 163 | 0 | 0 | 0.012564587 | 0.01541021 | 0.969060686 | 0.913602142 | 1.53485137 |
| 2 | Sheet10 | CV_T_mean | 163 | 163 | 0 | 0 | 0.0200810027 | 0.0275806118 | 0.99923077 | 0.998209941 | 0.0803502333 |
| 2 | Sheet10 | CV_C_std | 163 | 163 | 0 | 0 | 0.0256960004 | 0.0299824312 | 0.761943625 | 0.676861667 | 2.24206292 |
| 2 | Sheet10 | CV_T_std | 163 | 163 | 0 | 0 | 0.0119686354 | 0.0143266319 | 0.997466086 | 0.996838302 | 0.348519297 |
| 2 | Sheet10 | CV_C_skewness | 163 | 163 | 0 | 0 | 0.0127720068 | 0.0174537466 | 0.994917549 | 0.98446285 | 0.511131522 |
| 2 | Sheet10 | CV_T_skewness | 163 | 163 | 0 | 0 | 0.00605050183 | 0.00891673463 | 0.995277517 | 0.994391519 | 0.772521669 |
| 2 | Sheet10 | CV_C_kurtosis | 163 | 163 | 0 | 0 | 0.0740947572 | 0.10574096 | 0.994023442 | 0.985344037 | 0.82567821 |
| 2 | Sheet10 | CV_T_kurtosis | 163 | 163 | 0 | 0 | 0.0147477119 | 0.02247073 | 0.990817469 | 0.989706462 | 0.657621102 |
| 2 | Sheet10 | CV_CVCT | 163 | 163 | 0 | 0 | 0.114809359 | 0.196956504 | 0.997755823 | 0.99847317 | 0.379896803 |
| 2 | Sheet10 | CV_entropy | 163 | 163 | 0 | 0 | 4.51763874 | 4.51782838 | 0.982533691 | 0.942939411 | 74.5554071 |
| 2 | Sheet10 | dI_energy | 163 | 163 | 0 | 0 | 0.000994615023 | 0.00111429417 | 0.997431451 | 0.995087037 | 2.75928548 |
| 2 | Sheet10 | dI_Q | 163 | 163 | 0 | 0 | 0.000236805806 | 0.00026530023 | 0.997431448 | 0.995084266 | 2.7593253 |
| 2 | Sheet10 | dI_t_mean | 163 | 163 | 0 | 0 | 0.00746201698 | 0.00836115473 | 0.997432903 | 0.994663075 | 2.74536594 |
| 2 | Sheet10 | dI_C_mean | 163 | 163 | 0 | 0 | 0.000549632295 | 0.000704792613 | 0.768606715 | 0.769772391 | 0.0580086496 |
| 2 | Sheet10 | dI_T_mean | 163 | 163 | 0 | 0 | 0.0184244231 | 0.0232718278 | 0.998088998 | 0.99702603 | 0.0650919098 |
| 2 | Sheet10 | dI_C_std | 163 | 163 | 0 | 0 | 0.00035075857 | 0.000445543314 | -0.0165627409 | 0.0291230929 | 1.21069949 |
| 2 | Sheet10 | dI_T_std | 163 | 163 | 0 | 0 | 0.013949463 | 0.0178962591 | 0.887992546 | 0.861439473 | 10.7541601 |
| 2 | Sheet10 | dI_C_skewness | 163 | 163 | 0 | 0 | 0.0148990463 | 0.0196954696 | 0.872813393 | 0.901751819 | 14.3256311 |
| 2 | Sheet10 | dI_T_skewness | 163 | 163 | 0 | 0 | 0.231310025 | 0.306630575 | 0.633672067 | 0.620870534 | 75.0991145 |
| 2 | Sheet10 | dI_C_kurtosis | 163 | 163 | 0 | 0 | 0.0206682744 | 0.0253632735 | 0.246784859 | 0.220401683 | 1.14282973 |
| 2 | Sheet10 | dI_T_kurtosis | 163 | 163 | 0 | 0 | 0.346879728 | 0.524670162 | 0.359140114 | 0.466754877 | 16.5341698 |
| 2 | Sheet10 | dI_dI_devide_dt | 163 | 163 | 0 | 0 | 0.00133671574 | 0.0017903843 | 0.999054209 | 0.997913437 | 0.715355202 |
| 2 | Sheet10 | dI_entropy | 163 | 163 | 0 | 0 | 2.2407723 | 2.25937649 | -0.737278619 | -0.764371354 | 44.7442773 |
| 2 | Sheet10 | Charge_energy | 163 | 163 | 0 | 0 | 0.00135801863 | 0.00154087207 | 0.999994408 | 0.999894702 | 0.0184657815 |
| 2 | Sheet10 | Charge_Q | 163 | 163 | 0 | 0 | 0.000228884089 | 0.000757933884 | 0.999953309 | 0.999949429 | 0.012408936 |
| 2 | Sheet10 | Charge_t_mean | 163 | 163 | 0 | 0 | 0.017849646 | 0.102611255 | 0.994331929 | 0.999543477 | 0.080101732 |
| 2 | Sheet10 | Charge_V_mean | 163 | 163 | 0 | 0 | 0.00130158178 | 0.00133547904 | 0.99969266 | 0.999270537 | 0.0316566142 |
| 2 | Sheet10 | Charge_C_mean | 163 | 163 | 0 | 0 | 0.00312053105 | 0.00621556877 | 0.999477519 | 0.99952616 | 0.125367745 |
| 2 | Sheet10 | Charge_T_mean | 163 | 163 | 0 | 0 | 0.0135140899 | 0.0191554929 | 0.99965303 | 0.999861451 | 0.051973083 |
| 2 | Sheet10 | Charge_C_std | 163 | 163 | 0 | 0 | 0.00147836158 | 0.0032882471 | 0.998401236 | 0.997316279 | 0.0569964972 |
| 2 | Sheet10 | Charge_V_std | 163 | 163 | 0 | 0 | 0.00337858189 | 0.00355392379 | 0.994355791 | 0.9944407 | 2.25295488 |
| 2 | Sheet10 | Charge_T_std | 163 | 163 | 0 | 0 | 0.00211307869 | 0.0026517311 | 0.999847535 | 0.999545558 | 0.0597218259 |
| 2 | Sheet10 | Charge_C_skewness | 163 | 163 | 0 | 0 | 0.00366273409 | 0.00783537162 | 0.998604712 | 0.999558024 | 0.721099489 |
| 2 | Sheet10 | Charge_V_skewness | 163 | 163 | 0 | 0 | 0.0954054424 | 0.113010618 | 0.99736089 | 0.990954044 | 6.28198705 |
| 2 | Sheet10 | Charge_T_skewness | 163 | 163 | 0 | 0 | 0.00470270843 | 0.00634626399 | 0.998918477 | 0.999613444 | 1.64640697 |
| 2 | Sheet10 | Charge_C_kurtosis | 163 | 163 | 0 | 0 | 0.00589602676 | 0.0190606057 | 0.995139419 | 0.999315556 | 0.42316547 |
| 2 | Sheet10 | Charge_V_kurtosis | 163 | 163 | 0 | 0 | 0.665880904 | 0.861602409 | 0.995759251 | 0.995308651 | 15.6283732 |
| 2 | Sheet10 | Charge_T_kurtosis | 163 | 163 | 0 | 0 | 0.00539555506 | 0.0191424455 | 0.965186353 | 0.998459986 | 0.326185382 |
| 2 | Sheet11 | CC_energy | 130 | 130 | 0 | 0 | 0.0654271428 | 0.0770299133 | 0.994274304 | 0.977653662 | 1.15616769 |
| 2 | Sheet11 | CC_Q | 130 | 130 | 0 | 0 | 0.0153085415 | 0.0181083204 | 0.995253452 | 0.980521378 | 1.06171554 |
| 2 | Sheet11 | CC_t_mean | 130 | 130 | 0 | 0 | 0.0764284684 | 0.0904473048 | 0.99519288 | 0.98019487 | 1.06019073 |
| 2 | Sheet11 | CC_V_mean | 130 | 130 | 0 | 0 | 0.00412188004 | 0.00458216463 | 0.988674734 | 0.942600531 | 0.105011102 |
| 2 | Sheet11 | CC_T_mean | 130 | 130 | 0 | 0 | 0.0448343608 | 0.0530950214 | 0.996512636 | 0.99521501 | 0.157110983 |
| 2 | Sheet11 | CC_V_std | 130 | 130 | 0 | 0 | 0.00226080804 | 0.0028898242 | 0.98772396 | 0.963002312 | 1.58875951 |
| 2 | Sheet11 | CC_T_std | 130 | 130 | 0 | 0 | 0.0149663419 | 0.0416269585 | 0.953137925 | 0.983109128 | 0.509051904 |
| 2 | Sheet11 | CC_V_skewness | 130 | 130 | 0 | 0 | 0.158634196 | 0.170177651 | 0.99842279 | 0.998749129 | 48.006057 |
| 2 | Sheet11 | CC_T_skewness | 130 | 130 | 0 | 0 | 0.0119319288 | 0.0263945216 | 0.951956857 | 0.994896824 | 3.51560108 |
| 2 | Sheet11 | CC_V_kurtosis | 130 | 130 | 0 | 0 | 0.436240278 | 0.502415083 | 0.998340097 | 0.997968018 | 13.7159467 |
| 2 | Sheet11 | CC_T_kurtosis | 130 | 130 | 0 | 0 | 0.0124686675 | 0.0393186929 | 0.875276471 | 0.995016995 | 0.686585309 |
| 2 | Sheet11 | CC_CCCT | 130 | 130 | 0 | 0 | 0.153063053 | 0.181062795 | 0.995253298 | 0.98036131 | 1.061578 |
| 2 | Sheet11 | CC_entropy | 130 | 130 | 0 | 0 | 4.99395705 | 4.99431492 | 0.998625864 | 0.997240101 | 67.4426092 |
| 2 | Sheet11 | dV_energy | 130 | 130 | 0 | 0 | 0.00935559753 | 0.030818422 | 0.955297608 | 0.977235484 | 0.713771574 |
| 2 | Sheet11 | dV_Q | 130 | 130 | 0 | 0 | 0.00236658306 | 0.00781802493 | 0.955285944 | 0.979469602 | 0.712503874 |
| 2 | Sheet11 | dV_t_mean | 130 | 130 | 0 | 0 | 0.011840135 | 0.0393568861 | 0.954467764 | 0.979475064 | 0.712954702 |
| 2 | Sheet11 | dV_V_mean | 130 | 130 | 0 | 0 | 0.000148996611 | 0.000248876551 | 0.983508643 | 0.921892199 | 0.00377570871 |
| 2 | Sheet11 | dV_T_mean | 130 | 130 | 0 | 0 | 0.00889496325 | 0.0106811064 | 0.999503627 | 0.999004491 | 0.0299368483 |
| 2 | Sheet11 | dV_V_std | 130 | 130 | 0 | 0 | 0.000109450214 | 0.000126655804 | 0.676270069 | 0.65287885 | 0.381877688 |
| 2 | Sheet11 | dV_T_std | 130 | 130 | 0 | 0 | 0.00719206416 | 0.00956891042 | 0.997920101 | 0.994231793 | 1.11866672 |
| 2 | Sheet11 | dV_V_skewness | 130 | 130 | 0 | 0 | 0.00327594103 | 0.0105848604 | 0.984089188 | 0.98693488 | 2.03404873 |
| 2 | Sheet11 | dV_T_skewness | 130 | 130 | 0 | 0 | 0.0344732764 | 0.0439280605 | 0.974126784 | 0.961539827 | 20.5053019 |
| 2 | Sheet11 | dV_V_kurtosis | 130 | 130 | 0 | 0 | 0.00153389298 | 0.00195115132 | 0.960705493 | 0.918169031 | 0.0832674662 |
| 2 | Sheet11 | dV_T_kurtosis | 130 | 130 | 0 | 0 | 0.051012841 | 0.110610958 | 0.823793926 | 0.919228721 | 2.77911245 |
| 2 | Sheet11 | dV_dV_devide_dt | 130 | 130 | 0 | 0 | 8.78690876e-05 | 0.000396437792 | 0.977866289 | 0.994661798 | 0.29264054 |
| 2 | Sheet11 | dV_entropy | 130 | 130 | 0 | 0 | 4.78458677 | 4.78495132 | -0.292025721 | -0.310639189 | 63.3920454 |
| 2 | Sheet11 | CV_energy | 130 | 130 | 0 | 0 | 0.0472707662 | 0.0536734102 | 0.97851518 | 0.976637671 | 2.82257086 |
| 2 | Sheet11 | CV_Q | 130 | 130 | 0 | 0 | 0.011254448 | 0.0127787942 | 0.978514905 | 0.976637671 | 2.82244525 |
| 2 | Sheet11 | CV_t_mean | 130 | 130 | 0 | 0 | 0.0706626729 | 0.101224563 | 0.998219678 | 0.996028874 | 0.470258608 |
| 2 | Sheet11 | CV_C_mean | 130 | 130 | 0 | 0 | 0.014375003 | 0.016813594 | 0.983985262 | 0.959300055 | 1.79529939 |
| 2 | Sheet11 | CV_T_mean | 130 | 130 | 0 | 0 | 0.0230158265 | 0.0268251314 | 0.999426708 | 0.998000792 | 0.0911304701 |
| 2 | Sheet11 | CV_C_std | 130 | 130 | 0 | 0 | 0.0300688364 | 0.0348568807 | 0.853272191 | 0.808425624 | 2.64906892 |
| 2 | Sheet11 | CV_T_std | 130 | 130 | 0 | 0 | 0.0158309022 | 0.018379708 | 0.997412443 | 0.996083519 | 0.443559957 |
| 2 | Sheet11 | CV_C_skewness | 130 | 130 | 0 | 0 | 0.0113634863 | 0.0132585758 | 0.998322873 | 0.995667011 | 0.444852149 |
| 2 | Sheet11 | CV_T_skewness | 130 | 130 | 0 | 0 | 0.00652241775 | 0.00813916349 | 0.996514378 | 0.991796954 | 0.829390826 |
| 2 | Sheet11 | CV_C_kurtosis | 130 | 130 | 0 | 0 | 0.0733054901 | 0.0884110937 | 0.997160222 | 0.9955318 | 0.794731463 |
| 2 | Sheet11 | CV_T_kurtosis | 130 | 130 | 0 | 0 | 0.0171518898 | 0.0223382982 | 0.994788956 | 0.988530485 | 0.753888214 |
| 2 | Sheet11 | CV_CVCT | 130 | 130 | 0 | 0 | 0.132396187 | 0.196258955 | 0.99824508 | 0.996407137 | 0.44069461 |
| 2 | Sheet11 | CV_entropy | 130 | 130 | 0 | 0 | 4.46049006 | 4.46205231 | 0.971715708 | 0.971167846 | 74.9061221 |
| 2 | Sheet11 | dI_energy | 130 | 130 | 0 | 0 | 0.00109059785 | 0.00118925795 | 0.991914161 | 0.978085185 | 3.99388456 |
| 2 | Sheet11 | dI_Q | 130 | 130 | 0 | 0 | 0.000259666047 | 0.000283156582 | 0.991914149 | 0.978085185 | 3.99388277 |
| 2 | Sheet11 | dI_t_mean | 130 | 130 | 0 | 0 | 0.00814531544 | 0.00888830044 | 0.991979944 | 0.981391227 | 3.95989874 |
| 2 | Sheet11 | dI_C_mean | 130 | 130 | 0 | 0 | 0.000797934276 | 0.000980353747 | 0.0096073822 | -0.0190279807 | 0.0841311987 |
| 2 | Sheet11 | dI_T_mean | 130 | 130 | 0 | 0 | 0.0199880554 | 0.0240444289 | 0.997863196 | 0.997114527 | 0.0692078183 |
| 2 | Sheet11 | dI_C_std | 130 | 130 | 0 | 0 | 0.000424357579 | 0.00053107664 | -0.0447025489 | -0.0476996818 | 1.46918539 |
| 2 | Sheet11 | dI_T_std | 130 | 130 | 0 | 0 | 0.0164823333 | 0.0206557196 | 0.741940526 | 0.717931421 | 15.879104 |
| 2 | Sheet11 | dI_C_skewness | 130 | 130 | 0 | 0 | 0.0222593217 | 0.026406077 | 0.314887265 | 0.300916304 | 37.2331809 |
| 2 | Sheet11 | dI_T_skewness | 130 | 130 | 0 | 0 | 0.329683858 | 0.437050734 | 0.402024305 | 0.329331276 | 97.0132773 |
| 2 | Sheet11 | dI_C_kurtosis | 130 | 130 | 0 | 0 | 0.0254469721 | 0.0293362185 | -0.105614894 | -0.0576410985 | 1.41426449 |
| 2 | Sheet11 | dI_T_kurtosis | 130 | 130 | 0 | 0 | 0.479929566 | 0.885851829 | 0.0838509867 | 0.248891474 | 22.127958 |
| 2 | Sheet11 | dI_dI_devide_dt | 130 | 130 | 0 | 0 | 0.00162723077 | 0.00203496484 | 0.998091488 | 0.993906719 | 0.684004181 |
| 2 | Sheet11 | dI_entropy | 130 | 130 | 0 | 0 | 1.86780059 | 1.87669541 | -0.126610621 | -0.0441378281 | 40.2704437 |
| 2 | Sheet11 | Charge_energy | 130 | 130 | 0 | 0 | 0.00185393919 | 0.00442285449 | 0.999893409 | 0.999944011 | 0.025253931 |
| 2 | Sheet11 | Charge_Q | 130 | 130 | 0 | 0 | 0.000259379081 | 0.00109636218 | 0.9998927 | 0.999938549 | 0.0140782355 |
| 2 | Sheet11 | Charge_t_mean | 130 | 130 | 0 | 0 | 0.0148870839 | 0.0989077557 | 0.996003818 | 0.999725515 | 0.0669325422 |
| 2 | Sheet11 | Charge_V_mean | 130 | 130 | 0 | 0 | 0.00136482023 | 0.00140906184 | 0.999555477 | 0.999097351 | 0.0332059472 |
| 2 | Sheet11 | Charge_C_mean | 130 | 130 | 0 | 0 | 0.00323041845 | 0.00809390471 | 0.999112911 | 0.999475615 | 0.12957438 |
| 2 | Sheet11 | Charge_T_mean | 130 | 130 | 0 | 0 | 0.0128091826 | 0.0131839542 | 0.99997112 | 0.999808819 | 0.0486705553 |
| 2 | Sheet11 | Charge_C_std | 130 | 130 | 0 | 0 | 0.00163718307 | 0.00464175663 | 0.996763982 | 0.999366354 | 0.0628878583 |
| 2 | Sheet11 | Charge_V_std | 130 | 130 | 0 | 0 | 0.00377487004 | 0.00405126871 | 0.990759872 | 0.985968654 | 2.48284958 |
| 2 | Sheet11 | Charge_T_std | 130 | 130 | 0 | 0 | 0.00215942518 | 0.00263789502 | 0.999864371 | 0.999382758 | 0.0581790963 |
| 2 | Sheet11 | Charge_C_skewness | 130 | 130 | 0 | 0 | 0.00335962436 | 0.00690683083 | 0.998921733 | 0.999235271 | 0.668667828 |
| 2 | Sheet11 | Charge_V_skewness | 130 | 130 | 0 | 0 | 0.113476588 | 0.136109113 | 0.99801269 | 0.991451427 | 7.27203062 |
| 2 | Sheet11 | Charge_T_skewness | 130 | 130 | 0 | 0 | 0.00567656786 | 0.00956429045 | 0.9965393 | 0.998656234 | 1.90481658 |
| 2 | Sheet11 | Charge_C_kurtosis | 130 | 130 | 0 | 0 | 0.00598037878 | 0.0200161983 | 0.99505359 | 0.99891297 | 0.432992755 |
| 2 | Sheet11 | Charge_V_kurtosis | 130 | 130 | 0 | 0 | 0.811711861 | 1.05167173 | 0.998638169 | 0.994674212 | 17.7600305 |
| 2 | Sheet11 | Charge_T_kurtosis | 130 | 130 | 0 | 0 | 0.00419675717 | 0.0116150753 | 0.992514945 | 0.997248228 | 0.251690831 |
| 2 | Sheet12 | CC_energy | 211 | 211 | 0 | 0 | 0.0670394341 | 0.0782285384 | 0.994537759 | 0.975485423 | 1.17792168 |
| 2 | Sheet12 | CC_Q | 211 | 211 | 0 | 0 | 0.0157595464 | 0.0184544817 | 0.995537452 | 0.979763602 | 1.08559449 |
| 2 | Sheet12 | CC_t_mean | 211 | 211 | 0 | 0 | 0.0791139896 | 0.0926581681 | 0.995495125 | 0.979273986 | 1.0899292 |
| 2 | Sheet12 | CC_V_mean | 211 | 211 | 0 | 0 | 0.00396237749 | 0.00439562972 | 0.989618656 | 0.941534645 | 0.10105152 |
| 2 | Sheet12 | CC_T_mean | 211 | 211 | 0 | 0 | 0.0460791156 | 0.0544561655 | 0.996984396 | 0.995190404 | 0.160098279 |
| 2 | Sheet12 | CC_V_std | 211 | 211 | 0 | 0 | 0.00162702238 | 0.00213587957 | 0.963269598 | 0.921492525 | 1.19056831 |
| 2 | Sheet12 | CC_T_std | 211 | 211 | 0 | 0 | 0.0145603996 | 0.0430653045 | 0.924168044 | 0.992072467 | 0.493885435 |
| 2 | Sheet12 | CC_V_skewness | 211 | 211 | 0 | 0 | 0.132702401 | 0.140495604 | 0.997313319 | 0.996280068 | 81.7914689 |
| 2 | Sheet12 | CC_T_skewness | 211 | 211 | 0 | 0 | 0.011059602 | 0.0206305522 | 0.961129881 | 0.992836382 | 3.11691709 |
| 2 | Sheet12 | CC_V_kurtosis | 211 | 211 | 0 | 0 | 0.302531414 | 0.336630757 | 0.995218679 | 0.987929383 | 11.0693294 |
| 2 | Sheet12 | CC_T_kurtosis | 211 | 211 | 0 | 0 | 0.0114368792 | 0.025736016 | 0.921270124 | 0.98905577 | 0.618954919 |
| 2 | Sheet12 | CC_CCCT | 211 | 211 | 0 | 0 | 0.157576594 | 0.184525859 | 0.99553754 | 0.979761556 | 1.08549335 |
| 2 | Sheet12 | CC_entropy | 211 | 211 | 0 | 0 | 5.01504241 | 5.0151923 | 0.997918535 | 0.973151938 | 67.1969008 |
| 2 | Sheet12 | dV_energy | 211 | 211 | 0 | 0 | 0.00954005497 | 0.0220235899 | 0.952520367 | 0.979355232 | 0.747481542 |
| 2 | Sheet12 | dV_Q | 211 | 211 | 0 | 0 | 0.00241380929 | 0.00558750887 | 0.952430015 | 0.980780882 | 0.746195281 |
| 2 | Sheet12 | dV_t_mean | 211 | 211 | 0 | 0 | 0.0120901664 | 0.028032281 | 0.951993187 | 0.979996519 | 0.747532265 |
| 2 | Sheet12 | dV_V_mean | 211 | 211 | 0 | 0 | 0.000125193889 | 0.000175111682 | 0.976897417 | 0.939609511 | 0.0031730979 |
| 2 | Sheet12 | dV_T_mean | 211 | 211 | 0 | 0 | 0.00735611325 | 0.00931647851 | 0.999885788 | 0.999701077 | 0.0243710349 |
| 2 | Sheet12 | dV_V_std | 211 | 211 | 0 | 0 | 0.000139664599 | 0.000155331249 | 0.474857202 | 0.36657171 | 0.487901003 |
| 2 | Sheet12 | dV_T_std | 211 | 211 | 0 | 0 | 0.00792449938 | 0.0113427353 | 0.996650484 | 0.994616508 | 1.33888946 |
| 2 | Sheet12 | dV_V_skewness | 211 | 211 | 0 | 0 | 0.00228295294 | 0.00526109759 | 0.988509487 | 0.992957297 | 1.19912177 |
| 2 | Sheet12 | dV_T_skewness | 211 | 211 | 0 | 0 | 0.0366567714 | 0.0490668824 | 0.974677514 | 0.968001175 | 20.5958594 |
| 2 | Sheet12 | dV_V_kurtosis | 211 | 211 | 0 | 0 | 0.00166960607 | 0.00227625804 | 0.954409717 | 0.919607568 | 0.0902068209 |
| 2 | Sheet12 | dV_T_kurtosis | 211 | 211 | 0 | 0 | 0.0480083207 | 0.0807306391 | 0.908779934 | 0.942770276 | 2.58920666 |
| 2 | Sheet12 | dV_dV_devide_dt | 211 | 211 | 0 | 0 | 8.98160689e-05 | 0.0003253089 | 0.971423499 | 0.991209704 | 0.292128838 |
| 2 | Sheet12 | dV_entropy | 211 | 211 | 0 | 0 | 4.75606756 | 4.75631366 | 0.260823737 | 0.0635889883 | 63.2790067 |
| 2 | Sheet12 | CV_energy | 211 | 211 | 0 | 0 | 0.041600145 | 0.0489067272 | 0.978186697 | 0.972120949 | 2.50117239 |
| 2 | Sheet12 | CV_Q | 211 | 211 | 0 | 0 | 0.0099046229 | 0.0116442015 | 0.978184044 | 0.972117117 | 2.50109968 |
| 2 | Sheet12 | CV_t_mean | 211 | 211 | 0 | 0 | 0.0577354336 | 0.0703862433 | 0.999319199 | 0.997954791 | 0.418852243 |
| 2 | Sheet12 | CV_C_mean | 211 | 211 | 0 | 0 | 0.0147552058 | 0.0184721759 | 0.964036989 | 0.886221119 | 1.70271751 |
| 2 | Sheet12 | CV_T_mean | 211 | 211 | 0 | 0 | 0.0230469993 | 0.0275714919 | 0.999457878 | 0.998902671 | 0.0901491595 |
| 2 | Sheet12 | CV_C_std | 211 | 211 | 0 | 0 | 0.0282550883 | 0.0334444481 | 0.754361238 | 0.616849065 | 2.39846219 |
| 2 | Sheet12 | CV_T_std | 211 | 211 | 0 | 0 | 0.0143691529 | 0.0173115003 | 0.997030683 | 0.996720788 | 0.384313095 |
| 2 | Sheet12 | CV_C_skewness | 211 | 211 | 0 | 0 | 0.0130632703 | 0.0165979661 | 0.994974198 | 0.986368253 | 0.555085577 |
| 2 | Sheet12 | CV_T_skewness | 211 | 211 | 0 | 0 | 0.00659326322 | 0.00814272667 | 0.996543504 | 0.990735938 | 0.91779464 |
| 2 | Sheet12 | CV_C_kurtosis | 211 | 211 | 0 | 0 | 0.0709917978 | 0.0997635432 | 0.992836119 | 0.986776018 | 0.867787473 |
| 2 | Sheet12 | CV_T_kurtosis | 211 | 211 | 0 | 0 | 0.0150879212 | 0.0196602947 | 0.993371321 | 0.981671159 | 0.705967884 |
| 2 | Sheet12 | CV_CVCT | 211 | 211 | 0 | 0 | 0.108771097 | 0.134596501 | 0.999347472 | 0.997978102 | 0.394645527 |
| 2 | Sheet12 | CV_entropy | 211 | 211 | 0 | 0 | 4.55783336 | 4.55800923 | 0.986102475 | 0.952307859 | 73.7759314 |
| 2 | Sheet12 | dI_energy | 211 | 211 | 0 | 0 | 0.000969899728 | 0.00110946958 | 0.998270164 | 0.992696823 | 2.27402558 |
| 2 | Sheet12 | dI_Q | 211 | 211 | 0 | 0 | 0.000230926298 | 0.000264157506 | 0.998270398 | 0.992723649 | 2.27396716 |
| 2 | Sheet12 | dI_t_mean | 211 | 211 | 0 | 0 | 0.00726553103 | 0.00831825586 | 0.998278719 | 0.993030237 | 2.26017418 |
| 2 | Sheet12 | dI_C_mean | 211 | 211 | 0 | 0 | 0.000544026832 | 0.000698143496 | 0.78933208 | 0.789720366 | 0.0573966153 |
| 2 | Sheet12 | dI_T_mean | 211 | 211 | 0 | 0 | 0.017259459 | 0.0218371111 | 0.996099228 | 0.995738103 | 0.0602665642 |
| 2 | Sheet12 | dI_C_std | 211 | 211 | 0 | 0 | 0.000338252991 | 0.000415334924 | 0.0270371557 | 0.000532696312 | 1.17185745 |
| 2 | Sheet12 | dI_T_std | 211 | 211 | 0 | 0 | 0.0139352689 | 0.0173688312 | 0.927760985 | 0.926830265 | 8.49169427 |
| 2 | Sheet12 | dI_C_skewness | 211 | 211 | 0 | 0 | 0.0113908808 | 0.0155747064 | 0.912370197 | 0.919258824 | 13.0534002 |
| 2 | Sheet12 | dI_T_skewness | 211 | 211 | 0 | 0 | 0.203524921 | 0.275383493 | 0.562888375 | 0.548711692 | 83.9790928 |
| 2 | Sheet12 | dI_C_kurtosis | 211 | 211 | 0 | 0 | 0.0144972457 | 0.0185036042 | 0.363546705 | 0.360071524 | 0.800294209 |
| 2 | Sheet12 | dI_T_kurtosis | 211 | 211 | 0 | 0 | 0.278179254 | 0.377020456 | 0.377960625 | 0.376871384 | 13.9284996 |
| 2 | Sheet12 | dI_dI_devide_dt | 211 | 211 | 0 | 0 | 0.00120172405 | 0.00162808827 | 0.999459007 | 0.996932821 | 0.741491641 |
| 2 | Sheet12 | dI_entropy | 211 | 211 | 0 | 0 | 2.46297941 | 2.48883203 | -0.0372199595 | 0.160767773 | 47.0801365 |
| 2 | Sheet12 | Charge_energy | 211 | 211 | 0 | 0 | 0.00209910679 | 0.00863575454 | 0.999561629 | 0.999926546 | 0.0285109394 |
| 2 | Sheet12 | Charge_Q | 211 | 211 | 0 | 0 | 0.000392998173 | 0.00224744357 | 0.999589602 | 0.999958483 | 0.0212475815 |
| 2 | Sheet12 | Charge_t_mean | 211 | 211 | 0 | 0 | 0.0131509523 | 0.0830913914 | 0.995702168 | 0.999717681 | 0.0624829236 |
| 2 | Sheet12 | Charge_V_mean | 211 | 211 | 0 | 0 | 0.00120399085 | 0.0012194619 | 0.999905362 | 0.999591216 | 0.0293442023 |
| 2 | Sheet12 | Charge_C_mean | 211 | 211 | 0 | 0 | 0.00187983759 | 0.00274485684 | 0.999930714 | 0.999853093 | 0.0711259606 |
| 2 | Sheet12 | Charge_T_mean | 211 | 211 | 0 | 0 | 0.0137115293 | 0.0140226803 | 0.999984514 | 0.999909301 | 0.0514059115 |
| 2 | Sheet12 | Charge_C_std | 211 | 211 | 0 | 0 | 0.00126431369 | 0.00296969581 | 0.998494605 | 0.999382981 | 0.0483384473 |
| 2 | Sheet12 | Charge_V_std | 211 | 211 | 0 | 0 | 0.00288966983 | 0.00299658549 | 0.997733336 | 0.995953998 | 1.86589517 |
| 2 | Sheet12 | Charge_T_std | 211 | 211 | 0 | 0 | 0.00218027805 | 0.00268118807 | 0.999857938 | 0.999681915 | 0.0572684277 |
| 2 | Sheet12 | Charge_C_skewness | 211 | 211 | 0 | 0 | 0.00262569124 | 0.00494980097 | 0.999512064 | 0.999836485 | 0.662589109 |
| 2 | Sheet12 | Charge_V_skewness | 211 | 211 | 0 | 0 | 0.0744745059 | 0.0863836784 | 0.996736676 | 0.991959964 | 5.54337357 |
| 2 | Sheet12 | Charge_T_skewness | 211 | 211 | 0 | 0 | 0.00491165628 | 0.00659631351 | 0.998838024 | 0.998762144 | 2.20874539 |
| 2 | Sheet12 | Charge_C_kurtosis | 211 | 211 | 0 | 0 | 0.00443730918 | 0.0151148935 | 0.996433962 | 0.999835205 | 0.34283307 |
| 2 | Sheet12 | Charge_V_kurtosis | 211 | 211 | 0 | 0 | 0.471371334 | 0.58967097 | 0.994344153 | 0.994044426 | 13.2449231 |
| 2 | Sheet12 | Charge_T_kurtosis | 211 | 211 | 0 | 0 | 0.00320373503 | 0.00967109743 | 0.991619052 | 0.995977159 | 0.196628332 |
| 2 | Sheet13 | CC_energy | 225 | 225 | 0 | 0 | 0.0633951622 | 0.0757157517 | 0.994748813 | 0.970094817 | 1.10975716 |
| 2 | Sheet13 | CC_Q | 225 | 225 | 0 | 0 | 0.0148882252 | 0.0178469404 | 0.995729254 | 0.973442899 | 1.02165079 |
| 2 | Sheet13 | CC_t_mean | 225 | 225 | 0 | 0 | 0.074848416 | 0.0894068845 | 0.995751323 | 0.974036287 | 1.0272166 |
| 2 | Sheet13 | CC_V_mean | 225 | 225 | 0 | 0 | 0.00381394812 | 0.00427871956 | 0.989532789 | 0.963331226 | 0.0972744794 |
| 2 | Sheet13 | CC_T_mean | 225 | 225 | 0 | 0 | 0.0446479113 | 0.0534875857 | 0.997508293 | 0.994681837 | 0.152828786 |
| 2 | Sheet13 | CC_V_std | 225 | 225 | 0 | 0 | 0.00172460685 | 0.00217089351 | 0.957357567 | 0.914108195 | 1.27497423 |
| 2 | Sheet13 | CC_T_std | 225 | 225 | 0 | 0 | 0.0125163911 | 0.0359059056 | 0.979629578 | 0.99674647 | 0.398544979 |
| 2 | Sheet13 | CC_V_skewness | 225 | 225 | 0 | 0 | 0.134297261 | 0.143793693 | 0.997951269 | 0.997683312 | 64.0378301 |
| 2 | Sheet13 | CC_T_skewness | 225 | 225 | 0 | 0 | 0.0112277015 | 0.0199866598 | 0.97229705 | 0.994642066 | 2.49714428 |
| 2 | Sheet13 | CC_V_kurtosis | 225 | 225 | 0 | 0 | 0.304115008 | 0.345652766 | 0.995281476 | 0.993711547 | 11.1607863 |
| 2 | Sheet13 | CC_T_kurtosis | 225 | 225 | 0 | 0 | 0.0147801297 | 0.0310294018 | 0.947444587 | 0.995328433 | 0.762498576 |
| 2 | Sheet13 | CC_CCCT | 225 | 225 | 0 | 0 | 0.148866492 | 0.178453936 | 0.995729226 | 0.973624478 | 1.02156125 |
| 2 | Sheet13 | CC_entropy | 225 | 225 | 0 | 0 | 5.011206 | 5.01138758 | 0.978983543 | 0.970778406 | 67.2567806 |
| 2 | Sheet13 | dV_energy | 225 | 225 | 0 | 0 | 0.00589120308 | 0.00778793263 | 0.994047077 | 0.993009896 | 0.469210612 |
| 2 | Sheet13 | dV_Q | 225 | 225 | 0 | 0 | 0.00149201607 | 0.00197579182 | 0.993993252 | 0.99299988 | 0.468840906 |
| 2 | Sheet13 | dV_t_mean | 225 | 225 | 0 | 0 | 0.00744234118 | 0.00989354922 | 0.993715895 | 0.993120777 | 0.467699894 |
| 2 | Sheet13 | dV_V_mean | 225 | 225 | 0 | 0 | 0.000103214574 | 0.000130976133 | 0.978288401 | 0.945010506 | 0.00261608928 |
| 2 | Sheet13 | dV_T_mean | 225 | 225 | 0 | 0 | 0.00771139778 | 0.00969077619 | 0.999922457 | 0.999660767 | 0.0250122959 |
| 2 | Sheet13 | dV_V_std | 225 | 225 | 0 | 0 | 9.9548674e-05 | 0.000119709821 | 0.589228502 | 0.530254952 | 0.346819187 |
| 2 | Sheet13 | dV_T_std | 225 | 225 | 0 | 0 | 0.00796630747 | 0.0110321615 | 0.996917453 | 0.994905183 | 1.34325383 |
| 2 | Sheet13 | dV_V_skewness | 225 | 225 | 0 | 0 | 0.00197333554 | 0.00326311544 | 0.992477193 | 0.988749461 | 1.00534702 |
| 2 | Sheet13 | dV_T_skewness | 225 | 225 | 0 | 0 | 0.0374252978 | 0.0594787554 | 0.967947177 | 0.979042351 | 18.8705134 |
| 2 | Sheet13 | dV_V_kurtosis | 225 | 225 | 0 | 0 | 0.00191604267 | 0.00257439656 | 0.904053519 | 0.87821205 | 0.10353934 |
| 2 | Sheet13 | dV_T_kurtosis | 225 | 225 | 0 | 0 | 0.0527159684 | 0.0986895564 | 0.894500239 | 0.949254109 | 2.84362751 |
| 2 | Sheet13 | dV_dV_devide_dt | 225 | 225 | 0 | 0 | 5.52381361e-05 | 0.000104349903 | 0.996205825 | 0.998328848 | 0.176571733 |
| 2 | Sheet13 | dV_entropy | 225 | 225 | 0 | 0 | 4.74481803 | 4.74509268 | 0.49094902 | 0.340684553 | 63.2306166 |
| 2 | Sheet13 | CV_energy | 225 | 225 | 0 | 0 | 0.0423210219 | 0.0490886307 | 0.980284902 | 0.97572166 | 2.55658261 |
| 2 | Sheet13 | CV_Q | 225 | 225 | 0 | 0 | 0.0100759377 | 0.0116871787 | 0.98028474 | 0.975723767 | 2.55645557 |
| 2 | Sheet13 | CV_t_mean | 225 | 225 | 0 | 0 | 0.0570084403 | 0.0652305801 | 0.999704994 | 0.99924252 | 0.40619922 |
| 2 | Sheet13 | CV_C_mean | 225 | 225 | 0 | 0 | 0.0140949749 | 0.0167747699 | 0.957406143 | 0.880705021 | 1.66540634 |
| 2 | Sheet13 | CV_T_mean | 225 | 225 | 0 | 0 | 0.0246081075 | 0.0292552545 | 0.999255647 | 0.998689423 | 0.0973757723 |
| 2 | Sheet13 | CV_C_std | 225 | 225 | 0 | 0 | 0.0281324245 | 0.0331074391 | 0.64329319 | 0.550616308 | 2.40780628 |
| 2 | Sheet13 | CV_T_std | 225 | 225 | 0 | 0 | 0.0202468228 | 0.0353556342 | 0.977866314 | 0.991257892 | 0.514031805 |
| 2 | Sheet13 | CV_C_skewness | 225 | 225 | 0 | 0 | 0.0122608189 | 0.0145213169 | 0.994214758 | 0.977490518 | 0.511752085 |
| 2 | Sheet13 | CV_T_skewness | 225 | 225 | 0 | 0 | 0.00672199186 | 0.00803204988 | 0.997704777 | 0.993837969 | 0.803443969 |
| 2 | Sheet13 | CV_C_kurtosis | 225 | 225 | 0 | 0 | 0.0666132088 | 0.0793325887 | 0.993562376 | 0.978672252 | 0.793176987 |
| 2 | Sheet13 | CV_T_kurtosis | 225 | 225 | 0 | 0 | 0.0177532071 | 0.0230543637 | 0.993167177 | 0.986254741 | 0.764371962 |
| 2 | Sheet13 | CV_CVCT | 225 | 225 | 0 | 0 | 0.105946238 | 0.122695764 | 0.999715214 | 0.999196428 | 0.377558561 |
| 2 | Sheet13 | CV_entropy | 225 | 225 | 0 | 0 | 4.53411152 | 4.53422223 | 0.986342344 | 0.943008288 | 74.0186817 |
| 2 | Sheet13 | dI_energy | 225 | 225 | 0 | 0 | 0.000987405936 | 0.00110769467 | 0.998657535 | 0.995768015 | 2.30503894 |
| 2 | Sheet13 | dI_Q | 225 | 225 | 0 | 0 | 0.00023509651 | 0.000263735902 | 0.998657606 | 0.995759587 | 2.30503663 |
| 2 | Sheet13 | dI_t_mean | 225 | 225 | 0 | 0 | 0.00738181439 | 0.00828722609 | 0.998660882 | 0.99563132 | 2.28544438 |
| 2 | Sheet13 | dI_C_mean | 225 | 225 | 0 | 0 | 0.000542637363 | 0.000676443276 | 0.752862328 | 0.759673409 | 0.0572721107 |
| 2 | Sheet13 | dI_T_mean | 225 | 225 | 0 | 0 | 0.0181424127 | 0.0229077029 | 0.999137471 | 0.998459756 | 0.0635651548 |
| 2 | Sheet13 | dI_C_std | 225 | 225 | 0 | 0 | 0.000279636339 | 0.00035780716 | 0.118862652 | 0.112902444 | 0.970977285 |
| 2 | Sheet13 | dI_T_std | 225 | 225 | 0 | 0 | 0.0132335223 | 0.0165359555 | 0.948681762 | 0.943424989 | 7.04663667 |
| 2 | Sheet13 | dI_C_skewness | 225 | 225 | 0 | 0 | 0.0100519757 | 0.0143496515 | 0.920435174 | 0.935744838 | 10.0883363 |
| 2 | Sheet13 | dI_T_skewness | 225 | 225 | 0 | 0 | 0.171718868 | 0.228203991 | 0.419654782 | 0.462536873 | 99.5807479 |
| 2 | Sheet13 | dI_C_kurtosis | 225 | 225 | 0 | 0 | 0.0151526894 | 0.0189266248 | 0.477955205 | 0.463896966 | 0.834734832 |
| 2 | Sheet13 | dI_T_kurtosis | 225 | 225 | 0 | 0 | 0.18062607 | 0.238595785 | 0.400455809 | 0.419189011 | 9.45698903 |
| 2 | Sheet13 | dI_dI_devide_dt | 225 | 225 | 0 | 0 | 0.000952208902 | 0.00124418891 | 0.999620182 | 0.998770273 | 0.593184575 |
| 2 | Sheet13 | dI_entropy | 225 | 225 | 0 | 0 | 2.47495727 | 2.49896724 | -0.269572609 | -0.167176074 | 47.2088442 |
| 2 | Sheet13 | Charge_energy | 225 | 225 | 0 | 0 | 0.00145028221 | 0.00337550922 | 0.999948237 | 0.999947324 | 0.0196640694 |
| 2 | Sheet13 | Charge_Q | 225 | 225 | 0 | 0 | 0.000224490451 | 0.000868532765 | 0.999944324 | 0.999965234 | 0.0121137841 |
| 2 | Sheet13 | Charge_t_mean | 225 | 225 | 0 | 0 | 0.00590764695 | 0.0101470471 | 0.999942945 | 0.999396597 | 0.0276959699 |
| 2 | Sheet13 | Charge_V_mean | 225 | 225 | 0 | 0 | 0.00121436561 | 0.0012361937 | 0.999887543 | 0.999506953 | 0.0295916619 |
| 2 | Sheet13 | Charge_C_mean | 225 | 225 | 0 | 0 | 0.00222155602 | 0.00288492425 | 0.999961791 | 0.999668142 | 0.0849895761 |
| 2 | Sheet13 | Charge_T_mean | 225 | 225 | 0 | 0 | 0.0137901766 | 0.014124324 | 0.99998501 | 0.999926254 | 0.0517992172 |
| 2 | Sheet13 | Charge_C_std | 225 | 225 | 0 | 0 | 0.00101342448 | 0.00125476548 | 0.999889771 | 0.998821376 | 0.0387340867 |
| 2 | Sheet13 | Charge_V_std | 225 | 225 | 0 | 0 | 0.00289130656 | 0.00302496182 | 0.997612662 | 0.99605984 | 1.87570218 |
| 2 | Sheet13 | Charge_T_std | 225 | 225 | 0 | 0 | 0.00491720203 | 0.0298961535 | 0.990258278 | 0.999684998 | 0.119040182 |
| 2 | Sheet13 | Charge_C_skewness | 225 | 225 | 0 | 0 | 0.00249650663 | 0.00287016464 | 0.999964329 | 0.999593342 | 0.601406684 |
| 2 | Sheet13 | Charge_V_skewness | 225 | 225 | 0 | 0 | 0.0733365715 | 0.0838741632 | 0.998853474 | 0.994685787 | 5.47342661 |
| 2 | Sheet13 | Charge_T_skewness | 225 | 225 | 0 | 0 | 0.00434027218 | 0.00459645607 | 0.999911693 | 0.999483776 | 1.68370568 |
| 2 | Sheet13 | Charge_C_kurtosis | 225 | 225 | 0 | 0 | 0.00353084444 | 0.00833988522 | 0.99884218 | 0.999635482 | 0.269455247 |
| 2 | Sheet13 | Charge_V_kurtosis | 225 | 225 | 0 | 0 | 0.474715296 | 0.591059028 | 0.998025278 | 0.996370618 | 13.4383609 |
| 2 | Sheet13 | Charge_T_kurtosis | 225 | 225 | 0 | 0 | 0.00348940312 | 0.0120561022 | 0.989595464 | 0.997841603 | 0.216936099 |
| 2 | Sheet14 | CC_energy | 146 | 146 | 0 | 0 | 0.0730307588 | 0.0848412806 | 0.993735794 | 0.971091167 | 1.29517902 |
| 2 | Sheet14 | CC_Q | 146 | 146 | 0 | 0 | 0.0171444408 | 0.0199982647 | 0.994798993 | 0.974573183 | 1.19344885 |
| 2 | Sheet14 | CC_t_mean | 146 | 146 | 0 | 0 | 0.0856677304 | 0.0996537797 | 0.994796967 | 0.972672149 | 1.19276946 |
| 2 | Sheet14 | CC_V_mean | 146 | 146 | 0 | 0 | 0.00434920263 | 0.00479499899 | 0.986227441 | 0.946047011 | 0.110789894 |
| 2 | Sheet14 | CC_T_mean | 146 | 146 | 0 | 0 | 0.0394534734 | 0.04597469 | 0.996472297 | 0.993899723 | 0.147344815 |
| 2 | Sheet14 | CC_V_std | 146 | 146 | 0 | 0 | 0.00197466888 | 0.00263053379 | 0.982796159 | 0.903193403 | 1.41851139 |
| 2 | Sheet14 | CC_T_std | 146 | 146 | 0 | 0 | 0.0129351955 | 0.0388447941 | 0.883634595 | 0.991714297 | 0.556637129 |
| 2 | Sheet14 | CC_V_skewness | 146 | 146 | 0 | 0 | 0.149784409 | 0.159445197 | 0.998131999 | 0.998399738 | 56.9214497 |
| 2 | Sheet14 | CC_T_skewness | 146 | 146 | 0 | 0 | 0.0133234792 | 0.0193883323 | 0.979358435 | 0.994290143 | 4.09196221 |
| 2 | Sheet14 | CC_V_kurtosis | 146 | 146 | 0 | 0 | 0.381907323 | 0.435540537 | 0.997781155 | 0.997805906 | 12.8277578 |
| 2 | Sheet14 | CC_T_kurtosis | 146 | 146 | 0 | 0 | 0.0109388287 | 0.0201074738 | 0.967468452 | 0.994849272 | 0.611548326 |
| 2 | Sheet14 | CC_CCCT | 146 | 146 | 0 | 0 | 0.171414464 | 0.199955296 | 0.994798816 | 0.974498733 | 1.19325637 |
| 2 | Sheet14 | CC_entropy | 146 | 146 | 0 | 0 | 5.00282952 | 5.00309577 | 0.997925015 | 0.994828893 | 67.3339219 |
| 2 | Sheet14 | dV_energy | 146 | 146 | 0 | 0 | 0.0116346654 | 0.0296167674 | 0.950719869 | 0.975421041 | 0.895525558 |
| 2 | Sheet14 | dV_Q | 146 | 146 | 0 | 0 | 0.00294993024 | 0.00751304918 | 0.950750007 | 0.977145672 | 0.895974441 |
| 2 | Sheet14 | dV_t_mean | 146 | 146 | 0 | 0 | 0.0146428989 | 0.0373959971 | 0.950715012 | 0.974947677 | 0.889449037 |
| 2 | Sheet14 | dV_V_mean | 146 | 146 | 0 | 0 | 0.00010555964 | 0.00018462888 | 0.984592396 | 0.925025306 | 0.00267508146 |
| 2 | Sheet14 | dV_T_mean | 146 | 146 | 0 | 0 | 0.00646694269 | 0.00834841713 | 0.999675699 | 0.999357002 | 0.0233086236 |
| 2 | Sheet14 | dV_V_std | 146 | 146 | 0 | 0 | 0.000151387862 | 0.000167920329 | 0.539161107 | 0.474412193 | 0.529058146 |
| 2 | Sheet14 | dV_T_std | 146 | 146 | 0 | 0 | 0.00696392354 | 0.0091244369 | 0.995302459 | 0.989268603 | 1.38465127 |
| 2 | Sheet14 | dV_V_skewness | 146 | 146 | 0 | 0 | 0.00280298044 | 0.00748913791 | 0.987611808 | 0.983071599 | 1.65610284 |
| 2 | Sheet14 | dV_T_skewness | 146 | 146 | 0 | 0 | 0.0327323469 | 0.0408788667 | 0.858974372 | 0.822070122 | 49.0172461 |
| 2 | Sheet14 | dV_V_kurtosis | 146 | 146 | 0 | 0 | 0.00172018666 | 0.00229068329 | 0.950967437 | 0.895643624 | 0.0932513137 |
| 2 | Sheet14 | dV_T_kurtosis | 146 | 146 | 0 | 0 | 0.0413285029 | 0.0515862209 | 0.804448662 | 0.799381103 | 2.28852841 |
| 2 | Sheet14 | dV_dV_devide_dt | 146 | 146 | 0 | 0 | 8.6014058e-05 | 0.000406381448 | 0.972401918 | 0.993345128 | 0.284517167 |
| 2 | Sheet14 | dV_entropy | 146 | 146 | 0 | 0 | 4.77049976 | 4.77074566 | -0.180457176 | -0.237835116 | 63.3307156 |
| 2 | Sheet14 | CV_energy | 146 | 146 | 0 | 0 | 0.0443268917 | 0.0525528435 | 0.974269512 | 0.962530728 | 2.63804825 |
| 2 | Sheet14 | CV_Q | 146 | 146 | 0 | 0 | 0.0105542565 | 0.0125127829 | 0.974269415 | 0.962530728 | 2.63797778 |
| 2 | Sheet14 | CV_t_mean | 146 | 146 | 0 | 0 | 0.0600930999 | 0.0714271788 | 0.999449239 | 0.995950176 | 0.407616315 |
| 2 | Sheet14 | CV_C_mean | 146 | 146 | 0 | 0 | 0.0150144902 | 0.0180733874 | 0.972932205 | 0.925175695 | 1.83282127 |
| 2 | Sheet14 | CV_T_mean | 146 | 146 | 0 | 0 | 0.0179650806 | 0.0214931858 | 0.999652708 | 0.998199223 | 0.0739535223 |
| 2 | Sheet14 | CV_C_std | 146 | 146 | 0 | 0 | 0.029897382 | 0.0354081672 | 0.755669398 | 0.719174107 | 2.60789197 |
| 2 | Sheet14 | CV_T_std | 146 | 146 | 0 | 0 | 0.0120767349 | 0.0145225401 | 0.993795574 | 0.993656792 | 0.423837498 |
| 2 | Sheet14 | CV_C_skewness | 146 | 146 | 0 | 0 | 0.0125767565 | 0.017679444 | 0.994456854 | 0.990809008 | 0.503587241 |
| 2 | Sheet14 | CV_T_skewness | 146 | 146 | 0 | 0 | 0.00734331556 | 0.00878609988 | 0.997959935 | 0.992380438 | 0.935146295 |
| 2 | Sheet14 | CV_C_kurtosis | 146 | 146 | 0 | 0 | 0.0729849067 | 0.109006443 | 0.993067493 | 0.990288436 | 0.818307814 |
| 2 | Sheet14 | CV_T_kurtosis | 146 | 146 | 0 | 0 | 0.0180021038 | 0.0217895014 | 0.995380007 | 0.987996105 | 0.802105807 |
| 2 | Sheet14 | CV_CVCT | 146 | 146 | 0 | 0 | 0.112954894 | 0.136486885 | 0.999453544 | 0.99580363 | 0.383193505 |
| 2 | Sheet14 | CV_entropy | 146 | 146 | 0 | 0 | 4.51669232 | 4.51724559 | 0.985412127 | 0.969621889 | 74.6773845 |
| 2 | Sheet14 | dI_energy | 146 | 146 | 0 | 0 | 0.00112340241 | 0.00121918036 | 0.994575257 | 0.982404828 | 3.7823662 |
| 2 | Sheet14 | dI_Q | 146 | 146 | 0 | 0 | 0.000267494326 | 0.000290299802 | 0.994575193 | 0.982404828 | 3.78242702 |
| 2 | Sheet14 | dI_t_mean | 146 | 146 | 0 | 0 | 0.0084848432 | 0.00921217162 | 0.994538576 | 0.982487699 | 3.79252041 |
| 2 | Sheet14 | dI_C_mean | 146 | 146 | 0 | 0 | 0.000670279207 | 0.000833863633 | 0.36230524 | 0.363631631 | 0.0706758624 |
| 2 | Sheet14 | dI_T_mean | 146 | 146 | 0 | 0 | 0.0177045495 | 0.0218354941 | 0.997549845 | 0.996443751 | 0.0653426904 |
| 2 | Sheet14 | dI_C_std | 146 | 146 | 0 | 0 | 0.000381192766 | 0.000474090542 | 0.074019376 | 0.0804392045 | 1.32088664 |
| 2 | Sheet14 | dI_T_std | 146 | 146 | 0 | 0 | 0.0123657642 | 0.0155010516 | 0.618869858 | 0.627852275 | 13.5080238 |
| 2 | Sheet14 | dI_C_skewness | 146 | 146 | 0 | 0 | 0.019203979 | 0.0241345306 | 0.551116267 | 0.515945745 | 26.5892696 |
| 2 | Sheet14 | dI_T_skewness | 146 | 146 | 0 | 0 | 0.309206853 | 0.371667753 | 0.279268512 | 0.21050389 | 97.4675061 |
| 2 | Sheet14 | dI_C_kurtosis | 146 | 146 | 0 | 0 | 0.0240496583 | 0.0279324604 | 0.123770083 | 0.136297996 | 1.33479779 |
| 2 | Sheet14 | dI_T_kurtosis | 146 | 146 | 0 | 0 | 0.36437081 | 0.463070993 | 0.269749288 | 0.352068453 | 17.2897708 |
| 2 | Sheet14 | dI_dI_devide_dt | 146 | 146 | 0 | 0 | 0.00130190041 | 0.00159718826 | 0.998929752 | 0.993515051 | 0.590528629 |
| 2 | Sheet14 | dI_entropy | 146 | 146 | 0 | 0 | 1.98078965 | 1.99180627 | -0.384781782 | -0.329871596 | 41.6985354 |
| 2 | Sheet14 | Charge_energy | 146 | 146 | 0 | 0 | 0.0015692404 | 0.00351567637 | 0.999935029 | 0.999898778 | 0.0214189707 |
| 2 | Sheet14 | Charge_Q | 146 | 146 | 0 | 0 | 0.000241793828 | 0.00085767822 | 0.999935811 | 0.999891066 | 0.0131522704 |
| 2 | Sheet14 | Charge_t_mean | 146 | 146 | 0 | 0 | 0.0131248447 | 0.0980031031 | 0.994820934 | 0.999554623 | 0.0598554357 |
| 2 | Sheet14 | Charge_V_mean | 146 | 146 | 0 | 0 | 0.00130017424 | 0.00133144513 | 0.999754487 | 0.999032131 | 0.0316398865 |
| 2 | Sheet14 | Charge_C_mean | 146 | 146 | 0 | 0 | 0.0024969802 | 0.00362151626 | 0.999856192 | 0.999308802 | 0.0990142598 |
| 2 | Sheet14 | Charge_T_mean | 146 | 146 | 0 | 0 | 0.0101579883 | 0.0103973927 | 0.99998789 | 0.999907455 | 0.0404643172 |
| 2 | Sheet14 | Charge_C_std | 146 | 146 | 0 | 0 | 0.00131080486 | 0.0025870669 | 0.998959023 | 0.99898392 | 0.050345891 |
| 2 | Sheet14 | Charge_V_std | 146 | 146 | 0 | 0 | 0.00340289795 | 0.00361370706 | 0.993163794 | 0.989514416 | 2.24893658 |
| 2 | Sheet14 | Charge_T_std | 146 | 146 | 0 | 0 | 0.0025911086 | 0.00856831446 | 0.997382445 | 0.999509317 | 0.0883542844 |
| 2 | Sheet14 | Charge_C_skewness | 146 | 146 | 0 | 0 | 0.00318692021 | 0.00610563613 | 0.999158658 | 0.999635599 | 0.660832927 |
| 2 | Sheet14 | Charge_V_skewness | 146 | 146 | 0 | 0 | 0.0975784548 | 0.116411854 | 0.997737599 | 0.990670189 | 6.5226418 |
| 2 | Sheet14 | Charge_T_skewness | 146 | 146 | 0 | 0 | 0.00483200691 | 0.00598450006 | 0.99929752 | 0.999401347 | 1.60113129 |
| 2 | Sheet14 | Charge_C_kurtosis | 146 | 146 | 0 | 0 | 0.00624151312 | 0.0219243783 | 0.993286723 | 0.999633668 | 0.457933828 |
| 2 | Sheet14 | Charge_V_kurtosis | 146 | 146 | 0 | 0 | 0.683758129 | 0.90259633 | 0.995522309 | 0.99492148 | 16.2443327 |
| 2 | Sheet14 | Charge_T_kurtosis | 146 | 146 | 0 | 0 | 0.00434361665 | 0.0118376811 | 0.988658381 | 0.996668306 | 0.26248111 |
| 2 | Sheet15 | CC_energy | 167 | 167 | 0 | 0 | 0.0715914518 | 0.0825914469 | 0.994626041 | 0.977709813 | 1.28916301 |
| 2 | Sheet15 | CC_Q | 167 | 167 | 0 | 0 | 0.0168064109 | 0.0194559212 | 0.995492351 | 0.982316778 | 1.18862481 |
| 2 | Sheet15 | CC_t_mean | 167 | 167 | 0 | 0 | 0.0839083801 | 0.0970451862 | 0.99553043 | 0.983101986 | 1.18692196 |
| 2 | Sheet15 | CC_V_mean | 167 | 167 | 0 | 0 | 0.00434715504 | 0.00477415228 | 0.985115747 | 0.950614874 | 0.110670905 |
| 2 | Sheet15 | CC_T_mean | 167 | 167 | 0 | 0 | 0.0395539081 | 0.0462081802 | 0.996488009 | 0.994091851 | 0.146486925 |
| 2 | Sheet15 | CC_V_std | 167 | 167 | 0 | 0 | 0.00194253566 | 0.00244089353 | 0.986503595 | 0.904223207 | 1.40251989 |
| 2 | Sheet15 | CC_T_std | 167 | 167 | 0 | 0 | 0.0125611798 | 0.0344543841 | 0.938697273 | 0.992274697 | 0.530542646 |
| 2 | Sheet15 | CC_V_skewness | 167 | 167 | 0 | 0 | 0.152606145 | 0.161318874 | 0.998174872 | 0.998072701 | 58.9859366 |
| 2 | Sheet15 | CC_T_skewness | 167 | 167 | 0 | 0 | 0.0138590488 | 0.0227803774 | 0.972098761 | 0.988904499 | 3.76811767 |
| 2 | Sheet15 | CC_V_kurtosis | 167 | 167 | 0 | 0 | 0.3898221 | 0.438413669 | 0.997684676 | 0.996998258 | 13.0058888 |
| 2 | Sheet15 | CC_T_kurtosis | 167 | 167 | 0 | 0 | 0.0129282326 | 0.0295900458 | 0.936344446 | 0.992243778 | 0.703897787 |
| 2 | Sheet15 | CC_CCCT | 167 | 167 | 0 | 0 | 0.168052006 | 0.194548003 | 0.995492149 | 0.982312822 | 1.18856211 |
| 2 | Sheet15 | CC_entropy | 167 | 167 | 0 | 0 | 5.00079412 | 5.00104099 | 0.998052232 | 0.994657353 | 67.3369551 |
| 2 | Sheet15 | dV_energy | 167 | 167 | 0 | 0 | 0.0106146095 | 0.0281998106 | 0.961489856 | 0.989683151 | 0.800639462 |
| 2 | Sheet15 | dV_Q | 167 | 167 | 0 | 0 | 0.00268543577 | 0.00715254997 | 0.961546688 | 0.990912206 | 0.799304118 |
| 2 | Sheet15 | dV_t_mean | 167 | 167 | 0 | 0 | 0.0133369981 | 0.035572783 | 0.961692362 | 0.989849982 | 0.793908666 |
| 2 | Sheet15 | dV_V_mean | 167 | 167 | 0 | 0 | 0.000109579116 | 0.000158638224 | 0.991160348 | 0.963570472 | 0.00277689508 |
| 2 | Sheet15 | dV_T_mean | 167 | 167 | 0 | 0 | 0.00817065072 | 0.0130195868 | 0.999322015 | 0.998773534 | 0.0292325093 |
| 2 | Sheet15 | dV_V_std | 167 | 167 | 0 | 0 | 0.000145997224 | 0.000161956703 | 0.604470279 | 0.443692505 | 0.510899593 |
| 2 | Sheet15 | dV_T_std | 167 | 167 | 0 | 0 | 0.00673688581 | 0.00837457376 | 0.995950413 | 0.985189689 | 1.25273955 |
| 2 | Sheet15 | dV_V_skewness | 167 | 167 | 0 | 0 | 0.00224732716 | 0.00484658933 | 0.994915868 | 0.990639083 | 1.37234489 |
| 2 | Sheet15 | dV_T_skewness | 167 | 167 | 0 | 0 | 0.0301506024 | 0.0368150228 | 0.852571442 | 0.845030249 | 41.6744217 |
| 2 | Sheet15 | dV_V_kurtosis | 167 | 167 | 0 | 0 | 0.00156340225 | 0.00202157864 | 0.971789539 | 0.95017624 | 0.0846887205 |
| 2 | Sheet15 | dV_T_kurtosis | 167 | 167 | 0 | 0 | 0.0393244542 | 0.0485688327 | 0.712556956 | 0.722097973 | 2.20232852 |
| 2 | Sheet15 | dV_dV_devide_dt | 167 | 167 | 0 | 0 | 8.91508624e-05 | 0.000349511048 | 0.980839725 | 0.996792702 | 0.300813265 |
| 2 | Sheet15 | dV_entropy | 167 | 167 | 0 | 0 | 4.79647258 | 4.79675654 | -0.542674363 | -0.594054865 | 63.4524298 |
| 2 | Sheet15 | CV_energy | 167 | 167 | 0 | 0 | 0.0446228715 | 0.0525538382 | 0.976481564 | 0.974847207 | 2.59382653 |
| 2 | Sheet15 | CV_Q | 167 | 167 | 0 | 0 | 0.0106245647 | 0.0125128407 | 0.976482046 | 0.97486782 | 2.59373524 |
| 2 | Sheet15 | CV_t_mean | 167 | 167 | 0 | 0 | 0.0620692995 | 0.0779895887 | 0.998793026 | 0.997882676 | 0.418910617 |
| 2 | Sheet15 | CV_C_mean | 167 | 167 | 0 | 0 | 0.0145879426 | 0.0186369378 | 0.971179782 | 0.93206185 | 1.75024625 |
| 2 | Sheet15 | CV_T_mean | 167 | 167 | 0 | 0 | 0.0190165134 | 0.0228449707 | 0.999575533 | 0.998358704 | 0.0792336391 |
| 2 | Sheet15 | CV_C_std | 167 | 167 | 0 | 0 | 0.0288310177 | 0.0342497075 | 0.797174211 | 0.737567217 | 2.48644215 |
| 2 | Sheet15 | CV_T_std | 167 | 167 | 0 | 0 | 0.0136703439 | 0.0163860258 | 0.99271499 | 0.984957795 | 0.45921283 |
| 2 | Sheet15 | CV_C_skewness | 167 | 167 | 0 | 0 | 0.0116136821 | 0.0156068422 | 0.996465879 | 0.992632158 | 0.475163394 |
| 2 | Sheet15 | CV_T_skewness | 167 | 167 | 0 | 0 | 0.00755915362 | 0.0106936939 | 0.993085444 | 0.988583045 | 0.894755922 |
| 2 | Sheet15 | CV_C_kurtosis | 167 | 167 | 0 | 0 | 0.0697453048 | 0.10905993 | 0.993863552 | 0.992718428 | 0.808557095 |
| 2 | Sheet15 | CV_T_kurtosis | 167 | 167 | 0 | 0 | 0.0207579044 | 0.0331030164 | 0.983189813 | 0.972647901 | 0.883216188 |
| 2 | Sheet15 | CV_CVCT | 167 | 167 | 0 | 0 | 0.116408965 | 0.150278726 | 0.99883104 | 0.997983161 | 0.392911315 |
| 2 | Sheet15 | CV_entropy | 167 | 167 | 0 | 0 | 4.52734284 | 4.52794647 | 0.990560914 | 0.959170658 | 74.4369461 |
| 2 | Sheet15 | dI_energy | 167 | 167 | 0 | 0 | 0.000935492502 | 0.00107647687 | 0.995473186 | 0.99092263 | 2.86050529 |
| 2 | Sheet15 | dI_Q | 167 | 167 | 0 | 0 | 0.000222748258 | 0.000256313953 | 0.995473762 | 0.99092263 | 2.86053456 |
| 2 | Sheet15 | dI_t_mean | 167 | 167 | 0 | 0 | 0.00698537675 | 0.00805117916 | 0.995496895 | 0.990768672 | 2.83406991 |
| 2 | Sheet15 | dI_C_mean | 167 | 167 | 0 | 0 | 0.000652875399 | 0.000821311632 | 0.482425096 | 0.503629469 | 0.0688678201 |
| 2 | Sheet15 | dI_T_mean | 167 | 167 | 0 | 0 | 0.0160583092 | 0.0206259372 | 0.997484705 | 0.996743804 | 0.0601915175 |
| 2 | Sheet15 | dI_C_std | 167 | 167 | 0 | 0 | 0.000404046976 | 0.000550577858 | -0.173030698 | -0.127018768 | 1.39071766 |
| 2 | Sheet15 | dI_T_std | 167 | 167 | 0 | 0 | 0.015443256 | 0.0191135869 | 0.614851448 | 0.62001765 | 14.497086 |
| 2 | Sheet15 | dI_C_skewness | 167 | 167 | 0 | 0 | 0.0149026654 | 0.019221223 | 0.68517804 | 0.688310986 | 18.7022213 |
| 2 | Sheet15 | dI_T_skewness | 167 | 167 | 0 | 0 | 0.25623739 | 0.310114767 | 0.353932642 | 0.280927139 | 95.6969995 |
| 2 | Sheet15 | dI_C_kurtosis | 167 | 167 | 0 | 0 | 0.0217793597 | 0.025405145 | 0.174764347 | 0.177819061 | 1.20659798 |
| 2 | Sheet15 | dI_T_kurtosis | 167 | 167 | 0 | 0 | 0.284900993 | 0.380398128 | 0.29306958 | 0.405972068 | 14.1605317 |
| 2 | Sheet15 | dI_dI_devide_dt | 167 | 167 | 0 | 0 | 0.00141636793 | 0.00176001885 | 0.998994872 | 0.997015629 | 0.694384543 |
| 2 | Sheet15 | dI_entropy | 167 | 167 | 0 | 0 | 2.108391 | 2.12321489 | -0.477674123 | -0.438300855 | 43.2263205 |
| 2 | Sheet15 | Charge_energy | 167 | 167 | 0 | 0 | 0.00139967481 | 0.00156573395 | 0.999995076 | 0.999881476 | 0.0192240888 |
| 2 | Sheet15 | Charge_Q | 167 | 167 | 0 | 0 | 0.000157552759 | 0.000186453535 | 0.999996867 | 0.999948468 | 0.00863176542 |
| 2 | Sheet15 | Charge_t_mean | 167 | 167 | 0 | 0 | 0.0237187529 | 0.166574547 | 0.981134215 | 0.999618014 | 0.10840657 |
| 2 | Sheet15 | Charge_V_mean | 167 | 167 | 0 | 0 | 0.00130804616 | 0.00133448573 | 0.999756468 | 0.999515599 | 0.0318144315 |
| 2 | Sheet15 | Charge_C_mean | 167 | 167 | 0 | 0 | 0.00231727442 | 0.00261106298 | 0.999966029 | 0.999762953 | 0.0924711404 |
| 2 | Sheet15 | Charge_T_mean | 167 | 167 | 0 | 0 | 0.0102414594 | 0.0106788114 | 0.999975394 | 0.999889206 | 0.0410104166 |
| 2 | Sheet15 | Charge_C_std | 167 | 167 | 0 | 0 | 0.00116959887 | 0.00160921885 | 0.999660148 | 0.999580013 | 0.0450796791 |
| 2 | Sheet15 | Charge_V_std | 167 | 167 | 0 | 0 | 0.00346106596 | 0.00365048367 | 0.992795401 | 0.993282798 | 2.31606683 |
| 2 | Sheet15 | Charge_T_std | 167 | 167 | 0 | 0 | 0.00278907527 | 0.0131062525 | 0.988426654 | 0.998783199 | 0.0891452611 |
| 2 | Sheet15 | Charge_C_skewness | 167 | 167 | 0 | 0 | 0.00284885192 | 0.00384708652 | 0.999673864 | 0.999811908 | 0.575945448 |
| 2 | Sheet15 | Charge_V_skewness | 167 | 167 | 0 | 0 | 0.0985316773 | 0.113262965 | 0.998097313 | 0.991425045 | 6.45428826 |
| 2 | Sheet15 | Charge_T_skewness | 167 | 167 | 0 | 0 | 0.00489227043 | 0.00576255378 | 0.999465614 | 0.999214134 | 1.62597108 |
| 2 | Sheet15 | Charge_C_kurtosis | 167 | 167 | 0 | 0 | 0.00457202612 | 0.0118982307 | 0.997295542 | 0.99970111 | 0.331663361 |
| 2 | Sheet15 | Charge_V_kurtosis | 167 | 167 | 0 | 0 | 0.683878813 | 0.843771162 | 0.998159864 | 0.994420332 | 15.8208203 |
| 2 | Sheet15 | Charge_T_kurtosis | 167 | 167 | 0 | 0 | 0.00358639925 | 0.00690963739 | 0.997072716 | 0.996451973 | 0.21765394 |
| 3 | Sheet1 | CC_energy | 591 | 591 | 0 | 0 | 0.0535905185 | 0.0624606031 | 0.998123116 | 0.994495537 | 0.902708891 |
| 3 | Sheet1 | CC_Q | 591 | 591 | 0 | 0 | 0.0126014654 | 0.0147416772 | 0.99855024 | 0.995890255 | 0.820058402 |
| 3 | Sheet1 | CC_t_mean | 591 | 591 | 0 | 0 | 0.0944264275 | 0.110483236 | 0.998549593 | 0.995885502 | 0.81931712 |
| 3 | Sheet1 | CC_V_mean | 591 | 591 | 0 | 0 | 0.00344612637 | 0.00384021269 | 0.996707061 | 0.993665402 | 0.0891627135 |
| 3 | Sheet1 | CC_T_mean | 591 | 591 | 0 | 0 | 0.0139146154 | 0.0178927953 | 0.999978498 | 0.999959016 | 0.0476842411 |
| 3 | Sheet1 | CC_V_std | 591 | 591 | 0 | 0 | 0.0013252702 | 0.00157570171 | 0.988742107 | 0.985426031 | 0.840173269 |
| 3 | Sheet1 | CC_T_std | 591 | 591 | 0 | 0 | 0.00988335228 | 0.0130154295 | 0.999824665 | 0.999198874 | 0.766051683 |
| 3 | Sheet1 | CC_V_skewness | 591 | 591 | 0 | 0 | 0.0896467946 | 0.0984748521 | 0.943827128 | 0.929852331 | 37.1180421 |
| 3 | Sheet1 | CC_T_skewness | 591 | 591 | 0 | 0 | 0.0166288399 | 0.0262870951 | 0.999709006 | 0.998653067 | 1.83902403 |
| 3 | Sheet1 | CC_V_kurtosis | 591 | 591 | 0 | 0 | 0.164444616 | 0.19338618 | 0.909360185 | 0.935895278 | 6.55571952 |
| 3 | Sheet1 | CC_T_kurtosis | 591 | 591 | 0 | 0 | 0.0547273161 | 0.282907329 | 0.989862313 | 0.996817936 | 1.63288313 |
| 3 | Sheet1 | CC_CCCT | 591 | 591 | 0 | 0 | 0.188975778 | 0.221085134 | 0.998550298 | 0.99589361 | 0.819844853 |
| 3 | Sheet1 | CC_entropy | 591 | 591 | 0 | 0 | 5.07050785 | 5.07061402 | 0.997891527 | 0.996613741 | 66.8975591 |
| 3 | Sheet1 | dV_energy | 591 | 591 | 0 | 0 | 0.0056473567 | 0.00600663559 | 0.999093938 | 0.99818818 | 0.63250505 |
| 3 | Sheet1 | dV_Q | 591 | 591 | 0 | 0 | 0.00142806752 | 0.00151913905 | 0.999098556 | 0.998228408 | 0.631214479 |
| 3 | Sheet1 | dV_t_mean | 591 | 591 | 0 | 0 | 0.0107798491 | 0.011476874 | 0.99907066 | 0.998217944 | 0.635316464 |
| 3 | Sheet1 | dV_V_mean | 591 | 591 | 0 | 0 | 0.000100993523 | 0.00012557536 | 0.965578505 | 0.96270871 | 0.00255905694 |
| 3 | Sheet1 | dV_T_mean | 591 | 591 | 0 | 0 | 0.00589594982 | 0.00763787359 | 0.999991444 | 0.999973346 | 0.0200299334 |
| 3 | Sheet1 | dV_V_std | 591 | 591 | 0 | 0 | 0.000149086548 | 0.000163533101 | 0.602040472 | 0.596080988 | 0.516510188 |
| 3 | Sheet1 | dV_T_std | 591 | 591 | 0 | 0 | 0.00786318167 | 0.017215565 | 0.974284204 | 0.991389945 | 6.06318121 |
| 3 | Sheet1 | dV_V_skewness | 591 | 591 | 0 | 0 | 0.00168735284 | 0.0021323883 | 0.993375269 | 0.992125876 | 1.16764586 |
| 3 | Sheet1 | dV_T_skewness | 591 | 591 | 0 | 0 | 0.22678066 | 0.551360706 | 0.691538691 | 0.818223616 | 66.0185241 |
| 3 | Sheet1 | dV_V_kurtosis | 591 | 591 | 0 | 0 | 0.00173959213 | 0.00222428597 | 0.966173591 | 0.95623554 | 0.0957065898 |
| 3 | Sheet1 | dV_T_kurtosis | 591 | 591 | 0 | 0 | 0.679827318 | 3.67550324 | 0.272332136 | 0.772714745 | 27.2949163 |
| 3 | Sheet1 | dV_dV_devide_dt | 591 | 591 | 0 | 0 | 3.36972079e-05 | 4.14931179e-05 | 0.999707695 | 0.999531233 | 0.11481939 |
| 3 | Sheet1 | dV_entropy | 591 | 591 | 0 | 0 | 4.80166438 | 4.80197986 | -0.848702709 | -0.865653025 | 63.4594322 |
| 3 | Sheet1 | CV_energy | 591 | 591 | 0 | 0 | 0.0332443249 | 0.0386993165 | 0.988704512 | 0.981304775 | 2.34691617 |
| 3 | Sheet1 | CV_Q | 591 | 591 | 0 | 0 | 0.00791502058 | 0.00921370936 | 0.98870338 | 0.981315181 | 2.34682015 |
| 3 | Sheet1 | CV_t_mean | 591 | 591 | 0 | 0 | 0.0663223428 | 0.0762958328 | 0.99979407 | 0.998355718 | 0.480313451 |
| 3 | Sheet1 | CV_C_mean | 591 | 591 | 0 | 0 | 0.011205156 | 0.0132112585 | 0.960358926 | 0.948822465 | 1.51940597 |
| 3 | Sheet1 | CV_T_mean | 591 | 591 | 0 | 0 | 0.0179563016 | 0.0211889305 | 0.999982116 | 0.999926985 | 0.0703166694 |
| 3 | Sheet1 | CV_C_std | 591 | 591 | 0 | 0 | 0.0195114596 | 0.0228386521 | 0.734476812 | 0.714145648 | 2.31296735 |
| 3 | Sheet1 | CV_T_std | 591 | 591 | 0 | 0 | 0.0111198689 | 0.0132611341 | 0.999494735 | 0.999231196 | 0.465000561 |
| 3 | Sheet1 | CV_C_skewness | 591 | 591 | 0 | 0 | 0.0188656822 | 0.021901224 | 0.989762053 | 0.979784084 | 1.0116436 |
| 3 | Sheet1 | CV_T_skewness | 591 | 591 | 0 | 0 | 0.0118635797 | 0.0492264763 | 0.893717699 | 0.957219144 | 1.88019083 |
| 3 | Sheet1 | CV_C_kurtosis | 591 | 591 | 0 | 0 | 0.0897895732 | 0.103771427 | 0.989058659 | 0.979636601 | 1.51755392 |
| 3 | Sheet1 | CV_T_kurtosis | 591 | 591 | 0 | 0 | 0.0150920386 | 0.0190375758 | 0.994009837 | 0.990879686 | 0.747424339 |
| 3 | Sheet1 | CV_CVCT | 591 | 591 | 0 | 0 | 0.125022543 | 0.14522754 | 0.99979548 | 0.998351401 | 0.452851411 |
| 3 | Sheet1 | CV_entropy | 591 | 591 | 0 | 0 | 4.72360774 | 4.72370798 | 0.978382989 | 0.963686193 | 71.4120382 |
| 3 | Sheet1 | dI_energy | 591 | 591 | 0 | 0 | 0.00116424189 | 0.00245378647 | 0.941900538 | 0.981742049 | 2.5723004 |
| 3 | Sheet1 | dI_Q | 591 | 591 | 0 | 0 | 0.000277200778 | 0.000584234981 | 0.941897367 | 0.981737093 | 2.57229446 |
| 3 | Sheet1 | dI_t_mean | 591 | 591 | 0 | 0 | 0.00852761724 | 0.017699462 | 0.947124261 | 0.981717094 | 2.50067 |
| 3 | Sheet1 | dI_C_mean | 591 | 591 | 0 | 0 | 0.000526124917 | 0.00065318406 | 0.514506026 | 0.417345328 | 0.0554593726 |
| 3 | Sheet1 | dI_T_mean | 591 | 591 | 0 | 0 | 0.0146439124 | 0.0181680633 | 0.999955412 | 0.999892745 | 0.053216313 |
| 3 | Sheet1 | dI_C_std | 591 | 591 | 0 | 0 | 0.000314033493 | 0.000392778622 | 0.0674527891 | 0.0680439946 | 1.08312332 |
| 3 | Sheet1 | dI_T_std | 591 | 591 | 0 | 0 | 0.0121119223 | 0.0148542286 | 0.819848343 | 0.824588801 | 11.2333863 |
| 3 | Sheet1 | dI_C_skewness | 591 | 591 | 0 | 0 | 0.0104409869 | 0.0136941205 | 0.758236807 | 0.689880154 | 20.3258405 |
| 3 | Sheet1 | dI_T_skewness | 591 | 591 | 0 | 0 | 0.243230135 | 0.303144544 | 0.353582827 | 0.313569902 | 102.17721 |
| 3 | Sheet1 | dI_C_kurtosis | 591 | 591 | 0 | 0 | 0.0122103054 | 0.0152397351 | 0.177138579 | 0.139674539 | 0.677532694 |
| 3 | Sheet1 | dI_T_kurtosis | 591 | 591 | 0 | 0 | 0.270062282 | 0.349169966 | 0.386192211 | 0.395521372 | 13.1586203 |
| 3 | Sheet1 | dI_dI_devide_dt | 591 | 591 | 0 | 0 | 0.00125210388 | 0.00197525673 | 0.994834984 | 0.991525713 | 0.862581885 |
| 3 | Sheet1 | dI_entropy | 591 | 591 | 0 | 0 | 2.56951368 | 2.57586663 | -0.155399617 | 0.00539834725 | 48.114481 |
| 3 | Sheet1 | Charge_energy | 591 | 591 | 0 | 0 | 0.000971439926 | 0.00112079954 | 0.999998336 | 0.999984362 | 0.0132026503 |
| 3 | Sheet1 | Charge_Q | 591 | 591 | 0 | 0 | 0.000133359963 | 0.000154417476 | 0.999999067 | 0.999990583 | 0.00711231615 |
| 3 | Sheet1 | Charge_t_mean | 591 | 591 | 0 | 0 | 0.00522398183 | 0.00697551405 | 0.999978713 | 0.99987548 | 0.0206143137 |
| 3 | Sheet1 | Charge_V_mean | 591 | 591 | 0 | 0 | 0.0011178709 | 0.00113004804 | 0.999983792 | 0.999936287 | 0.0276294413 |
| 3 | Sheet1 | Charge_C_mean | 591 | 591 | 0 | 0 | 0.000736072713 | 0.000953865833 | 0.999994106 | 0.999968318 | 0.0330673289 |
| 3 | Sheet1 | Charge_T_mean | 591 | 591 | 0 | 0 | 0.00669194424 | 0.00786913616 | 0.999994071 | 0.99998349 | 0.0246281261 |
| 3 | Sheet1 | Charge_C_std | 591 | 591 | 0 | 0 | 0.000759357126 | 0.00260499623 | 0.97234486 | 0.992370033 | 0.0438937308 |
| 3 | Sheet1 | Charge_V_std | 591 | 591 | 0 | 0 | 0.00224550677 | 0.0023050052 | 0.999598729 | 0.999148299 | 1.13823923 |
| 3 | Sheet1 | Charge_T_std | 591 | 591 | 0 | 0 | 0.0103914084 | 0.0468523142 | 0.997821614 | 0.999842359 | 0.379276656 |
| 3 | Sheet1 | Charge_C_skewness | 591 | 591 | 0 | 0 | 0.000822063512 | 0.0011299864 | 0.999994765 | 0.99997291 | 0.429477672 |
| 3 | Sheet1 | Charge_V_skewness | 591 | 591 | 0 | 0 | 0.038643574 | 0.0423474352 | 0.997370912 | 0.996071745 | 4.49604392 |
| 3 | Sheet1 | Charge_T_skewness | 591 | 591 | 0 | 0 | 0.00769517285 | 0.011114759 | 0.99972998 | 0.999816533 | 2.68069893 |
| 3 | Sheet1 | Charge_C_kurtosis | 591 | 591 | 0 | 0 | 0.000625308376 | 0.00108116688 | 0.999769004 | 0.999883386 | 0.0531881591 |
| 3 | Sheet1 | Charge_V_kurtosis | 591 | 591 | 0 | 0 | 0.178012669 | 0.205547963 | 0.984063544 | 0.987647671 | 7.67405442 |
| 3 | Sheet1 | Charge_T_kurtosis | 591 | 591 | 0 | 0 | 0.0207921374 | 0.121024758 | 0.949960945 | 0.99302449 | 1.14755111 |
| 3 | Sheet2 | CC_energy | 551 | 551 | 0 | 0 | 0.0541874645 | 0.0634944089 | 0.998139648 | 0.993846115 | 0.915072039 |
| 3 | Sheet2 | CC_Q | 551 | 551 | 0 | 0 | 0.0127380992 | 0.0149793674 | 0.998561164 | 0.995087122 | 0.830994098 |
| 3 | Sheet2 | CC_t_mean | 551 | 551 | 0 | 0 | 0.0954878413 | 0.112437359 | 0.998548291 | 0.995040062 | 0.830611509 |
| 3 | Sheet2 | CC_V_mean | 551 | 551 | 0 | 0 | 0.0035508647 | 0.00398450931 | 0.996315123 | 0.993322884 | 0.0918771763 |
| 3 | Sheet2 | CC_T_mean | 551 | 551 | 0 | 0 | 0.014455339 | 0.019006019 | 0.999974946 | 0.999949355 | 0.0496574932 |
| 3 | Sheet2 | CC_V_std | 551 | 551 | 0 | 0 | 0.00130668081 | 0.00155564916 | 0.988624471 | 0.978719898 | 0.813895388 |
| 3 | Sheet2 | CC_T_std | 551 | 551 | 0 | 0 | 0.0102381146 | 0.0138207596 | 0.999767944 | 0.999516868 | 0.800857636 |
| 3 | Sheet2 | CC_V_skewness | 551 | 551 | 0 | 0 | 0.094109187 | 0.102251761 | 0.963545851 | 0.959085242 | 47.099834 |
| 3 | Sheet2 | CC_T_skewness | 551 | 551 | 0 | 0 | 0.0222725422 | 0.0374444466 | 0.999392049 | 0.99900411 | 2.56024607 |
| 3 | Sheet2 | CC_V_kurtosis | 551 | 551 | 0 | 0 | 0.186930838 | 0.215674053 | 0.91637447 | 0.945448735 | 7.31966671 |
| 3 | Sheet2 | CC_T_kurtosis | 551 | 551 | 0 | 0 | 0.0789375866 | 0.330953704 | 0.984550028 | 0.994982031 | 2.40028446 |
| 3 | Sheet2 | CC_CCCT | 551 | 551 | 0 | 0 | 0.191040713 | 0.224661345 | 0.998561257 | 0.995090613 | 0.830891755 |
| 3 | Sheet2 | CC_entropy | 551 | 551 | 0 | 0 | 5.06496855 | 5.06506039 | 0.9974458 | 0.992218612 | 66.9896218 |
| 3 | Sheet2 | dV_energy | 551 | 551 | 0 | 0 | 0.00494472312 | 0.00533503223 | 0.999030386 | 0.998091074 | 0.555719431 |
| 3 | Sheet2 | dV_Q | 551 | 551 | 0 | 0 | 0.00125213634 | 0.0013510777 | 0.999033847 | 0.998149753 | 0.555375054 |
| 3 | Sheet2 | dV_t_mean | 551 | 551 | 0 | 0 | 0.00939991681 | 0.0101861569 | 0.998959729 | 0.998064209 | 0.555921734 |
| 3 | Sheet2 | dV_V_mean | 551 | 551 | 0 | 0 | 8.91049335e-05 | 0.000111139137 | 0.958736464 | 0.953449243 | 0.00225775454 |
| 3 | Sheet2 | dV_T_mean | 551 | 551 | 0 | 0 | 0.00634335134 | 0.00804050313 | 0.999991266 | 0.999972382 | 0.0215624724 |
| 3 | Sheet2 | dV_V_std | 551 | 551 | 0 | 0 | 0.000123488941 | 0.000139164201 | 0.61924219 | 0.61508375 | 0.427439988 |
| 3 | Sheet2 | dV_T_std | 551 | 551 | 0 | 0 | 0.00893105245 | 0.0236602305 | 0.946827679 | 0.985355337 | 6.53595583 |
| 3 | Sheet2 | dV_V_skewness | 551 | 551 | 0 | 0 | 0.001653232 | 0.00210066081 | 0.992131171 | 0.990954571 | 1.16556911 |
| 3 | Sheet2 | dV_T_skewness | 551 | 551 | 0 | 0 | 0.226323693 | 0.680156276 | 0.510237669 | 0.833039942 | 81.7360009 |
| 3 | Sheet2 | dV_V_kurtosis | 551 | 551 | 0 | 0 | 0.0016930006 | 0.00216281881 | 0.961772396 | 0.946682998 | 0.0931809293 |
| 3 | Sheet2 | dV_T_kurtosis | 551 | 551 | 0 | 0 | 0.72822766 | 5.77878663 | 0.103484622 | 0.770940582 | 33.2162327 |
| 3 | Sheet2 | dV_dV_devide_dt | 551 | 551 | 0 | 0 | 3.08534128e-05 | 3.93018907e-05 | 0.999674261 | 0.999386024 | 0.104612791 |
| 3 | Sheet2 | dV_entropy | 551 | 551 | 0 | 0 | 4.80254799 | 4.80287733 | -0.858337786 | -0.857578898 | 63.461255 |
| 3 | Sheet2 | CV_energy | 551 | 551 | 0 | 0 | 0.0326213993 | 0.0384028496 | 0.988253621 | 0.983071383 | 2.28052225 |
| 3 | Sheet2 | CV_Q | 551 | 551 | 0 | 0 | 0.00776649136 | 0.00914284387 | 0.988252597 | 0.983072244 | 2.28042561 |
| 3 | Sheet2 | CV_t_mean | 551 | 551 | 0 | 0 | 0.0647234891 | 0.0740932119 | 0.999824122 | 0.998240497 | 0.456140788 |
| 3 | Sheet2 | CV_C_mean | 551 | 551 | 0 | 0 | 0.0106954105 | 0.0125043866 | 0.970310107 | 0.957845384 | 1.47442982 |
| 3 | Sheet2 | CV_T_mean | 551 | 551 | 0 | 0 | 0.0169104127 | 0.0199853518 | 0.999984466 | 0.999926903 | 0.0662776088 |
| 3 | Sheet2 | CV_C_std | 551 | 551 | 0 | 0 | 0.0191447167 | 0.0221833123 | 0.771422508 | 0.741661083 | 2.30276043 |
| 3 | Sheet2 | CV_T_std | 551 | 551 | 0 | 0 | 0.0111988548 | 0.0132568505 | 0.999329668 | 0.998956981 | 0.474278512 |
| 3 | Sheet2 | CV_C_skewness | 551 | 551 | 0 | 0 | 0.0196840358 | 0.0227346256 | 0.993002257 | 0.987373227 | 1.01744217 |
| 3 | Sheet2 | CV_T_skewness | 551 | 551 | 0 | 0 | 0.0181358764 | 0.0998267544 | 0.7447637 | 0.947006305 | 2.61238493 |
| 3 | Sheet2 | CV_C_kurtosis | 551 | 551 | 0 | 0 | 0.0937748294 | 0.107903531 | 0.992969944 | 0.987368062 | 1.49463825 |
| 3 | Sheet2 | CV_T_kurtosis | 551 | 551 | 0 | 0 | 0.0157377422 | 0.0208049791 | 0.995363935 | 0.994798265 | 0.746016983 |
| 3 | Sheet2 | CV_CVCT | 551 | 551 | 0 | 0 | 0.121091502 | 0.140436467 | 0.999830222 | 0.998326775 | 0.426822003 |
| 3 | Sheet2 | CV_entropy | 551 | 551 | 0 | 0 | 4.7192711 | 4.71939314 | 0.9814079 | 0.972004104 | 71.577359 |
| 3 | Sheet2 | dI_energy | 551 | 551 | 0 | 0 | 0.00122784842 | 0.00460180564 | 0.88770571 | 0.990305015 | 2.50911749 |
| 3 | Sheet2 | dI_Q | 551 | 551 | 0 | 0 | 0.000292336608 | 0.00109564181 | 0.887701631 | 0.99030731 | 2.50910542 |
| 3 | Sheet2 | dI_t_mean | 551 | 551 | 0 | 0 | 0.00919051038 | 0.034543932 | 0.888542807 | 0.99019067 | 2.49309271 |
| 3 | Sheet2 | dI_C_mean | 551 | 551 | 0 | 0 | 0.000497385278 | 0.000725731028 | 0.761700465 | 0.792587864 | 0.052450769 |
| 3 | Sheet2 | dI_T_mean | 551 | 551 | 0 | 0 | 0.0148344169 | 0.0182898102 | 0.999957433 | 0.999898065 | 0.053853837 |
| 3 | Sheet2 | dI_C_std | 551 | 551 | 0 | 0 | 0.000261675173 | 0.000330319197 | 0.123272522 | 0.0771671341 | 0.904864555 |
| 3 | Sheet2 | dI_T_std | 551 | 551 | 0 | 0 | 0.0124912107 | 0.0166001192 | 0.839366361 | 0.835867249 | 10.8738971 |
| 3 | Sheet2 | dI_C_skewness | 551 | 551 | 0 | 0 | 0.00959711955 | 0.021616248 | 0.870036339 | 0.939508762 | 13.6871633 |
| 3 | Sheet2 | dI_T_skewness | 551 | 551 | 0 | 0 | 0.268113806 | 0.734274967 | 0.181853923 | 0.404015767 | 108.533011 |
| 3 | Sheet2 | dI_C_kurtosis | 551 | 551 | 0 | 0 | 0.0128492308 | 0.0187132721 | 0.391610814 | 0.367390659 | 0.710540354 |
| 3 | Sheet2 | dI_T_kurtosis | 551 | 551 | 0 | 0 | 0.750973722 | 10.7511385 | -0.0435773778 | 0.280704812 | 36.9005609 |
| 3 | Sheet2 | dI_dI_devide_dt | 551 | 551 | 0 | 0 | 0.00116121694 | 0.00484908931 | 0.97840424 | 0.99418518 | 0.849747103 |
| 3 | Sheet2 | dI_entropy | 551 | 551 | 0 | 0 | 2.67642224 | 2.68827459 | -0.252608266 | -0.170840572 | 49.1453299 |
| 3 | Sheet2 | Charge_energy | 551 | 551 | 0 | 0 | 0.000974759544 | 0.00111630937 | 0.999998397 | 0.999983286 | 0.0132488145 |
| 3 | Sheet2 | Charge_Q | 551 | 551 | 0 | 0 | 0.000133975512 | 0.000158579088 | 0.99999904 | 0.999989742 | 0.00714652637 |
| 3 | Sheet2 | Charge_t_mean | 551 | 551 | 0 | 0 | 0.00568273673 | 0.0106805085 | 0.99994729 | 0.99953473 | 0.0221171086 |
| 3 | Sheet2 | Charge_V_mean | 551 | 551 | 0 | 0 | 0.00117472802 | 0.0011891447 | 0.999980337 | 0.999925037 | 0.0290179925 |
| 3 | Sheet2 | Charge_C_mean | 551 | 551 | 0 | 0 | 0.000803125371 | 0.00132245602 | 0.999984087 | 0.999944908 | 0.0365716814 |
| 3 | Sheet2 | Charge_T_mean | 551 | 551 | 0 | 0 | 0.00685192621 | 0.00816994249 | 0.999993744 | 0.999978121 | 0.0252798122 |
| 3 | Sheet2 | Charge_C_std | 551 | 551 | 0 | 0 | 0.00114806943 | 0.00460053316 | 0.927295024 | 0.991799082 | 0.0663008654 |
| 3 | Sheet2 | Charge_V_std | 551 | 551 | 0 | 0 | 0.00243341099 | 0.00249791053 | 0.999536536 | 0.99913646 | 1.23078992 |
| 3 | Sheet2 | Charge_T_std | 551 | 551 | 0 | 0 | 0.00820549318 | 0.0124060624 | 0.999940079 | 0.999937663 | 0.303161903 |
| 3 | Sheet2 | Charge_C_skewness | 551 | 551 | 0 | 0 | 0.000960201428 | 0.00155875285 | 0.999984793 | 0.999963989 | 0.487330629 |
| 3 | Sheet2 | Charge_V_skewness | 551 | 551 | 0 | 0 | 0.0433481416 | 0.0471512237 | 0.997814269 | 0.9963617 | 4.76339204 |
| 3 | Sheet2 | Charge_T_skewness | 551 | 551 | 0 | 0 | 0.00799827012 | 0.0117839974 | 0.999638553 | 0.999750579 | 3.20113865 |
| 3 | Sheet2 | Charge_C_kurtosis | 551 | 551 | 0 | 0 | 0.00129735358 | 0.00574029618 | 0.992913548 | 0.999855024 | 0.110688261 |
| 3 | Sheet2 | Charge_V_kurtosis | 551 | 551 | 0 | 0 | 0.209440409 | 0.241919828 | 0.988641249 | 0.991591375 | 8.51283049 |
| 3 | Sheet2 | Charge_T_kurtosis | 551 | 551 | 0 | 0 | 0.0113542198 | 0.0209708014 | 0.999482001 | 0.999785514 | 0.638284369 |
| 3 | Sheet3 | CC_energy | 666 | 666 | 0 | 0 | 0.0544454865 | 0.0642581209 | 0.997843943 | 0.995072358 | 0.922961821 |
| 3 | Sheet3 | CC_Q | 666 | 666 | 0 | 0 | 0.0127707878 | 0.0151332719 | 0.998337766 | 0.995963043 | 0.835901166 |
| 3 | Sheet3 | CC_t_mean | 666 | 666 | 0 | 0 | 0.0958840615 | 0.113505958 | 0.998328114 | 0.995950886 | 0.836837561 |
| 3 | Sheet3 | CC_V_mean | 666 | 666 | 0 | 0 | 0.00370740057 | 0.00416230173 | 0.995891374 | 0.993115818 | 0.0959795083 |
| 3 | Sheet3 | CC_T_mean | 666 | 666 | 0 | 0 | 0.0138603776 | 0.0179543355 | 0.999977431 | 0.999946704 | 0.0491420458 |
| 3 | Sheet3 | CC_V_std | 666 | 666 | 0 | 0 | 0.00148712995 | 0.00180529015 | 0.983148255 | 0.976996302 | 0.898145947 |
| 3 | Sheet3 | CC_T_std | 666 | 666 | 0 | 0 | 0.0101882733 | 0.0136254736 | 0.999731969 | 0.999216324 | 0.827394965 |
| 3 | Sheet3 | CC_V_skewness | 666 | 666 | 0 | 0 | 0.107284293 | 0.116711535 | 0.965393482 | 0.964343778 | 83.5125056 |
| 3 | Sheet3 | CC_T_skewness | 666 | 666 | 0 | 0 | 0.0204775519 | 0.0335597121 | 0.999471471 | 0.999121065 | 2.3939156 |
| 3 | Sheet3 | CC_V_kurtosis | 666 | 666 | 0 | 0 | 0.243324447 | 0.281854358 | 0.934455809 | 0.946232208 | 9.06087358 |
| 3 | Sheet3 | CC_T_kurtosis | 666 | 666 | 0 | 0 | 0.0693646995 | 0.252646838 | 0.990457942 | 0.996312553 | 2.13829835 |
| 3 | Sheet3 | CC_CCCT | 666 | 666 | 0 | 0 | 0.191530065 | 0.226968798 | 0.998337851 | 0.995959567 | 0.835792803 |
| 3 | Sheet3 | CC_entropy | 666 | 666 | 0 | 0 | 5.05200697 | 5.05210805 | 0.997414392 | 0.994050287 | 67.1747944 |
| 3 | Sheet3 | dV_energy | 666 | 666 | 0 | 0 | 0.00565907244 | 0.00598720367 | 0.998984506 | 0.998384226 | 0.642574696 |
| 3 | Sheet3 | dV_Q | 666 | 666 | 0 | 0 | 0.00143310893 | 0.00151621814 | 0.998988276 | 0.998458808 | 0.642245344 |
| 3 | Sheet3 | dV_t_mean | 666 | 666 | 0 | 0 | 0.0107632254 | 0.0114149413 | 0.998923636 | 0.998420755 | 0.643161551 |
| 3 | Sheet3 | dV_V_mean | 666 | 666 | 0 | 0 | 9.44013524e-05 | 0.000120039978 | 0.930969782 | 0.933975624 | 0.00239183841 |
| 3 | Sheet3 | dV_T_mean | 666 | 666 | 0 | 0 | 0.00690562105 | 0.00856883596 | 0.999990513 | 0.999958271 | 0.0242622983 |
| 3 | Sheet3 | dV_V_std | 666 | 666 | 0 | 0 | 0.000145081238 | 0.00015940485 | 0.525840637 | 0.516738968 | 0.502487959 |
| 3 | Sheet3 | dV_T_std | 666 | 666 | 0 | 0 | 0.00735988682 | 0.0133583337 | 0.980269437 | 0.990407601 | 5.09782729 |
| 3 | Sheet3 | dV_V_skewness | 666 | 666 | 0 | 0 | 0.00178623797 | 0.00239595105 | 0.985060472 | 0.984438841 | 1.33663003 |
| 3 | Sheet3 | dV_T_skewness | 666 | 666 | 0 | 0 | 0.164004084 | 0.327478499 | 0.793124026 | 0.871697202 | 49.5263205 |
| 3 | Sheet3 | dV_V_kurtosis | 666 | 666 | 0 | 0 | 0.00179035449 | 0.00227026095 | 0.925357883 | 0.914845138 | 0.0986807642 |
| 3 | Sheet3 | dV_T_kurtosis | 666 | 666 | 0 | 0 | 0.294014029 | 0.807737412 | 0.585855873 | 0.828826777 | 13.3174005 |
| 3 | Sheet3 | dV_dV_devide_dt | 666 | 666 | 0 | 0 | 4.38727708e-05 | 0.000109916065 | 0.99721098 | 0.999376302 | 0.147330282 |
| 3 | Sheet3 | dV_entropy | 666 | 666 | 0 | 0 | 4.79767278 | 4.79799845 | -0.743811116 | -0.763177942 | 63.4308723 |
| 3 | Sheet3 | CV_energy | 666 | 666 | 0 | 0 | 0.03673666 | 0.0423296191 | 0.991080355 | 0.987359785 | 2.50135703 |
| 3 | Sheet3 | CV_Q | 666 | 666 | 0 | 0 | 0.00874697605 | 0.0100786157 | 0.991079479 | 0.98735292 | 2.50128163 |
| 3 | Sheet3 | CV_t_mean | 666 | 666 | 0 | 0 | 0.0729418196 | 0.0834461545 | 0.99984529 | 0.998787763 | 0.495861029 |
| 3 | Sheet3 | CV_C_mean | 666 | 666 | 0 | 0 | 0.011906925 | 0.0138672051 | 0.964784328 | 0.951068603 | 1.65541991 |
| 3 | Sheet3 | CV_T_mean | 666 | 666 | 0 | 0 | 0.018183766 | 0.0212441803 | 0.999982713 | 0.99990198 | 0.0732681446 |
| 3 | Sheet3 | CV_C_std | 666 | 666 | 0 | 0 | 0.0214602385 | 0.0248067676 | 0.698631419 | 0.670045083 | 2.61207857 |
| 3 | Sheet3 | CV_T_std | 666 | 666 | 0 | 0 | 0.0123745892 | 0.0145566757 | 0.999132649 | 0.998746979 | 0.546619611 |
| 3 | Sheet3 | CV_C_skewness | 666 | 666 | 0 | 0 | 0.0227476364 | 0.026296046 | 0.991614085 | 0.989235539 | 1.16877033 |
| 3 | Sheet3 | CV_T_skewness | 666 | 666 | 0 | 0 | 0.0084844382 | 0.0133455997 | 0.995425324 | 0.997451549 | 1.17478499 |
| 3 | Sheet3 | CV_C_kurtosis | 666 | 666 | 0 | 0 | 0.106393972 | 0.122265411 | 0.991387069 | 0.989266086 | 1.67500795 |
| 3 | Sheet3 | CV_T_kurtosis | 666 | 666 | 0 | 0 | 0.019112009 | 0.0258973587 | 0.992648452 | 0.994380822 | 0.892542579 |
| 3 | Sheet3 | CV_CVCT | 666 | 666 | 0 | 0 | 0.138131904 | 0.159175335 | 0.999849206 | 0.998827308 | 0.469645629 |
| 3 | Sheet3 | CV_entropy | 666 | 666 | 0 | 0 | 4.71482744 | 4.71492411 | 0.981528185 | 0.958946774 | 71.5692618 |
| 3 | Sheet3 | dI_energy | 666 | 666 | 0 | 0 | 0.0009863552 | 0.00116917336 | 0.99620094 | 0.995924858 | 1.91336477 |
| 3 | Sheet3 | dI_Q | 666 | 666 | 0 | 0 | 0.000234856854 | 0.00027838837 | 0.996200704 | 0.995924939 | 1.91335815 |
| 3 | Sheet3 | dI_t_mean | 666 | 666 | 0 | 0 | 0.00742496556 | 0.0087833481 | 0.996255375 | 0.995992108 | 1.91190316 |
| 3 | Sheet3 | dI_C_mean | 666 | 666 | 0 | 0 | 0.000458461667 | 0.000577234231 | 0.90628212 | 0.834831677 | 0.0483445297 |
| 3 | Sheet3 | dI_T_mean | 666 | 666 | 0 | 0 | 0.0143707413 | 0.0179393519 | 0.99995664 | 0.999825458 | 0.0536785741 |
| 3 | Sheet3 | dI_C_std | 666 | 666 | 0 | 0 | 0.000255394466 | 0.000319778761 | 0.193492262 | 0.165986322 | 0.884738734 |
| 3 | Sheet3 | dI_T_std | 666 | 666 | 0 | 0 | 0.0126916557 | 0.0157223643 | 0.849775268 | 0.834208659 | 10.7461706 |
| 3 | Sheet3 | dI_C_skewness | 666 | 666 | 0 | 0 | 0.00849341382 | 0.0109942649 | 0.978872916 | 0.941493549 | 12.2376183 |
| 3 | Sheet3 | dI_T_skewness | 666 | 666 | 0 | 0 | 0.232024154 | 0.288975041 | 0.493994529 | 0.479310482 | 92.7664273 |
| 3 | Sheet3 | dI_C_kurtosis | 666 | 666 | 0 | 0 | 0.0109687488 | 0.0141640304 | 0.646901375 | 0.573726772 | 0.606371963 |
| 3 | Sheet3 | dI_T_kurtosis | 666 | 666 | 0 | 0 | 0.263198022 | 0.346380546 | 0.395942379 | 0.404418315 | 12.9441009 |
| 3 | Sheet3 | dI_dI_devide_dt | 666 | 666 | 0 | 0 | 0.000968884954 | 0.00188854534 | 0.995598666 | 0.998511604 | 0.753356633 |
| 3 | Sheet3 | dI_entropy | 666 | 666 | 0 | 0 | 2.75816176 | 2.7669492 | -0.424256887 | -0.377177294 | 49.9005878 |
| 3 | Sheet3 | Charge_energy | 666 | 666 | 0 | 0 | 0.00240575097 | 0.0141730977 | 0.999276798 | 0.999983426 | 0.0326259091 |
| 3 | Sheet3 | Charge_Q | 666 | 666 | 0 | 0 | 0.000342891808 | 0.002436454 | 0.99972659 | 0.999988585 | 0.0182503742 |
| 3 | Sheet3 | Charge_t_mean | 666 | 666 | 0 | 0 | 0.00654706516 | 0.012280641 | 0.999963045 | 0.999809128 | 0.0250111062 |
| 3 | Sheet3 | Charge_V_mean | 666 | 666 | 0 | 0 | 0.00128983342 | 0.00130901018 | 0.999973683 | 0.999878094 | 0.0318474681 |
| 3 | Sheet3 | Charge_C_mean | 666 | 666 | 0 | 0 | 0.000882424797 | 0.00149719771 | 0.999981958 | 0.999856686 | 0.04077795 |
| 3 | Sheet3 | Charge_T_mean | 666 | 666 | 0 | 0 | 0.00651362018 | 0.00765384366 | 0.999994409 | 0.999980623 | 0.0247838327 |
| 3 | Sheet3 | Charge_C_std | 666 | 666 | 0 | 0 | 0.000896909092 | 0.00234812297 | 0.989800887 | 0.999591484 | 0.0518722845 |
| 3 | Sheet3 | Charge_V_std | 666 | 666 | 0 | 0 | 0.00282579188 | 0.0029143847 | 0.999412125 | 0.999099536 | 1.41784937 |
| 3 | Sheet3 | Charge_T_std | 666 | 666 | 0 | 0 | 0.0163755186 | 0.101725576 | 0.98347278 | 0.998498586 | 0.639316404 |
| 3 | Sheet3 | Charge_C_skewness | 666 | 666 | 0 | 0 | 0.00109731237 | 0.00183526086 | 0.999981545 | 0.999840844 | 0.573375092 |
| 3 | Sheet3 | Charge_V_skewness | 666 | 666 | 0 | 0 | 0.0544433547 | 0.0601489441 | 0.997362431 | 0.997231256 | 5.51197259 |
| 3 | Sheet3 | Charge_T_skewness | 666 | 666 | 0 | 0 | 0.00816972851 | 0.0120172801 | 0.999618271 | 0.999530087 | 3.34893883 |
| 3 | Sheet3 | Charge_C_kurtosis | 666 | 666 | 0 | 0 | 0.00242991724 | 0.0120043568 | 0.989003112 | 0.999858737 | 0.206391564 |
| 3 | Sheet3 | Charge_V_kurtosis | 666 | 666 | 0 | 0 | 0.285805943 | 0.350327521 | 0.983657466 | 0.992899839 | 10.5389868 |
| 3 | Sheet3 | Charge_T_kurtosis | 666 | 666 | 0 | 0 | 0.0136929598 | 0.0489335374 | 0.992930284 | 0.998765218 | 0.771418796 |
| 3 | Sheet4 | CC_energy | 556 | 556 | 0 | 0 | 0.05606649 | 0.0650161366 | 0.997954452 | 0.995667745 | 0.94553956 |
| 3 | Sheet4 | CC_Q | 556 | 556 | 0 | 0 | 0.0131866466 | 0.0153393565 | 0.998427665 | 0.99668155 | 0.858610377 |
| 3 | Sheet4 | CC_t_mean | 556 | 556 | 0 | 0 | 0.0987361467 | 0.114860874 | 0.998422437 | 0.996684412 | 0.857223958 |
| 3 | Sheet4 | CC_V_mean | 556 | 556 | 0 | 0 | 0.00369721813 | 0.0040950365 | 0.996471627 | 0.992666192 | 0.0957213447 |
| 3 | Sheet4 | CC_T_mean | 556 | 556 | 0 | 0 | 0.014814615 | 0.0184079393 | 0.999980651 | 0.999964394 | 0.0516949069 |
| 3 | Sheet4 | CC_V_std | 556 | 556 | 0 | 0 | 0.00133070043 | 0.00162545909 | 0.990748556 | 0.978617221 | 0.814264475 |
| 3 | Sheet4 | CC_T_std | 556 | 556 | 0 | 0 | 0.010071871 | 0.0138979976 | 0.999793692 | 0.999724364 | 0.78726307 |
| 3 | Sheet4 | CC_V_skewness | 556 | 556 | 0 | 0 | 0.0999418782 | 0.106285269 | 0.980579683 | 0.968880886 | 51.0370039 |
| 3 | Sheet4 | CC_T_skewness | 556 | 556 | 0 | 0 | 0.0215648362 | 0.036701715 | 0.999438501 | 0.998570088 | 2.46460015 |
| 3 | Sheet4 | CC_V_kurtosis | 556 | 556 | 0 | 0 | 0.209782602 | 0.233447163 | 0.947553571 | 0.94642 | 7.94976737 |
| 3 | Sheet4 | CC_T_kurtosis | 556 | 556 | 0 | 0 | 0.0659669658 | 0.130388153 | 0.998048722 | 0.996970172 | 1.98333833 |
| 3 | Sheet4 | CC_CCCT | 556 | 556 | 0 | 0 | 0.197761344 | 0.230054758 | 0.998427745 | 0.996687047 | 0.858459723 |
| 3 | Sheet4 | CC_entropy | 556 | 556 | 0 | 0 | 5.05638141 | 5.05645695 | 0.996450148 | 0.993012901 | 67.1174732 |
| 3 | Sheet4 | dV_energy | 556 | 556 | 0 | 0 | 0.00518980215 | 0.00554348555 | 0.998960693 | 0.997791563 | 0.588672594 |
| 3 | Sheet4 | dV_Q | 556 | 556 | 0 | 0 | 0.00131667733 | 0.00140625379 | 0.998963686 | 0.99789566 | 0.589434335 |
| 3 | Sheet4 | dV_t_mean | 556 | 556 | 0 | 0 | 0.00985758038 | 0.0105567691 | 0.99892108 | 0.997710506 | 0.58839537 |
| 3 | Sheet4 | dV_V_mean | 556 | 556 | 0 | 0 | 9.2818435e-05 | 0.000115008083 | 0.954044441 | 0.951665403 | 0.0023517845 |
| 3 | Sheet4 | dV_T_mean | 556 | 556 | 0 | 0 | 0.00988149489 | 0.0519938925 | 0.999756793 | 0.999970537 | 0.0341270007 |
| 3 | Sheet4 | dV_V_std | 556 | 556 | 0 | 0 | 0.000126707969 | 0.000141640101 | 0.605292815 | 0.605637266 | 0.438565262 |
| 3 | Sheet4 | dV_T_std | 556 | 556 | 0 | 0 | 0.00783170729 | 0.0154036149 | 0.970078937 | 0.986140334 | 5.93242904 |
| 3 | Sheet4 | dV_V_skewness | 556 | 556 | 0 | 0 | 0.00178507029 | 0.00225042593 | 0.989789699 | 0.989305643 | 1.28310813 |
| 3 | Sheet4 | dV_T_skewness | 556 | 556 | 0 | 0 | 0.212895324 | 0.499047125 | 0.626277638 | 0.807193548 | 68.5684182 |
| 3 | Sheet4 | dV_V_kurtosis | 556 | 556 | 0 | 0 | 0.00159421366 | 0.00203844707 | 0.957862707 | 0.944553455 | 0.0878012829 |
| 3 | Sheet4 | dV_T_kurtosis | 556 | 556 | 0 | 0 | 0.447982956 | 1.63071884 | 0.639587665 | 0.805568568 | 19.631761 |
| 3 | Sheet4 | dV_dV_devide_dt | 556 | 556 | 0 | 0 | 3.26406838e-05 | 4.02815761e-05 | 0.999616446 | 0.999218682 | 0.109724391 |
| 3 | Sheet4 | dV_entropy | 556 | 556 | 0 | 0 | 4.79437666 | 4.79466917 | -0.834778703 | -0.823948526 | 63.4196561 |
| 3 | Sheet4 | CV_energy | 556 | 556 | 0 | 0 | 0.0350772673 | 0.0410435053 | 0.988789417 | 0.984435172 | 2.45771957 |
| 3 | Sheet4 | CV_Q | 556 | 556 | 0 | 0 | 0.00835200786 | 0.00977254233 | 0.988787963 | 0.984435102 | 2.45765345 |
| 3 | Sheet4 | CV_t_mean | 556 | 556 | 0 | 0 | 0.0701030362 | 0.0811186384 | 0.999790897 | 0.998959035 | 0.494044143 |
| 3 | Sheet4 | CV_C_mean | 556 | 556 | 0 | 0 | 0.0115400974 | 0.0138876474 | 0.961699658 | 0.945808128 | 1.59481196 |
| 3 | Sheet4 | CV_T_mean | 556 | 556 | 0 | 0 | 0.0178259116 | 0.0214797347 | 0.99998448 | 0.999907772 | 0.0704158781 |
| 3 | Sheet4 | CV_C_std | 556 | 556 | 0 | 0 | 0.0206535903 | 0.0246675006 | 0.755083556 | 0.737426514 | 2.49962499 |
| 3 | Sheet4 | CV_T_std | 556 | 556 | 0 | 0 | 0.0181400335 | 0.0710568921 | 0.933814963 | 0.997691026 | 0.804888524 |
| 3 | Sheet4 | CV_C_skewness | 556 | 556 | 0 | 0 | 0.0210008516 | 0.0249071652 | 0.991287577 | 0.98415821 | 1.08458754 |
| 3 | Sheet4 | CV_T_skewness | 556 | 556 | 0 | 0 | 0.0191688737 | 0.0932698226 | 0.750214515 | 0.934241134 | 2.72926566 |
| 3 | Sheet4 | CV_C_kurtosis | 556 | 556 | 0 | 0 | 0.09798435 | 0.115288033 | 0.991586155 | 0.983554925 | 1.55731449 |
| 3 | Sheet4 | CV_T_kurtosis | 556 | 556 | 0 | 0 | 0.0193743062 | 0.0329030081 | 0.984676597 | 0.987628231 | 0.922193976 |
| 3 | Sheet4 | CV_CVCT | 556 | 556 | 0 | 0 | 0.132138811 | 0.15436345 | 0.999798808 | 0.999006231 | 0.465752652 |
| 3 | Sheet4 | CV_entropy | 556 | 556 | 0 | 0 | 4.71827073 | 4.71837769 | 0.975970338 | 0.954539951 | 71.5378133 |
| 3 | Sheet4 | dI_energy | 556 | 556 | 0 | 0 | 0.00140695258 | 0.00682094604 | 0.811443972 | 0.986151751 | 2.82084907 |
| 3 | Sheet4 | dI_Q | 556 | 556 | 0 | 0 | 0.00033501009 | 0.00162413661 | 0.811434552 | 0.986148819 | 2.82086015 |
| 3 | Sheet4 | dI_t_mean | 556 | 556 | 0 | 0 | 0.0105773247 | 0.0507862333 | 0.815237231 | 0.986300389 | 2.81541375 |
| 3 | Sheet4 | dI_C_mean | 556 | 556 | 0 | 0 | 0.000549821599 | 0.00099518232 | 0.691442582 | 0.827122859 | 0.0579714386 |
| 3 | Sheet4 | dI_T_mean | 556 | 556 | 0 | 0 | 0.0135265805 | 0.0168950873 | 0.99997168 | 0.999898487 | 0.0495911774 |
| 3 | Sheet4 | dI_C_std | 556 | 556 | 0 | 0 | 0.000255333154 | 0.000346974168 | 0.17164272 | 0.231177969 | 0.883375613 |
| 3 | Sheet4 | dI_T_std | 556 | 556 | 0 | 0 | 0.0127917095 | 0.0157018074 | 0.831128253 | 0.785955218 | 11.25519 |
| 3 | Sheet4 | dI_C_skewness | 556 | 556 | 0 | 0 | 0.012040349 | 0.040347192 | 0.709144411 | 0.920888723 | 17.2289548 |
| 3 | Sheet4 | dI_T_skewness | 556 | 556 | 0 | 0 | 0.230722878 | 0.287317017 | 0.461277923 | 0.416767208 | 94.761015 |
| 3 | Sheet4 | dI_C_kurtosis | 556 | 556 | 0 | 0 | 0.0138383607 | 0.0255251644 | 0.349950785 | 0.376500314 | 0.765126499 |
| 3 | Sheet4 | dI_T_kurtosis | 556 | 556 | 0 | 0 | 0.286053122 | 0.376222344 | 0.337274042 | 0.343105287 | 14.0692623 |
| 3 | Sheet4 | dI_dI_devide_dt | 556 | 556 | 0 | 0 | 0.00117446794 | 0.00579449395 | 0.971755704 | 0.992035234 | 0.873334839 |
| 3 | Sheet4 | dI_entropy | 556 | 556 | 0 | 0 | 2.70016758 | 2.71339579 | -0.238901023 | -0.150469172 | 49.370563 |
| 3 | Sheet4 | Charge_energy | 556 | 556 | 0 | 0 | 0.000969490414 | 0.00111831022 | 0.999998268 | 0.999990435 | 0.0131695906 |
| 3 | Sheet4 | Charge_Q | 556 | 556 | 0 | 0 | 0.000137030875 | 0.00016042468 | 0.999998903 | 0.999988969 | 0.00730135286 |
| 3 | Sheet4 | Charge_t_mean | 556 | 556 | 0 | 0 | 0.00524786849 | 0.00882533388 | 0.999969994 | 0.9997994 | 0.0204068806 |
| 3 | Sheet4 | Charge_V_mean | 556 | 556 | 0 | 0 | 0.00122782791 | 0.00124091772 | 0.999977017 | 0.999929485 | 0.0303404267 |
| 3 | Sheet4 | Charge_C_mean | 556 | 556 | 0 | 0 | 0.000774626488 | 0.00114365628 | 0.999989843 | 0.999968652 | 0.0352556197 |
| 3 | Sheet4 | Charge_T_mean | 556 | 556 | 0 | 0 | 0.00697586129 | 0.00818525905 | 0.999994993 | 0.999981359 | 0.0260231094 |
| 3 | Sheet4 | Charge_C_std | 556 | 556 | 0 | 0 | 0.00123569168 | 0.00451549295 | 0.930202425 | 0.995410889 | 0.0713758555 |
| 3 | Sheet4 | Charge_V_std | 556 | 556 | 0 | 0 | 0.00261201079 | 0.00267715445 | 0.999446422 | 0.998993176 | 1.30839219 |
| 3 | Sheet4 | Charge_T_std | 556 | 556 | 0 | 0 | 0.0110738611 | 0.0681551248 | 0.992279086 | 0.998918193 | 0.431037681 |
| 3 | Sheet4 | Charge_C_skewness | 556 | 556 | 0 | 0 | 0.00089054208 | 0.0013803693 | 0.999990437 | 0.999972422 | 0.454462724 |
| 3 | Sheet4 | Charge_V_skewness | 556 | 556 | 0 | 0 | 0.0479787536 | 0.0513240201 | 0.998153341 | 0.99786508 | 5.15748528 |
| 3 | Sheet4 | Charge_T_skewness | 556 | 556 | 0 | 0 | 0.00853598153 | 0.0128573774 | 0.999660645 | 0.999737769 | 3.25976527 |
| 3 | Sheet4 | Charge_C_kurtosis | 556 | 556 | 0 | 0 | 0.00104143325 | 0.0038717349 | 0.996948512 | 0.999921613 | 0.0888393383 |
| 3 | Sheet4 | Charge_V_kurtosis | 556 | 556 | 0 | 0 | 0.236177238 | 0.26734629 | 0.991076972 | 0.99068349 | 9.27047682 |
| 3 | Sheet4 | Charge_T_kurtosis | 556 | 556 | 0 | 0 | 0.0462967118 | 0.236101091 | 0.858367596 | 0.983759069 | 2.60366234 |
| 3 | Sheet5 | CC_energy | 561 | 561 | 0 | 0 | 0.054267197 | 0.0632578576 | 0.998143893 | 0.993940459 | 0.916679285 |
| 3 | Sheet5 | CC_Q | 561 | 561 | 0 | 0 | 0.0127571253 | 0.0149216191 | 0.998568417 | 0.99529999 | 0.833084442 |
| 3 | Sheet5 | CC_t_mean | 561 | 561 | 0 | 0 | 0.0959485851 | 0.112151316 | 0.998564712 | 0.9952125 | 0.835434439 |
| 3 | Sheet5 | CC_V_mean | 561 | 561 | 0 | 0 | 0.00351094304 | 0.00392281339 | 0.996644265 | 0.99444273 | 0.0907763233 |
| 3 | Sheet5 | CC_T_mean | 561 | 561 | 0 | 0 | 0.0130237745 | 0.0165453441 | 0.999978349 | 0.999961327 | 0.0459428283 |
| 3 | Sheet5 | CC_V_std | 561 | 561 | 0 | 0 | 0.00126810039 | 0.00152711004 | 0.988129665 | 0.983760525 | 0.803988334 |
| 3 | Sheet5 | CC_T_std | 561 | 561 | 0 | 0 | 0.0092069867 | 0.0126064829 | 0.999757374 | 0.999500243 | 0.801873535 |
| 3 | Sheet5 | CC_V_skewness | 561 | 561 | 0 | 0 | 0.0918086227 | 0.100328142 | 0.961226621 | 0.96430726 | 41.334363 |
| 3 | Sheet5 | CC_T_skewness | 561 | 561 | 0 | 0 | 0.022636214 | 0.03884274 | 0.999413144 | 0.999467755 | 2.53990658 |
| 3 | Sheet5 | CC_V_kurtosis | 561 | 561 | 0 | 0 | 0.173990218 | 0.202934702 | 0.909467017 | 0.925688024 | 6.90991046 |
| 3 | Sheet5 | CC_T_kurtosis | 561 | 561 | 0 | 0 | 0.0868500279 | 0.379181502 | 0.982277007 | 0.995016162 | 2.58325432 |
| 3 | Sheet5 | CC_CCCT | 561 | 561 | 0 | 0 | 0.19131715 | 0.22378809 | 0.998568513 | 0.995301923 | 0.832928011 |
| 3 | Sheet5 | CC_entropy | 561 | 561 | 0 | 0 | 5.06957862 | 5.06966921 | 0.997283716 | 0.99215927 | 66.9113521 |
| 3 | Sheet5 | dV_energy | 561 | 561 | 0 | 0 | 0.0043203869 | 0.00473391802 | 0.999288415 | 0.997841932 | 0.47530879 |
| 3 | Sheet5 | dV_Q | 561 | 561 | 0 | 0 | 0.00109160359 | 0.00119659669 | 0.999290516 | 0.99790684 | 0.473939407 |
| 3 | Sheet5 | dV_t_mean | 561 | 561 | 0 | 0 | 0.00810372571 | 0.00894565371 | 0.999236272 | 0.99779422 | 0.469100926 |
| 3 | Sheet5 | dV_V_mean | 561 | 561 | 0 | 0 | 0.000104497894 | 0.000126694035 | 0.954885867 | 0.950507809 | 0.00264788123 |
| 3 | Sheet5 | dV_T_mean | 561 | 561 | 0 | 0 | 0.00620738732 | 0.00791292435 | 0.999991516 | 0.999968871 | 0.0216723389 |
| 3 | Sheet5 | dV_V_std | 561 | 561 | 0 | 0 | 0.000111748217 | 0.000127376571 | 0.658009178 | 0.656246653 | 0.3867687 |
| 3 | Sheet5 | dV_T_std | 561 | 561 | 0 | 0 | 0.00974701172 | 0.023313752 | 0.935296729 | 0.982714318 | 7.65867844 |
| 3 | Sheet5 | dV_V_skewness | 561 | 561 | 0 | 0 | 0.00164122208 | 0.00211862729 | 0.991877222 | 0.989951105 | 1.12002169 |
| 3 | Sheet5 | dV_T_skewness | 561 | 561 | 0 | 0 | 0.199188669 | 0.361983283 | 0.775353373 | 0.842948082 | 56.2204216 |
| 3 | Sheet5 | dV_V_kurtosis | 561 | 561 | 0 | 0 | 0.00165775483 | 0.00210427941 | 0.967156131 | 0.94513891 | 0.0911369699 |
| 3 | Sheet5 | dV_T_kurtosis | 561 | 561 | 0 | 0 | 0.34426749 | 0.740666692 | 0.576436415 | 0.781405694 | 15.3342252 |
| 3 | Sheet5 | dV_dV_devide_dt | 561 | 561 | 0 | 0 | 3.09539348e-05 | 3.87024318e-05 | 0.999746151 | 0.999359671 | 0.107155647 |
| 3 | Sheet5 | dV_entropy | 561 | 561 | 0 | 0 | 4.82604953 | 4.82638686 | -0.798510622 | -0.801370467 | 63.5780035 |
| 3 | Sheet5 | CV_energy | 561 | 561 | 0 | 0 | 0.0344946772 | 0.0397311557 | 0.99041385 | 0.983693374 | 2.37222532 |
| 3 | Sheet5 | CV_Q | 561 | 561 | 0 | 0 | 0.00821263382 | 0.0094592436 | 0.990412958 | 0.98369786 | 2.37213379 |
| 3 | Sheet5 | CV_t_mean | 561 | 561 | 0 | 0 | 0.068480519 | 0.0780274602 | 0.999831593 | 0.998734534 | 0.469920275 |
| 3 | Sheet5 | CV_C_mean | 561 | 561 | 0 | 0 | 0.011068114 | 0.0129274189 | 0.969860579 | 0.956133625 | 1.54136563 |
| 3 | Sheet5 | CV_T_mean | 561 | 561 | 0 | 0 | 0.0163717429 | 0.0191844715 | 0.999985843 | 0.999938355 | 0.0656367006 |
| 3 | Sheet5 | CV_C_std | 561 | 561 | 0 | 0 | 0.0198812051 | 0.0230149766 | 0.769876911 | 0.753017027 | 2.40184298 |
| 3 | Sheet5 | CV_T_std | 561 | 561 | 0 | 0 | 0.0116092878 | 0.0136579763 | 0.99919188 | 0.998957736 | 0.542472895 |
| 3 | Sheet5 | CV_C_skewness | 561 | 561 | 0 | 0 | 0.0203014415 | 0.0234053394 | 0.993000089 | 0.984850093 | 1.04266033 |
| 3 | Sheet5 | CV_T_skewness | 561 | 561 | 0 | 0 | 0.00925774339 | 0.0339227397 | 0.973010149 | 0.98762917 | 1.19911234 |
| 3 | Sheet5 | CV_C_kurtosis | 561 | 561 | 0 | 0 | 0.0974621953 | 0.111867285 | 0.992804361 | 0.985598471 | 1.54105443 |
| 3 | Sheet5 | CV_T_kurtosis | 561 | 561 | 0 | 0 | 0.0196013978 | 0.0304587859 | 0.993093365 | 0.994518241 | 0.875471889 |
| 3 | Sheet5 | CV_CVCT | 561 | 561 | 0 | 0 | 0.129310612 | 0.148815218 | 0.999836968 | 0.998768262 | 0.443787635 |
| 3 | Sheet5 | CV_entropy | 561 | 561 | 0 | 0 | 4.71372122 | 4.71382818 | 0.982244616 | 0.965295739 | 71.6795487 |
| 3 | Sheet5 | dI_energy | 561 | 561 | 0 | 0 | 0.00163863057 | 0.00590778298 | 0.826234991 | 0.983863494 | 3.31805726 |
| 3 | Sheet5 | dI_Q | 561 | 561 | 0 | 0 | 0.000390148427 | 0.00140661723 | 0.826225111 | 0.98386295 | 3.31806998 |
| 3 | Sheet5 | dI_t_mean | 561 | 561 | 0 | 0 | 0.0122470361 | 0.0442061515 | 0.828161069 | 0.984245872 | 3.29232945 |
| 3 | Sheet5 | dI_C_mean | 561 | 561 | 0 | 0 | 0.000503314813 | 0.000806780963 | 0.690429885 | 0.760560742 | 0.0530724492 |
| 3 | Sheet5 | dI_T_mean | 561 | 561 | 0 | 0 | 0.0144192247 | 0.0180070454 | 0.9999593 | 0.999863999 | 0.0539247553 |
| 3 | Sheet5 | dI_C_std | 561 | 561 | 0 | 0 | 0.000240193555 | 0.000309084287 | 0.17272237 | 0.14602689 | 0.831901138 |
| 3 | Sheet5 | dI_T_std | 561 | 561 | 0 | 0 | 0.012748935 | 0.0158595671 | 0.872384992 | 0.848916072 | 11.3641531 |
| 3 | Sheet5 | dI_C_skewness | 561 | 561 | 0 | 0 | 0.00969795537 | 0.028634406 | 0.745150785 | 0.900274788 | 15.2163383 |
| 3 | Sheet5 | dI_T_skewness | 561 | 561 | 0 | 0 | 0.237633547 | 0.294695246 | 0.51130192 | 0.468098016 | 94.606345 |
| 3 | Sheet5 | dI_C_kurtosis | 561 | 561 | 0 | 0 | 0.0114604059 | 0.0164728899 | 0.375389842 | 0.360018922 | 0.634127651 |
| 3 | Sheet5 | dI_T_kurtosis | 561 | 561 | 0 | 0 | 0.287708026 | 0.383361167 | 0.348995352 | 0.375699564 | 14.1212966 |
| 3 | Sheet5 | dI_dI_devide_dt | 561 | 561 | 0 | 0 | 0.00106039243 | 0.00473492672 | 0.978298424 | 0.993021422 | 0.789789259 |
| 3 | Sheet5 | dI_entropy | 561 | 561 | 0 | 0 | 2.69295152 | 2.7033617 | -0.204595938 | -0.208764062 | 49.2951403 |
| 3 | Sheet5 | Charge_energy | 561 | 561 | 0 | 0 | 0.00100444624 | 0.00115291943 | 0.999998308 | 0.999988378 | 0.013612478 |
| 3 | Sheet5 | Charge_Q | 561 | 561 | 0 | 0 | 0.000135644541 | 0.000158135531 | 0.999999011 | 0.999991232 | 0.00722026607 |
| 3 | Sheet5 | Charge_t_mean | 561 | 561 | 0 | 0 | 0.00574894167 | 0.0117711839 | 0.999947923 | 0.999586934 | 0.0220556007 |
| 3 | Sheet5 | Charge_V_mean | 561 | 561 | 0 | 0 | 0.00114456088 | 0.00115962567 | 0.999977557 | 0.999917217 | 0.028249104 |
| 3 | Sheet5 | Charge_C_mean | 561 | 561 | 0 | 0 | 0.000845062632 | 0.00139339837 | 0.999983134 | 0.999934616 | 0.0389366152 |
| 3 | Sheet5 | Charge_T_mean | 561 | 561 | 0 | 0 | 0.00615786894 | 0.00734599919 | 0.999994712 | 0.999978115 | 0.0233030492 |
| 3 | Sheet5 | Charge_C_std | 561 | 561 | 0 | 0 | 0.00122359179 | 0.00470455675 | 0.940664285 | 0.998620215 | 0.070605577 |
| 3 | Sheet5 | Charge_V_std | 561 | 561 | 0 | 0 | 0.00234125374 | 0.00240856941 | 0.999571805 | 0.999243942 | 1.2015715 |
| 3 | Sheet5 | Charge_T_std | 561 | 561 | 0 | 0 | 0.011526946 | 0.0720526259 | 0.991285082 | 0.998557567 | 0.462934864 |
| 3 | Sheet5 | Charge_C_skewness | 561 | 561 | 0 | 0 | 0.00098906485 | 0.00164896893 | 0.999983512 | 0.999937063 | 0.502710016 |
| 3 | Sheet5 | Charge_V_skewness | 561 | 561 | 0 | 0 | 0.0410421911 | 0.0450456878 | 0.997948633 | 0.997144665 | 4.4671918 |
| 3 | Sheet5 | Charge_T_skewness | 561 | 561 | 0 | 0 | 0.00815341748 | 0.0122927668 | 0.999521859 | 0.999479174 | 3.48854226 |
| 3 | Sheet5 | Charge_C_kurtosis | 561 | 561 | 0 | 0 | 0.0015624461 | 0.00685019481 | 0.992368624 | 0.999811529 | 0.133301631 |
| 3 | Sheet5 | Charge_V_kurtosis | 561 | 561 | 0 | 0 | 0.198058521 | 0.23089217 | 0.989444034 | 0.992971241 | 8.07783238 |
| 3 | Sheet5 | Charge_T_kurtosis | 561 | 561 | 0 | 0 | 0.0123922989 | 0.0232338233 | 0.999367344 | 0.999678655 | 0.717014793 |
| 3 | Sheet6 | CC_energy | 541 | 541 | 0 | 0 | 0.0549726476 | 0.0635585563 | 0.998147291 | 0.995211895 | 0.936765589 |
| 3 | Sheet6 | CC_Q | 541 | 541 | 0 | 0 | 0.0129186846 | 0.0149878502 | 0.998567182 | 0.996238042 | 0.8510515 |
| 3 | Sheet6 | CC_t_mean | 541 | 541 | 0 | 0 | 0.0971004847 | 0.112714807 | 0.998555231 | 0.99617728 | 0.852906165 |
| 3 | Sheet6 | CC_V_mean | 541 | 541 | 0 | 0 | 0.00363368306 | 0.00402602426 | 0.996462672 | 0.993450923 | 0.0939525461 |
| 3 | Sheet6 | CC_T_mean | 541 | 541 | 0 | 0 | 0.0123796573 | 0.0159018501 | 0.999982125 | 0.99996529 | 0.0443947636 |
| 3 | Sheet6 | CC_V_std | 541 | 541 | 0 | 0 | 0.00127780149 | 0.0015628562 | 0.987791286 | 0.979443031 | 0.794288633 |
| 3 | Sheet6 | CC_T_std | 541 | 541 | 0 | 0 | 0.00844133809 | 0.0116662289 | 0.999766941 | 0.999554604 | 0.775913691 |
| 3 | Sheet6 | CC_V_skewness | 541 | 541 | 0 | 0 | 0.0968476978 | 0.104670373 | 0.969896744 | 0.970462274 | 51.9206975 |
| 3 | Sheet6 | CC_T_skewness | 541 | 541 | 0 | 0 | 0.0245985913 | 0.0427332519 | 0.999244458 | 0.999343993 | 2.86710192 |
| 3 | Sheet6 | CC_V_kurtosis | 541 | 541 | 0 | 0 | 0.198903207 | 0.228301994 | 0.927099632 | 0.944685142 | 7.75347683 |
| 3 | Sheet6 | CC_T_kurtosis | 541 | 541 | 0 | 0 | 0.0860848236 | 0.263874571 | 0.990769151 | 0.996267523 | 2.63685252 |
| 3 | Sheet6 | CC_CCCT | 541 | 541 | 0 | 0 | 0.193743796 | 0.224784126 | 0.998567231 | 0.996234041 | 0.850915405 |
| 3 | Sheet6 | CC_entropy | 541 | 541 | 0 | 0 | 5.06342001 | 5.06350824 | 0.996801188 | 0.991978991 | 67.0090083 |
| 3 | Sheet6 | dV_energy | 541 | 541 | 0 | 0 | 0.00527908074 | 0.00565967759 | 0.999079314 | 0.997715724 | 0.587387718 |
| 3 | Sheet6 | dV_Q | 541 | 541 | 0 | 0 | 0.00133887909 | 0.00143514257 | 0.999082809 | 0.997800472 | 0.587938547 |
| 3 | Sheet6 | dV_t_mean | 541 | 541 | 0 | 0 | 0.0100201978 | 0.0107825407 | 0.999035234 | 0.997769608 | 0.586695431 |
| 3 | Sheet6 | dV_V_mean | 541 | 541 | 0 | 0 | 9.2334109e-05 | 0.000113182824 | 0.945800937 | 0.938181858 | 0.00233956198 |
| 3 | Sheet6 | dV_T_mean | 541 | 541 | 0 | 0 | 0.00614597052 | 0.0077229015 | 0.999992849 | 0.999970595 | 0.0218377127 |
| 3 | Sheet6 | dV_V_std | 541 | 541 | 0 | 0 | 0.000129358725 | 0.000145067831 | 0.59586597 | 0.582888202 | 0.447988793 |
| 3 | Sheet6 | dV_T_std | 541 | 541 | 0 | 0 | 0.00759001608 | 0.0181487746 | 0.956382126 | 0.987904955 | 6.12522022 |
| 3 | Sheet6 | dV_V_skewness | 541 | 541 | 0 | 0 | 0.00172484054 | 0.00221438589 | 0.987948401 | 0.985555124 | 1.21094551 |
| 3 | Sheet6 | dV_T_skewness | 541 | 541 | 0 | 0 | 0.213935158 | 0.533382318 | 0.679435738 | 0.8624027 | 61.6514543 |
| 3 | Sheet6 | dV_V_kurtosis | 541 | 541 | 0 | 0 | 0.00162781491 | 0.00205833772 | 0.957805067 | 0.951193749 | 0.089564523 |
| 3 | Sheet6 | dV_T_kurtosis | 541 | 541 | 0 | 0 | 0.534948076 | 2.52804244 | 0.385401475 | 0.795110341 | 22.9665042 |
| 3 | Sheet6 | dV_dV_devide_dt | 541 | 541 | 0 | 0 | 3.35388166e-05 | 4.18626133e-05 | 0.999623563 | 0.99915716 | 0.114896516 |
| 3 | Sheet6 | dV_entropy | 541 | 541 | 0 | 0 | 4.81508741 | 4.815435 | -0.78935493 | -0.778040295 | 63.5217303 |
| 3 | Sheet6 | CV_energy | 541 | 541 | 0 | 0 | 0.03762888 | 0.0430395355 | 0.989016633 | 0.984463118 | 2.58037751 |
| 3 | Sheet6 | CV_Q | 541 | 541 | 0 | 0 | 0.00895955125 | 0.0102478227 | 0.989015258 | 0.984452963 | 2.58030412 |
| 3 | Sheet6 | CV_t_mean | 541 | 541 | 0 | 0 | 0.0744946103 | 0.0843095044 | 0.999811007 | 0.998466615 | 0.50628379 |
| 3 | Sheet6 | CV_C_mean | 541 | 541 | 0 | 0 | 0.0119709108 | 0.0140003565 | 0.961845877 | 0.955825582 | 1.67933426 |
| 3 | Sheet6 | CV_T_mean | 541 | 541 | 0 | 0 | 0.0167303529 | 0.019569355 | 0.999986683 | 0.999928533 | 0.0675260052 |
| 3 | Sheet6 | CV_C_std | 541 | 541 | 0 | 0 | 0.0216314368 | 0.0251649048 | 0.700158449 | 0.682619085 | 2.64318326 |
| 3 | Sheet6 | CV_T_std | 541 | 541 | 0 | 0 | 0.0119043733 | 0.0139763416 | 0.999086288 | 0.998857066 | 0.59922755 |
| 3 | Sheet6 | CV_C_skewness | 541 | 541 | 0 | 0 | 0.0217393456 | 0.025216778 | 0.991889969 | 0.988702227 | 1.10016119 |
| 3 | Sheet6 | CV_T_skewness | 541 | 541 | 0 | 0 | 0.0102070014 | 0.0287169279 | 0.968056247 | 0.990077598 | 1.29872273 |
| 3 | Sheet6 | CV_C_kurtosis | 541 | 541 | 0 | 0 | 0.101796381 | 0.117369244 | 0.991770162 | 0.988558309 | 1.57270977 |
| 3 | Sheet6 | CV_T_kurtosis | 541 | 541 | 0 | 0 | 0.0228769048 | 0.0416895275 | 0.976730413 | 0.985503968 | 1.02108417 |
| 3 | Sheet6 | CV_CVCT | 541 | 541 | 0 | 0 | 0.141759335 | 0.161968519 | 0.999810468 | 0.998484974 | 0.481841161 |
| 3 | Sheet6 | CV_entropy | 541 | 541 | 0 | 0 | 4.71020847 | 4.71029366 | 0.979688415 | 0.967847931 | 71.6559729 |
| 3 | Sheet6 | dI_energy | 541 | 541 | 0 | 0 | 0.000916178431 | 0.00104936334 | 0.997799077 | 0.993083814 | 1.815772 |
| 3 | Sheet6 | dI_Q | 541 | 541 | 0 | 0 | 0.000218152053 | 0.000249865989 | 0.997798845 | 0.993086543 | 1.81577936 |
| 3 | Sheet6 | dI_t_mean | 541 | 541 | 0 | 0 | 0.00683884407 | 0.0078543928 | 0.997794642 | 0.99334611 | 1.7981858 |
| 3 | Sheet6 | dI_C_mean | 541 | 541 | 0 | 0 | 0.000493224356 | 0.000604940297 | 0.878777135 | 0.8690691 | 0.0520378037 |
| 3 | Sheet6 | dI_T_mean | 541 | 541 | 0 | 0 | 0.0146269475 | 0.0177192275 | 0.999960582 | 0.999878761 | 0.0551405081 |
| 3 | Sheet6 | dI_C_std | 541 | 541 | 0 | 0 | 0.000246380554 | 0.000304438426 | 0.179152148 | 0.171055226 | 0.852967349 |
| 3 | Sheet6 | dI_T_std | 541 | 541 | 0 | 0 | 0.0130834842 | 0.0160909249 | 0.790190883 | 0.759014724 | 12.3799021 |
| 3 | Sheet6 | dI_C_skewness | 541 | 541 | 0 | 0 | 0.00778365128 | 0.0104330311 | 0.97370999 | 0.970183153 | 9.10183098 |
| 3 | Sheet6 | dI_T_skewness | 541 | 541 | 0 | 0 | 0.241111569 | 0.30138548 | 0.45983284 | 0.441680289 | 99.5314593 |
| 3 | Sheet6 | dI_C_kurtosis | 541 | 541 | 0 | 0 | 0.013448701 | 0.0172538325 | 0.517443423 | 0.474789977 | 0.742484148 |
| 3 | Sheet6 | dI_T_kurtosis | 541 | 541 | 0 | 0 | 0.294591465 | 0.378471083 | 0.380566996 | 0.380726877 | 14.1941095 |
| 3 | Sheet6 | dI_dI_devide_dt | 541 | 541 | 0 | 0 | 0.000938925107 | 0.00148815713 | 0.997752947 | 0.997689812 | 0.711203846 |
| 3 | Sheet6 | dI_entropy | 541 | 541 | 0 | 0 | 2.72255496 | 2.73283886 | -0.355038694 | -0.32992894 | 49.5826318 |
| 3 | Sheet6 | Charge_energy | 541 | 541 | 0 | 0 | 0.00102728041 | 0.00116339138 | 0.999998403 | 0.999987647 | 0.0140120753 |
| 3 | Sheet6 | Charge_Q | 541 | 541 | 0 | 0 | 0.000132187571 | 0.000153093919 | 0.99999904 | 0.999992194 | 0.00708274072 |
| 3 | Sheet6 | Charge_t_mean | 541 | 541 | 0 | 0 | 0.00535321684 | 0.00843934968 | 0.999975577 | 0.999873759 | 0.0205047909 |
| 3 | Sheet6 | Charge_V_mean | 541 | 541 | 0 | 0 | 0.00120688137 | 0.00122220156 | 0.999979107 | 0.999909587 | 0.0297770294 |
| 3 | Sheet6 | Charge_C_mean | 541 | 541 | 0 | 0 | 0.00079059071 | 0.00103749057 | 0.999992901 | 0.999967563 | 0.0367309065 |
| 3 | Sheet6 | Charge_T_mean | 541 | 541 | 0 | 0 | 0.00571023356 | 0.00682377236 | 0.999995843 | 0.999983858 | 0.0218633415 |
| 3 | Sheet6 | Charge_C_std | 541 | 541 | 0 | 0 | 0.000769285818 | 0.0018277862 | 0.991634563 | 0.999553751 | 0.0444133088 |
| 3 | Sheet6 | Charge_V_std | 541 | 541 | 0 | 0 | 0.00254199278 | 0.00261502132 | 0.999461052 | 0.999138385 | 1.30055016 |
| 3 | Sheet6 | Charge_T_std | 541 | 541 | 0 | 0 | 0.00683666299 | 0.0107423179 | 0.999928387 | 0.999925502 | 0.297184153 |
| 3 | Sheet6 | Charge_C_skewness | 541 | 541 | 0 | 0 | 0.000990836088 | 0.00138234279 | 0.999993492 | 0.999967336 | 0.510194926 |
| 3 | Sheet6 | Charge_V_skewness | 541 | 541 | 0 | 0 | 0.0462372401 | 0.0504153795 | 0.997860423 | 0.996146492 | 4.79647143 |
| 3 | Sheet6 | Charge_T_skewness | 541 | 541 | 0 | 0 | 0.00841790354 | 0.01258176 | 0.999500497 | 0.999333308 | 3.69658843 |
| 3 | Sheet6 | Charge_C_kurtosis | 541 | 541 | 0 | 0 | 0.00141762108 | 0.00571124048 | 0.995038094 | 0.999821845 | 0.121276574 |
| 3 | Sheet6 | Charge_V_kurtosis | 541 | 541 | 0 | 0 | 0.231519366 | 0.268603419 | 0.990100771 | 0.993296793 | 8.94988889 |
| 3 | Sheet6 | Charge_T_kurtosis | 541 | 541 | 0 | 0 | 0.0126958651 | 0.0241893924 | 0.999595801 | 0.999492383 | 0.735971176 |
| 3 | Sheet7 | CC_energy | 526 | 526 | 0 | 0 | 0.0545802028 | 0.0645298462 | 0.997625353 | 0.993206233 | 0.926304406 |
| 3 | Sheet7 | CC_Q | 526 | 526 | 0 | 0 | 0.0128222356 | 0.0152171 | 0.998165657 | 0.994342403 | 0.841152193 |
| 3 | Sheet7 | CC_t_mean | 526 | 526 | 0 | 0 | 0.0962834257 | 0.114300637 | 0.998151296 | 0.994310698 | 0.842188531 |
| 3 | Sheet7 | CC_V_mean | 526 | 526 | 0 | 0 | 0.00365617253 | 0.0041008089 | 0.995680239 | 0.991966993 | 0.0945512672 |
| 3 | Sheet7 | CC_T_mean | 526 | 526 | 0 | 0 | 0.0128484562 | 0.0164076386 | 0.999980113 | 0.999949866 | 0.0459069764 |
| 3 | Sheet7 | CC_V_std | 526 | 526 | 0 | 0 | 0.00145186774 | 0.00175265334 | 0.98588294 | 0.977290867 | 0.892240001 |
| 3 | Sheet7 | CC_T_std | 526 | 526 | 0 | 0 | 0.00887712044 | 0.0123945747 | 0.999718345 | 0.999010273 | 0.786173964 |
| 3 | Sheet7 | CC_V_skewness | 526 | 526 | 0 | 0 | 0.10420629 | 0.111867678 | 0.973958357 | 0.973186093 | 64.8754681 |
| 3 | Sheet7 | CC_T_skewness | 526 | 526 | 0 | 0 | 0.0232633955 | 0.039647621 | 0.999302649 | 0.999438223 | 2.82584302 |
| 3 | Sheet7 | CC_V_kurtosis | 526 | 526 | 0 | 0 | 0.228339501 | 0.257881861 | 0.936968789 | 0.936806063 | 8.6226605 |
| 3 | Sheet7 | CC_T_kurtosis | 526 | 526 | 0 | 0 | 0.0742049078 | 0.145352274 | 0.996875115 | 0.998047592 | 2.34906029 |
| 3 | Sheet7 | CC_CCCT | 526 | 526 | 0 | 0 | 0.192280875 | 0.228208154 | 0.998165713 | 0.994342501 | 0.84094325 |
| 3 | Sheet7 | CC_entropy | 526 | 526 | 0 | 0 | 5.05417446 | 5.05426246 | 0.995632003 | 0.992921849 | 67.123812 |
| 3 | Sheet7 | dV_energy | 526 | 526 | 0 | 0 | 0.0047518236 | 0.00514903004 | 0.999171486 | 0.997625167 | 0.524092347 |
| 3 | Sheet7 | dV_Q | 526 | 526 | 0 | 0 | 0.00120113692 | 0.0013019144 | 0.999173874 | 0.997627537 | 0.522825194 |
| 3 | Sheet7 | dV_t_mean | 526 | 526 | 0 | 0 | 0.00901180629 | 0.00979254319 | 0.999139416 | 0.997601234 | 0.523028476 |
| 3 | Sheet7 | dV_V_mean | 526 | 526 | 0 | 0 | 9.56910335e-05 | 0.000120264208 | 0.934454723 | 0.928695607 | 0.00242466462 |
| 3 | Sheet7 | dV_T_mean | 526 | 526 | 0 | 0 | 0.00562822528 | 0.0072702906 | 0.999993796 | 0.99997081 | 0.019889654 |
| 3 | Sheet7 | dV_V_std | 526 | 526 | 0 | 0 | 0.000122457224 | 0.00013788468 | 0.635797707 | 0.636308953 | 0.423998843 |
| 3 | Sheet7 | dV_T_std | 526 | 526 | 0 | 0 | 0.00791969526 | 0.0162817738 | 0.967357299 | 0.989956618 | 5.99505875 |
| 3 | Sheet7 | dV_V_skewness | 526 | 526 | 0 | 0 | 0.00175144023 | 0.00254545469 | 0.980935378 | 0.982843929 | 1.22833366 |
| 3 | Sheet7 | dV_T_skewness | 526 | 526 | 0 | 0 | 0.17834728 | 0.406992893 | 0.660938462 | 0.832763953 | 65.9444951 |
| 3 | Sheet7 | dV_V_kurtosis | 526 | 526 | 0 | 0 | 0.00172609229 | 0.00222238746 | 0.948128452 | 0.939028022 | 0.0949569339 |
| 3 | Sheet7 | dV_T_kurtosis | 526 | 526 | 0 | 0 | 0.409151712 | 2.4364189 | 0.497994466 | 0.72209378 | 19.0339431 |
| 3 | Sheet7 | dV_dV_devide_dt | 526 | 526 | 0 | 0 | 2.75376119e-05 | 3.43830041e-05 | 0.999749974 | 0.999393737 | 0.0951243516 |
| 3 | Sheet7 | dV_entropy | 526 | 526 | 0 | 0 | 4.82415113 | 4.82446609 | -0.737232743 | -0.752423515 | 63.5651635 |
| 3 | Sheet7 | CV_energy | 526 | 526 | 0 | 0 | 0.0374490173 | 0.0493966647 | 0.970620775 | 0.985443436 | 2.54608943 |
| 3 | Sheet7 | CV_Q | 526 | 526 | 0 | 0 | 0.00891620184 | 0.0117608109 | 0.970617907 | 0.985451105 | 2.54600738 |
| 3 | Sheet7 | CV_t_mean | 526 | 526 | 0 | 0 | 0.0686243626 | 0.0791426755 | 0.999801312 | 0.998085687 | 0.463465957 |
| 3 | Sheet7 | CV_C_mean | 526 | 526 | 0 | 0 | 0.0111173958 | 0.0140879562 | 0.944438008 | 0.933693655 | 1.55466935 |
| 3 | Sheet7 | CV_T_mean | 526 | 526 | 0 | 0 | 0.0157606021 | 0.0185855983 | 0.999986985 | 0.999915482 | 0.0634703773 |
| 3 | Sheet7 | CV_C_std | 526 | 526 | 0 | 0 | 0.0198368782 | 0.023270059 | 0.659094253 | 0.626313065 | 2.42090309 |
| 3 | Sheet7 | CV_T_std | 526 | 526 | 0 | 0 | 0.0112313179 | 0.0134239228 | 0.998627683 | 0.998062764 | 0.547263566 |
| 3 | Sheet7 | CV_C_skewness | 526 | 526 | 0 | 0 | 0.0205894939 | 0.0242043804 | 0.991325066 | 0.987398895 | 1.03875381 |
| 3 | Sheet7 | CV_T_skewness | 526 | 526 | 0 | 0 | 0.0249587408 | 0.138091839 | 0.566456663 | 0.927286528 | 3.1148278 |
| 3 | Sheet7 | CV_C_kurtosis | 526 | 526 | 0 | 0 | 0.0964843373 | 0.112714638 | 0.990681874 | 0.987611963 | 1.48231196 |
| 3 | Sheet7 | CV_T_kurtosis | 526 | 526 | 0 | 0 | 0.0213208234 | 0.0485793227 | 0.972247978 | 0.98210856 | 0.943790489 |
| 3 | Sheet7 | CV_CVCT | 526 | 526 | 0 | 0 | 0.129969626 | 0.150799886 | 0.999810164 | 0.998162226 | 0.438998969 |
| 3 | Sheet7 | CV_entropy | 526 | 526 | 0 | 0 | 4.71471117 | 4.7148888 | 0.879283307 | 0.910240332 | 71.6596447 |
| 3 | Sheet7 | dI_energy | 526 | 526 | 0 | 0 | 0.00182305847 | 0.00735577464 | 0.760437401 | 0.971464399 | 3.60118543 |
| 3 | Sheet7 | dI_Q | 526 | 526 | 0 | 0 | 0.000434063568 | 0.0017513752 | 0.760430008 | 0.971458462 | 3.60117869 |
| 3 | Sheet7 | dI_t_mean | 526 | 526 | 0 | 0 | 0.0136033857 | 0.0549820897 | 0.763638642 | 0.971318161 | 3.56489568 |
| 3 | Sheet7 | dI_C_mean | 526 | 526 | 0 | 0 | 0.000506810761 | 0.000763778514 | 0.842422941 | 0.88221746 | 0.0534749416 |
| 3 | Sheet7 | dI_T_mean | 526 | 526 | 0 | 0 | 0.014608225 | 0.0180337347 | 0.999960557 | 0.999881201 | 0.0548710466 |
| 3 | Sheet7 | dI_C_std | 526 | 526 | 0 | 0 | 0.000265674907 | 0.000330107315 | 0.208454112 | 0.176244575 | 0.920283692 |
| 3 | Sheet7 | dI_T_std | 526 | 526 | 0 | 0 | 0.0128252136 | 0.0169464256 | 0.805903477 | 0.791273409 | 11.6580649 |
| 3 | Sheet7 | dI_C_skewness | 526 | 526 | 0 | 0 | 0.0104462896 | 0.022507754 | 0.907405863 | 0.944472386 | 12.0338973 |
| 3 | Sheet7 | dI_T_skewness | 526 | 526 | 0 | 0 | 0.237486912 | 0.324440188 | 0.456885992 | 0.490405986 | 91.0527851 |
| 3 | Sheet7 | dI_C_kurtosis | 526 | 526 | 0 | 0 | 0.0150097698 | 0.0190031368 | 0.504975486 | 0.499943497 | 0.828319964 |
| 3 | Sheet7 | dI_T_kurtosis | 526 | 526 | 0 | 0 | 0.298122183 | 0.487476207 | 0.131769626 | 0.34994084 | 14.6359458 |
| 3 | Sheet7 | dI_dI_devide_dt | 526 | 526 | 0 | 0 | 0.00146634853 | 0.00655552307 | 0.96142362 | 0.985755094 | 1.11757694 |
| 3 | Sheet7 | dI_entropy | 526 | 526 | 0 | 0 | 2.73199416 | 2.74361686 | -0.267885092 | -0.224113014 | 49.6703653 |
| 3 | Sheet7 | Charge_energy | 526 | 526 | 0 | 0 | 0.00550363469 | 0.0410472224 | 0.993617755 | 0.99984762 | 0.0746126163 |
| 3 | Sheet7 | Charge_Q | 526 | 526 | 0 | 0 | 0.000559289665 | 0.00447019159 | 0.999061163 | 0.999967842 | 0.029796022 |
| 3 | Sheet7 | Charge_t_mean | 526 | 526 | 0 | 0 | 0.00545137301 | 0.0104718685 | 0.999961038 | 0.999689633 | 0.0207685495 |
| 3 | Sheet7 | Charge_V_mean | 526 | 526 | 0 | 0 | 0.00126251419 | 0.00128218368 | 0.999968346 | 0.999889426 | 0.0311488658 |
| 3 | Sheet7 | Charge_C_mean | 526 | 526 | 0 | 0 | 0.000758629 | 0.00121475385 | 0.99998579 | 0.999903691 | 0.0352478242 |
| 3 | Sheet7 | Charge_T_mean | 526 | 526 | 0 | 0 | 0.00589270955 | 0.00702140062 | 0.999995529 | 0.999975098 | 0.0224930632 |
| 3 | Sheet7 | Charge_C_std | 526 | 526 | 0 | 0 | 0.00123681094 | 0.00556293962 | 0.94368062 | 0.999074507 | 0.0713859025 |
| 3 | Sheet7 | Charge_V_std | 526 | 526 | 0 | 0 | 0.00273052964 | 0.00280664906 | 0.999340039 | 0.998970034 | 1.38954982 |
| 3 | Sheet7 | Charge_T_std | 526 | 526 | 0 | 0 | 0.00858761761 | 0.0395258569 | 0.996458636 | 0.999774667 | 0.36369099 |
| 3 | Sheet7 | Charge_C_skewness | 526 | 526 | 0 | 0 | 0.00099177665 | 0.00159424025 | 0.999986026 | 0.999903031 | 0.5340424 |
| 3 | Sheet7 | Charge_V_skewness | 526 | 526 | 0 | 0 | 0.0517392169 | 0.0560300795 | 0.997636678 | 0.996917194 | 5.25327726 |
| 3 | Sheet7 | Charge_T_skewness | 526 | 526 | 0 | 0 | 0.00834294116 | 0.0126397133 | 0.999489713 | 0.999170899 | 3.7154953 |
| 3 | Sheet7 | Charge_C_kurtosis | 526 | 526 | 0 | 0 | 0.00164491349 | 0.007292709 | 0.992487854 | 0.999389972 | 0.141331485 |
| 3 | Sheet7 | Charge_V_kurtosis | 526 | 526 | 0 | 0 | 0.264161648 | 0.301372946 | 0.99007353 | 0.994213626 | 9.88777861 |
| 3 | Sheet7 | Charge_T_kurtosis | 526 | 526 | 0 | 0 | 0.0129421381 | 0.02454058 | 0.999407902 | 0.999652775 | 0.753027564 |
| 3 | Sheet8 | CC_energy | 616 | 616 | 0 | 0 | 0.055598589 | 0.0646683017 | 0.99779855 | 0.994484691 | 0.941243627 |
| 3 | Sheet8 | CC_Q | 616 | 616 | 0 | 0 | 0.0130598504 | 0.0152461714 | 0.998311748 | 0.995743554 | 0.854079488 |
| 3 | Sheet8 | CC_t_mean | 616 | 616 | 0 | 0 | 0.0982322087 | 0.114714175 | 0.998278766 | 0.995707347 | 0.85658298 |
| 3 | Sheet8 | CC_V_mean | 616 | 616 | 0 | 0 | 0.00372148645 | 0.00412418562 | 0.996333171 | 0.994298333 | 0.0962980359 |
| 3 | Sheet8 | CC_T_mean | 616 | 616 | 0 | 0 | 0.01278062 | 0.0160615033 | 0.999982025 | 0.999957749 | 0.0464347185 |
| 3 | Sheet8 | CC_V_std | 616 | 616 | 0 | 0 | 0.00140622002 | 0.00171565751 | 0.988407077 | 0.981065359 | 0.864171862 |
| 3 | Sheet8 | CC_T_std | 616 | 616 | 0 | 0 | 0.00907799049 | 0.0126802047 | 0.999753901 | 0.999513468 | 0.79282657 |
| 3 | Sheet8 | CC_V_skewness | 616 | 616 | 0 | 0 | 0.106826296 | 0.114461008 | 0.967999003 | 0.966998089 | 62.6925365 |
| 3 | Sheet8 | CC_T_skewness | 616 | 616 | 0 | 0 | 0.0217843368 | 0.0375682883 | 0.999430451 | 0.999570146 | 2.53852423 |
| 3 | Sheet8 | CC_V_kurtosis | 616 | 616 | 0 | 0 | 0.231017066 | 0.259564264 | 0.925494155 | 0.932222701 | 8.69170554 |
| 3 | Sheet8 | CC_T_kurtosis | 616 | 616 | 0 | 0 | 0.0709535847 | 0.14154301 | 0.997533591 | 0.998149157 | 2.15865406 |
| 3 | Sheet8 | CC_CCCT | 616 | 616 | 0 | 0 | 0.195866346 | 0.228661711 | 0.998311823 | 0.995751637 | 0.85398255 |
| 3 | Sheet8 | CC_entropy | 616 | 616 | 0 | 0 | 5.05119697 | 5.051281 | 0.994854109 | 0.994759575 | 67.1568821 |
| 3 | Sheet8 | dV_energy | 616 | 616 | 0 | 0 | 0.00560213468 | 0.00594937117 | 0.999000265 | 0.998032414 | 0.628136307 |
| 3 | Sheet8 | dV_Q | 616 | 616 | 0 | 0 | 0.00142169169 | 0.00150952452 | 0.999003691 | 0.998057671 | 0.629123518 |
| 3 | Sheet8 | dV_t_mean | 616 | 616 | 0 | 0 | 0.0106642874 | 0.0113680164 | 0.998923438 | 0.997994051 | 0.629245797 |
| 3 | Sheet8 | dV_V_mean | 616 | 616 | 0 | 0 | 9.92643429e-05 | 0.000123408489 | 0.947445697 | 0.942704296 | 0.00251512462 |
| 3 | Sheet8 | dV_T_mean | 616 | 616 | 0 | 0 | 0.00612410858 | 0.00780364359 | 0.9999931 | 0.999968684 | 0.0220127289 |
| 3 | Sheet8 | dV_V_std | 616 | 616 | 0 | 0 | 0.000138867912 | 0.000153066314 | 0.579967711 | 0.562599263 | 0.480954205 |
| 3 | Sheet8 | dV_T_std | 616 | 616 | 0 | 0 | 0.00845744573 | 0.0197877608 | 0.941402273 | 0.982638076 | 6.79548027 |
| 3 | Sheet8 | dV_V_skewness | 616 | 616 | 0 | 0 | 0.00176850388 | 0.00231361508 | 0.988150046 | 0.986274693 | 1.2561718 |
| 3 | Sheet8 | dV_T_skewness | 616 | 616 | 0 | 0 | 0.177730334 | 0.39540387 | 0.705581815 | 0.82730053 | 62.3475593 |
| 3 | Sheet8 | dV_V_kurtosis | 616 | 616 | 0 | 0 | 0.00173154158 | 0.00219476281 | 0.950783347 | 0.943573464 | 0.0953291138 |
| 3 | Sheet8 | dV_T_kurtosis | 616 | 616 | 0 | 0 | 0.368661517 | 1.1804223 | 0.691811258 | 0.776810732 | 16.3495591 |
| 3 | Sheet8 | dV_dV_devide_dt | 616 | 616 | 0 | 0 | 3.2140658e-05 | 4.02853786e-05 | 0.99966379 | 0.999419313 | 0.109407879 |
| 3 | Sheet8 | dV_entropy | 616 | 616 | 0 | 0 | 4.80937771 | 4.80967527 | -0.757015848 | -0.779399103 | 63.493168 |
| 3 | Sheet8 | CV_energy | 616 | 616 | 0 | 0 | 0.0359147794 | 0.0418225301 | 0.990414655 | 0.98516661 | 2.46158474 |
| 3 | Sheet8 | CV_Q | 616 | 616 | 0 | 0 | 0.00855124336 | 0.00995782689 | 0.990414011 | 0.985167791 | 2.46150954 |
| 3 | Sheet8 | CV_t_mean | 616 | 616 | 0 | 0 | 0.0714593742 | 0.0821900774 | 0.999822784 | 0.998529727 | 0.489039958 |
| 3 | Sheet8 | CV_C_mean | 616 | 616 | 0 | 0 | 0.0114403864 | 0.0135320822 | 0.961129026 | 0.939840667 | 1.59277434 |
| 3 | Sheet8 | CV_T_mean | 616 | 616 | 0 | 0 | 0.0164719634 | 0.0195225859 | 0.999986099 | 0.99992135 | 0.067474496 |
| 3 | Sheet8 | CV_C_std | 616 | 616 | 0 | 0 | 0.0205710768 | 0.0241756147 | 0.749630268 | 0.696448991 | 2.49227121 |
| 3 | Sheet8 | CV_T_std | 616 | 616 | 0 | 0 | 0.0121712935 | 0.0214599136 | 0.994181476 | 0.998197979 | 0.593003586 |
| 3 | Sheet8 | CV_C_skewness | 616 | 616 | 0 | 0 | 0.0204657296 | 0.0240304466 | 0.99165827 | 0.989045259 | 1.04745305 |
| 3 | Sheet8 | CV_T_skewness | 616 | 616 | 0 | 0 | 0.00949161789 | 0.0159137173 | 0.993280259 | 0.997286984 | 1.23672349 |
| 3 | Sheet8 | CV_C_kurtosis | 616 | 616 | 0 | 0 | 0.0961971016 | 0.11242666 | 0.991706211 | 0.988969176 | 1.51233787 |
| 3 | Sheet8 | CV_T_kurtosis | 616 | 616 | 0 | 0 | 0.0205686716 | 0.0247471985 | 0.995930057 | 0.99315303 | 0.934051983 |
| 3 | Sheet8 | CV_CVCT | 616 | 616 | 0 | 0 | 0.135087368 | 0.156941134 | 0.999827558 | 0.998599046 | 0.462369555 |
| 3 | Sheet8 | CV_entropy | 616 | 616 | 0 | 0 | 4.71509238 | 4.71517523 | 0.975273777 | 0.958433392 | 71.6468933 |
| 3 | Sheet8 | dI_energy | 616 | 616 | 0 | 0 | 0.000952935716 | 0.00119813608 | 0.995051859 | 0.99653144 | 1.91427883 |
| 3 | Sheet8 | dI_Q | 616 | 616 | 0 | 0 | 0.000226901167 | 0.000285282808 | 0.995051817 | 0.996529489 | 1.91429482 |
| 3 | Sheet8 | dI_t_mean | 616 | 616 | 0 | 0 | 0.00721531273 | 0.0090826445 | 0.994951011 | 0.996254484 | 1.92454002 |
| 3 | Sheet8 | dI_C_mean | 616 | 616 | 0 | 0 | 0.000436382489 | 0.000549146305 | 0.867346017 | 0.855087783 | 0.0460072001 |
| 3 | Sheet8 | dI_T_mean | 616 | 616 | 0 | 0 | 0.0143869696 | 0.017727674 | 0.999964274 | 0.999838991 | 0.0549875987 |
| 3 | Sheet8 | dI_C_std | 616 | 616 | 0 | 0 | 0.000236972128 | 0.000295303432 | 0.122349109 | 0.091885748 | 0.819742904 |
| 3 | Sheet8 | dI_T_std | 616 | 616 | 0 | 0 | 0.0125805386 | 0.0155363376 | 0.783099598 | 0.756174161 | 11.6743636 |
| 3 | Sheet8 | dI_C_skewness | 616 | 616 | 0 | 0 | 0.00771706418 | 0.0105030134 | 0.964742989 | 0.956110087 | 11.7180075 |
| 3 | Sheet8 | dI_T_skewness | 616 | 616 | 0 | 0 | 0.241461557 | 0.297097986 | 0.462893421 | 0.443901777 | 95.7870552 |
| 3 | Sheet8 | dI_C_kurtosis | 616 | 616 | 0 | 0 | 0.0112295924 | 0.0148140853 | 0.42477173 | 0.44105312 | 0.621437211 |
| 3 | Sheet8 | dI_T_kurtosis | 616 | 616 | 0 | 0 | 0.268884045 | 0.360948723 | 0.345119828 | 0.350074107 | 13.1415532 |
| 3 | Sheet8 | dI_dI_devide_dt | 616 | 616 | 0 | 0 | 0.00092744639 | 0.0020651439 | 0.995771756 | 0.999093056 | 0.694770871 |
| 3 | Sheet8 | dI_entropy | 616 | 616 | 0 | 0 | 2.70606871 | 2.71546233 | -0.17332306 | -0.0720951694 | 49.4183731 |
| 3 | Sheet8 | Charge_energy | 616 | 616 | 0 | 0 | 0.00218865172 | 0.0124313531 | 0.999424631 | 0.999978695 | 0.0296891886 |
| 3 | Sheet8 | Charge_Q | 616 | 616 | 0 | 0 | 0.0002241835 | 0.00133461794 | 0.999914367 | 0.999989347 | 0.0119389951 |
| 3 | Sheet8 | Charge_t_mean | 616 | 616 | 0 | 0 | 0.006929904 | 0.0148462819 | 0.999928522 | 0.999538521 | 0.0265626716 |
| 3 | Sheet8 | Charge_V_mean | 616 | 616 | 0 | 0 | 0.00126683898 | 0.00128354791 | 0.99997535 | 0.999915241 | 0.0312764142 |
| 3 | Sheet8 | Charge_C_mean | 616 | 616 | 0 | 0 | 0.000868891917 | 0.00172657328 | 0.999969659 | 0.999822267 | 0.040073966 |
| 3 | Sheet8 | Charge_T_mean | 616 | 616 | 0 | 0 | 0.00618097913 | 0.00736343857 | 0.999995186 | 0.999981672 | 0.0239865591 |
| 3 | Sheet8 | Charge_C_std | 616 | 616 | 0 | 0 | 0.000790931826 | 0.00192443801 | 0.991858642 | 0.999631854 | 0.0456689061 |
| 3 | Sheet8 | Charge_V_std | 616 | 616 | 0 | 0 | 0.00272910179 | 0.00279616546 | 0.999472138 | 0.999305857 | 1.37986375 |
| 3 | Sheet8 | Charge_T_std | 616 | 616 | 0 | 0 | 0.0132066339 | 0.0844667705 | 0.983213561 | 0.998201214 | 0.563913224 |
| 3 | Sheet8 | Charge_C_skewness | 616 | 616 | 0 | 0 | 0.00110773069 | 0.00203064756 | 0.999971029 | 0.999842187 | 0.584717053 |
| 3 | Sheet8 | Charge_V_skewness | 616 | 616 | 0 | 0 | 0.0516336958 | 0.0556704492 | 0.997583629 | 0.996271104 | 5.36536593 |
| 3 | Sheet8 | Charge_T_skewness | 616 | 616 | 0 | 0 | 0.00904998002 | 0.0138694213 | 0.999536714 | 0.999554077 | 3.64841036 |
| 3 | Sheet8 | Charge_C_kurtosis | 616 | 616 | 0 | 0 | 0.0019763651 | 0.00911570661 | 0.990743381 | 0.999811844 | 0.168829573 |
| 3 | Sheet8 | Charge_V_kurtosis | 616 | 616 | 0 | 0 | 0.261415561 | 0.299016262 | 0.98797313 | 0.9912624 | 9.98004409 |
| 3 | Sheet8 | Charge_T_kurtosis | 616 | 616 | 0 | 0 | 0.0334921621 | 0.174850069 | 0.919477356 | 0.989676873 | 1.91209227 |
| 4 | Sheet1 | CC_energy | 798 | 798 | 0 | 0 | 0.0584465137 | 0.0674934359 | 0.998104886 | 0.996975588 | 1.03112255 |
| 4 | Sheet1 | CC_Q | 798 | 798 | 0 | 0 | 0.0141187178 | 0.0164040711 | 0.998409252 | 0.99744015 | 0.965257779 |
| 4 | Sheet1 | CC_t_mean | 798 | 798 | 0 | 0 | 0.106163104 | 0.123192669 | 0.998401232 | 0.997442729 | 0.967748181 |
| 4 | Sheet1 | CC_V_mean | 798 | 798 | 0 | 0 | 0.00284225038 | 0.0032795905 | 0.995458383 | 0.993924161 | 0.0733105334 |
| 4 | Sheet1 | CC_T_mean | 798 | 798 | 0 | 0 | 0.0136485825 | 0.0171584216 | 0.999980419 | 0.999946963 | 0.0492746983 |
| 4 | Sheet1 | CC_V_std | 798 | 798 | 0 | 0 | 0.00175075556 | 0.00222814807 | 0.97467418 | 0.975261928 | 1.1778683 |
| 4 | Sheet1 | CC_T_std | 798 | 798 | 0 | 0 | 0.0080956604 | 0.0105545052 | 0.999768735 | 0.999114893 | 0.666358371 |
| 4 | Sheet1 | CC_V_skewness | 798 | 798 | 0 | 0 | 0.0415942439 | 0.0508159199 | 0.861843948 | 0.855032114 | 10.7218754 |
| 4 | Sheet1 | CC_T_skewness | 798 | 798 | 0 | 0 | 0.0175048907 | 0.0301915687 | 0.999344676 | 0.999536123 | 2.89324809 |
| 4 | Sheet1 | CC_V_kurtosis | 798 | 798 | 0 | 0 | 0.0491837338 | 0.065171836 | 0.845593274 | 0.925585749 | 2.09792401 |
| 4 | Sheet1 | CC_T_kurtosis | 798 | 798 | 0 | 0 | 0.049653736 | 0.188952328 | 0.985621624 | 0.992658298 | 1.97891615 |
| 4 | Sheet1 | CC_CCCT | 798 | 798 | 0 | 0 | 0.211754643 | 0.246039136 | 0.99840915 | 0.997440946 | 0.965155489 |
| 4 | Sheet1 | CC_entropy | 798 | 798 | 0 | 0 | 5.09044311 | 5.09094154 | 0.90343332 | 0.944965489 | 66.1118823 |
| 4 | Sheet1 | dV_energy | 798 | 798 | 0 | 0 | 0.0037530877 | 0.00421175928 | 0.999236335 | 0.998817354 | 0.419661372 |
| 4 | Sheet1 | dV_Q | 798 | 798 | 0 | 0 | 0.000950205427 | 0.00106656419 | 0.999238857 | 0.998851122 | 0.419311828 |
| 4 | Sheet1 | dV_t_mean | 798 | 798 | 0 | 0 | 0.00714336936 | 0.00805850738 | 0.999147748 | 0.998741292 | 0.420297744 |
| 4 | Sheet1 | dV_V_mean | 798 | 798 | 0 | 0 | 9.77329978e-05 | 0.00011995118 | 0.963539595 | 0.957332392 | 0.00247643698 |
| 4 | Sheet1 | dV_T_mean | 798 | 798 | 0 | 0 | 0.00612106851 | 0.00789263089 | 0.999990936 | 0.999959242 | 0.0217334559 |
| 4 | Sheet1 | dV_V_std | 798 | 798 | 0 | 0 | 9.10485345e-05 | 0.000107607729 | 0.566066679 | 0.555104511 | 0.314738493 |
| 4 | Sheet1 | dV_T_std | 798 | 798 | 0 | 0 | 0.00683451445 | 0.00935778136 | 0.992953653 | 0.993721667 | 4.74127197 |
| 4 | Sheet1 | dV_V_skewness | 798 | 798 | 0 | 0 | 0.00180084034 | 0.00238880491 | 0.99207545 | 0.989407118 | 1.23216916 |
| 4 | Sheet1 | dV_T_skewness | 798 | 798 | 0 | 0 | 0.170356446 | 0.429480437 | 0.702440811 | 0.856354915 | 55.7300721 |
| 4 | Sheet1 | dV_V_kurtosis | 798 | 798 | 0 | 0 | 0.00186164426 | 0.00241560697 | 0.959345588 | 0.952175694 | 0.102401847 |
| 4 | Sheet1 | dV_T_kurtosis | 798 | 798 | 0 | 0 | 0.419548746 | 2.29867821 | 0.331190075 | 0.844064301 | 18.6496457 |
| 4 | Sheet1 | dV_dV_devide_dt | 798 | 798 | 0 | 0 | 4.03957116e-05 | 4.9665948e-05 | 0.999722493 | 0.999584927 | 0.137618273 |
| 4 | Sheet1 | dV_entropy | 798 | 798 | 0 | 0 | 4.81103229 | 4.81136664 | -0.856493031 | -0.857870797 | 63.5062424 |
| 4 | Sheet1 | CV_energy | 798 | 798 | 0 | 0 | 0.0317526397 | 0.0371034583 | 0.987723817 | 0.981489702 | 2.23574464 |
| 4 | Sheet1 | CV_Q | 798 | 798 | 0 | 0 | 0.00755987171 | 0.00883376782 | 0.987723817 | 0.981490764 | 2.23566079 |
| 4 | Sheet1 | CV_t_mean | 798 | 798 | 0 | 0 | 0.0636220795 | 0.0734326214 | 0.999742613 | 0.998483331 | 0.463742428 |
| 4 | Sheet1 | CV_C_mean | 798 | 798 | 0 | 0 | 0.0105832077 | 0.0125260007 | 0.94481047 | 0.935330031 | 1.42442969 |
| 4 | Sheet1 | CV_T_mean | 798 | 798 | 0 | 0 | 0.0153257636 | 0.0180872927 | 0.999985307 | 0.999875577 | 0.0617542906 |
| 4 | Sheet1 | CV_C_std | 798 | 798 | 0 | 0 | 0.0182575921 | 0.0214652329 | 0.5850917 | 0.550953465 | 2.14732378 |
| 4 | Sheet1 | CV_T_std | 798 | 798 | 0 | 0 | 0.00892784776 | 0.0106418696 | 0.999550073 | 0.999308812 | 0.406441703 |
| 4 | Sheet1 | CV_C_skewness | 798 | 798 | 0 | 0 | 0.017939709 | 0.020975409 | 0.983720309 | 0.980257908 | 0.976733517 |
| 4 | Sheet1 | CV_T_skewness | 798 | 798 | 0 | 0 | 0.00738266676 | 0.00884380959 | 0.997195852 | 0.996406651 | 1.22309955 |
| 4 | Sheet1 | CV_C_kurtosis | 798 | 798 | 0 | 0 | 0.0861253617 | 0.100156488 | 0.980649033 | 0.976322861 | 1.49007673 |
| 4 | Sheet1 | CV_T_kurtosis | 798 | 798 | 0 | 0 | 0.0145456334 | 0.0173837102 | 0.992826934 | 0.99161122 | 0.740163037 |
| 4 | Sheet1 | CV_CVCT | 798 | 798 | 0 | 0 | 0.119070712 | 0.138850266 | 0.99975306 | 0.998522855 | 0.434088054 |
| 4 | Sheet1 | CV_entropy | 798 | 798 | 0 | 0 | 4.72533475 | 4.72540498 | 0.97279022 | 0.959041529 | 71.3906949 |
| 4 | Sheet1 | dI_energy | 798 | 798 | 0 | 0 | 0.00114321983 | 0.0013773654 | 0.984244463 | 0.986669264 | 2.62038769 |
| 4 | Sheet1 | dI_Q | 798 | 798 | 0 | 0 | 0.000272195014 | 0.000327943905 | 0.984244477 | 0.986669264 | 2.62038583 |
| 4 | Sheet1 | dI_t_mean | 798 | 798 | 0 | 0 | 0.00860813886 | 0.0103845275 | 0.984069705 | 0.986608657 | 2.62133054 |
| 4 | Sheet1 | dI_C_mean | 798 | 798 | 0 | 0 | 0.000533501316 | 0.000656874027 | 0.279202905 | 0.235782157 | 0.0562221224 |
| 4 | Sheet1 | dI_T_mean | 798 | 798 | 0 | 0 | 0.0148751279 | 0.0183124189 | 0.999952591 | 0.99971699 | 0.0559060537 |
| 4 | Sheet1 | dI_C_std | 798 | 798 | 0 | 0 | 0.000293090557 | 0.000366101319 | 0.0433348956 | 0.0403296193 | 1.01568064 |
| 4 | Sheet1 | dI_T_std | 798 | 798 | 0 | 0 | 0.0126128883 | 0.015716203 | 0.777320993 | 0.777991165 | 12.7616375 |
| 4 | Sheet1 | dI_C_skewness | 798 | 798 | 0 | 0 | 0.00884299344 | 0.0114230062 | 0.624198265 | 0.572214818 | 20.3423253 |
| 4 | Sheet1 | dI_T_skewness | 798 | 798 | 0 | 0 | 0.241112671 | 0.298132125 | 0.515149367 | 0.471966 | 95.126993 |
| 4 | Sheet1 | dI_C_kurtosis | 798 | 798 | 0 | 0 | 0.01121984 | 0.0140540937 | 0.0764916236 | 0.0661936396 | 0.623229028 |
| 4 | Sheet1 | dI_T_kurtosis | 798 | 798 | 0 | 0 | 0.313153843 | 0.435534019 | 0.27819427 | 0.302154048 | 15.1187828 |
| 4 | Sheet1 | dI_dI_devide_dt | 798 | 798 | 0 | 0 | 0.00117894103 | 0.00175047071 | 0.993297584 | 0.9946334 | 0.789191338 |
| 4 | Sheet1 | dI_entropy | 798 | 798 | 0 | 0 | 2.53082246 | 2.53538422 | 0.280318617 | 0.239029115 | 47.7320531 |
| 4 | Sheet1 | Charge_energy | 798 | 798 | 0 | 0 | 0.00720629869 | 0.0240643391 | 0.998616908 | 0.99955574 | 0.101578757 |
| 4 | Sheet1 | Charge_Q | 798 | 798 | 0 | 0 | 0.00170916112 | 0.00419361284 | 0.999547803 | 0.999609474 | 0.0948480764 |
| 4 | Sheet1 | Charge_t_mean | 798 | 798 | 0 | 0 | 0.0175635798 | 0.0336309428 | 0.999203621 | 0.999545745 | 0.0711146856 |
| 4 | Sheet1 | Charge_V_mean | 798 | 798 | 0 | 0 | 0.000778816521 | 0.000884166106 | 0.999677809 | 0.999278185 | 0.019205796 |
| 4 | Sheet1 | Charge_C_mean | 798 | 798 | 0 | 0 | 0.00156204506 | 0.00256750618 | 0.999937838 | 0.999638608 | 0.0712354245 |
| 4 | Sheet1 | Charge_T_mean | 798 | 798 | 0 | 0 | 0.00611656401 | 0.00707329389 | 0.999995766 | 0.999985312 | 0.0234562532 |
| 4 | Sheet1 | Charge_C_std | 798 | 798 | 0 | 0 | 0.000696391237 | 0.00131151308 | 0.992714835 | 0.998619968 | 0.040274345 |
| 4 | Sheet1 | Charge_V_std | 798 | 798 | 0 | 0 | 0.00122825364 | 0.00134975869 | 0.998712464 | 0.998679706 | 0.653055402 |
| 4 | Sheet1 | Charge_T_std | 798 | 798 | 0 | 0 | 0.0226532075 | 0.141066925 | 0.963764129 | 0.99777125 | 0.957617879 |
| 4 | Sheet1 | Charge_C_skewness | 798 | 798 | 0 | 0 | 0.00163691022 | 0.00263874059 | 0.999933966 | 0.999641631 | 0.984477637 |
| 4 | Sheet1 | Charge_V_skewness | 798 | 798 | 0 | 0 | 0.0139494434 | 0.0168121896 | 0.99881137 | 0.995800734 | 1.6439128 |
| 4 | Sheet1 | Charge_T_skewness | 798 | 798 | 0 | 0 | 0.00565279157 | 0.00825591298 | 0.999673638 | 0.999534918 | 2.56370816 |
| 4 | Sheet1 | Charge_C_kurtosis | 798 | 798 | 0 | 0 | 0.00105251233 | 0.00262130943 | 0.998304912 | 0.999449458 | 0.089903971 |
| 4 | Sheet1 | Charge_V_kurtosis | 798 | 798 | 0 | 0 | 0.0604732894 | 0.0773601817 | 0.993009624 | 0.985856457 | 2.75722632 |
| 4 | Sheet1 | Charge_T_kurtosis | 798 | 798 | 0 | 0 | 0.0209594904 | 0.102198916 | 0.91989032 | 0.99353037 | 1.21869923 |
| 4 | Sheet2 | CC_energy | 672 | 672 | 0 | 0 | 0.0647099646 | 0.076341737 | 0.996784099 | 0.99508743 | 1.12701252 |
| 4 | Sheet2 | CC_Q | 672 | 672 | 0 | 0 | 0.0158257594 | 0.0187532121 | 0.997332375 | 0.995497298 | 1.06753922 |
| 4 | Sheet2 | CC_t_mean | 672 | 672 | 0 | 0 | 0.11857783 | 0.140738827 | 0.997304276 | 0.995475489 | 1.06652395 |
| 4 | Sheet2 | CC_V_mean | 672 | 672 | 0 | 0 | 0.00275594231 | 0.00324396856 | 0.991142225 | 0.987431001 | 0.0711340063 |
| 4 | Sheet2 | CC_T_mean | 672 | 672 | 0 | 0 | 0.0122447842 | 0.0158634913 | 0.999978811 | 0.999930522 | 0.0449759688 |
| 4 | Sheet2 | CC_V_std | 672 | 672 | 0 | 0 | 0.00223564991 | 0.00312025335 | 0.925033286 | 0.920521176 | 1.46193842 |
| 4 | Sheet2 | CC_T_std | 672 | 672 | 0 | 0 | 0.00923181352 | 0.0115614041 | 0.999670495 | 0.99911051 | 0.800497022 |
| 4 | Sheet2 | CC_V_skewness | 672 | 672 | 0 | 0 | 0.0519575622 | 0.0662178284 | 0.728071295 | 0.790769716 | 15.3168421 |
| 4 | Sheet2 | CC_T_skewness | 672 | 672 | 0 | 0 | 0.0144613043 | 0.0232669448 | 0.99958906 | 0.999394432 | 2.39385539 |
| 4 | Sheet2 | CC_V_kurtosis | 672 | 672 | 0 | 0 | 0.0750535681 | 0.11041969 | 0.765913626 | 0.921085777 | 3.19907927 |
| 4 | Sheet2 | CC_T_kurtosis | 672 | 672 | 0 | 0 | 0.0341871082 | 0.070253333 | 0.998219105 | 0.994369608 | 1.37342978 |
| 4 | Sheet2 | CC_CCCT | 672 | 672 | 0 | 0 | 0.237363072 | 0.281282896 | 0.997332029 | 0.995495961 | 1.06744249 |
| 4 | Sheet2 | CC_entropy | 672 | 672 | 0 | 0 | 5.07543067 | 5.07624438 | 0.837676049 | 0.899815157 | 66.0009118 |
| 4 | Sheet2 | dV_energy | 672 | 672 | 0 | 0 | 0.00532215689 | 0.00565429747 | 0.999053979 | 0.99832925 | 0.599115848 |
| 4 | Sheet2 | dV_Q | 672 | 672 | 0 | 0 | 0.00134956728 | 0.00143377206 | 0.999055936 | 0.998374725 | 0.599575483 |
| 4 | Sheet2 | dV_t_mean | 672 | 672 | 0 | 0 | 0.0101111744 | 0.0107912493 | 0.998982335 | 0.998234178 | 0.598949794 |
| 4 | Sheet2 | dV_V_mean | 672 | 672 | 0 | 0 | 9.52263205e-05 | 0.000117646991 | 0.946638952 | 0.941369255 | 0.00241283236 |
| 4 | Sheet2 | dV_T_mean | 672 | 672 | 0 | 0 | 0.00632632401 | 0.00806189146 | 0.999991433 | 0.999970461 | 0.0228696094 |
| 4 | Sheet2 | dV_V_std | 672 | 672 | 0 | 0 | 0.000131223211 | 0.000145319485 | 0.558906289 | 0.53623531 | 0.454218998 |
| 4 | Sheet2 | dV_T_std | 672 | 672 | 0 | 0 | 0.00725090708 | 0.0108923856 | 0.988153132 | 0.992044177 | 5.0854974 |
| 4 | Sheet2 | dV_V_skewness | 672 | 672 | 0 | 0 | 0.00189493218 | 0.00246144265 | 0.98711571 | 0.984757271 | 1.34149136 |
| 4 | Sheet2 | dV_T_skewness | 672 | 672 | 0 | 0 | 0.17083798 | 0.354083227 | 0.779317731 | 0.868093779 | 50.1559591 |
| 4 | Sheet2 | dV_V_kurtosis | 672 | 672 | 0 | 0 | 0.00172374022 | 0.00221220941 | 0.945812161 | 0.938922595 | 0.0949102393 |
| 4 | Sheet2 | dV_T_kurtosis | 672 | 672 | 0 | 0 | 0.310358358 | 0.953517296 | 0.58561662 | 0.841507264 | 14.0244825 |
| 4 | Sheet2 | dV_dV_devide_dt | 672 | 672 | 0 | 0 | 3.41632224e-05 | 4.24216872e-05 | 0.999668328 | 0.999476721 | 0.115678523 |
| 4 | Sheet2 | dV_entropy | 672 | 672 | 0 | 0 | 4.80553103 | 4.80586381 | -0.852212281 | -0.858015431 | 63.4752436 |
| 4 | Sheet2 | CV_energy | 672 | 672 | 0 | 0 | 0.0365857567 | 0.0492667434 | 0.956065613 | 0.9829845 | 2.55383247 |
| 4 | Sheet2 | CV_Q | 672 | 672 | 0 | 0 | 0.00871055868 | 0.0117298887 | 0.95606545 | 0.982983471 | 2.55373433 |
| 4 | Sheet2 | CV_t_mean | 672 | 672 | 0 | 0 | 0.064662274 | 0.0742562188 | 0.999746767 | 0.998027771 | 0.460719016 |
| 4 | Sheet2 | CV_C_mean | 672 | 672 | 0 | 0 | 0.0116573186 | 0.0169370634 | 0.879446399 | 0.919243913 | 1.58847778 |
| 4 | Sheet2 | CV_T_mean | 672 | 672 | 0 | 0 | 0.0143848141 | 0.016963446 | 0.999987873 | 0.999928229 | 0.0584181689 |
| 4 | Sheet2 | CV_C_std | 672 | 672 | 0 | 0 | 0.0191350423 | 0.0222116374 | 0.676110486 | 0.664003706 | 2.29136283 |
| 4 | Sheet2 | CV_T_std | 672 | 672 | 0 | 0 | 0.00885914833 | 0.0105697968 | 0.999379301 | 0.999206996 | 0.440432333 |
| 4 | Sheet2 | CV_C_skewness | 672 | 672 | 0 | 0 | 0.0198601845 | 0.0230316511 | 0.988637261 | 0.985270703 | 1.04934559 |
| 4 | Sheet2 | CV_T_skewness | 672 | 672 | 0 | 0 | 0.0303591558 | 0.164907355 | 0.402165501 | 0.903597772 | 4.61199117 |
| 4 | Sheet2 | CV_C_kurtosis | 672 | 672 | 0 | 0 | 0.0929280959 | 0.107489571 | 0.987848021 | 0.981807568 | 1.52576189 |
| 4 | Sheet2 | CV_T_kurtosis | 672 | 672 | 0 | 0 | 0.0168858328 | 0.024867697 | 0.98773132 | 0.992161384 | 0.83172002 |
| 4 | Sheet2 | CV_CVCT | 672 | 672 | 0 | 0 | 0.122663165 | 0.141900798 | 0.999750822 | 0.998043192 | 0.437101992 |
| 4 | Sheet2 | CV_entropy | 672 | 672 | 0 | 0 | 4.72179791 | 4.72200411 | 0.818158893 | 0.894977543 | 71.3983317 |
| 4 | Sheet2 | dI_energy | 672 | 672 | 0 | 0 | 0.00150830834 | 0.0067154741 | 0.774289599 | 0.979660004 | 3.02347465 |
| 4 | Sheet2 | dI_Q | 672 | 672 | 0 | 0 | 0.000359120606 | 0.00159892231 | 0.774289283 | 0.979657038 | 3.0234722 |
| 4 | Sheet2 | dI_t_mean | 672 | 672 | 0 | 0 | 0.0112967689 | 0.0501897567 | 0.777316562 | 0.979778623 | 3.00690981 |
| 4 | Sheet2 | dI_C_mean | 672 | 672 | 0 | 0 | 0.000459237236 | 0.000716838162 | 0.848763228 | 0.80846192 | 0.0484123992 |
| 4 | Sheet2 | dI_T_mean | 672 | 672 | 0 | 0 | 0.013893941 | 0.0171785387 | 0.999960418 | 0.999846423 | 0.0528402467 |
| 4 | Sheet2 | dI_C_std | 672 | 672 | 0 | 0 | 0.000286651851 | 0.000364624981 | 0.185731479 | 0.185198276 | 0.994927376 |
| 4 | Sheet2 | dI_T_std | 672 | 672 | 0 | 0 | 0.0123611986 | 0.0171648134 | 0.810853266 | 0.80654402 | 12.2735298 |
| 4 | Sheet2 | dI_C_skewness | 672 | 672 | 0 | 0 | 0.0082515206 | 0.023307766 | 0.909396714 | 0.948123957 | 14.1272512 |
| 4 | Sheet2 | dI_T_skewness | 672 | 672 | 0 | 0 | 0.270890302 | 0.556062434 | 0.313619975 | 0.534023587 | 96.0056408 |
| 4 | Sheet2 | dI_C_kurtosis | 672 | 672 | 0 | 0 | 0.0106689336 | 0.0216733207 | 0.484703186 | 0.555078389 | 0.590097612 |
| 4 | Sheet2 | dI_T_kurtosis | 672 | 672 | 0 | 0 | 0.546493349 | 5.32600727 | 0.0212424446 | 0.385877756 | 25.780327 |
| 4 | Sheet2 | dI_dI_devide_dt | 672 | 672 | 0 | 0 | 0.00155731823 | 0.00725989552 | 0.944417769 | 0.983674902 | 1.17069186 |
| 4 | Sheet2 | dI_entropy | 672 | 672 | 0 | 0 | 2.70822385 | 2.71920467 | -0.261836916 | -0.130331202 | 49.4388 |
| 4 | Sheet2 | Charge_energy | 672 | 672 | 0 | 0 | 0.0174093533 | 0.0501020859 | 0.992564501 | 0.997866928 | 0.242191413 |
| 4 | Sheet2 | Charge_Q | 672 | 672 | 0 | 0 | 0.00461373843 | 0.0125776896 | 0.993964652 | 0.998134855 | 0.252543663 |
| 4 | Sheet2 | Charge_t_mean | 672 | 672 | 0 | 0 | 0.030724625 | 0.0584474908 | 0.998049463 | 0.998519147 | 0.12210849 |
| 4 | Sheet2 | Charge_V_mean | 672 | 672 | 0 | 0 | 0.00101093385 | 0.00122728346 | 0.998838132 | 0.996298379 | 0.0249321686 |
| 4 | Sheet2 | Charge_C_mean | 672 | 672 | 0 | 0 | 0.00241516359 | 0.0042337323 | 0.99979988 | 0.998579402 | 0.110723654 |
| 4 | Sheet2 | Charge_T_mean | 672 | 672 | 0 | 0 | 0.00512992374 | 0.00625035351 | 0.99999645 | 0.999981612 | 0.0199147183 |
| 4 | Sheet2 | Charge_C_std | 672 | 672 | 0 | 0 | 0.00155641551 | 0.00689746568 | 0.87174857 | 0.997566566 | 0.0899507242 |
| 4 | Sheet2 | Charge_V_std | 672 | 672 | 0 | 0 | 0.00151708991 | 0.00171671719 | 0.9942651 | 0.99264761 | 0.796118424 |
| 4 | Sheet2 | Charge_T_std | 672 | 672 | 0 | 0 | 0.0147435297 | 0.100207262 | 0.975804689 | 0.998772621 | 0.677952906 |
| 4 | Sheet2 | Charge_C_skewness | 672 | 672 | 0 | 0 | 0.00254828616 | 0.00433200377 | 0.999794011 | 0.99851293 | 1.65613284 |
| 4 | Sheet2 | Charge_V_skewness | 672 | 672 | 0 | 0 | 0.0163400109 | 0.0191916997 | 0.996684489 | 0.985583848 | 1.8569648 |
| 4 | Sheet2 | Charge_T_skewness | 672 | 672 | 0 | 0 | 0.00598004741 | 0.00882887946 | 0.999562923 | 0.999226056 | 2.92718462 |
| 4 | Sheet2 | Charge_C_kurtosis | 672 | 672 | 0 | 0 | 0.00202871227 | 0.00707263932 | 0.989374122 | 0.998492446 | 0.1744312 |
| 4 | Sheet2 | Charge_V_kurtosis | 672 | 672 | 0 | 0 | 0.0766321749 | 0.0955502068 | 0.981252481 | 0.963749752 | 3.36941975 |
| 4 | Sheet2 | Charge_T_kurtosis | 672 | 672 | 0 | 0 | 0.0186587942 | 0.0924031222 | 0.93931438 | 0.993981608 | 1.08288246 |
| 4 | Sheet3 | CC_energy | 672 | 672 | 0 | 0 | 0.0613328602 | 0.0704812118 | 0.997991606 | 0.996080692 | 1.06864638 |
| 4 | Sheet3 | CC_Q | 672 | 672 | 0 | 0 | 0.0148512552 | 0.0171704296 | 0.998310268 | 0.996681396 | 1.00223339 |
| 4 | Sheet3 | CC_t_mean | 672 | 672 | 0 | 0 | 0.11146178 | 0.128732982 | 0.998317811 | 0.996693496 | 1.00298954 |
| 4 | Sheet3 | CC_V_mean | 672 | 672 | 0 | 0 | 0.00289344898 | 0.0033594946 | 0.994897189 | 0.992369778 | 0.0746715879 |
| 4 | Sheet3 | CC_T_mean | 672 | 672 | 0 | 0 | 0.0110382117 | 0.0140445682 | 0.999985489 | 0.999963225 | 0.0419199338 |
| 4 | Sheet3 | CC_V_std | 672 | 672 | 0 | 0 | 0.00178070676 | 0.00230301201 | 0.97137523 | 0.97269949 | 1.18656553 |
| 4 | Sheet3 | CC_T_std | 672 | 672 | 0 | 0 | 0.00651302421 | 0.00850888243 | 0.999778051 | 0.999252115 | 0.647688349 |
| 4 | Sheet3 | CC_V_skewness | 672 | 672 | 0 | 0 | 0.0410815977 | 0.0499997598 | 0.857910013 | 0.840068793 | 10.725814 |
| 4 | Sheet3 | CC_T_skewness | 672 | 672 | 0 | 0 | 0.0189513113 | 0.03537558 | 0.999164019 | 0.999289721 | 3.00016223 |
| 4 | Sheet3 | CC_V_kurtosis | 672 | 672 | 0 | 0 | 0.0494278161 | 0.0660268153 | 0.820414791 | 0.91211871 | 2.10959997 |
| 4 | Sheet3 | CC_T_kurtosis | 672 | 672 | 0 | 0 | 0.0543493407 | 0.189705475 | 0.987760154 | 0.992956879 | 2.12818194 |
| 4 | Sheet3 | CC_CCCT | 672 | 672 | 0 | 0 | 0.222753492 | 0.257538855 | 0.998310361 | 0.996686881 | 1.00222872 |
| 4 | Sheet3 | CC_entropy | 672 | 672 | 0 | 0 | 5.08731031 | 5.08778826 | 0.893476742 | 0.925937529 | 66.1008812 |
| 4 | Sheet3 | dV_energy | 672 | 672 | 0 | 0 | 0.00374232732 | 0.00422638226 | 0.998940431 | 0.998271042 | 0.420354961 |
| 4 | Sheet3 | dV_Q | 672 | 672 | 0 | 0 | 0.000947093755 | 0.00106977385 | 0.998945558 | 0.998311851 | 0.419835621 |
| 4 | Sheet3 | dV_t_mean | 672 | 672 | 0 | 0 | 0.00713832969 | 0.00808294787 | 0.99882793 | 0.998191155 | 0.421927815 |
| 4 | Sheet3 | dV_V_mean | 672 | 672 | 0 | 0 | 8.83077778e-05 | 0.000108798589 | 0.968567845 | 0.962467298 | 0.00223760193 |
| 4 | Sheet3 | dV_T_mean | 672 | 672 | 0 | 0 | 0.0059851537 | 0.00760858716 | 0.999992906 | 0.999965558 | 0.0223966075 |
| 4 | Sheet3 | dV_V_std | 672 | 672 | 0 | 0 | 9.11611252e-05 | 0.000108486858 | 0.592662139 | 0.578393554 | 0.31508195 |
| 4 | Sheet3 | dV_T_std | 672 | 672 | 0 | 0 | 0.00703680245 | 0.009688398 | 0.988435113 | 0.990502492 | 6.11260578 |
| 4 | Sheet3 | dV_V_skewness | 672 | 672 | 0 | 0 | 0.00177357049 | 0.00232086852 | 0.991991491 | 0.988803909 | 1.22426842 |
| 4 | Sheet3 | dV_T_skewness | 672 | 672 | 0 | 0 | 0.232921893 | 0.484575342 | 0.737688857 | 0.864918598 | 57.5094791 |
| 4 | Sheet3 | dV_V_kurtosis | 672 | 672 | 0 | 0 | 0.00174976189 | 0.00224740814 | 0.963044906 | 0.949863275 | 0.0962857442 |
| 4 | Sheet3 | dV_T_kurtosis | 672 | 672 | 0 | 0 | 0.474181332 | 1.56752037 | 0.511971587 | 0.79635017 | 19.8962473 |
| 4 | Sheet3 | dV_dV_devide_dt | 672 | 672 | 0 | 0 | 4.08224562e-05 | 4.91689185e-05 | 0.999693761 | 0.999520229 | 0.138534888 |
| 4 | Sheet3 | dV_entropy | 672 | 672 | 0 | 0 | 4.81230193 | 4.81260512 | -0.843294181 | -0.847222764 | 63.5112723 |
| 4 | Sheet3 | CV_energy | 672 | 672 | 0 | 0 | 0.0350962566 | 0.0405488146 | 0.987395732 | 0.980364193 | 2.42929897 |
| 4 | Sheet3 | CV_Q | 672 | 672 | 0 | 0 | 0.00835625748 | 0.00965441516 | 0.98739291 | 0.980367278 | 2.42924118 |
| 4 | Sheet3 | CV_t_mean | 672 | 672 | 0 | 0 | 0.0695982982 | 0.0797376329 | 0.99974968 | 0.998287295 | 0.478228961 |
| 4 | Sheet3 | CV_C_mean | 672 | 672 | 0 | 0 | 0.011083024 | 0.013104556 | 0.949630096 | 0.922386203 | 1.55536999 |
| 4 | Sheet3 | CV_T_mean | 672 | 672 | 0 | 0 | 0.013214098 | 0.0156362507 | 0.99999017 | 0.999937719 | 0.0552562858 |
| 4 | Sheet3 | CV_C_std | 672 | 672 | 0 | 0 | 0.0197942898 | 0.0232756169 | 0.668380205 | 0.627836055 | 2.38212679 |
| 4 | Sheet3 | CV_T_std | 672 | 672 | 0 | 0 | 0.0093585129 | 0.0148997193 | 0.996531302 | 0.998463569 | 0.540962486 |
| 4 | Sheet3 | CV_C_skewness | 672 | 672 | 0 | 0 | 0.020010903 | 0.0233777556 | 0.986270372 | 0.976272476 | 1.03781678 |
| 4 | Sheet3 | CV_T_skewness | 672 | 672 | 0 | 0 | 0.0150162964 | 0.059045157 | 0.863866112 | 0.948148909 | 2.1054491 |
| 4 | Sheet3 | CV_C_kurtosis | 672 | 672 | 0 | 0 | 0.0983589148 | 0.114175341 | 0.98540789 | 0.975073282 | 1.58489157 |
| 4 | Sheet3 | CV_T_kurtosis | 672 | 672 | 0 | 0 | 0.0192238407 | 0.0301572064 | 0.986513014 | 0.993143762 | 0.908574624 |
| 4 | Sheet3 | CV_CVCT | 672 | 672 | 0 | 0 | 0.132023399 | 0.152268853 | 0.999757256 | 0.998345571 | 0.453703226 |
| 4 | Sheet3 | CV_entropy | 672 | 672 | 0 | 0 | 4.69178378 | 4.69187964 | 0.973034373 | 0.951361507 | 71.777716 |
| 4 | Sheet3 | dI_energy | 672 | 672 | 0 | 0 | 0.00136999849 | 0.00417599924 | 0.865183893 | 0.99174598 | 2.95207087 |
| 4 | Sheet3 | dI_Q | 672 | 672 | 0 | 0 | 0.000326198333 | 0.000994300185 | 0.865173731 | 0.991728937 | 2.9520743 |
| 4 | Sheet3 | dI_t_mean | 672 | 672 | 0 | 0 | 0.0102316535 | 0.0311918102 | 0.86696486 | 0.991748669 | 2.92789796 |
| 4 | Sheet3 | dI_C_mean | 672 | 672 | 0 | 0 | 0.000524201111 | 0.000759872143 | 0.509901412 | 0.543001837 | 0.055257559 |
| 4 | Sheet3 | dI_T_mean | 672 | 672 | 0 | 0 | 0.0142775949 | 0.0178350312 | 0.999961046 | 0.999795155 | 0.0562228967 |
| 4 | Sheet3 | dI_C_std | 672 | 672 | 0 | 0 | 0.000274919876 | 0.000341365754 | 0.0830261566 | 0.0718303327 | 0.951244798 |
| 4 | Sheet3 | dI_T_std | 672 | 672 | 0 | 0 | 0.012218564 | 0.0148342474 | 0.792382969 | 0.778320536 | 14.3995662 |
| 4 | Sheet3 | dI_C_skewness | 672 | 672 | 0 | 0 | 0.00952011215 | 0.0217629809 | 0.66582412 | 0.818541909 | 19.4556174 |
| 4 | Sheet3 | dI_T_skewness | 672 | 672 | 0 | 0 | 0.263607456 | 0.342380636 | 0.479399146 | 0.492370094 | 96.3793068 |
| 4 | Sheet3 | dI_C_kurtosis | 672 | 672 | 0 | 0 | 0.0108326258 | 0.0143301637 | 0.318007718 | 0.25977486 | 0.600837029 |
| 4 | Sheet3 | dI_T_kurtosis | 672 | 672 | 0 | 0 | 0.378323078 | 0.52853551 | 0.379863674 | 0.254887919 | 17.7511454 |
| 4 | Sheet3 | dI_dI_devide_dt | 672 | 672 | 0 | 0 | 0.00114705681 | 0.00484725688 | 0.967919968 | 0.997332357 | 0.806381211 |
| 4 | Sheet3 | dI_entropy | 672 | 672 | 0 | 0 | 2.61171764 | 2.61946871 | -0.16603828 | 0.116384779 | 48.5214871 |
| 4 | Sheet3 | Charge_energy | 672 | 672 | 0 | 0 | 0.00846282372 | 0.0247356466 | 0.998548663 | 0.99953145 | 0.117701963 |
| 4 | Sheet3 | Charge_Q | 672 | 672 | 0 | 0 | 0.00216080025 | 0.00571154261 | 0.999052316 | 0.999509108 | 0.118262347 |
| 4 | Sheet3 | Charge_t_mean | 672 | 672 | 0 | 0 | 0.0196580485 | 0.0366192753 | 0.99924391 | 0.999383755 | 0.0765648049 |
| 4 | Sheet3 | Charge_V_mean | 672 | 672 | 0 | 0 | 0.000793288846 | 0.000912526193 | 0.99963787 | 0.998766719 | 0.0195498827 |
| 4 | Sheet3 | Charge_C_mean | 672 | 672 | 0 | 0 | 0.00158181478 | 0.0026503497 | 0.999938235 | 0.999429705 | 0.0739380123 |
| 4 | Sheet3 | Charge_T_mean | 672 | 672 | 0 | 0 | 0.00484094444 | 0.00571047633 | 0.999997204 | 0.999984262 | 0.0194035969 |
| 4 | Sheet3 | Charge_C_std | 672 | 672 | 0 | 0 | 0.000957677041 | 0.00304622886 | 0.977354026 | 0.998682501 | 0.055153764 |
| 4 | Sheet3 | Charge_V_std | 672 | 672 | 0 | 0 | 0.00126983713 | 0.00139925977 | 0.998554811 | 0.997891821 | 0.674037077 |
| 4 | Sheet3 | Charge_T_std | 672 | 672 | 0 | 0 | 0.0102588359 | 0.0745447163 | 0.982639673 | 0.998722836 | 0.531822969 |
| 4 | Sheet3 | Charge_C_skewness | 672 | 672 | 0 | 0 | 0.00172532514 | 0.00273596298 | 0.99993667 | 0.999451453 | 1.03045794 |
| 4 | Sheet3 | Charge_V_skewness | 672 | 672 | 0 | 0 | 0.0142850728 | 0.0169417439 | 0.998901346 | 0.994357271 | 1.60265383 |
| 4 | Sheet3 | Charge_T_skewness | 672 | 672 | 0 | 0 | 0.00582390709 | 0.00855579223 | 0.999676304 | 0.999615242 | 2.93456373 |
| 4 | Sheet3 | Charge_C_kurtosis | 672 | 672 | 0 | 0 | 0.0023908792 | 0.00960884506 | 0.987889156 | 0.999297708 | 0.205178386 |
| 4 | Sheet3 | Charge_V_kurtosis | 672 | 672 | 0 | 0 | 0.0643967932 | 0.0818462748 | 0.994194265 | 0.982962276 | 2.83422735 |
| 4 | Sheet3 | Charge_T_kurtosis | 672 | 672 | 0 | 0 | 0.0256344825 | 0.128760225 | 0.901899315 | 0.99073007 | 1.52651403 |
| 4 | Sheet4 | CC_energy | 726 | 726 | 0 | 0 | 0.0648894851 | 0.0765178762 | 0.997366367 | 0.996592743 | 1.14792132 |
| 4 | Sheet4 | CC_Q | 726 | 726 | 0 | 0 | 0.0155877452 | 0.0181026959 | 0.998163288 | 0.997095502 | 1.06949874 |
| 4 | Sheet4 | CC_t_mean | 726 | 726 | 0 | 0 | 0.116885001 | 0.135749323 | 0.998162407 | 0.997100676 | 1.06934315 |
| 4 | Sheet4 | CC_V_mean | 726 | 726 | 0 | 0 | 0.00301186316 | 0.00349298184 | 0.994835831 | 0.9903556 | 0.0776253053 |
| 4 | Sheet4 | CC_T_mean | 726 | 726 | 0 | 0 | 0.0108526546 | 0.0137511398 | 0.999985099 | 0.999952459 | 0.0417789754 |
| 4 | Sheet4 | CC_V_std | 726 | 726 | 0 | 0 | 0.00195041868 | 0.00251715778 | 0.962851634 | 0.964874038 | 1.3098374 |
| 4 | Sheet4 | CC_T_std | 726 | 726 | 0 | 0 | 0.00719321228 | 0.00909976621 | 0.999666925 | 0.99908323 | 0.780586898 |
| 4 | Sheet4 | CC_V_skewness | 726 | 726 | 0 | 0 | 0.0452694381 | 0.0549698229 | 0.83364942 | 0.848904875 | 12.5530729 |
| 4 | Sheet4 | CC_T_skewness | 726 | 726 | 0 | 0 | 0.014915637 | 0.0236200408 | 0.999627625 | 0.999393189 | 2.42629887 |
| 4 | Sheet4 | CC_V_kurtosis | 726 | 726 | 0 | 0 | 0.0572855581 | 0.0759398462 | 0.815730513 | 0.920764205 | 2.45364051 |
| 4 | Sheet4 | CC_T_kurtosis | 726 | 726 | 0 | 0 | 0.0379769146 | 0.18333008 | 0.989068267 | 0.986181527 | 1.51554952 |
| 4 | Sheet4 | CC_CCCT | 726 | 726 | 0 | 0 | 0.23379161 | 0.2715178 | 0.998163124 | 0.997096496 | 1.06943949 |
| 4 | Sheet4 | CC_entropy | 726 | 726 | 0 | 0 | 5.08459743 | 5.08520924 | 0.898693551 | 0.941562181 | 66.0630703 |
| 4 | Sheet4 | dV_energy | 726 | 726 | 0 | 0 | 0.00512637784 | 0.00549503268 | 0.99922723 | 0.998734698 | 0.564255779 |
| 4 | Sheet4 | dV_Q | 726 | 726 | 0 | 0 | 0.00130197639 | 0.00139521913 | 0.999229484 | 0.998755521 | 0.565564325 |
| 4 | Sheet4 | dV_t_mean | 726 | 726 | 0 | 0 | 0.00971456833 | 0.0104876789 | 0.99914571 | 0.998669062 | 0.562663664 |
| 4 | Sheet4 | dV_V_mean | 726 | 726 | 0 | 0 | 0.00010234149 | 0.000127141131 | 0.957639887 | 0.954649066 | 0.0025931877 |
| 4 | Sheet4 | dV_T_mean | 726 | 726 | 0 | 0 | 0.00570993309 | 0.00731712066 | 0.99999324 | 0.999958127 | 0.0216781091 |
| 4 | Sheet4 | dV_V_std | 726 | 726 | 0 | 0 | 0.000123935358 | 0.000138976098 | 0.635806367 | 0.609925666 | 0.429110802 |
| 4 | Sheet4 | dV_T_std | 726 | 726 | 0 | 0 | 0.00673397623 | 0.0103412536 | 0.983890123 | 0.99100032 | 5.89601641 |
| 4 | Sheet4 | dV_V_skewness | 726 | 726 | 0 | 0 | 0.00193174458 | 0.00255773941 | 0.989048581 | 0.985348456 | 1.31142477 |
| 4 | Sheet4 | dV_T_skewness | 726 | 726 | 0 | 0 | 0.236030572 | 0.665998146 | 0.609017497 | 0.855728213 | 63.6131877 |
| 4 | Sheet4 | dV_V_kurtosis | 726 | 726 | 0 | 0 | 0.00167308266 | 0.00218503289 | 0.964755357 | 0.94945211 | 0.0919784646 |
| 4 | Sheet4 | dV_T_kurtosis | 726 | 726 | 0 | 0 | 0.731540745 | 4.53942772 | 0.291696126 | 0.759075046 | 29.6819787 |
| 4 | Sheet4 | dV_dV_devide_dt | 726 | 726 | 0 | 0 | 3.13752217e-05 | 3.89293118e-05 | 0.999708589 | 0.999562641 | 0.108644771 |
| 4 | Sheet4 | dV_entropy | 726 | 726 | 0 | 0 | 4.8275787 | 4.82792519 | -0.838287903 | -0.841937692 | 63.5864788 |
| 4 | Sheet4 | CV_energy | 726 | 726 | 0 | 0 | 0.0352493799 | 0.0412019305 | 0.988947999 | 0.981665068 | 2.33897652 |
| 4 | Sheet4 | CV_Q | 726 | 726 | 0 | 0 | 0.00839253757 | 0.00980969487 | 0.988944939 | 0.981664284 | 2.33889894 |
| 4 | Sheet4 | CV_t_mean | 726 | 726 | 0 | 0 | 0.0698831254 | 0.08068541 | 0.999792739 | 0.998457102 | 0.449025673 |
| 4 | Sheet4 | CV_C_mean | 726 | 726 | 0 | 0 | 0.0103819429 | 0.0123708764 | 0.950788617 | 0.929554743 | 1.49318158 |
| 4 | Sheet4 | CV_T_mean | 726 | 726 | 0 | 0 | 0.0120967607 | 0.0143612078 | 0.999990856 | 0.999937124 | 0.0512864879 |
| 4 | Sheet4 | CV_C_std | 726 | 726 | 0 | 0 | 0.0189658768 | 0.0224537792 | 0.695678983 | 0.649500538 | 2.31073822 |
| 4 | Sheet4 | CV_T_std | 726 | 726 | 0 | 0 | 0.00843177308 | 0.0101803741 | 0.998985624 | 0.998652065 | 0.510522876 |
| 4 | Sheet4 | CV_C_skewness | 726 | 726 | 0 | 0 | 0.0194386051 | 0.0228051168 | 0.98728184 | 0.978291389 | 0.978709073 |
| 4 | Sheet4 | CV_T_skewness | 726 | 726 | 0 | 0 | 0.00908284446 | 0.0180847628 | 0.988238586 | 0.996059212 | 1.14372078 |
| 4 | Sheet4 | CV_C_kurtosis | 726 | 726 | 0 | 0 | 0.0965121462 | 0.11270291 | 0.986720112 | 0.977376595 | 1.48972935 |
| 4 | Sheet4 | CV_T_kurtosis | 726 | 726 | 0 | 0 | 0.0206981958 | 0.0310379666 | 0.989634315 | 0.993747122 | 0.919989731 |
| 4 | Sheet4 | CV_CVCT | 726 | 726 | 0 | 0 | 0.132651208 | 0.154580292 | 0.999798871 | 0.998472851 | 0.426266662 |
| 4 | Sheet4 | CV_entropy | 726 | 726 | 0 | 0 | 4.67457146 | 4.67466016 | 0.973692716 | 0.955289813 | 72.0512707 |
| 4 | Sheet4 | dI_energy | 726 | 726 | 0 | 0 | 0.0012741014 | 0.002604274 | 0.948091006 | 0.993580445 | 2.59628578 |
| 4 | Sheet4 | dI_Q | 726 | 726 | 0 | 0 | 0.000303360553 | 0.000620067452 | 0.948083028 | 0.99358217 | 2.596279 |
| 4 | Sheet4 | dI_t_mean | 726 | 726 | 0 | 0 | 0.00955771745 | 0.0195658226 | 0.948414804 | 0.993794726 | 2.58618627 |
| 4 | Sheet4 | dI_C_mean | 726 | 726 | 0 | 0 | 0.000428616208 | 0.000531202344 | 0.810534326 | 0.725241039 | 0.0451858238 |
| 4 | Sheet4 | dI_T_mean | 726 | 726 | 0 | 0 | 0.0142963844 | 0.0176344218 | 0.999960827 | 0.999686356 | 0.0570964762 |
| 4 | Sheet4 | dI_C_std | 726 | 726 | 0 | 0 | 0.000252044183 | 0.000308512437 | 0.153592599 | 0.111252989 | 0.874284938 |
| 4 | Sheet4 | dI_T_std | 726 | 726 | 0 | 0 | 0.0115092663 | 0.0141825014 | 0.788460561 | 0.783256999 | 13.7988403 |
| 4 | Sheet4 | dI_C_skewness | 726 | 726 | 0 | 0 | 0.00637409572 | 0.00932647271 | 0.961895829 | 0.912824676 | 11.4228988 |
| 4 | Sheet4 | dI_T_skewness | 726 | 726 | 0 | 0 | 0.261204672 | 0.335006593 | 0.504005554 | 0.502110313 | 93.680933 |
| 4 | Sheet4 | dI_C_kurtosis | 726 | 726 | 0 | 0 | 0.00995795097 | 0.0127888559 | 0.404728525 | 0.354766473 | 0.551516311 |
| 4 | Sheet4 | dI_T_kurtosis | 726 | 726 | 0 | 0 | 0.35145623 | 0.45635084 | 0.305435709 | 0.327163758 | 16.6514549 |
| 4 | Sheet4 | dI_dI_devide_dt | 726 | 726 | 0 | 0 | 0.00100760599 | 0.00319847449 | 0.985076599 | 0.998592249 | 0.751349069 |
| 4 | Sheet4 | dI_entropy | 726 | 726 | 0 | 0 | 2.69399312 | 2.70123686 | -0.301393168 | -0.131599567 | 49.300567 |
| 4 | Sheet4 | Charge_energy | 726 | 726 | 0 | 0 | 0.011651985 | 0.0443491502 | 0.995047872 | 0.999259722 | 0.162558916 |
| 4 | Sheet4 | Charge_Q | 726 | 726 | 0 | 0 | 0.00295502942 | 0.0106323744 | 0.996300965 | 0.999365185 | 0.162520468 |
| 4 | Sheet4 | Charge_t_mean | 726 | 726 | 0 | 0 | 0.0210703966 | 0.0391319851 | 0.999458262 | 0.999509855 | 0.0795038413 |
| 4 | Sheet4 | Charge_V_mean | 726 | 726 | 0 | 0 | 0.0008321675 | 0.000934994444 | 0.999610676 | 0.999026281 | 0.0204650243 |
| 4 | Sheet4 | Charge_C_mean | 726 | 726 | 0 | 0 | 0.0016191287 | 0.00276669863 | 0.999929776 | 0.999660688 | 0.0784602961 |
| 4 | Sheet4 | Charge_T_mean | 726 | 726 | 0 | 0 | 0.00437713371 | 0.00522519913 | 0.999997493 | 0.999980337 | 0.017824046 |
| 4 | Sheet4 | Charge_C_std | 726 | 726 | 0 | 0 | 0.00084043006 | 0.00242768831 | 0.993598214 | 0.999123511 | 0.0484371216 |
| 4 | Sheet4 | Charge_V_std | 726 | 726 | 0 | 0 | 0.00132857921 | 0.00146370666 | 0.998512135 | 0.997638487 | 0.722793592 |
| 4 | Sheet4 | Charge_T_std | 726 | 726 | 0 | 0 | 0.0144644722 | 0.0899463208 | 0.967434948 | 0.998154002 | 0.7823191 |
| 4 | Sheet4 | Charge_C_skewness | 726 | 726 | 0 | 0 | 0.00193163871 | 0.0029277649 | 0.999928833 | 0.999655796 | 1.01771813 |
| 4 | Sheet4 | Charge_V_skewness | 726 | 726 | 0 | 0 | 0.0148434899 | 0.0183326709 | 0.998824164 | 0.994780958 | 1.52093752 |
| 4 | Sheet4 | Charge_T_skewness | 726 | 726 | 0 | 0 | 0.00581101636 | 0.00872399262 | 0.999549279 | 0.999218328 | 3.37427196 |
| 4 | Sheet4 | Charge_C_kurtosis | 726 | 726 | 0 | 0 | 0.0033281065 | 0.0144450012 | 0.9900081 | 0.998830847 | 0.282248396 |
| 4 | Sheet4 | Charge_V_kurtosis | 726 | 726 | 0 | 0 | 0.0731274176 | 0.0975239173 | 0.994159826 | 0.983305212 | 2.98149468 |
| 4 | Sheet4 | Charge_T_kurtosis | 726 | 726 | 0 | 0 | 0.0211592196 | 0.0990350784 | 0.903782705 | 0.984309916 | 1.30839719 |
| 4 | Sheet5 | CC_energy | 738 | 738 | 0 | 0 | 0.0625186282 | 0.0738003479 | 0.997166213 | 0.996117715 | 1.10601838 |
| 4 | Sheet5 | CC_Q | 738 | 738 | 0 | 0 | 0.0151438444 | 0.0177867266 | 0.99781303 | 0.996684656 | 1.03889983 |
| 4 | Sheet5 | CC_t_mean | 738 | 738 | 0 | 0 | 0.113799097 | 0.133673487 | 0.997799588 | 0.996664504 | 1.04094151 |
| 4 | Sheet5 | CC_V_mean | 738 | 738 | 0 | 0 | 0.00281663794 | 0.00332168609 | 0.993617854 | 0.989530667 | 0.0726093481 |
| 4 | Sheet5 | CC_T_mean | 738 | 738 | 0 | 0 | 0.0117679777 | 0.0150690462 | 0.999981123 | 0.999941515 | 0.0447160972 |
| 4 | Sheet5 | CC_V_std | 738 | 738 | 0 | 0 | 0.00198423132 | 0.00267008082 | 0.950422039 | 0.956017553 | 1.3206445 |
| 4 | Sheet5 | CC_T_std | 738 | 738 | 0 | 0 | 0.00852360919 | 0.0108702116 | 0.999626758 | 0.99892732 | 0.800982981 |
| 4 | Sheet5 | CC_V_skewness | 738 | 738 | 0 | 0 | 0.0488219382 | 0.0589635918 | 0.791611342 | 0.812905355 | 14.2805814 |
| 4 | Sheet5 | CC_T_skewness | 738 | 738 | 0 | 0 | 0.0125363606 | 0.0174086494 | 0.99979481 | 0.999426312 | 2.04022708 |
| 4 | Sheet5 | CC_V_kurtosis | 738 | 738 | 0 | 0 | 0.0671530133 | 0.0905182844 | 0.790777574 | 0.919480007 | 2.86882164 |
| 4 | Sheet5 | CC_T_kurtosis | 738 | 738 | 0 | 0 | 0.0451003752 | 0.30132906 | 0.972480893 | 0.979660131 | 1.80619902 |
| 4 | Sheet5 | CC_CCCT | 738 | 738 | 0 | 0 | 0.227130871 | 0.266776967 | 0.997812927 | 0.99668864 | 1.03882638 |
| 4 | Sheet5 | CC_entropy | 738 | 738 | 0 | 0 | 5.0775676 | 5.07830286 | 0.871016683 | 0.924373101 | 66.0465646 |
| 4 | Sheet5 | dV_energy | 738 | 738 | 0 | 0 | 0.00507290397 | 0.00544580848 | 0.999087394 | 0.998506219 | 0.561074113 |
| 4 | Sheet5 | dV_Q | 738 | 738 | 0 | 0 | 0.00128868154 | 0.00138287087 | 0.9990913 | 0.998559823 | 0.562507617 |
| 4 | Sheet5 | dV_t_mean | 738 | 738 | 0 | 0 | 0.00964142682 | 0.0104118638 | 0.999005022 | 0.99839301 | 0.561147469 |
| 4 | Sheet5 | dV_V_mean | 738 | 738 | 0 | 0 | 0.000103659223 | 0.000129173638 | 0.950678716 | 0.941682974 | 0.00262654619 |
| 4 | Sheet5 | dV_T_mean | 738 | 738 | 0 | 0 | 0.00593098686 | 0.00760835523 | 0.999991973 | 0.999945635 | 0.022180448 |
| 4 | Sheet5 | dV_V_std | 738 | 738 | 0 | 0 | 0.000121566637 | 0.000137247319 | 0.600758269 | 0.568879616 | 0.420834219 |
| 4 | Sheet5 | dV_T_std | 738 | 738 | 0 | 0 | 0.00639123894 | 0.00860967039 | 0.991390428 | 0.992292698 | 4.92619024 |
| 4 | Sheet5 | dV_V_skewness | 738 | 738 | 0 | 0 | 0.00185877188 | 0.00260157375 | 0.985855972 | 0.982893785 | 1.27569792 |
| 4 | Sheet5 | dV_T_skewness | 738 | 738 | 0 | 0 | 0.232162785 | 0.963380907 | 0.434685504 | 0.870718328 | 64.1629855 |
| 4 | Sheet5 | dV_V_kurtosis | 738 | 738 | 0 | 0 | 0.00173909337 | 0.00221850959 | 0.953658242 | 0.938531526 | 0.095646463 |
| 4 | Sheet5 | dV_T_kurtosis | 738 | 738 | 0 | 0 | 1.09697754 | 11.0495961 | 0.238416969 | 0.812121263 | 47.9679448 |
| 4 | Sheet5 | dV_dV_devide_dt | 738 | 738 | 0 | 0 | 3.20597336e-05 | 4.02719739e-05 | 0.999635994 | 0.999494194 | 0.110522762 |
| 4 | Sheet5 | dV_entropy | 738 | 738 | 0 | 0 | 4.82779261 | 4.8281326 | -0.798323039 | -0.810232204 | 63.5857201 |
| 4 | Sheet5 | CV_energy | 738 | 738 | 0 | 0 | 0.033244477 | 0.0385685784 | 0.989720757 | 0.986134007 | 2.27221122 |
| 4 | Sheet5 | CV_Q | 738 | 738 | 0 | 0 | 0.00791503582 | 0.00918255417 | 0.989720716 | 0.986131588 | 2.27211983 |
| 4 | Sheet5 | CV_t_mean | 738 | 738 | 0 | 0 | 0.0659063107 | 0.0757173296 | 0.999795334 | 0.998590439 | 0.457350623 |
| 4 | Sheet5 | CV_C_mean | 738 | 738 | 0 | 0 | 0.0107063313 | 0.0126207695 | 0.956094175 | 0.934649718 | 1.46811635 |
| 4 | Sheet5 | CV_T_mean | 738 | 738 | 0 | 0 | 0.013503448 | 0.0159656869 | 0.999988963 | 0.999910078 | 0.0568479596 |
| 4 | Sheet5 | CV_C_std | 738 | 738 | 0 | 0 | 0.0187958407 | 0.0218855321 | 0.711502133 | 0.677847094 | 2.24813788 |
| 4 | Sheet5 | CV_T_std | 738 | 738 | 0 | 0 | 0.00908933927 | 0.0108270798 | 0.999277601 | 0.999144633 | 0.487283231 |
| 4 | Sheet5 | CV_C_skewness | 738 | 738 | 0 | 0 | 0.0184833364 | 0.021365235 | 0.990908158 | 0.981620421 | 0.969927686 |
| 4 | Sheet5 | CV_T_skewness | 738 | 738 | 0 | 0 | 0.0082121243 | 0.00972090153 | 0.997801405 | 0.996700307 | 1.11190418 |
| 4 | Sheet5 | CV_C_kurtosis | 738 | 738 | 0 | 0 | 0.0875439144 | 0.10085585 | 0.990522438 | 0.980179513 | 1.43168156 |
| 4 | Sheet5 | CV_T_kurtosis | 738 | 738 | 0 | 0 | 0.0190694747 | 0.0266632152 | 0.991159249 | 0.993285458 | 0.885507604 |
| 4 | Sheet5 | CV_CVCT | 738 | 738 | 0 | 0 | 0.124619879 | 0.144354357 | 0.999802181 | 0.998612113 | 0.432506093 |
| 4 | Sheet5 | CV_entropy | 738 | 738 | 0 | 0 | 4.72274758 | 4.72281938 | 0.974401284 | 0.96141678 | 71.5374207 |
| 4 | Sheet5 | dI_energy | 738 | 738 | 0 | 0 | 0.000884857108 | 0.0010786284 | 0.994249501 | 0.992894189 | 1.83789262 |
| 4 | Sheet5 | dI_Q | 738 | 738 | 0 | 0 | 0.000210680264 | 0.000256816285 | 0.994249501 | 0.992894189 | 1.83789262 |
| 4 | Sheet5 | dI_t_mean | 738 | 738 | 0 | 0 | 0.00664253616 | 0.00811396547 | 0.994255706 | 0.992354408 | 1.8321283 |
| 4 | Sheet5 | dI_C_mean | 738 | 738 | 0 | 0 | 0.000465149393 | 0.000575462783 | 0.797181587 | 0.735161123 | 0.0490407516 |
| 4 | Sheet5 | dI_T_mean | 738 | 738 | 0 | 0 | 0.0137003265 | 0.0171330812 | 0.9999606 | 0.999656917 | 0.0541872748 |
| 4 | Sheet5 | dI_C_std | 738 | 738 | 0 | 0 | 0.000234779591 | 0.000290570741 | 0.140607941 | 0.127030253 | 0.810167997 |
| 4 | Sheet5 | dI_T_std | 738 | 738 | 0 | 0 | 0.011168357 | 0.0139064502 | 0.792557514 | 0.782334109 | 11.9586185 |
| 4 | Sheet5 | dI_C_skewness | 738 | 738 | 0 | 0 | 0.00660444386 | 0.00910590647 | 0.962019515 | 0.913296916 | 11.12794 |
| 4 | Sheet5 | dI_T_skewness | 738 | 738 | 0 | 0 | 0.248790869 | 0.319665038 | 0.442112231 | 0.441400545 | 102.559839 |
| 4 | Sheet5 | dI_C_kurtosis | 738 | 738 | 0 | 0 | 0.0100611881 | 0.013129071 | 0.403367305 | 0.380141798 | 0.557519835 |
| 4 | Sheet5 | dI_T_kurtosis | 738 | 738 | 0 | 0 | 0.309741251 | 0.40102062 | 0.33287148 | 0.372953529 | 14.8084798 |
| 4 | Sheet5 | dI_dI_devide_dt | 738 | 738 | 0 | 0 | 0.000910966072 | 0.00225756318 | 0.993033435 | 0.998295716 | 0.664722443 |
| 4 | Sheet5 | dI_entropy | 738 | 738 | 0 | 0 | 2.66898808 | 2.6754029 | -0.190649932 | -0.0678985734 | 49.0686542 |
| 4 | Sheet5 | Charge_energy | 738 | 738 | 0 | 0 | 0.0135298044 | 0.0445600456 | 0.994116639 | 0.999031961 | 0.189927102 |
| 4 | Sheet5 | Charge_Q | 738 | 738 | 0 | 0 | 0.00332086061 | 0.00989878451 | 0.996355088 | 0.999136811 | 0.18369908 |
| 4 | Sheet5 | Charge_t_mean | 738 | 738 | 0 | 0 | 0.0253584584 | 0.0476771079 | 0.999042798 | 0.999031207 | 0.100029018 |
| 4 | Sheet5 | Charge_V_mean | 738 | 738 | 0 | 0 | 0.000901533647 | 0.00105762875 | 0.999341035 | 0.998268695 | 0.0222051301 |
| 4 | Sheet5 | Charge_C_mean | 738 | 738 | 0 | 0 | 0.00195746578 | 0.00340559749 | 0.999890282 | 0.999342629 | 0.0912713682 |
| 4 | Sheet5 | Charge_T_mean | 738 | 738 | 0 | 0 | 0.00487641969 | 0.00580232237 | 0.999996866 | 0.999977967 | 0.0196304827 |
| 4 | Sheet5 | Charge_C_std | 738 | 738 | 0 | 0 | 0.00107776467 | 0.00323885948 | 0.977094068 | 0.998763746 | 0.0623161441 |
| 4 | Sheet5 | Charge_V_std | 738 | 738 | 0 | 0 | 0.00139092309 | 0.00155042529 | 0.997123547 | 0.99617779 | 0.74560209 |
| 4 | Sheet5 | Charge_T_std | 738 | 738 | 0 | 0 | 0.0129713783 | 0.0860367678 | 0.977221832 | 0.998723091 | 0.632586167 |
| 4 | Sheet5 | Charge_C_skewness | 738 | 738 | 0 | 0 | 0.00208799589 | 0.00349444533 | 0.999887226 | 0.999339076 | 1.26820797 |
| 4 | Sheet5 | Charge_V_skewness | 738 | 738 | 0 | 0 | 0.015540147 | 0.0187691365 | 0.998125146 | 0.990204003 | 1.69847696 |
| 4 | Sheet5 | Charge_T_skewness | 738 | 738 | 0 | 0 | 0.00632664676 | 0.00973038734 | 0.999433866 | 0.998884598 | 3.47158536 |
| 4 | Sheet5 | Charge_C_kurtosis | 738 | 738 | 0 | 0 | 0.00320279741 | 0.0134942869 | 0.983272865 | 0.999111232 | 0.274002281 |
| 4 | Sheet5 | Charge_V_kurtosis | 738 | 738 | 0 | 0 | 0.0756459672 | 0.0997694695 | 0.989673603 | 0.974807036 | 3.23052619 |
| 4 | Sheet5 | Charge_T_kurtosis | 738 | 738 | 0 | 0 | 0.0221109915 | 0.105128291 | 0.910525027 | 0.991101324 | 1.33185601 |
| 4 | Sheet6 | CC_energy | 714 | 714 | 0 | 0 | 0.0669176128 | 0.0832278885 | 0.99556725 | 0.996220066 | 1.18251497 |
| 4 | Sheet6 | CC_Q | 714 | 714 | 0 | 0 | 0.0162197798 | 0.0200106666 | 0.996575427 | 0.996746459 | 1.11173411 |
| 4 | Sheet6 | CC_t_mean | 714 | 714 | 0 | 0 | 0.121768264 | 0.150332909 | 0.996553113 | 0.996762564 | 1.11278945 |
| 4 | Sheet6 | CC_V_mean | 714 | 714 | 0 | 0 | 0.00286161872 | 0.00336306527 | 0.994078782 | 0.989522861 | 0.0737503241 |
| 4 | Sheet6 | CC_T_mean | 714 | 714 | 0 | 0 | 0.0109381333 | 0.0139437004 | 0.999983212 | 0.999947219 | 0.0418767613 |
| 4 | Sheet6 | CC_V_std | 714 | 714 | 0 | 0 | 0.00209947495 | 0.00283334575 | 0.947506074 | 0.94318428 | 1.40006949 |
| 4 | Sheet6 | CC_T_std | 714 | 714 | 0 | 0 | 0.00815219144 | 0.0102992774 | 0.999571506 | 0.997870754 | 0.841556364 |
| 4 | Sheet6 | CC_V_skewness | 714 | 714 | 0 | 0 | 0.0487895887 | 0.0593544968 | 0.810141402 | 0.853035274 | 14.2972703 |
| 4 | Sheet6 | CC_T_skewness | 714 | 714 | 0 | 0 | 0.0124457481 | 0.0178466907 | 0.999795018 | 0.999311537 | 1.95906861 |
| 4 | Sheet6 | CC_V_kurtosis | 714 | 714 | 0 | 0 | 0.0666053556 | 0.091815941 | 0.808138603 | 0.931080618 | 2.85655937 |
| 4 | Sheet6 | CC_T_kurtosis | 714 | 714 | 0 | 0 | 0.0257395299 | 0.0405555377 | 0.999586634 | 0.994760425 | 1.00223681 |
| 4 | Sheet6 | CC_CCCT | 714 | 714 | 0 | 0 | 0.243259159 | 0.300137571 | 0.996574968 | 0.996747447 | 1.11153466 |
| 4 | Sheet6 | CC_entropy | 714 | 714 | 0 | 0 | 5.08301102 | 5.08372057 | 0.877225403 | 0.937827806 | 66.0161273 |
| 4 | Sheet6 | dV_energy | 714 | 714 | 0 | 0 | 0.00500726445 | 0.00538797374 | 0.999242826 | 0.998534095 | 0.547710484 |
| 4 | Sheet6 | dV_Q | 714 | 714 | 0 | 0 | 0.00126560061 | 0.00136222114 | 0.999245086 | 0.998572885 | 0.546325054 |
| 4 | Sheet6 | dV_t_mean | 714 | 714 | 0 | 0 | 0.00940200508 | 0.0101916143 | 0.999179819 | 0.998468935 | 0.541102118 |
| 4 | Sheet6 | dV_V_mean | 714 | 714 | 0 | 0 | 0.000100943197 | 0.000125578206 | 0.945701628 | 0.938717194 | 0.00255781508 |
| 4 | Sheet6 | dV_T_mean | 714 | 714 | 0 | 0 | 0.005692699 | 0.007239279 | 0.999993396 | 0.999966134 | 0.021460377 |
| 4 | Sheet6 | dV_V_std | 714 | 714 | 0 | 0 | 0.000129707402 | 0.000144529457 | 0.630438903 | 0.603352377 | 0.449264853 |
| 4 | Sheet6 | dV_T_std | 714 | 714 | 0 | 0 | 0.00711973865 | 0.0117625938 | 0.97915353 | 0.987830912 | 5.60186115 |
| 4 | Sheet6 | dV_V_skewness | 714 | 714 | 0 | 0 | 0.00181842055 | 0.00253466666 | 0.985737197 | 0.982866824 | 1.23953469 |
| 4 | Sheet6 | dV_T_skewness | 714 | 714 | 0 | 0 | 0.193270012 | 0.557414348 | 0.60796821 | 0.861607138 | 63.8784869 |
| 4 | Sheet6 | dV_V_kurtosis | 714 | 714 | 0 | 0 | 0.00192610262 | 0.00250153366 | 0.943444738 | 0.923977681 | 0.105891163 |
| 4 | Sheet6 | dV_T_kurtosis | 714 | 714 | 0 | 0 | 0.542321802 | 3.415901 | 0.157168977 | 0.780250982 | 24.7797178 |
| 4 | Sheet6 | dV_dV_devide_dt | 714 | 714 | 0 | 0 | 4.01487479e-05 | 4.88719322e-05 | 0.999570738 | 0.999241811 | 0.139907931 |
| 4 | Sheet6 | dV_entropy | 714 | 714 | 0 | 0 | 4.83362825 | 4.83398365 | -0.788194703 | -0.793410816 | 63.614482 |
| 4 | Sheet6 | CV_energy | 714 | 714 | 0 | 0 | 0.0328128548 | 0.0383747597 | 0.989451848 | 0.985623254 | 2.21913243 |
| 4 | Sheet6 | CV_Q | 714 | 714 | 0 | 0 | 0.00781234201 | 0.00913645053 | 0.989451527 | 0.985623056 | 2.21906274 |
| 4 | Sheet6 | CV_t_mean | 714 | 714 | 0 | 0 | 0.0652060666 | 0.0752703087 | 0.999789217 | 0.99836896 | 0.446174828 |
| 4 | Sheet6 | CV_C_mean | 714 | 714 | 0 | 0 | 0.0102916439 | 0.0122460457 | 0.948820576 | 0.9353888 | 1.41677693 |
| 4 | Sheet6 | CV_T_mean | 714 | 714 | 0 | 0 | 0.0122423483 | 0.0145073012 | 0.999990757 | 0.99993235 | 0.0517171217 |
| 4 | Sheet6 | CV_C_std | 714 | 714 | 0 | 0 | 0.0182497914 | 0.0215604281 | 0.653560464 | 0.616968198 | 2.19362533 |
| 4 | Sheet6 | CV_T_std | 714 | 714 | 0 | 0 | 0.00871320411 | 0.0103996084 | 0.999054223 | 0.998787649 | 0.50429034 |
| 4 | Sheet6 | CV_C_skewness | 714 | 714 | 0 | 0 | 0.0185091782 | 0.0218521759 | 0.988481761 | 0.98594824 | 0.96583394 |
| 4 | Sheet6 | CV_T_skewness | 714 | 714 | 0 | 0 | 0.0101312288 | 0.0320999423 | 0.95238253 | 0.983934785 | 1.28923289 |
| 4 | Sheet6 | CV_C_kurtosis | 714 | 714 | 0 | 0 | 0.087681682 | 0.102921801 | 0.987692382 | 0.98422213 | 1.41941367 |
| 4 | Sheet6 | CV_T_kurtosis | 714 | 714 | 0 | 0 | 0.0193460009 | 0.0284329803 | 0.989289372 | 0.991955639 | 0.865508167 |
| 4 | Sheet6 | CV_CVCT | 714 | 714 | 0 | 0 | 0.122652501 | 0.142937091 | 0.999794567 | 0.998399018 | 0.419746296 |
| 4 | Sheet6 | CV_entropy | 714 | 714 | 0 | 0 | 4.72328503 | 4.72334744 | 0.972375896 | 0.960572173 | 71.5648931 |
| 4 | Sheet6 | dI_energy | 714 | 714 | 0 | 0 | 0.00129924664 | 0.00333522729 | 0.89835207 | 0.980078003 | 2.60688822 |
| 4 | Sheet6 | dI_Q | 714 | 714 | 0 | 0 | 0.00030934485 | 0.000794101686 | 0.898351953 | 0.980078003 | 2.60689155 |
| 4 | Sheet6 | dI_t_mean | 714 | 714 | 0 | 0 | 0.00976575253 | 0.0252283139 | 0.897747562 | 0.980332668 | 2.60187795 |
| 4 | Sheet6 | dI_C_mean | 714 | 714 | 0 | 0 | 0.000451713735 | 0.00058584761 | 0.844834749 | 0.751468252 | 0.0476233167 |
| 4 | Sheet6 | dI_T_mean | 714 | 714 | 0 | 0 | 0.0147954368 | 0.0181641243 | 0.999957707 | 0.999644881 | 0.0590473843 |
| 4 | Sheet6 | dI_C_std | 714 | 714 | 0 | 0 | 0.000237559363 | 0.000297334113 | 0.109479979 | 0.0821721138 | 0.822559047 |
| 4 | Sheet6 | dI_T_std | 714 | 714 | 0 | 0 | 0.0116766279 | 0.0143512213 | 0.776937792 | 0.765494855 | 12.9804165 |
| 4 | Sheet6 | dI_C_skewness | 714 | 714 | 0 | 0 | 0.00678489827 | 0.0127421961 | 0.954036859 | 0.930784767 | 11.4828838 |
| 4 | Sheet6 | dI_T_skewness | 714 | 714 | 0 | 0 | 0.254742547 | 0.330162519 | 0.550669874 | 0.535699587 | 91.8771722 |
| 4 | Sheet6 | dI_C_kurtosis | 714 | 714 | 0 | 0 | 0.00884497907 | 0.0125496508 | 0.501806442 | 0.503678798 | 0.489624716 |
| 4 | Sheet6 | dI_T_kurtosis | 714 | 714 | 0 | 0 | 0.345367141 | 0.469661967 | 0.386192601 | 0.415378013 | 16.2026882 |
| 4 | Sheet6 | dI_dI_devide_dt | 714 | 714 | 0 | 0 | 0.0012058998 | 0.00520909447 | 0.961027877 | 0.994293736 | 0.915624032 |
| 4 | Sheet6 | dI_entropy | 714 | 714 | 0 | 0 | 2.7188106 | 2.72530422 | -0.206025702 | -0.184127215 | 49.5331724 |
| 4 | Sheet6 | Charge_energy | 714 | 714 | 0 | 0 | 0.0173078881 | 0.0651215229 | 0.987646796 | 0.998378587 | 0.242141875 |
| 4 | Sheet6 | Charge_Q | 714 | 714 | 0 | 0 | 0.00432660119 | 0.0155328962 | 0.990887931 | 0.998736566 | 0.23859415 |
| 4 | Sheet6 | Charge_t_mean | 714 | 714 | 0 | 0 | 0.0255240434 | 0.0482860269 | 0.999087357 | 0.999222492 | 0.0998507819 |
| 4 | Sheet6 | Charge_V_mean | 714 | 714 | 0 | 0 | 0.000908727745 | 0.00104657933 | 0.999335537 | 0.998521897 | 0.0223742939 |
| 4 | Sheet6 | Charge_C_mean | 714 | 714 | 0 | 0 | 0.0019596378 | 0.00343572862 | 0.999881748 | 0.999414166 | 0.0919046334 |
| 4 | Sheet6 | Charge_T_mean | 714 | 714 | 0 | 0 | 0.00445667676 | 0.00531636707 | 0.999997481 | 0.99998111 | 0.018040131 |
| 4 | Sheet6 | Charge_C_std | 714 | 714 | 0 | 0 | 0.00126855276 | 0.0042094579 | 0.970778841 | 0.998616291 | 0.0733589584 |
| 4 | Sheet6 | Charge_V_std | 714 | 714 | 0 | 0 | 0.00139235907 | 0.0015345154 | 0.997142119 | 0.995675309 | 0.749647765 |
| 4 | Sheet6 | Charge_T_std | 714 | 714 | 0 | 0 | 0.0157725528 | 0.0994905002 | 0.958601951 | 0.997948071 | 0.824817884 |
| 4 | Sheet6 | Charge_C_skewness | 714 | 714 | 0 | 0 | 0.00215832304 | 0.00353946269 | 0.999877508 | 0.999424979 | 1.27074323 |
| 4 | Sheet6 | Charge_V_skewness | 714 | 714 | 0 | 0 | 0.0152754117 | 0.0185237557 | 0.998027383 | 0.990488721 | 1.64684057 |
| 4 | Sheet6 | Charge_T_skewness | 714 | 714 | 0 | 0 | 0.00666524661 | 0.0216057359 | 0.994822868 | 0.998273948 | 4.04465621 |
| 4 | Sheet6 | Charge_C_kurtosis | 714 | 714 | 0 | 0 | 0.00364404585 | 0.0159150533 | 0.980171812 | 0.999028898 | 0.311861797 |
| 4 | Sheet6 | Charge_V_kurtosis | 714 | 714 | 0 | 0 | 0.0775388988 | 0.107433712 | 0.987084488 | 0.976554341 | 3.28258345 |
| 4 | Sheet6 | Charge_T_kurtosis | 714 | 714 | 0 | 0 | 0.0214781665 | 0.0941954629 | 0.895598599 | 0.991118361 | 1.3270517 |
| 4 | Sheet7 | CC_energy | 600 | 600 | 0 | 0 | 0.0745255619 | 0.0910425241 | 0.994693382 | 0.994683763 | 1.31654029 |
| 4 | Sheet7 | CC_Q | 600 | 600 | 0 | 0 | 0.018489191 | 0.0229145996 | 0.995112864 | 0.995061764 | 1.26646132 |
| 4 | Sheet7 | CC_t_mean | 600 | 600 | 0 | 0 | 0.138657456 | 0.17199806 | 0.99508246 | 0.995046374 | 1.26640154 |
| 4 | Sheet7 | CC_V_mean | 600 | 600 | 0 | 0 | 0.00298150446 | 0.0034700384 | 0.989209731 | 0.977893494 | 0.0768613331 |
| 4 | Sheet7 | CC_T_mean | 600 | 600 | 0 | 0 | 0.0105287609 | 0.0130441827 | 0.999984751 | 0.999960278 | 0.0400339956 |
| 4 | Sheet7 | CC_V_std | 600 | 600 | 0 | 0 | 0.00273936776 | 0.00391829673 | 0.838418233 | 0.835843877 | 1.78292359 |
| 4 | Sheet7 | CC_T_std | 600 | 600 | 0 | 0 | 0.00953017328 | 0.0118637864 | 0.999451837 | 0.997701827 | 0.977864796 |
| 4 | Sheet7 | CC_V_skewness | 600 | 600 | 0 | 0 | 0.0574399448 | 0.0794705432 | 0.759410344 | 0.79811555 | 19.7732226 |
| 4 | Sheet7 | CC_T_skewness | 600 | 600 | 0 | 0 | 0.013912908 | 0.020137907 | 0.999717465 | 0.999059997 | 2.21840083 |
| 4 | Sheet7 | CC_V_kurtosis | 600 | 600 | 0 | 0 | 0.0943456883 | 0.153289102 | 0.730975053 | 0.888911414 | 4.02023854 |
| 4 | Sheet7 | CC_T_kurtosis | 600 | 600 | 0 | 0 | 0.0325140827 | 0.0558597148 | 0.99921191 | 0.992248534 | 1.27288937 |
| 4 | Sheet7 | CC_CCCT | 600 | 600 | 0 | 0 | 0.277303832 | 0.343694794 | 0.995112398 | 0.99505897 | 1.26634705 |
| 4 | Sheet7 | CC_entropy | 600 | 600 | 0 | 0 | 5.06570955 | 5.06673313 | 0.818270332 | 0.878368823 | 65.9506789 |
| 4 | Sheet7 | dV_energy | 600 | 600 | 0 | 0 | 0.00384205542 | 0.00558114379 | 0.995532332 | 0.998279731 | 0.423667444 |
| 4 | Sheet7 | dV_Q | 600 | 600 | 0 | 0 | 0.000972604093 | 0.00141379039 | 0.995540314 | 0.998283481 | 0.423273813 |
| 4 | Sheet7 | dV_t_mean | 600 | 600 | 0 | 0 | 0.0073233497 | 0.0106538746 | 0.99543768 | 0.998081522 | 0.42495147 |
| 4 | Sheet7 | dV_V_mean | 600 | 600 | 0 | 0 | 9.77097321e-05 | 0.000129655099 | 0.918752377 | 0.927877912 | 0.00247577546 |
| 4 | Sheet7 | dV_T_mean | 600 | 600 | 0 | 0 | 0.00591664162 | 0.00754147309 | 0.999993685 | 0.999965222 | 0.0221697055 |
| 4 | Sheet7 | dV_V_std | 600 | 600 | 0 | 0 | 8.74151031e-05 | 0.000101845017 | 0.660437349 | 0.647199687 | 0.302259372 |
| 4 | Sheet7 | dV_T_std | 600 | 600 | 0 | 0 | 0.00578303319 | 0.007480413 | 0.991583632 | 0.990728474 | 4.65443891 |
| 4 | Sheet7 | dV_V_skewness | 600 | 600 | 0 | 0 | 0.00191567221 | 0.00361436546 | 0.965051566 | 0.984056426 | 1.35450169 |
| 4 | Sheet7 | dV_T_skewness | 600 | 600 | 0 | 0 | 0.181022552 | 0.491658914 | 0.670209627 | 0.872879695 | 56.0753292 |
| 4 | Sheet7 | dV_V_kurtosis | 600 | 600 | 0 | 0 | 0.00171749786 | 0.00216090348 | 0.939035524 | 0.924868514 | 0.0945127365 |
| 4 | Sheet7 | dV_T_kurtosis | 600 | 600 | 0 | 0 | 0.485279915 | 2.62254322 | 0.347521849 | 0.82859857 | 21.2427132 |
| 4 | Sheet7 | dV_dV_devide_dt | 600 | 600 | 0 | 0 | 5.670552e-05 | 0.000272386361 | 0.9831927 | 0.996485126 | 0.196031921 |
| 4 | Sheet7 | dV_entropy | 600 | 600 | 0 | 0 | 4.8301338 | 4.83042539 | -0.621768081 | -0.683121343 | 63.5927047 |
| 4 | Sheet7 | CV_energy | 600 | 600 | 0 | 0 | 0.0313311937 | 0.0371297694 | 0.990553073 | 0.985698682 | 2.11291854 |
| 4 | Sheet7 | CV_Q | 600 | 600 | 0 | 0 | 0.00745943036 | 0.00883977204 | 0.990552741 | 0.985698794 | 2.11286079 |
| 4 | Sheet7 | CV_t_mean | 600 | 600 | 0 | 0 | 0.0650263952 | 0.0839702425 | 0.999506648 | 0.997779716 | 0.441032315 |
| 4 | Sheet7 | CV_C_mean | 600 | 600 | 0 | 0 | 0.0105697193 | 0.013502345 | 0.938786146 | 0.937684829 | 1.46304223 |
| 4 | Sheet7 | CV_T_mean | 600 | 600 | 0 | 0 | 0.0115970533 | 0.0137112902 | 0.99999083 | 0.999942222 | 0.0483434022 |
| 4 | Sheet7 | CV_C_std | 600 | 600 | 0 | 0 | 0.018003353 | 0.0208965923 | 0.728296885 | 0.671397887 | 2.18392184 |
| 4 | Sheet7 | CV_T_std | 600 | 600 | 0 | 0 | 0.008723509 | 0.0138869775 | 0.994832639 | 0.997599396 | 0.52367377 |
| 4 | Sheet7 | CV_C_skewness | 600 | 600 | 0 | 0 | 0.0196026934 | 0.0250254185 | 0.984947246 | 0.987625504 | 0.996031967 |
| 4 | Sheet7 | CV_T_skewness | 600 | 600 | 0 | 0 | 0.0113912378 | 0.0346168017 | 0.947026695 | 0.980152081 | 1.47117387 |
| 4 | Sheet7 | CV_C_kurtosis | 600 | 600 | 0 | 0 | 0.0920573798 | 0.117505916 | 0.983613526 | 0.986646306 | 1.43095808 |
| 4 | Sheet7 | CV_T_kurtosis | 600 | 600 | 0 | 0 | 0.0298337655 | 0.0892000749 | 0.880287594 | 0.977249042 | 1.34809091 |
| 4 | Sheet7 | CV_CVCT | 600 | 600 | 0 | 0 | 0.122095579 | 0.163094269 | 0.999488887 | 0.997800687 | 0.414183707 |
| 4 | Sheet7 | CV_entropy | 600 | 600 | 0 | 0 | 4.73084014 | 4.73090889 | 0.929682891 | 0.960738105 | 71.641182 |
| 4 | Sheet7 | dI_energy | 600 | 600 | 0 | 0 | 0.000880378005 | 0.00102527348 | 0.997618272 | 0.996757935 | 1.74730447 |
| 4 | Sheet7 | dI_Q | 600 | 600 | 0 | 0 | 0.000209608778 | 0.000244106874 | 0.997618272 | 0.996757935 | 1.74730411 |
| 4 | Sheet7 | dI_t_mean | 600 | 600 | 0 | 0 | 0.0065794077 | 0.00766869072 | 0.997626467 | 0.996715435 | 1.73256816 |
| 4 | Sheet7 | dI_C_mean | 600 | 600 | 0 | 0 | 0.00046561695 | 0.000574601429 | 0.881462918 | 0.871687017 | 0.0491248478 |
| 4 | Sheet7 | dI_T_mean | 600 | 600 | 0 | 0 | 0.0148443841 | 0.0180888907 | 0.999960503 | 0.999789152 | 0.0583907737 |
| 4 | Sheet7 | dI_C_std | 600 | 600 | 0 | 0 | 0.000255316377 | 0.000315476666 | 0.0568201527 | 0.0463938511 | 0.882394085 |
| 4 | Sheet7 | dI_T_std | 600 | 600 | 0 | 0 | 0.0113619773 | 0.0141192824 | 0.777714434 | 0.779012963 | 12.7923629 |
| 4 | Sheet7 | dI_C_skewness | 600 | 600 | 0 | 0 | 0.00855511218 | 0.011522573 | 0.966728584 | 0.96212345 | 9.8491956 |
| 4 | Sheet7 | dI_T_skewness | 600 | 600 | 0 | 0 | 0.234220708 | 0.298735297 | 0.508040191 | 0.497797216 | 94.1201325 |
| 4 | Sheet7 | dI_C_kurtosis | 600 | 600 | 0 | 0 | 0.0134032016 | 0.0176257667 | 0.445340277 | 0.485531238 | 0.740376722 |
| 4 | Sheet7 | dI_T_kurtosis | 600 | 600 | 0 | 0 | 0.333615457 | 0.456687325 | 0.245640173 | 0.315508014 | 15.9785105 |
| 4 | Sheet7 | dI_dI_devide_dt | 600 | 600 | 0 | 0 | 0.00122595222 | 0.0029008148 | 0.992674936 | 0.998855727 | 0.92521102 |
| 4 | Sheet7 | dI_entropy | 600 | 600 | 0 | 0 | 2.72023164 | 2.73074806 | -0.287813082 | -0.281486149 | 49.5611739 |
| 4 | Sheet7 | Charge_energy | 600 | 600 | 0 | 0 | 0.0216769763 | 0.0642378269 | 0.986535684 | 0.997699077 | 0.303096239 |
| 4 | Sheet7 | Charge_Q | 600 | 600 | 0 | 0 | 0.00579142028 | 0.0162623116 | 0.989123137 | 0.997653104 | 0.319120077 |
| 4 | Sheet7 | Charge_t_mean | 600 | 600 | 0 | 0 | 0.0490128174 | 0.149503555 | 0.989693691 | 0.998519329 | 0.190802838 |
| 4 | Sheet7 | Charge_V_mean | 600 | 600 | 0 | 0 | 0.00110216301 | 0.00139839682 | 0.998474641 | 0.99476843 | 0.0271350492 |
| 4 | Sheet7 | Charge_C_mean | 600 | 600 | 0 | 0 | 0.00316314934 | 0.00690363352 | 0.999406178 | 0.998338523 | 0.148943776 |
| 4 | Sheet7 | Charge_T_mean | 600 | 600 | 0 | 0 | 0.00404698542 | 0.00493237292 | 0.999997816 | 0.999983167 | 0.0162121282 |
| 4 | Sheet7 | Charge_C_std | 600 | 600 | 0 | 0 | 0.00121794905 | 0.00415009287 | 0.980226171 | 0.998658912 | 0.0704434268 |
| 4 | Sheet7 | Charge_V_std | 600 | 600 | 0 | 0 | 0.00171890903 | 0.00205873745 | 0.991211593 | 0.985028843 | 0.917701855 |
| 4 | Sheet7 | Charge_T_std | 600 | 600 | 0 | 0 | 0.0123148439 | 0.0801829748 | 0.967129658 | 0.997935397 | 0.667905207 |
| 4 | Sheet7 | Charge_C_skewness | 600 | 600 | 0 | 0 | 0.00343577832 | 0.00770618509 | 0.999323562 | 0.998372162 | 1.94569499 |
| 4 | Sheet7 | Charge_V_skewness | 600 | 600 | 0 | 0 | 0.0204937213 | 0.0276873887 | 0.994303966 | 0.980316635 | 2.13119372 |
| 4 | Sheet7 | Charge_T_skewness | 600 | 600 | 0 | 0 | 0.00625203172 | 0.00953967259 | 0.999320748 | 0.998628385 | 3.68934185 |
| 4 | Sheet7 | Charge_C_kurtosis | 600 | 600 | 0 | 0 | 0.0058408335 | 0.0300206461 | 0.948729214 | 0.996410338 | 0.501592066 |
| 4 | Sheet7 | Charge_V_kurtosis | 600 | 600 | 0 | 0 | 0.102152686 | 0.151562892 | 0.971731027 | 0.955576705 | 4.13605064 |
| 4 | Sheet7 | Charge_T_kurtosis | 600 | 600 | 0 | 0 | 0.0229789986 | 0.102187807 | 0.898564776 | 0.99029964 | 1.39886993 |
| 4 | Sheet8 | CC_energy | 750 | 750 | 0 | 0 | 0.0678821435 | 0.0791927291 | 0.997400227 | 0.996309817 | 1.20919426 |
| 4 | Sheet8 | CC_Q | 750 | 750 | 0 | 0 | 0.016724489 | 0.0197592879 | 0.997632437 | 0.996647027 | 1.15553675 |
| 4 | Sheet8 | CC_t_mean | 750 | 750 | 0 | 0 | 0.125678408 | 0.148420748 | 0.997622802 | 0.996627727 | 1.15783317 |
| 4 | Sheet8 | CC_V_mean | 750 | 750 | 0 | 0 | 0.00296247203 | 0.00346095614 | 0.991878445 | 0.985863683 | 0.0763383054 |
| 4 | Sheet8 | CC_T_mean | 750 | 750 | 0 | 0 | 0.0122431637 | 0.0155051249 | 0.999979169 | 0.999935203 | 0.0464816349 |
| 4 | Sheet8 | CC_V_std | 750 | 750 | 0 | 0 | 0.00244218889 | 0.0034489005 | 0.916282571 | 0.907170395 | 1.61547335 |
| 4 | Sheet8 | CC_T_std | 750 | 750 | 0 | 0 | 0.00998911039 | 0.0124473259 | 0.999532592 | 0.998463798 | 0.921745639 |
| 4 | Sheet8 | CC_V_skewness | 750 | 750 | 0 | 0 | 0.0574996944 | 0.0757685355 | 0.748767729 | 0.827318676 | 18.0888783 |
| 4 | Sheet8 | CC_T_skewness | 750 | 750 | 0 | 0 | 0.0129403753 | 0.0177256091 | 0.999792701 | 0.999379569 | 2.05082317 |
| 4 | Sheet8 | CC_V_kurtosis | 750 | 750 | 0 | 0 | 0.0879136412 | 0.135354434 | 0.753023184 | 0.925015675 | 3.75552236 |
| 4 | Sheet8 | CC_T_kurtosis | 750 | 750 | 0 | 0 | 0.108809828 | 0.675750295 | 0.875180755 | 0.926035012 | 4.37912601 |
| 4 | Sheet8 | CC_CCCT | 750 | 750 | 0 | 0 | 0.250840451 | 0.296365085 | 0.997632261 | 0.996650695 | 1.15547224 |
| 4 | Sheet8 | CC_entropy | 750 | 750 | 0 | 0 | 5.07267733 | 5.07361687 | 0.84249737 | 0.904514179 | 65.9835791 |
| 4 | Sheet8 | dV_energy | 750 | 750 | 0 | 0 | 0.00569417433 | 0.00602479276 | 0.99914201 | 0.998676876 | 0.629082001 |
| 4 | Sheet8 | dV_Q | 750 | 750 | 0 | 0 | 0.00144063088 | 0.00152453981 | 0.999144359 | 0.998690088 | 0.628126674 |
| 4 | Sheet8 | dV_t_mean | 750 | 750 | 0 | 0 | 0.010731862 | 0.0114720919 | 0.998981971 | 0.998588719 | 0.623891723 |
| 4 | Sheet8 | dV_V_mean | 750 | 750 | 0 | 0 | 9.99391974e-05 | 0.000122884273 | 0.937676355 | 0.929879709 | 0.00253229376 |
| 4 | Sheet8 | dV_T_mean | 750 | 750 | 0 | 0 | 0.00577812395 | 0.0073790395 | 0.999993358 | 0.999957639 | 0.0215872465 |
| 4 | Sheet8 | dV_V_std | 750 | 750 | 0 | 0 | 0.000150564965 | 0.000163960091 | 0.604864555 | 0.579412529 | 0.521799808 |
| 4 | Sheet8 | dV_T_std | 750 | 750 | 0 | 0 | 0.00637006106 | 0.00892077824 | 0.991871306 | 0.9929571 | 4.63186861 |
| 4 | Sheet8 | dV_V_skewness | 750 | 750 | 0 | 0 | 0.00204003253 | 0.00278693943 | 0.98154788 | 0.979682346 | 1.43589838 |
| 4 | Sheet8 | dV_T_skewness | 750 | 750 | 0 | 0 | 0.204642841 | 0.53562675 | 0.579698705 | 0.814965446 | 75.7244582 |
| 4 | Sheet8 | dV_V_kurtosis | 750 | 750 | 0 | 0 | 0.00193807375 | 0.00248562796 | 0.937576986 | 0.925515132 | 0.106641379 |
| 4 | Sheet8 | dV_T_kurtosis | 750 | 750 | 0 | 0 | 0.420922643 | 1.93860277 | 0.630162265 | 0.764042063 | 18.0126302 |
| 4 | Sheet8 | dV_dV_devide_dt | 750 | 750 | 0 | 0 | 2.90710395e-05 | 3.63995881e-05 | 0.999748063 | 0.999606022 | 0.100400121 |
| 4 | Sheet8 | dV_entropy | 750 | 750 | 0 | 0 | 4.82721308 | 4.82756976 | -0.805660842 | -0.799890481 | 63.5798683 |
| 4 | Sheet8 | CV_energy | 750 | 750 | 0 | 0 | 0.0340766711 | 0.0397902316 | 0.991035696 | 0.987727111 | 2.28108372 |
| 4 | Sheet8 | CV_Q | 750 | 750 | 0 | 0 | 0.00811345493 | 0.00947371373 | 0.991033398 | 0.987719431 | 2.28101729 |
| 4 | Sheet8 | CV_t_mean | 750 | 750 | 0 | 0 | 0.0674903333 | 0.0778458138 | 0.999799045 | 0.99840836 | 0.453228932 |
| 4 | Sheet8 | CV_C_mean | 750 | 750 | 0 | 0 | 0.0107302732 | 0.0126622915 | 0.943528827 | 0.93975049 | 1.49029042 |
| 4 | Sheet8 | CV_T_mean | 750 | 750 | 0 | 0 | 0.0141858386 | 0.0166941166 | 0.999987979 | 0.999922432 | 0.059934587 |
| 4 | Sheet8 | CV_C_std | 750 | 750 | 0 | 0 | 0.0192004978 | 0.022387025 | 0.641446258 | 0.6134135 | 2.32189068 |
| 4 | Sheet8 | CV_T_std | 750 | 750 | 0 | 0 | 0.00954511144 | 0.0113533473 | 0.998984323 | 0.998715105 | 0.492174458 |
| 4 | Sheet8 | CV_C_skewness | 750 | 750 | 0 | 0 | 0.0195226295 | 0.0231894143 | 0.986805755 | 0.986991578 | 1.00245509 |
| 4 | Sheet8 | CV_T_skewness | 750 | 750 | 0 | 0 | 0.00816050244 | 0.00974676628 | 0.99791251 | 0.996803209 | 1.06763687 |
| 4 | Sheet8 | CV_C_kurtosis | 750 | 750 | 0 | 0 | 0.0911920203 | 0.107877668 | 0.986168071 | 0.985783796 | 1.44064071 |
| 4 | Sheet8 | CV_T_kurtosis | 750 | 750 | 0 | 0 | 0.0189684229 | 0.0227006561 | 0.994698098 | 0.991802723 | 0.863038483 |
| 4 | Sheet8 | CV_CVCT | 750 | 750 | 0 | 0 | 0.127658631 | 0.148872274 | 0.999799664 | 0.998410969 | 0.428757236 |
| 4 | Sheet8 | CV_entropy | 750 | 750 | 0 | 0 | 4.71845287 | 4.71851417 | 0.967469087 | 0.965860629 | 71.6556183 |
| 4 | Sheet8 | dI_energy | 750 | 750 | 0 | 0 | 0.0010996638 | 0.00279882801 | 0.949011117 | 0.993428781 | 2.12740567 |
| 4 | Sheet8 | dI_Q | 750 | 750 | 0 | 0 | 0.000261834226 | 0.00066639152 | 0.949008604 | 0.993422865 | 2.12742858 |
| 4 | Sheet8 | dI_t_mean | 750 | 750 | 0 | 0 | 0.00823523484 | 0.0210599995 | 0.949043744 | 0.993385268 | 2.11519264 |
| 4 | Sheet8 | dI_C_mean | 750 | 750 | 0 | 0 | 0.000440045356 | 0.000553166092 | 0.907131388 | 0.837073147 | 0.0463970706 |
| 4 | Sheet8 | dI_T_mean | 750 | 750 | 0 | 0 | 0.0141078775 | 0.0172337795 | 0.999962186 | 0.999661482 | 0.0557765582 |
| 4 | Sheet8 | dI_C_std | 750 | 750 | 0 | 0 | 0.000240861268 | 0.000301351337 | 0.216197167 | 0.205963559 | 0.832204974 |
| 4 | Sheet8 | dI_T_std | 750 | 750 | 0 | 0 | 0.0117858937 | 0.0146640313 | 0.717193138 | 0.681924759 | 11.5034496 |
| 4 | Sheet8 | dI_C_skewness | 750 | 750 | 0 | 0 | 0.00805647347 | 0.0105922851 | 0.977867472 | 0.942563055 | 13.0426466 |
| 4 | Sheet8 | dI_T_skewness | 750 | 750 | 0 | 0 | 0.226752067 | 0.28349497 | 0.494575096 | 0.485572209 | 94.0006394 |
| 4 | Sheet8 | dI_C_kurtosis | 750 | 750 | 0 | 0 | 0.0105480667 | 0.0148600165 | 0.539505955 | 0.52864121 | 0.583591073 |
| 4 | Sheet8 | dI_T_kurtosis | 750 | 750 | 0 | 0 | 0.273597432 | 0.350206228 | 0.403559562 | 0.423159285 | 13.3308189 |
| 4 | Sheet8 | dI_dI_devide_dt | 750 | 750 | 0 | 0 | 0.00123418646 | 0.0038418688 | 0.985957265 | 0.998790366 | 0.960898631 |
| 4 | Sheet8 | dI_entropy | 750 | 750 | 0 | 0 | 2.76562405 | 2.77464251 | -0.0673904064 | -0.0293976127 | 49.9635334 |
| 4 | Sheet8 | Charge_energy | 750 | 750 | 0 | 0 | 0.0163398468 | 0.0464904761 | 0.994512832 | 0.998036704 | 0.229632843 |
| 4 | Sheet8 | Charge_Q | 750 | 750 | 0 | 0 | 0.00424033997 | 0.0109644107 | 0.996232008 | 0.998272224 | 0.234961981 |
| 4 | Sheet8 | Charge_t_mean | 750 | 750 | 0 | 0 | 0.0328842003 | 0.0614389347 | 0.998589465 | 0.998624154 | 0.127690133 |
| 4 | Sheet8 | Charge_V_mean | 750 | 750 | 0 | 0 | 0.00104588589 | 0.00127282382 | 0.998941561 | 0.997492447 | 0.0257377523 |
| 4 | Sheet8 | Charge_C_mean | 750 | 750 | 0 | 0 | 0.00251649885 | 0.00436512452 | 0.999813354 | 0.999095181 | 0.119381307 |
| 4 | Sheet8 | Charge_T_mean | 750 | 750 | 0 | 0 | 0.00489675251 | 0.00588342553 | 0.999996931 | 0.999977159 | 0.0197621884 |
| 4 | Sheet8 | Charge_C_std | 750 | 750 | 0 | 0 | 0.000930309554 | 0.00259018843 | 0.991092375 | 0.998488061 | 0.0538358588 |
| 4 | Sheet8 | Charge_V_std | 750 | 750 | 0 | 0 | 0.00162809825 | 0.00185902829 | 0.994761197 | 0.992732545 | 0.879361725 |
| 4 | Sheet8 | Charge_T_std | 750 | 750 | 0 | 0 | 0.0137059473 | 0.0870084702 | 0.973742561 | 0.998258258 | 0.643476273 |
| 4 | Sheet8 | Charge_C_skewness | 750 | 750 | 0 | 0 | 0.0027399552 | 0.00450609897 | 0.999807186 | 0.999035959 | 1.47952192 |
| 4 | Sheet8 | Charge_V_skewness | 750 | 750 | 0 | 0 | 0.0185205232 | 0.0225994849 | 0.996505571 | 0.987243462 | 1.91990454 |
| 4 | Sheet8 | Charge_T_skewness | 750 | 750 | 0 | 0 | 0.00603060664 | 0.00901130828 | 0.999437847 | 0.999080048 | 3.46480995 |
| 4 | Sheet8 | Charge_C_kurtosis | 750 | 750 | 0 | 0 | 0.00359495618 | 0.0152529154 | 0.983524933 | 0.998661658 | 0.306001082 |
| 4 | Sheet8 | Charge_V_kurtosis | 750 | 750 | 0 | 0 | 0.0916729581 | 0.119209468 | 0.981370632 | 0.970577298 | 3.72358868 |
| 4 | Sheet8 | Charge_T_kurtosis | 750 | 750 | 0 | 0 | 0.0158904521 | 0.070939686 | 0.939653782 | 0.993868818 | 0.972098652 |
| 5 | Sheet1 | CC_energy | 196 | 196 | 0 | 0 | 0.0701967016 | 0.0835435036 | 0.996244866 | 0.992989027 | 1.2571981 |
| 5 | Sheet1 | CC_Q | 196 | 196 | 0 | 0 | 0.017212677 | 0.0208955622 | 0.996692032 | 0.994119006 | 1.20511111 |
| 5 | Sheet1 | CC_t_mean | 196 | 196 | 0 | 0 | 1.47493254 | 6.01828895 | 0.874347983 | 0.99319781 | 14.7333769 |
| 5 | Sheet1 | CC_V_mean | 196 | 196 | 0 | 0 | 0.00332858606 | 0.00393013701 | 0.997602587 | 0.98646734 | 0.0850725441 |
| 5 | Sheet1 | CC_T_mean | 196 | 196 | 0 | 0 | 0.0268222899 | 0.034644832 | 0.999926929 | 0.997022847 | 0.106709898 |
| 5 | Sheet1 | CC_V_std | 196 | 196 | 0 | 0 | 0.00228222401 | 0.00354575591 | 0.980923087 | 0.974195348 | 1.63420844 |
| 5 | Sheet1 | CC_T_std | 196 | 196 | 0 | 0 | 0.011938521 | 0.016899818 | 0.999861528 | 0.998415797 | 0.637475656 |
| 5 | Sheet1 | CC_V_skewness | 196 | 196 | 0 | 0 | 0.0760369586 | 0.0977060854 | 0.921818679 | 0.943510587 | 29.4743025 |
| 5 | Sheet1 | CC_T_skewness | 196 | 196 | 0 | 0 | 0.0245884395 | 0.0808747533 | 0.945032994 | 0.982674179 | 7.0084137 |
| 5 | Sheet1 | CC_V_kurtosis | 196 | 196 | 0 | 0 | 0.124723976 | 0.168176054 | 0.719395539 | 0.813551785 | 5.27466542 |
| 5 | Sheet1 | CC_T_kurtosis | 196 | 196 | 0 | 0 | 0.0574727228 | 0.258390081 | 0.763710742 | 0.892344349 | 3.02652232 |
| 5 | Sheet1 | CC_CCCT | 196 | 196 | 0 | 0 | 2.95016102 | 12.0382836 | 0.87430662 | 0.993368327 | 14.7350514 |
| 5 | Sheet1 | CC_entropy | 196 | 196 | 0 | 0 | 5.05935971 | 5.06003342 | 0.824946847 | 0.829875128 | 66.1717799 |
| 5 | Sheet1 | dV_energy | 196 | 196 | 0 | 0 | 0.00556926121 | 0.00635699381 | 0.999920713 | 0.99726988 | 0.468220856 |
| 5 | Sheet1 | dV_Q | 196 | 196 | 0 | 0 | 0.00140600456 | 0.00160557704 | 0.999921039 | 0.99732885 | 0.466500719 |
| 5 | Sheet1 | dV_t_mean | 196 | 196 | 0 | 0 | 0.148668221 | 0.624063129 | 0.833293467 | 0.995406769 | 7.99557027 |
| 5 | Sheet1 | dV_V_mean | 196 | 196 | 0 | 0 | 0.00012234058 | 0.000233078975 | 0.988296612 | 0.979778307 | 0.00309982716 |
| 5 | Sheet1 | dV_T_mean | 196 | 196 | 0 | 0 | 0.00657645381 | 0.00842317168 | 0.999992352 | 0.999548566 | 0.0254492782 |
| 5 | Sheet1 | dV_V_std | 196 | 196 | 0 | 0 | 0.000126733416 | 0.000143483078 | 0.881052892 | 0.712975639 | 0.442377117 |
| 5 | Sheet1 | dV_T_std | 196 | 196 | 0 | 0 | 0.00722579095 | 0.00937125688 | 0.999105053 | 0.994690249 | 1.7369979 |
| 5 | Sheet1 | dV_V_skewness | 196 | 196 | 0 | 0 | 0.00266412849 | 0.00462560757 | 0.997178059 | 0.989549682 | 1.92777809 |
| 5 | Sheet1 | dV_T_skewness | 196 | 196 | 0 | 0 | 0.199767797 | 0.791702221 | 0.561421933 | 0.712191744 | 65.087464 |
| 5 | Sheet1 | dV_V_kurtosis | 196 | 196 | 0 | 0 | 0.00251729089 | 0.00370718129 | 0.982513256 | 0.937140307 | 0.137054186 |
| 5 | Sheet1 | dV_T_kurtosis | 196 | 196 | 0 | 0 | 1.08901873 | 7.14062117 | 0.0782174856 | 0.70115232 | 47.032493 |
| 5 | Sheet1 | dV_dV_devide_dt | 196 | 196 | 0 | 0 | 4.22889153e-05 | 5.7322346e-05 | 0.999976562 | 0.998917833 | 0.152919517 |
| 5 | Sheet1 | dV_entropy | 196 | 196 | 0 | 0 | 4.8330429 | 4.83491264 | 0.40405385 | -0.0696647123 | 63.6119926 |
| 5 | Sheet1 | CV_energy | 196 | 196 | 0 | 0 | 0.0420913853 | 0.0482001029 | 0.997755765 | 0.986880125 | 2.71249706 |
| 5 | Sheet1 | CV_Q | 196 | 196 | 0 | 0 | 0.0100217414 | 0.0114761791 | 0.997755911 | 0.986880125 | 2.71241634 |
| 5 | Sheet1 | CV_t_mean | 196 | 196 | 0 | 0 | 0.26862254 | 0.974205953 | 0.958723472 | 0.997849473 | 1.82348615 |
| 5 | Sheet1 | CV_C_mean | 196 | 196 | 0 | 0 | 0.012848612 | 0.0152916779 | 0.998755839 | 0.953337743 | 1.67033207 |
| 5 | Sheet1 | CV_T_mean | 196 | 196 | 0 | 0 | 0.0162918446 | 0.0198735906 | 0.999951675 | 0.998426954 | 0.0711845385 |
| 5 | Sheet1 | CV_C_std | 196 | 196 | 0 | 0 | 0.0253811405 | 0.0305034591 | 0.997858946 | 0.800388879 | 2.47678314 |
| 5 | Sheet1 | CV_T_std | 196 | 196 | 0 | 0 | 0.010385253 | 0.0127645436 | 0.999955155 | 0.998544892 | 0.424633761 |
| 5 | Sheet1 | CV_C_skewness | 196 | 196 | 0 | 0 | 0.015492525 | 0.0204746064 | 0.999032671 | 0.991647077 | 0.689004999 |
| 5 | Sheet1 | CV_T_skewness | 196 | 196 | 0 | 0 | 0.0234883483 | 0.104697637 | 0.820114966 | 0.958101507 | 3.23523999 |
| 5 | Sheet1 | CV_C_kurtosis | 196 | 196 | 0 | 0 | 0.0809681964 | 0.103564026 | 0.998731531 | 0.992276614 | 1.04705287 |
| 5 | Sheet1 | CV_T_kurtosis | 196 | 196 | 0 | 0 | 0.0472700259 | 0.225632523 | 0.762450084 | 0.954286033 | 2.19176168 |
| 5 | Sheet1 | CV_CVCT | 196 | 196 | 0 | 0 | 0.530377418 | 1.95000943 | 0.95875529 | 0.997805638 | 1.80066436 |
| 5 | Sheet1 | CV_entropy | 196 | 196 | 0 | 0 | 4.59494086 | 4.59647584 | 0.996615635 | 0.986013276 | 73.225933 |
| 5 | Sheet1 | dI_energy | 196 | 191 | 0 | 5 | 0.00167300442 | 0.00404446669 | 0.865688367 | 0.964303598 | 4.85233562 |
| 5 | Sheet1 | dI_Q | 196 | 191 | 0 | 5 | 0.000398344353 | 0.000963007998 | 0.865697491 | 0.964303598 | 4.85231502 |
| 5 | Sheet1 | dI_t_mean | 196 | 191 | 0 | 5 | 0.0125293466 | 0.0301926702 | 0.86807275 | 0.96515955 | 4.8229628 |
| 5 | Sheet1 | dI_C_mean | 196 | 191 | 0 | 5 | 0.00127209507 | 0.00520406754 | 0.0138031903 | 0.561225786 | 0.134178466 |
| 5 | Sheet1 | dI_T_mean | 196 | 191 | 0 | 5 | 0.0158544332 | 0.0199122848 | 0.999933277 | 0.996646789 | 0.0628315441 |
| 5 | Sheet1 | dI_C_std | 196 | 191 | 0 | 5 | 0.000771765437 | 0.00314148862 | -0.0774671862 | -0.0538733122 | 2.67185476 |
| 5 | Sheet1 | dI_T_std | 196 | 191 | 0 | 5 | 0.0137132311 | 0.0168046789 | 0.905209434 | 0.855144929 | 14.5616647 |
| 5 | Sheet1 | dI_C_skewness | 196 | 191 | 0 | 5 | 0.0164831441 | 0.0224897524 | 0.753909681 | 0.779870488 | 21.7421496 |
| 5 | Sheet1 | dI_T_skewness | 196 | 191 | 0 | 5 | 0.373559257 | 0.674031731 | 0.270700854 | 0.313446562 | 98.5911639 |
| 5 | Sheet1 | dI_C_kurtosis | 196 | 191 | 0 | 5 | 0.0187516021 | 0.0225842885 | 0.171268317 | 0.139275627 | 1.0391918 |
| 5 | Sheet1 | dI_T_kurtosis | 196 | 191 | 0 | 5 | 0.753967809 | 1.86426172 | 0.0641908725 | 0.213932068 | 32.0075462 |
| 5 | Sheet1 | dI_dI_devide_dt | 196 | 191 | 0 | 5 | 0.00228479499 | 0.00831224984 | 0.976865237 | 0.96223337 | 1.18285489 |
| 5 | Sheet1 | dI_entropy | 196 | 191 | 0 | 5 | 2.17904466 | 2.19774521 | -0.243950384 | -0.238651421 | 44.0353677 |
| 5 | Sheet1 | Charge_energy | 196 | 196 | 0 | 0 | 0.0125328722 | 0.0333538094 | 0.996292431 | 0.993137247 | 0.175492229 |
| 5 | Sheet1 | Charge_Q | 196 | 196 | 0 | 0 | 0.00422724842 | 0.014013076 | 0.990227769 | 0.99094582 | 0.234849101 |
| 5 | Sheet1 | Charge_t_mean | 196 | 196 | 0 | 0 | 1.4520629 | 6.25927498 | 0.904126374 | 0.997481448 | 5.82684056 |
| 5 | Sheet1 | Charge_V_mean | 196 | 196 | 0 | 0 | 0.00122673247 | 0.00200625243 | 0.9995804 | 0.998436516 | 0.0300310517 |
| 5 | Sheet1 | Charge_C_mean | 196 | 196 | 0 | 0 | 0.00294951448 | 0.00406716726 | 0.999976123 | 0.999266868 | 0.128378247 |
| 5 | Sheet1 | Charge_T_mean | 196 | 196 | 0 | 0 | 0.00823430414 | 0.00947161983 | 0.999993732 | 0.999783248 | 0.0348056738 |
| 5 | Sheet1 | Charge_C_std | 196 | 196 | 0 | 0 | 0.00118511819 | 0.00152519192 | 0.999998599 | 0.99961909 | 0.0528368329 |
| 5 | Sheet1 | Charge_V_std | 196 | 196 | 0 | 0 | 0.00203544024 | 0.00253099315 | 0.997974634 | 0.991766609 | 1.26572623 |
| 5 | Sheet1 | Charge_T_std | 196 | 196 | 0 | 0 | 0.00230171405 | 0.00382865746 | 0.999992325 | 0.999660528 | 0.0918237168 |
| 5 | Sheet1 | Charge_C_skewness | 196 | 196 | 0 | 0 | 0.00399479998 | 0.00689737785 | 0.999945669 | 0.999446963 | 0.767720831 |
| 5 | Sheet1 | Charge_V_skewness | 196 | 196 | 0 | 0 | 0.0329414305 | 0.0416644341 | 0.998019023 | 0.994523823 | 2.70372465 |
| 5 | Sheet1 | Charge_T_skewness | 196 | 196 | 0 | 0 | 0.0426613873 | 0.203159358 | 0.845011849 | 0.975556423 | 15.3486333 |
| 5 | Sheet1 | Charge_C_kurtosis | 196 | 196 | 0 | 0 | 0.0239639869 | 0.107422322 | 0.952939422 | 0.997894636 | 1.66973672 |
| 5 | Sheet1 | Charge_V_kurtosis | 196 | 196 | 0 | 0 | 0.206254566 | 0.322681703 | 0.979429253 | 0.9875256 | 6.22004772 |
| 5 | Sheet1 | Charge_T_kurtosis | 196 | 196 | 0 | 0 | 0.0426990954 | 0.218000585 | 0.809503692 | 0.931028218 | 2.48133101 |
| 5 | Sheet2 | CC_energy | 306 | 306 | 0 | 0 | 0.0753153739 | 0.0899022052 | 0.99543055 | 0.993876515 | 1.32329989 |
| 5 | Sheet2 | CC_Q | 306 | 306 | 0 | 0 | 0.0186981865 | 0.0228591043 | 0.995746682 | 0.994523164 | 1.28168686 |
| 5 | Sheet2 | CC_t_mean | 306 | 306 | 0 | 0 | 1.83219096 | 6.85537107 | 0.873891622 | 0.992923886 | 19.0209273 |
| 5 | Sheet2 | CC_V_mean | 306 | 306 | 0 | 0 | 0.00336671514 | 0.00414362329 | 0.99663335 | 0.987379866 | 0.086232971 |
| 5 | Sheet2 | CC_T_mean | 306 | 306 | 0 | 0 | 0.0358168325 | 0.0451981844 | 0.999919427 | 0.999050967 | 0.132677374 |
| 5 | Sheet2 | CC_V_std | 306 | 306 | 0 | 0 | 0.00262131406 | 0.00402695798 | 0.9779605 | 0.959723038 | 1.85629957 |
| 5 | Sheet2 | CC_T_std | 306 | 306 | 0 | 0 | 0.0187124277 | 0.0293165997 | 0.999676316 | 0.998206218 | 0.791773412 |
| 5 | Sheet2 | CC_V_skewness | 306 | 306 | 0 | 0 | 0.0774599784 | 0.0981012362 | 0.884990386 | 0.895732805 | 27.6499715 |
| 5 | Sheet2 | CC_T_skewness | 306 | 306 | 0 | 0 | 0.0918798187 | 0.410256987 | 0.44209015 | 0.930685365 | 29.9705597 |
| 5 | Sheet2 | CC_V_kurtosis | 306 | 306 | 0 | 0 | 0.128534497 | 0.168313736 | 0.686094229 | 0.783392962 | 5.22621758 |
| 5 | Sheet2 | CC_T_kurtosis | 306 | 306 | 0 | 0 | 0.290538813 | 1.32013281 | 0.270658087 | 0.912860279 | 15.2197184 |
| 5 | Sheet2 | CC_CCCT | 306 | 306 | 0 | 0 | 3.66372269 | 13.7126578 | 0.873884165 | 0.992872256 | 19.0192458 |
| 5 | Sheet2 | CC_entropy | 306 | 306 | 0 | 0 | 5.0243742 | 5.02508968 | 0.788038483 | 0.825793486 | 66.2563616 |
| 5 | Sheet2 | dV_energy | 306 | 306 | 0 | 0 | 0.00740200192 | 0.00856893559 | 0.999611235 | 0.990354704 | 0.654477768 |
| 5 | Sheet2 | dV_Q | 306 | 306 | 0 | 0 | 0.00187591499 | 0.00217193658 | 0.999610271 | 0.990438467 | 0.654481303 |
| 5 | Sheet2 | dV_t_mean | 306 | 306 | 0 | 0 | 0.179680205 | 0.680688112 | 0.877978532 | 0.988607719 | 10.4460096 |
| 5 | Sheet2 | dV_V_mean | 306 | 306 | 0 | 0 | 0.000153011913 | 0.000200113932 | 0.988469713 | 0.922224491 | 0.00387762462 |
| 5 | Sheet2 | dV_T_mean | 306 | 306 | 0 | 0 | 0.00730275186 | 0.00948179067 | 0.9999943 | 0.999875926 | 0.0259469145 |
| 5 | Sheet2 | dV_V_std | 306 | 306 | 0 | 0 | 0.000165835929 | 0.000192235055 | 0.673444784 | 0.635449707 | 0.57831833 |
| 5 | Sheet2 | dV_T_std | 306 | 306 | 0 | 0 | 0.00715582301 | 0.00916199122 | 0.999160785 | 0.997108081 | 1.55147425 |
| 5 | Sheet2 | dV_V_skewness | 306 | 306 | 0 | 0 | 0.0043265855 | 0.00600909463 | 0.994226725 | 0.963404835 | 2.56473765 |
| 5 | Sheet2 | dV_T_skewness | 306 | 306 | 0 | 0 | 0.147984921 | 0.756749103 | 0.357231401 | 0.851441704 | 59.288262 |
| 5 | Sheet2 | dV_V_kurtosis | 306 | 306 | 0 | 0 | 0.00396683453 | 0.00572475317 | 0.956281067 | 0.76944393 | 0.215533222 |
| 5 | Sheet2 | dV_T_kurtosis | 306 | 306 | 0 | 0 | 0.930388509 | 7.00252123 | 0.139823347 | 0.831307157 | 39.0360283 |
| 5 | Sheet2 | dV_dV_devide_dt | 306 | 306 | 0 | 0 | 0.00061163534 | 0.0020397406 | 0.974376687 | 0.991355098 | 2.01736493 |
| 5 | Sheet2 | dV_entropy | 306 | 306 | 0 | 0 | 4.59871562 | 4.60335852 | 0.641974697 | 0.361549949 | 62.4807592 |
| 5 | Sheet2 | CV_energy | 306 | 306 | 0 | 0 | 0.0302909034 | 0.0367584408 | 0.997838718 | 0.988769073 | 1.98165913 |
| 5 | Sheet2 | CV_Q | 306 | 306 | 0 | 0 | 0.00721076037 | 0.00875042193 | 0.997838515 | 0.988769073 | 1.98148357 |
| 5 | Sheet2 | CV_t_mean | 306 | 306 | 0 | 0 | 0.114855199 | 0.37539929 | 0.990575319 | 0.998821297 | 0.870181845 |
| 5 | Sheet2 | CV_C_mean | 306 | 306 | 0 | 0 | 0.0262033393 | 0.0647637612 | 0.972427455 | 0.897512114 | 3.02829397 |
| 5 | Sheet2 | CV_T_mean | 306 | 306 | 0 | 0 | 0.0157038398 | 0.0195527633 | 0.99996724 | 0.999509987 | 0.0636412748 |
| 5 | Sheet2 | CV_C_std | 306 | 306 | 0 | 0 | 0.020301399 | 0.024515186 | 0.997934973 | 0.733376052 | 1.85478664 |
| 5 | Sheet2 | CV_T_std | 306 | 306 | 0 | 0 | 0.00858042425 | 0.0104641869 | 0.999969102 | 0.99659462 | 0.270676764 |
| 5 | Sheet2 | CV_C_skewness | 306 | 306 | 0 | 0 | 0.0138631377 | 0.0187909709 | 0.998758431 | 0.975283249 | 0.658980673 |
| 5 | Sheet2 | CV_T_skewness | 306 | 306 | 0 | 0 | 0.016942357 | 0.0636535755 | 0.718368531 | 0.923525602 | 2.93776308 |
| 5 | Sheet2 | CV_C_kurtosis | 306 | 306 | 0 | 0 | 0.0697244597 | 0.0923280014 | 0.99837084 | 0.978020202 | 0.993220053 |
| 5 | Sheet2 | CV_T_kurtosis | 306 | 306 | 0 | 0 | 0.0213585714 | 0.0794468199 | 0.821796722 | 0.978570515 | 1.10375584 |
| 5 | Sheet2 | CV_CVCT | 306 | 306 | 0 | 0 | 0.221153079 | 0.750693589 | 0.990589221 | 0.998752083 | 0.838053877 |
| 5 | Sheet2 | CV_entropy | 306 | 306 | 0 | 0 | 4.6451185 | 4.64619625 | 0.996968565 | 0.929440815 | 72.3727193 |
| 5 | Sheet2 | dI_energy | 306 | 301 | 0 | 5 | 0.00197934322 | 0.0061347343 | 0.807350516 | 0.985135201 | 3.97945289 |
| 5 | Sheet2 | dI_Q | 306 | 301 | 0 | 5 | 0.000471221864 | 0.00146058868 | 0.807318201 | 0.985115839 | 3.97942283 |
| 5 | Sheet2 | dI_t_mean | 306 | 301 | 0 | 5 | 0.014661627 | 0.0455116634 | 0.811848766 | 0.984496159 | 3.91588244 |
| 5 | Sheet2 | dI_C_mean | 306 | 301 | 0 | 5 | 0.00151566716 | 0.00624077038 | 0.261471635 | 0.862790167 | 0.159808289 |
| 5 | Sheet2 | dI_T_mean | 306 | 301 | 0 | 5 | 0.0129984188 | 0.0164779853 | 0.999973967 | 0.999582957 | 0.0480779669 |
| 5 | Sheet2 | dI_C_std | 306 | 301 | 0 | 5 | 0.00089134836 | 0.0038032533 | 0.070342279 | 0.174666104 | 3.09155507 |
| 5 | Sheet2 | dI_T_std | 306 | 301 | 0 | 5 | 0.0116125287 | 0.01464092 | 0.975197647 | 0.933996404 | 7.24734377 |
| 5 | Sheet2 | dI_C_skewness | 306 | 301 | 0 | 5 | 0.0196982032 | 0.0507741103 | 0.770451892 | 0.954029719 | 28.5542485 |
| 5 | Sheet2 | dI_T_skewness | 306 | 301 | 0 | 5 | 0.217353696 | 0.33632966 | 0.342564371 | 0.43211948 | 102.44164 |
| 5 | Sheet2 | dI_C_kurtosis | 306 | 301 | 0 | 5 | 0.0109004436 | 0.0146366463 | 0.409983602 | 0.44849081 | 0.602495331 |
| 5 | Sheet2 | dI_T_kurtosis | 306 | 301 | 0 | 5 | 0.319427625 | 0.782382052 | 0.280814606 | 0.410877279 | 16.1712535 |
| 5 | Sheet2 | dI_dI_devide_dt | 306 | 301 | 0 | 5 | 0.00440313309 | 0.0168759664 | 0.805133669 | 0.982396415 | 3.33739734 |
| 5 | Sheet2 | dI_entropy | 306 | 301 | 0 | 5 | 2.63077632 | 2.65743855 | 0.0282688566 | 0.291326709 | 48.7095435 |
| 5 | Sheet2 | Charge_energy | 306 | 306 | 0 | 0 | 0.0217505873 | 0.0590575949 | 0.988210493 | 0.988983913 | 0.300792305 |
| 5 | Sheet2 | Charge_Q | 306 | 306 | 0 | 0 | 0.00587994521 | 0.0157019724 | 0.98796578 | 0.986448841 | 0.322131813 |
| 5 | Sheet2 | Charge_t_mean | 306 | 306 | 0 | 0 | 2.19932872 | 8.59785349 | 0.863601785 | 0.997622799 | 9.77629814 |
| 5 | Sheet2 | Charge_V_mean | 306 | 306 | 0 | 0 | 0.0013546751 | 0.00245457714 | 0.99938023 | 0.998207474 | 0.0332398774 |
| 5 | Sheet2 | Charge_C_mean | 306 | 306 | 0 | 0 | 0.00332696745 | 0.00458285163 | 0.999974306 | 0.999549356 | 0.132070716 |
| 5 | Sheet2 | Charge_T_mean | 306 | 306 | 0 | 0 | 0.0117024454 | 0.0140289163 | 0.999990396 | 0.999884826 | 0.0458152218 |
| 5 | Sheet2 | Charge_C_std | 306 | 306 | 0 | 0 | 0.00116880679 | 0.00160636618 | 0.999998542 | 0.999663273 | 0.0505313925 |
| 5 | Sheet2 | Charge_V_std | 306 | 306 | 0 | 0 | 0.00204934184 | 0.00277486678 | 0.996909043 | 0.992678705 | 1.22024759 |
| 5 | Sheet2 | Charge_T_std | 306 | 306 | 0 | 0 | 0.00406513321 | 0.00975052711 | 0.999967369 | 0.999635631 | 0.130548681 |
| 5 | Sheet2 | Charge_C_skewness | 306 | 306 | 0 | 0 | 0.00449624466 | 0.00829946806 | 0.999923332 | 0.99952297 | 1.0693373 |
| 5 | Sheet2 | Charge_V_skewness | 306 | 306 | 0 | 0 | 0.030590784 | 0.037776451 | 0.997701169 | 0.995727674 | 2.82659358 |
| 5 | Sheet2 | Charge_T_skewness | 306 | 306 | 0 | 0 | 0.0521140155 | 0.213822405 | 0.837490738 | 0.946367884 | 24.0518946 |
| 5 | Sheet2 | Charge_C_kurtosis | 306 | 306 | 0 | 0 | 0.0186538109 | 0.0909664811 | 0.967957518 | 0.998475097 | 1.36355384 |
| 5 | Sheet2 | Charge_V_kurtosis | 306 | 306 | 0 | 0 | 0.191088666 | 0.370510321 | 0.944336692 | 0.985318461 | 6.5864003 |
| 5 | Sheet2 | Charge_T_kurtosis | 306 | 306 | 0 | 0 | 0.043196419 | 0.224415867 | 0.870542058 | 0.930602035 | 2.42037662 |
| 5 | Sheet3 | CC_energy | 339 | 339 | 0 | 0 | 0.0741568887 | 0.102091147 | 0.992569098 | 0.995507456 | 1.33767037 |
| 5 | Sheet3 | CC_Q | 339 | 339 | 0 | 0 | 0.0172147246 | 0.0210434124 | 0.997066587 | 0.996234087 | 1.21435172 |
| 5 | Sheet3 | CC_t_mean | 339 | 339 | 0 | 0 | 1.50110973 | 5.86632042 | 0.903210507 | 0.996869843 | 15.9129769 |
| 5 | Sheet3 | CC_V_mean | 339 | 339 | 0 | 0 | 0.00333481345 | 0.003936265 | 0.997502811 | 0.987243454 | 0.0852632839 |
| 5 | Sheet3 | CC_T_mean | 339 | 339 | 0 | 0 | 0.0392659031 | 0.0492736142 | 0.999922404 | 0.999108576 | 0.140881391 |
| 5 | Sheet3 | CC_V_std | 339 | 339 | 0 | 0 | 0.00223649905 | 0.00332386937 | 0.984075199 | 0.965514756 | 1.61756631 |
| 5 | Sheet3 | CC_T_std | 339 | 339 | 0 | 0 | 0.0176141642 | 0.0253470813 | 0.999799297 | 0.998155238 | 0.694692531 |
| 5 | Sheet3 | CC_V_skewness | 339 | 339 | 0 | 0 | 0.0735921946 | 0.0910676909 | 0.91874562 | 0.930410998 | 27.1554166 |
| 5 | Sheet3 | CC_T_skewness | 339 | 339 | 0 | 0 | 0.053723937 | 0.257918634 | 0.492733339 | 0.926200296 | 17.9937871 |
| 5 | Sheet3 | CC_V_kurtosis | 339 | 339 | 0 | 0 | 0.120666922 | 0.155871809 | 0.755418056 | 0.82081294 | 5.00973231 |
| 5 | Sheet3 | CC_T_kurtosis | 339 | 339 | 0 | 0 | 0.137760817 | 0.735549794 | 0.295942096 | 0.922158701 | 7.36647 |
| 5 | Sheet3 | CC_CCCT | 339 | 339 | 0 | 0 | 3.00283109 | 11.7391504 | 0.903083935 | 0.996865989 | 15.9182411 |
| 5 | Sheet3 | CC_entropy | 339 | 339 | 0 | 0 | 5.04392142 | 5.04450367 | 0.832902618 | 0.860369199 | 66.2358549 |
| 5 | Sheet3 | dV_energy | 339 | 339 | 0 | 0 | 0.00772298251 | 0.00871771505 | 0.999710365 | 0.992835955 | 0.657632571 |
| 5 | Sheet3 | dV_Q | 339 | 339 | 0 | 0 | 0.00195617094 | 0.00220850864 | 0.999710208 | 0.992611713 | 0.657306592 |
| 5 | Sheet3 | dV_t_mean | 339 | 339 | 0 | 0 | 0.165368211 | 0.652415679 | 0.869754988 | 0.990765857 | 9.38286537 |
| 5 | Sheet3 | dV_V_mean | 339 | 339 | 0 | 0 | 0.000141178468 | 0.000223923141 | 0.98744636 | 0.978037819 | 0.00357755215 |
| 5 | Sheet3 | dV_T_mean | 339 | 339 | 0 | 0 | 0.00766573624 | 0.00970567405 | 0.999994313 | 0.99986624 | 0.0264789107 |
| 5 | Sheet3 | dV_V_std | 339 | 339 | 0 | 0 | 0.000170002553 | 0.000194572811 | 0.74367273 | 0.632942655 | 0.594089662 |
| 5 | Sheet3 | dV_T_std | 339 | 339 | 0 | 0 | 0.00789140818 | 0.00993041445 | 0.999275008 | 0.997609723 | 1.46332668 |
| 5 | Sheet3 | dV_V_skewness | 339 | 339 | 0 | 0 | 0.00415069635 | 0.00796246992 | 0.991167891 | 0.987280109 | 2.59934554 |
| 5 | Sheet3 | dV_T_skewness | 339 | 339 | 0 | 0 | 0.228395835 | 1.18712705 | 0.328755002 | 0.825214846 | 101.048168 |
| 5 | Sheet3 | dV_V_kurtosis | 339 | 339 | 0 | 0 | 0.00421253143 | 0.00623970323 | 0.951680993 | 0.865488574 | 0.228644653 |
| 5 | Sheet3 | dV_T_kurtosis | 339 | 339 | 0 | 0 | 1.58484574 | 15.1904299 | 0.189268147 | 0.832015882 | 67.8691758 |
| 5 | Sheet3 | dV_dV_devide_dt | 339 | 339 | 0 | 0 | 0.000537915395 | 0.00194887019 | 0.970938145 | 0.992586002 | 1.83082554 |
| 5 | Sheet3 | dV_entropy | 339 | 339 | 0 | 0 | 4.65624843 | 4.65988772 | 0.481879272 | 0.356846374 | 62.7638383 |
| 5 | Sheet3 | CV_energy | 339 | 339 | 0 | 0 | 0.03675255 | 0.0435401934 | 0.997636054 | 0.989884152 | 2.31301779 |
| 5 | Sheet3 | CV_Q | 339 | 339 | 0 | 0 | 0.00875014583 | 0.0103660537 | 0.997636204 | 0.989884152 | 2.31289919 |
| 5 | Sheet3 | CV_t_mean | 339 | 339 | 0 | 0 | 0.127947184 | 0.414900463 | 0.987567139 | 0.997978258 | 0.944272412 |
| 5 | Sheet3 | CV_C_mean | 339 | 339 | 0 | 0 | 0.0264485853 | 0.0625054166 | 0.972479014 | 0.91503016 | 3.04811676 |
| 5 | Sheet3 | CV_T_mean | 339 | 339 | 0 | 0 | 0.0204526209 | 0.0252657693 | 0.999958737 | 0.999469273 | 0.081202785 |
| 5 | Sheet3 | CV_C_std | 339 | 339 | 0 | 0 | 0.0231900037 | 0.0283605714 | 0.997571122 | 0.780206315 | 2.11013738 |
| 5 | Sheet3 | CV_T_std | 339 | 339 | 0 | 0 | 0.0114321119 | 0.0144260616 | 0.999957043 | 0.998835666 | 0.337573349 |
| 5 | Sheet3 | CV_C_skewness | 339 | 339 | 0 | 0 | 0.0149183391 | 0.0199494595 | 0.998307784 | 0.987017363 | 0.718736754 |
| 5 | Sheet3 | CV_T_skewness | 339 | 339 | 0 | 0 | 0.0158338638 | 0.0528997808 | 0.787423421 | 0.957581492 | 2.47910572 |
| 5 | Sheet3 | CV_C_kurtosis | 339 | 339 | 0 | 0 | 0.0726830642 | 0.0955729561 | 0.997787767 | 0.987255159 | 1.05858998 |
| 5 | Sheet3 | CV_T_kurtosis | 339 | 339 | 0 | 0 | 0.0241237974 | 0.066375892 | 0.847784847 | 0.975414754 | 1.1976631 |
| 5 | Sheet3 | CV_CVCT | 339 | 339 | 0 | 0 | 0.242329836 | 0.794645705 | 0.988270018 | 0.998213685 | 0.894136253 |
| 5 | Sheet3 | CV_entropy | 339 | 339 | 0 | 0 | 4.64132051 | 4.64228296 | 0.997372853 | 0.93852463 | 72.3462477 |
| 5 | Sheet3 | dI_energy | 339 | 329 | 0 | 10 | 0.00138339457 | 0.00398836907 | 0.87455144 | 0.968487454 | 2.93803867 |
| 5 | Sheet3 | dI_Q | 339 | 329 | 0 | 10 | 0.000329386634 | 0.000949684583 | 0.874534249 | 0.968462518 | 2.9381041 |
| 5 | Sheet3 | dI_t_mean | 339 | 329 | 0 | 10 | 0.0106906048 | 0.0318357342 | 0.856672566 | 0.967469453 | 3.01260399 |
| 5 | Sheet3 | dI_C_mean | 339 | 329 | 0 | 10 | 0.00125443479 | 0.00567827886 | 0.269816174 | 0.748956073 | 0.132233687 |
| 5 | Sheet3 | dI_T_mean | 339 | 329 | 0 | 10 | 0.0153693504 | 0.0193689498 | 0.999959251 | 0.999648029 | 0.0555931969 |
| 5 | Sheet3 | dI_C_std | 339 | 329 | 0 | 10 | 0.000812884253 | 0.0035964572 | -0.265054442 | -0.00717588068 | 2.8066817 |
| 5 | Sheet3 | dI_T_std | 339 | 329 | 0 | 10 | 0.0127468221 | 0.0159818058 | 0.961273762 | 0.904144231 | 7.95430001 |
| 5 | Sheet3 | dI_C_skewness | 339 | 329 | 0 | 10 | 0.016431615 | 0.0422644377 | 0.584547232 | 0.745068709 | 28.571783 |
| 5 | Sheet3 | dI_T_skewness | 339 | 329 | 0 | 10 | 0.200084165 | 0.314038462 | 0.418526007 | 0.520984581 | 91.5893591 |
| 5 | Sheet3 | dI_C_kurtosis | 339 | 329 | 0 | 10 | 0.0104426077 | 0.0148877085 | 0.389251716 | 0.454416393 | 0.577916192 |
| 5 | Sheet3 | dI_T_kurtosis | 339 | 329 | 0 | 10 | 0.305961957 | 0.644776449 | 0.219868282 | 0.39512607 | 15.2936308 |
| 5 | Sheet3 | dI_dI_devide_dt | 339 | 329 | 0 | 10 | 0.00333082831 | 0.0128031268 | 0.857273642 | 0.979757223 | 2.36691288 |
| 5 | Sheet3 | dI_entropy | 339 | 329 | 0 | 10 | 2.60876564 | 2.61946782 | 0.181640474 | 0.107752868 | 48.495992 |
| 5 | Sheet3 | Charge_energy | 339 | 339 | 0 | 0 | 0.0149880282 | 0.0492099863 | 0.993351758 | 0.994720452 | 0.209980598 |
| 5 | Sheet3 | Charge_Q | 339 | 339 | 0 | 0 | 0.0042389139 | 0.0141118074 | 0.992172113 | 0.993963327 | 0.235725979 |
| 5 | Sheet3 | Charge_t_mean | 339 | 339 | 0 | 0 | 1.8255434 | 7.53152817 | 0.887999283 | 0.998801048 | 8.04428135 |
| 5 | Sheet3 | Charge_V_mean | 339 | 339 | 0 | 0 | 0.00119629771 | 0.00201416227 | 0.999592227 | 0.999233326 | 0.0293031156 |
| 5 | Sheet3 | Charge_C_mean | 339 | 339 | 0 | 0 | 0.00357216833 | 0.00572776336 | 0.999968544 | 0.999622654 | 0.145041829 |
| 5 | Sheet3 | Charge_T_mean | 339 | 339 | 0 | 0 | 0.0124563912 | 0.0140683267 | 0.999994231 | 0.99994548 | 0.0476378552 |
| 5 | Sheet3 | Charge_C_std | 339 | 339 | 0 | 0 | 0.00116881363 | 0.00150502795 | 0.999998775 | 0.999840751 | 0.0505815136 |
| 5 | Sheet3 | Charge_V_std | 339 | 339 | 0 | 0 | 0.00192979973 | 0.00241263121 | 0.998136283 | 0.995327877 | 1.19010481 |
| 5 | Sheet3 | Charge_T_std | 339 | 339 | 0 | 0 | 0.00322609128 | 0.00646552596 | 0.999986672 | 0.999838595 | 0.0956039527 |
| 5 | Sheet3 | Charge_C_skewness | 339 | 339 | 0 | 0 | 0.00393608472 | 0.00699114118 | 0.999947384 | 0.999713845 | 0.852389712 |
| 5 | Sheet3 | Charge_V_skewness | 339 | 339 | 0 | 0 | 0.0303768674 | 0.0368495267 | 0.99847097 | 0.997338356 | 2.63338439 |
| 5 | Sheet3 | Charge_T_skewness | 339 | 339 | 0 | 0 | 0.0335161301 | 0.165220879 | 0.897921461 | 0.979881349 | 13.2021546 |
| 5 | Sheet3 | Charge_C_kurtosis | 339 | 339 | 0 | 0 | 0.014641555 | 0.0698833225 | 0.976849644 | 0.999069149 | 1.04664259 |
| 5 | Sheet3 | Charge_V_kurtosis | 339 | 339 | 0 | 0 | 0.194054228 | 0.360825968 | 0.960164358 | 0.991337722 | 6.28662657 |
| 5 | Sheet3 | Charge_T_kurtosis | 339 | 339 | 0 | 0 | 0.0550591796 | 0.262705794 | 0.696851576 | 0.891367292 | 3.18268115 |
| 5 | Sheet4 | CC_energy | 251 | 251 | 0 | 0 | 0.0805379199 | 0.10670412 | 0.99249416 | 0.992251945 | 1.4357622 |
| 5 | Sheet4 | CC_Q | 251 | 251 | 0 | 0 | 0.0198197581 | 0.026913225 | 0.993284533 | 0.994045153 | 1.3809452 |
| 5 | Sheet4 | CC_t_mean | 251 | 251 | 0 | 0 | 1.05301212 | 4.23458413 | 0.950771099 | 0.993877021 | 9.79149974 |
| 5 | Sheet4 | CC_V_mean | 251 | 251 | 0 | 0 | 0.00352421884 | 0.00419078446 | 0.997631389 | 0.985257446 | 0.0900820243 |
| 5 | Sheet4 | CC_T_mean | 251 | 251 | 0 | 0 | 0.0350847989 | 0.0452742406 | 0.999915192 | 0.997441852 | 0.13277694 |
| 5 | Sheet4 | CC_V_std | 251 | 251 | 0 | 0 | 0.00249920342 | 0.00386689613 | 0.979586252 | 0.966025422 | 1.7910589 |
| 5 | Sheet4 | CC_T_std | 251 | 251 | 0 | 0 | 0.0159548922 | 0.0230946493 | 0.999796013 | 0.99824853 | 0.73910642 |
| 5 | Sheet4 | CC_V_skewness | 251 | 251 | 0 | 0 | 0.0813857523 | 0.107011057 | 0.9290004 | 0.937797002 | 28.8898397 |
| 5 | Sheet4 | CC_T_skewness | 251 | 251 | 0 | 0 | 0.0864120388 | 0.35841527 | 0.620853084 | 0.933794726 | 26.0582606 |
| 5 | Sheet4 | CC_V_kurtosis | 251 | 251 | 0 | 0 | 0.141367454 | 0.202807446 | 0.777332775 | 0.854970973 | 5.81986848 |
| 5 | Sheet4 | CC_T_kurtosis | 251 | 251 | 0 | 0 | 0.225948961 | 1.10902597 | 0.480699046 | 0.920755075 | 11.3839004 |
| 5 | Sheet4 | CC_CCCT | 251 | 251 | 0 | 0 | 2.10410735 | 8.46750836 | 0.950765272 | 0.99396827 | 9.78239285 |
| 5 | Sheet4 | CC_entropy | 251 | 251 | 0 | 0 | 5.04296997 | 5.04368017 | 0.835833418 | 0.833030544 | 66.2082709 |
| 5 | Sheet4 | dV_energy | 251 | 251 | 0 | 0 | 0.00766699637 | 0.00883014873 | 0.999715079 | 0.988744451 | 0.650103584 |
| 5 | Sheet4 | dV_Q | 251 | 251 | 0 | 0 | 0.00194498978 | 0.00223991444 | 0.999714275 | 0.988739139 | 0.650847064 |
| 5 | Sheet4 | dV_t_mean | 251 | 251 | 0 | 0 | 0.220823838 | 0.764188296 | 0.874848047 | 0.985361923 | 12.2222571 |
| 5 | Sheet4 | dV_V_mean | 251 | 251 | 0 | 0 | 0.00019140839 | 0.000470368366 | 0.968458879 | 0.979974957 | 0.00484995741 |
| 5 | Sheet4 | dV_T_mean | 251 | 251 | 0 | 0 | 0.00734347245 | 0.00927917208 | 0.999993786 | 0.999836843 | 0.026972677 |
| 5 | Sheet4 | dV_V_std | 251 | 251 | 0 | 0 | 0.000165329622 | 0.000190126682 | 0.775712768 | 0.637083665 | 0.577677336 |
| 5 | Sheet4 | dV_T_std | 251 | 251 | 0 | 0 | 0.00795903316 | 0.00992844359 | 0.999172777 | 0.99672472 | 1.64471478 |
| 5 | Sheet4 | dV_V_skewness | 251 | 251 | 0 | 0 | 0.00653159538 | 0.0206982915 | 0.967252534 | 0.991099222 | 4.38848341 |
| 5 | Sheet4 | dV_T_skewness | 251 | 251 | 0 | 0 | 0.13389105 | 0.446468873 | 0.620678628 | 0.836040979 | 57.5913013 |
| 5 | Sheet4 | dV_V_kurtosis | 251 | 251 | 0 | 0 | 0.00401824627 | 0.00568962063 | 0.96216325 | 0.895632707 | 0.218316157 |
| 5 | Sheet4 | dV_T_kurtosis | 251 | 251 | 0 | 0 | 0.321111555 | 1.55346833 | 0.810129904 | 0.799131095 | 13.8097073 |
| 5 | Sheet4 | dV_dV_devide_dt | 251 | 251 | 0 | 0 | 7.80636748e-05 | 0.00012136397 | 0.999860548 | 0.992538797 | 0.276805578 |
| 5 | Sheet4 | dV_entropy | 251 | 251 | 0 | 0 | 4.64351589 | 4.64810628 | 0.0306566691 | -0.11525624 | 62.6933267 |
| 5 | Sheet4 | CV_energy | 251 | 251 | 0 | 0 | 0.0366459194 | 0.0439055488 | 0.997604444 | 0.985376589 | 2.3560572 |
| 5 | Sheet4 | CV_Q | 251 | 251 | 0 | 0 | 0.00872493819 | 0.0104532216 | 0.997604462 | 0.985375071 | 2.35596844 |
| 5 | Sheet4 | CV_t_mean | 251 | 251 | 0 | 0 | 0.0699369972 | 0.115254363 | 0.999102307 | 0.997745391 | 0.487497817 |
| 5 | Sheet4 | CV_C_mean | 251 | 251 | 0 | 0 | 0.0118794711 | 0.0145350443 | 0.998509986 | 0.939414912 | 1.48684994 |
| 5 | Sheet4 | CV_T_mean | 251 | 251 | 0 | 0 | 0.0168179752 | 0.0211858153 | 0.999948917 | 0.998816164 | 0.0703003303 |
| 5 | Sheet4 | CV_C_std | 251 | 251 | 0 | 0 | 0.0231982566 | 0.0285412333 | 0.997496553 | 0.816547145 | 2.20961256 |
| 5 | Sheet4 | CV_T_std | 251 | 251 | 0 | 0 | 0.0107755514 | 0.0134003111 | 0.999953775 | 0.998039841 | 0.379048804 |
| 5 | Sheet4 | CV_C_skewness | 251 | 251 | 0 | 0 | 0.0149942518 | 0.0211136168 | 0.998779532 | 0.988084234 | 0.686972636 |
| 5 | Sheet4 | CV_T_skewness | 251 | 251 | 0 | 0 | 0.0164030874 | 0.0625487369 | 0.873634071 | 0.935614494 | 2.33935003 |
| 5 | Sheet4 | CV_C_kurtosis | 251 | 251 | 0 | 0 | 0.0745666334 | 0.101550256 | 0.998568055 | 0.989319674 | 1.00632888 |
| 5 | Sheet4 | CV_T_kurtosis | 251 | 251 | 0 | 0 | 0.0264447875 | 0.0805493806 | 0.920197128 | 0.974464613 | 1.24680645 |
| 5 | Sheet4 | CV_CVCT | 251 | 251 | 0 | 0 | 0.132815753 | 0.225625443 | 0.999115207 | 0.997904183 | 0.463022756 |
| 5 | Sheet4 | CV_entropy | 251 | 251 | 0 | 0 | 4.60757218 | 4.60941991 | 0.99533309 | 0.962942291 | 72.8503727 |
| 5 | Sheet4 | dI_energy | 251 | 240 | 0 | 11 | 0.00155904418 | 0.00446716122 | 0.919761989 | 0.951508707 | 3.56777361 |
| 5 | Sheet4 | dI_Q | 251 | 240 | 0 | 11 | 0.000371239381 | 0.00106378621 | 0.919735012 | 0.951513047 | 3.56812382 |
| 5 | Sheet4 | dI_t_mean | 251 | 240 | 0 | 11 | 0.0123142928 | 0.0358891253 | 0.909052977 | 0.951234396 | 3.73302093 |
| 5 | Sheet4 | dI_C_mean | 251 | 240 | 0 | 11 | 0.00140575039 | 0.00549545281 | 0.172954733 | 0.795170055 | 0.148399167 |
| 5 | Sheet4 | dI_T_mean | 251 | 240 | 0 | 11 | 0.0152479833 | 0.0189301646 | 0.999946502 | 0.997621485 | 0.0574979372 |
| 5 | Sheet4 | dI_C_std | 251 | 240 | 0 | 11 | 0.000909490049 | 0.00355024638 | -0.227030098 | 0.119383149 | 3.14503213 |
| 5 | Sheet4 | dI_T_std | 251 | 240 | 0 | 11 | 0.0119924942 | 0.0152086501 | 0.963147849 | 0.952499879 | 9.19637506 |
| 5 | Sheet4 | dI_C_skewness | 251 | 240 | 0 | 11 | 0.0199075066 | 0.0445745156 | 0.734056259 | 0.794480807 | 16.5198705 |
| 5 | Sheet4 | dI_T_skewness | 251 | 240 | 0 | 11 | 0.280594965 | 0.487973591 | 0.17265912 | 0.276567532 | 111.685326 |
| 5 | Sheet4 | dI_C_kurtosis | 251 | 240 | 0 | 11 | 0.0174348131 | 0.0228407106 | 0.561954485 | 0.597461761 | 0.95757626 |
| 5 | Sheet4 | dI_T_kurtosis | 251 | 240 | 0 | 11 | 0.390587241 | 1.01006325 | 0.137036533 | 0.303644708 | 19.3064346 |
| 5 | Sheet4 | dI_dI_devide_dt | 251 | 240 | 0 | 11 | 0.00273004109 | 0.0106865346 | 0.968071267 | 0.985580894 | 1.73048849 |
| 5 | Sheet4 | dI_entropy | 251 | 240 | 0 | 11 | 2.47797972 | 2.50526608 | -0.549221053 | -0.538461482 | 47.2539587 |
| 5 | Sheet4 | Charge_energy | 251 | 251 | 0 | 0 | 0.0181955561 | 0.0626144465 | 0.989480525 | 0.992167898 | 0.253685334 |
| 5 | Sheet4 | Charge_Q | 251 | 251 | 0 | 0 | 0.00482410815 | 0.0162074654 | 0.989832903 | 0.99064295 | 0.266935418 |
| 5 | Sheet4 | Charge_t_mean | 251 | 251 | 0 | 0 | 2.87697054 | 10.2854406 | 0.78027078 | 0.99276921 | 12.3797649 |
| 5 | Sheet4 | Charge_V_mean | 251 | 251 | 0 | 0 | 0.00127577522 | 0.00216522224 | 0.99955282 | 0.997936634 | 0.031255239 |
| 5 | Sheet4 | Charge_C_mean | 251 | 251 | 0 | 0 | 0.00315483271 | 0.00428782193 | 0.999976458 | 0.999438437 | 0.133315232 |
| 5 | Sheet4 | Charge_T_mean | 251 | 251 | 0 | 0 | 0.0100439351 | 0.0115708163 | 0.999993147 | 0.999877822 | 0.0405089748 |
| 5 | Sheet4 | Charge_C_std | 251 | 251 | 0 | 0 | 0.00127219644 | 0.00166465663 | 0.999998421 | 0.999663062 | 0.0561589374 |
| 5 | Sheet4 | Charge_V_std | 251 | 251 | 0 | 0 | 0.0021123816 | 0.00267843915 | 0.997892134 | 0.991584899 | 1.30737504 |
| 5 | Sheet4 | Charge_T_std | 251 | 251 | 0 | 0 | 0.00320067534 | 0.0059672408 | 0.999986178 | 0.999848226 | 0.111010211 |
| 5 | Sheet4 | Charge_C_skewness | 251 | 251 | 0 | 0 | 0.00423110163 | 0.00738804462 | 0.999946563 | 0.999508253 | 0.817430515 |
| 5 | Sheet4 | Charge_V_skewness | 251 | 251 | 0 | 0 | 0.0365775452 | 0.0502874962 | 0.997764443 | 0.995905141 | 3.0685683 |
| 5 | Sheet4 | Charge_T_skewness | 251 | 251 | 0 | 0 | 0.0264634876 | 0.124087949 | 0.956272984 | 0.990687915 | 8.74545022 |
| 5 | Sheet4 | Charge_C_kurtosis | 251 | 251 | 0 | 0 | 0.00623200447 | 0.0130255026 | 0.999654522 | 0.999546955 | 0.422921792 |
| 5 | Sheet4 | Charge_V_kurtosis | 251 | 251 | 0 | 0 | 0.336036742 | 0.968612676 | 0.863138464 | 0.983099222 | 10.3865957 |
| 5 | Sheet4 | Charge_T_kurtosis | 251 | 251 | 0 | 0 | 0.0386630857 | 0.212544449 | 0.868305857 | 0.938721305 | 2.14617434 |
| 5 | Sheet5 | CC_energy | 273 | 273 | 0 | 0 | 0.0752210987 | 0.0898851717 | 0.995943312 | 0.993895059 | 1.34120537 |
| 5 | Sheet5 | CC_Q | 273 | 273 | 0 | 0 | 0.0185751753 | 0.0226748569 | 0.996285835 | 0.995097056 | 1.2934875 |
| 5 | Sheet5 | CC_t_mean | 273 | 273 | 0 | 0 | 1.86313641 | 6.6128922 | 0.902944301 | 0.9947783 | 19.192869 |
| 5 | Sheet5 | CC_V_mean | 273 | 273 | 0 | 0 | 0.00344843392 | 0.00414520187 | 0.997076662 | 0.98500276 | 0.0882231105 |
| 5 | Sheet5 | CC_T_mean | 273 | 273 | 0 | 0 | 0.0362636081 | 0.0459783597 | 0.999920692 | 0.998540854 | 0.135450355 |
| 5 | Sheet5 | CC_V_std | 273 | 273 | 0 | 0 | 0.00256210693 | 0.00396864549 | 0.977600434 | 0.959345024 | 1.8235693 |
| 5 | Sheet5 | CC_T_std | 273 | 273 | 0 | 0 | 0.0168018637 | 0.0247897409 | 0.999802355 | 0.997930419 | 0.694650313 |
| 5 | Sheet5 | CC_V_skewness | 273 | 273 | 0 | 0 | 0.081682381 | 0.105483817 | 0.911050051 | 0.919908559 | 28.6896443 |
| 5 | Sheet5 | CC_T_skewness | 273 | 273 | 0 | 0 | 0.0599154361 | 0.286585837 | 0.506997704 | 0.926482384 | 16.5698664 |
| 5 | Sheet5 | CC_V_kurtosis | 273 | 273 | 0 | 0 | 0.139750875 | 0.193210282 | 0.705283638 | 0.814920803 | 5.72219657 |
| 5 | Sheet5 | CC_T_kurtosis | 273 | 273 | 0 | 0 | 0.144422184 | 0.804277939 | 0.252547295 | 0.936799622 | 7.44875583 |
| 5 | Sheet5 | CC_CCCT | 273 | 273 | 0 | 0 | 3.72776715 | 13.2314677 | 0.902809771 | 0.994975324 | 19.2019161 |
| 5 | Sheet5 | CC_entropy | 273 | 273 | 0 | 0 | 5.02493274 | 5.02573275 | 0.805719085 | 0.839386398 | 66.2373198 |
| 5 | Sheet5 | dV_energy | 273 | 273 | 0 | 0 | 0.00578775114 | 0.00702543453 | 0.999657473 | 0.982704339 | 0.505086727 |
| 5 | Sheet5 | dV_Q | 273 | 273 | 0 | 0 | 0.00146480188 | 0.00177873035 | 0.999657383 | 0.983059984 | 0.504433018 |
| 5 | Sheet5 | dV_t_mean | 273 | 273 | 0 | 0 | 0.19679346 | 0.715833 | 0.885523436 | 0.979142195 | 11.2106201 |
| 5 | Sheet5 | dV_V_mean | 273 | 273 | 0 | 0 | 0.00018252422 | 0.000328352507 | 0.97760653 | 0.967007606 | 0.00462522207 |
| 5 | Sheet5 | dV_T_mean | 273 | 273 | 0 | 0 | 0.00721117046 | 0.00920489753 | 0.999994677 | 0.999807728 | 0.0258982564 |
| 5 | Sheet5 | dV_V_std | 273 | 273 | 0 | 0 | 0.000126834813 | 0.000153309326 | 0.743071391 | 0.682680512 | 0.441940837 |
| 5 | Sheet5 | dV_T_std | 273 | 273 | 0 | 0 | 0.00720041108 | 0.00884690098 | 0.999366382 | 0.996935291 | 1.45938847 |
| 5 | Sheet5 | dV_V_skewness | 273 | 273 | 0 | 0 | 0.00510200669 | 0.012465653 | 0.982057973 | 0.982963848 | 3.24432579 |
| 5 | Sheet5 | dV_T_skewness | 273 | 273 | 0 | 0 | 0.148937059 | 0.697743328 | 0.302764432 | 0.812635772 | 64.969307 |
| 5 | Sheet5 | dV_V_kurtosis | 273 | 273 | 0 | 0 | 0.00414924084 | 0.00577391173 | 0.956584706 | 0.839591227 | 0.225527192 |
| 5 | Sheet5 | dV_T_kurtosis | 273 | 273 | 0 | 0 | 0.771772573 | 5.57866554 | 0.0871476123 | 0.86794916 | 34.1315429 |
| 5 | Sheet5 | dV_dV_devide_dt | 273 | 273 | 0 | 0 | 8.51185139e-05 | 0.000124327711 | 0.999883897 | 0.988579841 | 0.29125902 |
| 5 | Sheet5 | dV_entropy | 273 | 273 | 0 | 0 | 4.61835932 | 4.6226097 | 0.271822517 | -0.0349990526 | 62.5719679 |
| 5 | Sheet5 | CV_energy | 273 | 273 | 0 | 0 | 0.0391478801 | 0.0466014544 | 0.996804996 | 0.984138125 | 2.57896612 |
| 5 | Sheet5 | CV_Q | 273 | 273 | 0 | 0 | 0.00932100737 | 0.0110955528 | 0.996805026 | 0.98412161 | 2.5789034 |
| 5 | Sheet5 | CV_t_mean | 273 | 273 | 0 | 0 | 0.0943415817 | 0.219222955 | 0.996478039 | 0.997110514 | 0.670815282 |
| 5 | Sheet5 | CV_C_mean | 273 | 273 | 0 | 0 | 0.0133056794 | 0.0158738688 | 0.99817487 | 0.920739712 | 1.6737596 |
| 5 | Sheet5 | CV_T_mean | 273 | 273 | 0 | 0 | 0.0204247732 | 0.0253612788 | 0.999929638 | 0.998882344 | 0.0853696593 |
| 5 | Sheet5 | CV_C_std | 273 | 273 | 0 | 0 | 0.0261512578 | 0.031506407 | 0.996969862 | 0.756990809 | 2.49228173 |
| 5 | Sheet5 | CV_T_std | 273 | 273 | 0 | 0 | 0.0138229121 | 0.0170694348 | 0.999939341 | 0.997323522 | 0.444164619 |
| 5 | Sheet5 | CV_C_skewness | 273 | 273 | 0 | 0 | 0.0165723168 | 0.0221559702 | 0.998909341 | 0.984820514 | 0.75424965 |
| 5 | Sheet5 | CV_T_skewness | 273 | 273 | 0 | 0 | 0.0249249888 | 0.0983319485 | 0.725095698 | 0.920519583 | 3.31131458 |
| 5 | Sheet5 | CV_C_kurtosis | 273 | 273 | 0 | 0 | 0.0829291042 | 0.106765271 | 0.998668494 | 0.985179108 | 1.10673299 |
| 5 | Sheet5 | CV_T_kurtosis | 273 | 273 | 0 | 0 | 0.0396512922 | 0.130448913 | 0.869006382 | 0.959926559 | 1.80436485 |
| 5 | Sheet5 | CV_CVCT | 273 | 273 | 0 | 0 | 0.178932653 | 0.425431341 | 0.996651423 | 0.997309572 | 0.636242528 |
| 5 | Sheet5 | CV_entropy | 273 | 273 | 0 | 0 | 4.60276207 | 4.60433748 | 0.996470418 | 0.943931024 | 72.8891252 |
| 5 | Sheet5 | dI_energy | 273 | 262 | 0 | 11 | 0.00142819812 | 0.00376013139 | 0.918434008 | 0.975935232 | 3.39821778 |
| 5 | Sheet5 | dI_Q | 273 | 262 | 0 | 11 | 0.000340062521 | 0.000895283352 | 0.918434512 | 0.975909877 | 3.39825186 |
| 5 | Sheet5 | dI_t_mean | 273 | 262 | 0 | 11 | 0.0107195397 | 0.0289884756 | 0.914557622 | 0.97574056 | 3.38238289 |
| 5 | Sheet5 | dI_C_mean | 273 | 262 | 0 | 11 | 0.00139857993 | 0.00544758895 | 0.406003318 | 0.791878391 | 0.147586104 |
| 5 | Sheet5 | dI_T_mean | 273 | 262 | 0 | 11 | 0.016323111 | 0.0199149504 | 0.999948153 | 0.999326752 | 0.061183043 |
| 5 | Sheet5 | dI_C_std | 273 | 262 | 0 | 11 | 0.000922935141 | 0.0036524902 | -0.214625775 | -0.0475153391 | 3.18846616 |
| 5 | Sheet5 | dI_T_std | 273 | 262 | 0 | 11 | 0.0130341482 | 0.0160927343 | 0.955105644 | 0.925246881 | 9.14191923 |
| 5 | Sheet5 | dI_C_skewness | 273 | 262 | 0 | 11 | 0.0199559327 | 0.056487757 | 0.294547297 | 0.762440447 | 18.5809303 |
| 5 | Sheet5 | dI_T_skewness | 273 | 262 | 0 | 11 | 0.183465758 | 0.271582826 | 0.514289336 | 0.41517643 | 96.1020281 |
| 5 | Sheet5 | dI_C_kurtosis | 273 | 262 | 0 | 11 | 0.0182299962 | 0.0316499346 | 0.107830419 | 0.360010416 | 1.00331259 |
| 5 | Sheet5 | dI_T_kurtosis | 273 | 262 | 0 | 11 | 0.29330942 | 0.620742984 | -0.130489084 | 0.207438884 | 15.2913234 |
| 5 | Sheet5 | dI_dI_devide_dt | 273 | 262 | 0 | 11 | 0.00319142187 | 0.0133655133 | 0.926496088 | 0.950833504 | 1.98484256 |
| 5 | Sheet5 | dI_entropy | 273 | 262 | 0 | 11 | 2.44138163 | 2.45907063 | -0.43104524 | -0.345258952 | 46.8664029 |
| 5 | Sheet5 | Charge_energy | 273 | 273 | 0 | 0 | 0.0174986946 | 0.0461839894 | 0.994066364 | 0.992281973 | 0.245259167 |
| 5 | Sheet5 | Charge_Q | 273 | 273 | 0 | 0 | 0.0047236239 | 0.0120924709 | 0.994293409 | 0.989527051 | 0.262516952 |
| 5 | Sheet5 | Charge_t_mean | 273 | 273 | 0 | 0 | 2.28884235 | 8.48444289 | 0.887951088 | 0.998591612 | 9.80608325 |
| 5 | Sheet5 | Charge_V_mean | 273 | 273 | 0 | 0 | 0.00130654395 | 0.00228560912 | 0.99947013 | 0.997994116 | 0.0320194255 |
| 5 | Sheet5 | Charge_C_mean | 273 | 273 | 0 | 0 | 0.00309664172 | 0.00438762401 | 0.999975004 | 0.999436159 | 0.129312344 |
| 5 | Sheet5 | Charge_T_mean | 273 | 273 | 0 | 0 | 0.0109253543 | 0.0126269082 | 0.999992153 | 0.999905043 | 0.0438313635 |
| 5 | Sheet5 | Charge_C_std | 273 | 273 | 0 | 0 | 0.00117264043 | 0.00158939584 | 0.999998529 | 0.999705694 | 0.0512587477 |
| 5 | Sheet5 | Charge_V_std | 273 | 273 | 0 | 0 | 0.00213080503 | 0.00273839189 | 0.997483694 | 0.992583951 | 1.30109913 |
| 5 | Sheet5 | Charge_T_std | 273 | 273 | 0 | 0 | 0.00305256374 | 0.00594514176 | 0.99998879 | 0.99980006 | 0.0956532592 |
| 5 | Sheet5 | Charge_C_skewness | 273 | 273 | 0 | 0 | 0.00432292584 | 0.00781680163 | 0.999938398 | 0.999393104 | 0.873604033 |
| 5 | Sheet5 | Charge_V_skewness | 273 | 273 | 0 | 0 | 0.0354571159 | 0.0450415417 | 0.997793072 | 0.996000028 | 3.04427063 |
| 5 | Sheet5 | Charge_T_skewness | 273 | 273 | 0 | 0 | 0.0363311464 | 0.180940174 | 0.897179014 | 0.978136398 | 12.1728893 |
| 5 | Sheet5 | Charge_C_kurtosis | 273 | 273 | 0 | 0 | 0.0140802131 | 0.0663684434 | 0.982231996 | 0.998454154 | 0.983494636 |
| 5 | Sheet5 | Charge_V_kurtosis | 273 | 273 | 0 | 0 | 0.279363008 | 0.695296277 | 0.899816196 | 0.983182071 | 8.90133972 |
| 5 | Sheet5 | Charge_T_kurtosis | 273 | 273 | 0 | 0 | 0.0498557383 | 0.255581045 | 0.732269264 | 0.936856831 | 2.86591292 |
| 5 | Sheet6 | CC_energy | 218 | 218 | 0 | 0 | 0.0766059014 | 0.0978433906 | 0.994000137 | 0.993532055 | 1.3678595 |
| 5 | Sheet6 | CC_Q | 218 | 218 | 0 | 0 | 0.0188844177 | 0.0251794645 | 0.994110671 | 0.993591128 | 1.31784721 |
| 5 | Sheet6 | CC_t_mean | 218 | 218 | 0 | 0 | 0.387479071 | 1.87063407 | 0.989402393 | 0.995083886 | 3.26508189 |
| 5 | Sheet6 | CC_V_mean | 218 | 218 | 0 | 0 | 0.00343985919 | 0.00403120725 | 0.997877002 | 0.985359093 | 0.0879238281 |
| 5 | Sheet6 | CC_T_mean | 218 | 218 | 0 | 0 | 0.0312733706 | 0.0403801239 | 0.999921918 | 0.997171432 | 0.121017726 |
| 5 | Sheet6 | CC_V_std | 218 | 218 | 0 | 0 | 0.0022930943 | 0.00354625422 | 0.983007486 | 0.975118566 | 1.64536714 |
| 5 | Sheet6 | CC_T_std | 218 | 218 | 0 | 0 | 0.0127349255 | 0.0180614452 | 0.999868188 | 0.998333207 | 0.644818491 |
| 5 | Sheet6 | CC_V_skewness | 218 | 218 | 0 | 0 | 0.0774653265 | 0.100555672 | 0.928249171 | 0.944574206 | 28.5524185 |
| 5 | Sheet6 | CC_T_skewness | 218 | 218 | 0 | 0 | 0.0639874739 | 0.228749892 | 0.709591391 | 0.916950185 | 20.026754 |
| 5 | Sheet6 | CC_V_kurtosis | 218 | 218 | 0 | 0 | 0.127816739 | 0.176451013 | 0.747063565 | 0.835194817 | 5.35586363 |
| 5 | Sheet6 | CC_T_kurtosis | 218 | 218 | 0 | 0 | 0.162817255 | 0.68027444 | 0.52647591 | 0.951420611 | 8.46010733 |
| 5 | Sheet6 | CC_CCCT | 218 | 218 | 0 | 0 | 0.772941631 | 3.74335219 | 0.989397736 | 0.995168436 | 3.25704513 |
| 5 | Sheet6 | CC_entropy | 218 | 218 | 0 | 0 | 5.05148214 | 5.05214714 | 0.832722057 | 0.836082801 | 66.1809722 |
| 5 | Sheet6 | dV_energy | 218 | 218 | 0 | 0 | 0.00722497546 | 0.00831455269 | 0.999825506 | 0.992446728 | 0.612104132 |
| 5 | Sheet6 | dV_Q | 218 | 218 | 0 | 0 | 0.00183248677 | 0.0021080721 | 0.999825551 | 0.992374914 | 0.61269299 |
| 5 | Sheet6 | dV_t_mean | 218 | 218 | 0 | 0 | 0.248233626 | 0.80814689 | 0.885964138 | 0.990838449 | 13.5504515 |
| 5 | Sheet6 | dV_V_mean | 218 | 218 | 0 | 0 | 0.000207881156 | 0.000598640132 | 0.944328892 | 0.9792812 | 0.00526727846 |
| 5 | Sheet6 | dV_T_mean | 218 | 218 | 0 | 0 | 0.00707541597 | 0.00911123868 | 0.999993126 | 0.999812066 | 0.0266398706 |
| 5 | Sheet6 | dV_V_std | 218 | 218 | 0 | 0 | 0.000159095689 | 0.000183720028 | 0.816104442 | 0.69553516 | 0.555799092 |
| 5 | Sheet6 | dV_T_std | 218 | 218 | 0 | 0 | 0.00736005009 | 0.00939816455 | 0.999288127 | 0.996377993 | 1.65581143 |
| 5 | Sheet6 | dV_V_skewness | 218 | 218 | 0 | 0 | 0.00598898107 | 0.0212605658 | 0.961835053 | 0.992634373 | 4.1354206 |
| 5 | Sheet6 | dV_T_skewness | 218 | 218 | 0 | 0 | 0.209959077 | 1.13004788 | 0.365461524 | 0.821020498 | 81.7062539 |
| 5 | Sheet6 | dV_V_kurtosis | 218 | 218 | 0 | 0 | 0.00376509486 | 0.00521614415 | 0.969321577 | 0.916864205 | 0.204712006 |
| 5 | Sheet6 | dV_T_kurtosis | 218 | 218 | 0 | 0 | 1.89957412 | 18.1964362 | 0.00532681772 | 0.766573404 | 72.0358803 |
| 5 | Sheet6 | dV_dV_devide_dt | 218 | 218 | 0 | 0 | 7.11222526e-05 | 0.000104214662 | 0.999924694 | 0.995121527 | 0.256311863 |
| 5 | Sheet6 | dV_entropy | 218 | 218 | 0 | 0 | 4.70010416 | 4.70322965 | 0.216385338 | 0.0344094393 | 62.9719869 |
| 5 | Sheet6 | CV_energy | 218 | 218 | 0 | 0 | 0.0393291569 | 0.0468017743 | 0.997656066 | 0.985908127 | 2.55645869 |
| 5 | Sheet6 | CV_Q | 218 | 218 | 0 | 0 | 0.0093639813 | 0.0111431151 | 0.99765605 | 0.985897702 | 2.55637112 |
| 5 | Sheet6 | CV_t_mean | 218 | 218 | 0 | 0 | 0.081236766 | 0.137791877 | 0.998563389 | 0.998519685 | 0.553617052 |
| 5 | Sheet6 | CV_C_mean | 218 | 218 | 0 | 0 | 0.0124134343 | 0.0149985159 | 0.998588903 | 0.939711664 | 1.60758564 |
| 5 | Sheet6 | CV_T_mean | 218 | 218 | 0 | 0 | 0.0165185194 | 0.0204669547 | 0.999943691 | 0.998970272 | 0.0705038638 |
| 5 | Sheet6 | CV_C_std | 218 | 218 | 0 | 0 | 0.0247450517 | 0.0301484051 | 0.997625471 | 0.796959348 | 2.40661204 |
| 5 | Sheet6 | CV_T_std | 218 | 218 | 0 | 0 | 0.0115616141 | 0.0139881646 | 0.999950004 | 0.99776564 | 0.448194849 |
| 5 | Sheet6 | CV_C_skewness | 218 | 218 | 0 | 0 | 0.0155217683 | 0.0222080103 | 0.998882077 | 0.986504651 | 0.697366479 |
| 5 | Sheet6 | CV_T_skewness | 218 | 218 | 0 | 0 | 0.0230274229 | 0.0791021522 | 0.824443144 | 0.928843339 | 3.00523369 |
| 5 | Sheet6 | CV_C_kurtosis | 218 | 218 | 0 | 0 | 0.0799832826 | 0.108935662 | 0.998651689 | 0.986888049 | 1.0489123 |
| 5 | Sheet6 | CV_T_kurtosis | 218 | 218 | 0 | 0 | 0.0332937144 | 0.0988072108 | 0.909873384 | 0.979405433 | 1.50496783 |
| 5 | Sheet6 | CV_CVCT | 218 | 218 | 0 | 0 | 0.154020847 | 0.272926411 | 0.998552988 | 0.998501151 | 0.524974252 |
| 5 | Sheet6 | CV_entropy | 218 | 218 | 0 | 0 | 4.59730448 | 4.59944064 | 0.994131312 | 0.974051649 | 73.1164289 |
| 5 | Sheet6 | dI_energy | 218 | 206 | 0 | 12 | 0.00163803641 | 0.00404428351 | 0.813387538 | 0.916398781 | 4.66899245 |
| 5 | Sheet6 | dI_Q | 218 | 206 | 0 | 12 | 0.000390027497 | 0.000962999499 | 0.813370877 | 0.916372699 | 4.66909641 |
| 5 | Sheet6 | dI_t_mean | 218 | 206 | 0 | 12 | 0.012210897 | 0.0300015889 | 0.818781667 | 0.919767498 | 4.61977879 |
| 5 | Sheet6 | dI_C_mean | 218 | 206 | 0 | 12 | 0.001470484 | 0.00506177508 | -0.551385363 | 0.471302426 | 0.155094809 |
| 5 | Sheet6 | dI_T_mean | 218 | 206 | 0 | 12 | 0.015198047 | 0.0192338548 | 0.999936104 | 0.998600829 | 0.0584778257 |
| 5 | Sheet6 | dI_C_std | 218 | 206 | 0 | 12 | 0.000862964589 | 0.00331941182 | -0.790015444 | 0.118513221 | 2.96118813 |
| 5 | Sheet6 | dI_T_std | 218 | 206 | 0 | 12 | 0.0120232676 | 0.0151709058 | 0.920116051 | 0.867659923 | 11.8207251 |
| 5 | Sheet6 | dI_C_skewness | 218 | 206 | 0 | 12 | 0.0139170152 | 0.0191293674 | 0.850534616 | 0.886110225 | 16.53467 |
| 5 | Sheet6 | dI_T_skewness | 218 | 206 | 0 | 12 | 0.296020227 | 0.431469083 | 0.217283271 | 0.325930059 | 102.441248 |
| 5 | Sheet6 | dI_C_kurtosis | 218 | 206 | 0 | 12 | 0.0268726845 | 0.043051546 | 0.127855913 | 0.217903338 | 1.49366138 |
| 5 | Sheet6 | dI_T_kurtosis | 218 | 206 | 0 | 12 | 0.408727908 | 0.776562368 | -0.00378793725 | 0.269482288 | 19.8223633 |
| 5 | Sheet6 | dI_dI_devide_dt | 218 | 206 | 0 | 12 | 0.00239368263 | 0.00684886258 | 0.977494662 | 0.948630084 | 1.27482406 |
| 5 | Sheet6 | dI_entropy | 218 | 206 | 0 | 12 | 2.18430575 | 2.19867444 | -0.210713194 | -0.242980925 | 44.1006826 |
| 5 | Sheet6 | Charge_energy | 218 | 218 | 0 | 0 | 0.0152765234 | 0.0461142877 | 0.993890694 | 0.993178766 | 0.213802921 |
| 5 | Sheet6 | Charge_Q | 218 | 218 | 0 | 0 | 0.0038760941 | 0.0111923752 | 0.994772145 | 0.990965263 | 0.215297355 |
| 5 | Sheet6 | Charge_t_mean | 218 | 218 | 0 | 0 | 0.382458701 | 2.22135935 | 0.989153409 | 0.998626241 | 1.44383115 |
| 5 | Sheet6 | Charge_V_mean | 218 | 218 | 0 | 0 | 0.00120898304 | 0.00199980985 | 0.999632226 | 0.998589191 | 0.0296193111 |
| 5 | Sheet6 | Charge_C_mean | 218 | 218 | 0 | 0 | 0.00301091792 | 0.0040666258 | 0.999978946 | 0.999630502 | 0.130490585 |
| 5 | Sheet6 | Charge_T_mean | 218 | 218 | 0 | 0 | 0.00864141892 | 0.00988436572 | 0.999994756 | 0.99989112 | 0.0356267846 |
| 5 | Sheet6 | Charge_C_std | 218 | 218 | 0 | 0 | 0.00124710593 | 0.00162162964 | 0.999998578 | 0.999617761 | 0.0556627822 |
| 5 | Sheet6 | Charge_V_std | 218 | 218 | 0 | 0 | 0.00201864175 | 0.00251575972 | 0.998238038 | 0.992875299 | 1.25374256 |
| 5 | Sheet6 | Charge_T_std | 218 | 218 | 0 | 0 | 0.00244955818 | 0.00393155469 | 0.999993468 | 0.999730116 | 0.0925385317 |
| 5 | Sheet6 | Charge_C_skewness | 218 | 218 | 0 | 0 | 0.00409045422 | 0.00692009824 | 0.99995554 | 0.999567954 | 0.742942141 |
| 5 | Sheet6 | Charge_V_skewness | 218 | 218 | 0 | 0 | 0.0334625862 | 0.0428780442 | 0.998411676 | 0.995899619 | 2.7990667 |
| 5 | Sheet6 | Charge_T_skewness | 218 | 218 | 0 | 0 | 0.0114963107 | 0.041100258 | 0.996014547 | 0.998976063 | 3.22196395 |
| 5 | Sheet6 | Charge_C_kurtosis | 218 | 218 | 0 | 0 | 0.00609936704 | 0.0120467124 | 0.999691114 | 0.999483398 | 0.406846838 |
| 5 | Sheet6 | Charge_V_kurtosis | 218 | 218 | 0 | 0 | 0.268924905 | 0.684248352 | 0.917935153 | 0.987956001 | 8.2191373 |
| 5 | Sheet6 | Charge_T_kurtosis | 218 | 218 | 0 | 0 | 0.0269407902 | 0.158146367 | 0.922722373 | 0.981272612 | 1.48299471 |
| 5 | Sheet7 | CC_energy | 185 | 185 | 0 | 0 | 0.0885884342 | 0.119176131 | 0.989406394 | 0.992695501 | 1.57037646 |
| 5 | Sheet7 | CC_Q | 185 | 185 | 0 | 0 | 0.0209948757 | 0.0280805029 | 0.99231967 | 0.993953982 | 1.45496815 |
| 5 | Sheet7 | CC_t_mean | 185 | 185 | 0 | 0 | 0.156977101 | 0.235442525 | 0.999936323 | 0.995410518 | 1.22438887 |
| 5 | Sheet7 | CC_V_mean | 185 | 185 | 0 | 0 | 0.00364988767 | 0.00423454465 | 0.997816615 | 0.983237936 | 0.093322575 |
| 5 | Sheet7 | CC_T_mean | 185 | 185 | 0 | 0 | 0.0290321742 | 0.0371677574 | 0.999923489 | 0.997208218 | 0.116739168 |
| 5 | Sheet7 | CC_V_std | 185 | 185 | 0 | 0 | 0.00258340255 | 0.00391433833 | 0.980234503 | 0.974309162 | 1.835183 |
| 5 | Sheet7 | CC_T_std | 185 | 185 | 0 | 0 | 0.0131936751 | 0.01827576 | 0.99984014 | 0.997592965 | 0.787410703 |
| 5 | Sheet7 | CC_V_skewness | 185 | 185 | 0 | 0 | 0.0813637809 | 0.105225212 | 0.923977202 | 0.945422842 | 30.6736188 |
| 5 | Sheet7 | CC_T_skewness | 185 | 185 | 0 | 0 | 0.0478574041 | 0.186579614 | 0.630291917 | 0.899186915 | 15.8528214 |
| 5 | Sheet7 | CC_V_kurtosis | 185 | 185 | 0 | 0 | 0.136884434 | 0.188887801 | 0.728115825 | 0.835076381 | 5.70218246 |
| 5 | Sheet7 | CC_T_kurtosis | 185 | 185 | 0 | 0 | 0.0895234297 | 0.391948168 | 0.663987036 | 0.91920511 | 4.6799982 |
| 5 | Sheet7 | CC_CCCT | 185 | 185 | 0 | 0 | 0.311690956 | 0.467012226 | 0.999935792 | 0.995563554 | 1.21568282 |
| 5 | Sheet7 | CC_entropy | 185 | 185 | 0 | 0 | 5.04716506 | 5.04792066 | 0.83111591 | 0.831635851 | 66.1713962 |
| 5 | Sheet7 | dV_energy | 185 | 185 | 0 | 0 | 0.00506515636 | 0.00632349075 | 0.999850277 | 0.993766347 | 0.427534038 |
| 5 | Sheet7 | dV_Q | 185 | 185 | 0 | 0 | 0.00128369867 | 0.00160354641 | 0.999849812 | 0.993728441 | 0.427624949 |
| 5 | Sheet7 | dV_t_mean | 185 | 185 | 0 | 0 | 0.00841103844 | 0.0109500904 | 0.99997579 | 0.993554073 | 0.391225572 |
| 5 | Sheet7 | dV_V_mean | 185 | 185 | 0 | 0 | 0.000179951604 | 0.000468462941 | 0.964457738 | 0.974635154 | 0.00455948273 |
| 5 | Sheet7 | dV_T_mean | 185 | 185 | 0 | 0 | 0.0068633086 | 0.00912777423 | 0.999991039 | 0.999813786 | 0.0269384691 |
| 5 | Sheet7 | dV_V_std | 185 | 185 | 0 | 0 | 0.000103991992 | 0.000130883921 | 0.83490933 | 0.784612031 | 0.362466219 |
| 5 | Sheet7 | dV_T_std | 185 | 185 | 0 | 0 | 0.00709279258 | 0.00888944793 | 0.999104965 | 0.994909605 | 1.84358787 |
| 5 | Sheet7 | dV_V_skewness | 185 | 185 | 0 | 0 | 0.00522563152 | 0.0161227755 | 0.976925907 | 0.984200751 | 3.71612377 |
| 5 | Sheet7 | dV_T_skewness | 185 | 185 | 0 | 0 | 0.21219132 | 0.864816386 | 0.382064714 | 0.791683172 | 73.1876099 |
| 5 | Sheet7 | dV_V_kurtosis | 185 | 185 | 0 | 0 | 0.00350897995 | 0.00477078984 | 0.974708892 | 0.923535878 | 0.190918724 |
| 5 | Sheet7 | dV_T_kurtosis | 185 | 185 | 0 | 0 | 4.01901536 | 24.1789995 | 0.0320758656 | 0.650529439 | 74.0754786 |
| 5 | Sheet7 | dV_dV_devide_dt | 185 | 185 | 0 | 0 | 5.99321527e-05 | 7.69642754e-05 | 0.999969588 | 0.997318138 | 0.220501748 |
| 5 | Sheet7 | dV_entropy | 185 | 185 | 0 | 0 | 4.72423217 | 4.72705858 | 0.281561129 | -0.000812207567 | 63.0872229 |
| 5 | Sheet7 | CV_energy | 185 | 185 | 0 | 0 | 0.0352807061 | 0.0432521965 | 0.997751497 | 0.985957697 | 2.3208426 |
| 5 | Sheet7 | CV_Q | 185 | 185 | 0 | 0 | 0.00839984742 | 0.0102976578 | 0.997751583 | 0.985957697 | 2.32074801 |
| 5 | Sheet7 | CV_t_mean | 185 | 185 | 0 | 0 | 0.0734560738 | 0.119654469 | 0.999042886 | 0.998086682 | 0.48699245 |
| 5 | Sheet7 | CV_C_mean | 185 | 185 | 0 | 0 | 0.0109828701 | 0.0135357555 | 0.998639481 | 0.953538532 | 1.47385302 |
| 5 | Sheet7 | CV_T_mean | 185 | 185 | 0 | 0 | 0.012715659 | 0.0161086214 | 0.999954101 | 0.99931011 | 0.0554138516 |
| 5 | Sheet7 | CV_C_std | 185 | 185 | 0 | 0 | 0.0223890263 | 0.0277762059 | 0.997664358 | 0.817150601 | 2.23489139 |
| 5 | Sheet7 | CV_T_std | 185 | 185 | 0 | 0 | 0.00834867362 | 0.0108018477 | 0.999950261 | 0.997718055 | 0.385956053 |
| 5 | Sheet7 | CV_C_skewness | 185 | 185 | 0 | 0 | 0.0149389426 | 0.0203126748 | 0.999095685 | 0.990614457 | 0.659169468 |
| 5 | Sheet7 | CV_T_skewness | 185 | 185 | 0 | 0 | 0.0155914433 | 0.0580957204 | 0.907149715 | 0.970821804 | 2.06524787 |
| 5 | Sheet7 | CV_C_kurtosis | 185 | 185 | 0 | 0 | 0.0775932491 | 0.100302866 | 0.99890306 | 0.990593609 | 0.989935388 |
| 5 | Sheet7 | CV_T_kurtosis | 185 | 185 | 0 | 0 | 0.0251030776 | 0.0650204351 | 0.96113745 | 0.993758766 | 1.13665128 |
| 5 | Sheet7 | CV_CVCT | 185 | 185 | 0 | 0 | 0.138625706 | 0.234659162 | 0.999053 | 0.998117951 | 0.459648226 |
| 5 | Sheet7 | CV_entropy | 185 | 185 | 0 | 0 | 4.58751199 | 4.58979408 | 0.995214835 | 0.975059681 | 73.3723756 |
| 5 | Sheet7 | dI_energy | 185 | 175 | 0 | 10 | 0.00255963275 | 0.00707899156 | 0.624214308 | 0.887094093 | 8.14584389 |
| 5 | Sheet7 | dI_Q | 185 | 175 | 0 | 10 | 0.000609462478 | 0.00168559488 | 0.624190254 | 0.887094093 | 8.1461681 |
| 5 | Sheet7 | dI_t_mean | 185 | 175 | 0 | 10 | 0.0202906657 | 0.0563252621 | 0.596952627 | 0.886530325 | 8.58973345 |
| 5 | Sheet7 | dI_C_mean | 185 | 175 | 0 | 10 | 0.00211494006 | 0.00743869939 | 0.358551288 | 0.416383789 | 0.223043031 |
| 5 | Sheet7 | dI_T_mean | 185 | 175 | 0 | 10 | 0.0146125624 | 0.018818887 | 0.999936786 | 0.997583946 | 0.0578505694 |
| 5 | Sheet7 | dI_C_std | 185 | 175 | 0 | 10 | 0.00138640601 | 0.004721588 | -0.0109970739 | -0.128210927 | 4.78856882 |
| 5 | Sheet7 | dI_T_std | 185 | 175 | 0 | 10 | 0.0126871132 | 0.0159011001 | 0.880457209 | 0.783062285 | 15.8139737 |
| 5 | Sheet7 | dI_C_skewness | 185 | 175 | 0 | 10 | 0.031916544 | 0.0699536702 | -0.348864966 | 0.310564263 | 40.4843871 |
| 5 | Sheet7 | dI_T_skewness | 185 | 175 | 0 | 10 | 0.41107786 | 1.07401179 | 0.0655662994 | 0.35494547 | 114.750153 |
| 5 | Sheet7 | dI_C_kurtosis | 185 | 175 | 0 | 10 | 0.0274256922 | 0.0400721145 | -0.0552166796 | -0.059927295 | 1.51587728 |
| 5 | Sheet7 | dI_T_kurtosis | 185 | 175 | 0 | 10 | 1.36732768 | 11.3253117 | -0.0284848853 | 0.231907051 | 63.2287011 |
| 5 | Sheet7 | dI_dI_devide_dt | 185 | 175 | 0 | 10 | 0.00534375291 | 0.0180935429 | 0.867157038 | 0.848921991 | 2.56143485 |
| 5 | Sheet7 | dI_entropy | 185 | 175 | 0 | 10 | 2.0411853 | 2.05452951 | 0.0674803586 | -0.00792662961 | 42.4258969 |
| 5 | Sheet7 | Charge_energy | 185 | 185 | 0 | 0 | 0.0185722147 | 0.0619416474 | 0.987540929 | 0.991558318 | 0.259191719 |
| 5 | Sheet7 | Charge_Q | 185 | 185 | 0 | 0 | 0.00572673838 | 0.0184966996 | 0.984093537 | 0.988254805 | 0.316873362 |
| 5 | Sheet7 | Charge_t_mean | 185 | 185 | 0 | 0 | 0.0486736226 | 0.14227105 | 0.999961626 | 0.999217712 | 0.174316682 |
| 5 | Sheet7 | Charge_V_mean | 185 | 185 | 0 | 0 | 0.00123860278 | 0.00207381901 | 0.999612218 | 0.997509571 | 0.0303547754 |
| 5 | Sheet7 | Charge_C_mean | 185 | 185 | 0 | 0 | 0.00331220088 | 0.00464568422 | 0.999972847 | 0.999478792 | 0.147035234 |
| 5 | Sheet7 | Charge_T_mean | 185 | 185 | 0 | 0 | 0.00752633298 | 0.00877013286 | 0.999994338 | 0.999888177 | 0.0318895828 |
| 5 | Sheet7 | Charge_C_std | 185 | 185 | 0 | 0 | 0.00129199846 | 0.00170553283 | 0.999998335 | 0.999522384 | 0.0585084194 |
| 5 | Sheet7 | Charge_V_std | 185 | 185 | 0 | 0 | 0.00208928355 | 0.0026247417 | 0.997997083 | 0.991865358 | 1.29027395 |
| 5 | Sheet7 | Charge_T_std | 185 | 185 | 0 | 0 | 0.00230911753 | 0.00410192449 | 0.999990468 | 0.999535651 | 0.104630591 |
| 5 | Sheet7 | Charge_C_skewness | 185 | 185 | 0 | 0 | 0.00429934946 | 0.0072142958 | 0.999951398 | 0.999334748 | 0.74821027 |
| 5 | Sheet7 | Charge_V_skewness | 185 | 185 | 0 | 0 | 0.0356343357 | 0.0459832531 | 0.998107426 | 0.993790986 | 2.96533115 |
| 5 | Sheet7 | Charge_T_skewness | 185 | 185 | 0 | 0 | 0.0191848597 | 0.118039453 | 0.966614022 | 0.994876995 | 5.21503022 |
| 5 | Sheet7 | Charge_C_kurtosis | 185 | 185 | 0 | 0 | 0.00629034405 | 0.0122777296 | 0.999637742 | 0.999414351 | 0.414713523 |
| 5 | Sheet7 | Charge_V_kurtosis | 185 | 185 | 0 | 0 | 0.264468574 | 0.560315424 | 0.948081639 | 0.986950836 | 7.90664446 |
| 5 | Sheet7 | Charge_T_kurtosis | 185 | 185 | 0 | 0 | 0.0365373899 | 0.199410296 | 0.851858511 | 0.948351086 | 2.02446308 |
| 5 | Sheet8 | CC_energy | 207 | 207 | 0 | 0 | 0.0808420838 | 0.118911411 | 0.990649975 | 0.994486747 | 1.45064292 |
| 5 | Sheet8 | CC_Q | 207 | 207 | 0 | 0 | 0.0199655962 | 0.0307033276 | 0.991160733 | 0.995022513 | 1.40017038 |
| 5 | Sheet8 | CC_t_mean | 207 | 207 | 0 | 0 | 0.226243106 | 1.07477219 | 0.996578442 | 0.995750398 | 1.85058003 |
| 5 | Sheet8 | CC_V_mean | 207 | 207 | 0 | 0 | 0.00351582137 | 0.00421641344 | 0.997904693 | 0.985025598 | 0.0898450586 |
| 5 | Sheet8 | CC_T_mean | 207 | 207 | 0 | 0 | 0.0344356443 | 0.0448199592 | 0.999910797 | 0.99760258 | 0.132941178 |
| 5 | Sheet8 | CC_V_std | 207 | 207 | 0 | 0 | 0.00246997979 | 0.00386012561 | 0.980277461 | 0.97117414 | 1.76329517 |
| 5 | Sheet8 | CC_T_std | 207 | 207 | 0 | 0 | 0.0133044332 | 0.0196082331 | 0.99984501 | 0.997146638 | 0.64379093 |
| 5 | Sheet8 | CC_V_skewness | 207 | 207 | 0 | 0 | 0.0849514792 | 0.112556591 | 0.931270755 | 0.944810642 | 30.6275217 |
| 5 | Sheet8 | CC_T_skewness | 207 | 207 | 0 | 0 | 0.0309078591 | 0.110252726 | 0.880532213 | 0.966764891 | 9.0299363 |
| 5 | Sheet8 | CC_V_kurtosis | 207 | 207 | 0 | 0 | 0.152171962 | 0.226450651 | 0.681333685 | 0.82829767 | 6.31842234 |
| 5 | Sheet8 | CC_T_kurtosis | 207 | 207 | 0 | 0 | 0.0470922932 | 0.21682034 | 0.678880643 | 0.898746902 | 2.50375404 |
| 5 | Sheet8 | CC_CCCT | 207 | 207 | 0 | 0 | 0.451487504 | 2.14702157 | 0.996586311 | 0.995678006 | 1.84653854 |
| 5 | Sheet8 | CC_entropy | 207 | 207 | 0 | 0 | 5.04668514 | 5.04738593 | 0.82640593 | 0.826486914 | 66.2024773 |
| 5 | Sheet8 | dV_energy | 207 | 207 | 0 | 0 | 0.00599274483 | 0.00701583524 | 0.999836129 | 0.992144798 | 0.515679119 |
| 5 | Sheet8 | dV_Q | 207 | 207 | 0 | 0 | 0.00152031721 | 0.00177960864 | 0.999836664 | 0.992519564 | 0.516331133 |
| 5 | Sheet8 | dV_t_mean | 207 | 207 | 0 | 0 | 0.00976732293 | 0.0126375404 | 0.999969956 | 0.98969326 | 0.472920912 |
| 5 | Sheet8 | dV_V_mean | 207 | 207 | 0 | 0 | 0.000221784103 | 0.000628323474 | 0.956585729 | 0.974059973 | 0.00561917479 |
| 5 | Sheet8 | dV_T_mean | 207 | 207 | 0 | 0 | 0.00717559738 | 0.00928004037 | 0.999993963 | 0.999868426 | 0.0269580097 |
| 5 | Sheet8 | dV_V_std | 207 | 207 | 0 | 0 | 0.000131545481 | 0.000158001904 | 0.827731661 | 0.780856631 | 0.45894521 |
| 5 | Sheet8 | dV_T_std | 207 | 207 | 0 | 0 | 0.00670427477 | 0.00832312948 | 0.999373698 | 0.996244198 | 1.45959075 |
| 5 | Sheet8 | dV_V_skewness | 207 | 207 | 0 | 0 | 0.00815273579 | 0.0271801688 | 0.956752877 | 0.983646946 | 5.84212114 |
| 5 | Sheet8 | dV_T_skewness | 207 | 207 | 0 | 0 | 0.091784557 | 0.259863364 | 0.919300712 | 0.912624827 | 34.31543 |
| 5 | Sheet8 | dV_V_kurtosis | 207 | 207 | 0 | 0 | 0.00367341215 | 0.00515590778 | 0.968163045 | 0.911464591 | 0.199825529 |
| 5 | Sheet8 | dV_T_kurtosis | 207 | 207 | 0 | 0 | 0.703151607 | 4.15200478 | 0.632550382 | 0.808336366 | 26.0637289 |
| 5 | Sheet8 | dV_dV_devide_dt | 207 | 207 | 0 | 0 | 0.000191690517 | 0.00189538501 | 0.969639674 | 0.988972133 | 0.683090645 |
| 5 | Sheet8 | dV_entropy | 207 | 207 | 0 | 0 | 4.70182328 | 4.7046655 | 0.254037208 | -0.0145928784 | 62.9779638 |
| 5 | Sheet8 | CV_energy | 207 | 207 | 0 | 0 | 0.0376543287 | 0.0451229559 | 0.997745815 | 0.987758548 | 2.43682927 |
| 5 | Sheet8 | CV_Q | 207 | 207 | 0 | 0 | 0.00896497493 | 0.0107430975 | 0.99774576 | 0.987758548 | 2.43674356 |
| 5 | Sheet8 | CV_t_mean | 207 | 207 | 0 | 0 | 0.0717775805 | 0.0941666968 | 0.999745401 | 0.998342642 | 0.472004235 |
| 5 | Sheet8 | CV_C_mean | 207 | 207 | 0 | 0 | 0.0115213223 | 0.0139776036 | 0.998480064 | 0.945024407 | 1.54247438 |
| 5 | Sheet8 | CV_T_mean | 207 | 207 | 0 | 0 | 0.0161150851 | 0.0203535477 | 0.999934762 | 0.998576701 | 0.0694918963 |
| 5 | Sheet8 | CV_C_std | 207 | 207 | 0 | 0 | 0.0233342766 | 0.0285916979 | 0.99746867 | 0.782049929 | 2.31176562 |
| 5 | Sheet8 | CV_T_std | 207 | 207 | 0 | 0 | 0.0111452646 | 0.0141109379 | 0.99994219 | 0.991617149 | 0.419576853 |
| 5 | Sheet8 | CV_C_skewness | 207 | 207 | 0 | 0 | 0.0160128074 | 0.0229592084 | 0.999156807 | 0.988798963 | 0.700439209 |
| 5 | Sheet8 | CV_T_skewness | 207 | 207 | 0 | 0 | 0.0176649639 | 0.0693488138 | 0.860423888 | 0.955732972 | 2.15755962 |
| 5 | Sheet8 | CV_C_kurtosis | 207 | 207 | 0 | 0 | 0.0837429125 | 0.112932429 | 0.998970117 | 0.989257612 | 1.05412364 |
| 5 | Sheet8 | CV_T_kurtosis | 207 | 207 | 0 | 0 | 0.0346666699 | 0.132098641 | 0.851539473 | 0.961873992 | 1.49515184 |
| 5 | Sheet8 | CV_CVCT | 207 | 207 | 0 | 0 | 0.136290845 | 0.182290243 | 0.999750757 | 0.998544906 | 0.448224076 |
| 5 | Sheet8 | CV_entropy | 207 | 207 | 0 | 0 | 4.5766894 | 4.57894843 | 0.995216024 | 0.974003281 | 73.4582102 |
| 5 | Sheet8 | dI_energy | 207 | 196 | 0 | 11 | 0.00241971759 | 0.00617531654 | 0.638740503 | 0.829252297 | 7.47760623 |
| 5 | Sheet8 | dI_Q | 207 | 196 | 0 | 11 | 0.00057612623 | 0.00147032687 | 0.638727437 | 0.829252297 | 7.47766288 |
| 5 | Sheet8 | dI_t_mean | 207 | 196 | 0 | 11 | 0.0180126035 | 0.045842184 | 0.647318152 | 0.830128868 | 7.39067948 |
| 5 | Sheet8 | dI_C_mean | 207 | 196 | 0 | 11 | 0.00214453657 | 0.00825362302 | -0.73896859 | 0.250467471 | 0.226071528 |
| 5 | Sheet8 | dI_T_mean | 207 | 196 | 0 | 11 | 0.0158045302 | 0.020206797 | 0.999937249 | 0.99871104 | 0.0609512508 |
| 5 | Sheet8 | dI_C_std | 207 | 196 | 0 | 11 | 0.00135609189 | 0.00528520688 | -0.852803489 | -0.0665078214 | 4.64821521 |
| 5 | Sheet8 | dI_T_std | 207 | 196 | 0 | 11 | 0.0130284162 | 0.0162334821 | 0.902452061 | 0.803603696 | 13.4455745 |
| 5 | Sheet8 | dI_C_skewness | 207 | 196 | 0 | 11 | 0.0167225615 | 0.0216297464 | 0.690676663 | 0.696795735 | 24.3653463 |
| 5 | Sheet8 | dI_T_skewness | 207 | 196 | 0 | 11 | 0.325774267 | 0.487671048 | 0.318605978 | 0.271810703 | 100.443566 |
| 5 | Sheet8 | dI_C_kurtosis | 207 | 196 | 0 | 11 | 0.0290512229 | 0.0485590825 | 0.0833388891 | 0.123343082 | 1.61885401 |
| 5 | Sheet8 | dI_T_kurtosis | 207 | 196 | 0 | 11 | 0.460315683 | 0.829968818 | 0.34509097 | 0.238392996 | 21.9844678 |
| 5 | Sheet8 | dI_dI_devide_dt | 207 | 196 | 0 | 11 | 0.00363860564 | 0.0121526912 | 0.939305173 | 0.960310785 | 1.79693064 |
| 5 | Sheet8 | dI_entropy | 207 | 196 | 0 | 11 | 2.06873983 | 2.08299592 | 0.0368135212 | 0.00910136088 | 42.754692 |
| 5 | Sheet8 | Charge_energy | 207 | 207 | 0 | 0 | 0.018766918 | 0.0668096928 | 0.989712155 | 0.99302285 | 0.263391515 |
| 5 | Sheet8 | Charge_Q | 207 | 207 | 0 | 0 | 0.00491995105 | 0.0167585733 | 0.990923708 | 0.990606486 | 0.274057005 |
| 5 | Sheet8 | Charge_t_mean | 207 | 207 | 0 | 0 | 0.194495673 | 1.27797772 | 0.996369293 | 0.998747171 | 0.710067562 |
| 5 | Sheet8 | Charge_V_mean | 207 | 207 | 0 | 0 | 0.00124877357 | 0.00206600469 | 0.999631237 | 0.998042288 | 0.0305812192 |
| 5 | Sheet8 | Charge_C_mean | 207 | 207 | 0 | 0 | 0.00333562228 | 0.00444726942 | 0.999973632 | 0.999569763 | 0.148845111 |
| 5 | Sheet8 | Charge_T_mean | 207 | 207 | 0 | 0 | 0.00918391419 | 0.010510932 | 0.999994142 | 0.999891764 | 0.0381158571 |
| 5 | Sheet8 | Charge_C_std | 207 | 207 | 0 | 0 | 0.00138968269 | 0.00180008075 | 0.999998192 | 0.999594116 | 0.0625638548 |
| 5 | Sheet8 | Charge_V_std | 207 | 207 | 0 | 0 | 0.00214439833 | 0.00269362311 | 0.998198858 | 0.99210015 | 1.34189497 |
| 5 | Sheet8 | Charge_T_std | 207 | 207 | 0 | 0 | 0.00254174323 | 0.00430409411 | 0.999992522 | 0.999270762 | 0.0912972268 |
| 5 | Sheet8 | Charge_C_skewness | 207 | 207 | 0 | 0 | 0.00444908121 | 0.00725718772 | 0.999954807 | 0.999571116 | 0.747904215 |
| 5 | Sheet8 | Charge_V_skewness | 207 | 207 | 0 | 0 | 0.0384731604 | 0.0519601879 | 0.99812623 | 0.995954693 | 3.0687403 |
| 5 | Sheet8 | Charge_T_skewness | 207 | 207 | 0 | 0 | 0.0400271157 | 0.205027328 | 0.84752473 | 0.97899146 | 12.5852023 |
| 5 | Sheet8 | Charge_C_kurtosis | 207 | 207 | 0 | 0 | 0.0115646067 | 0.071112076 | 0.984554819 | 0.998173523 | 0.74736072 |
| 5 | Sheet8 | Charge_V_kurtosis | 207 | 207 | 0 | 0 | 0.362367113 | 1.04843406 | 0.878441454 | 0.986117425 | 10.3902534 |
| 5 | Sheet8 | Charge_T_kurtosis | 207 | 207 | 0 | 0 | 0.0381685373 | 0.207946142 | 0.769731018 | 0.912917654 | 2.16664356 |
| 6 | Sheet1 | CC_energy | 807 | 807 | 0 | 0 | 0.0458061504 | 0.102261413 | 0.857933248 | 0.958011393 | 2.07161512 |
| 6 | Sheet1 | CC_Q | 807 | 807 | 0 | 0 | 0.0111071525 | 0.0255380581 | 0.857743522 | 0.960742666 | 2.0279221 |
| 6 | Sheet1 | CC_t_mean | 807 | 807 | 0 | 0 | 0.0623945242 | 0.0748871342 | 0.999191638 | 0.968382341 | 1.38523341 |
| 6 | Sheet1 | CC_V_mean | 807 | 807 | 0 | 0 | 0.00322080127 | 0.0057810743 | 0.663800281 | 0.917929951 | 0.0797856219 |
| 6 | Sheet1 | CC_T_mean | 807 | 807 | 0 | 0 | 0.0131237224 | 0.0184352021 | 0.999983666 | 0.999957365 | 0.049169058 |
| 6 | Sheet1 | CC_V_std | 807 | 807 | 0 | 0 | 0.00174194025 | 0.00268789016 | 0.553526838 | 0.582907058 | 1.98033378 |
| 6 | Sheet1 | CC_T_std | 807 | 807 | 0 | 0 | 0.00784137604 | 0.0369108023 | 0.992049743 | 0.999170274 | 1.51075396 |
| 6 | Sheet1 | CC_V_skewness | 807 | 807 | 0 | 0 | 0.0151934595 | 0.0669271807 | 0.691365731 | 0.969199383 | 8.79772104 |
| 6 | Sheet1 | CC_T_skewness | 807 | 807 | 0 | 0 | 0.0561960345 | 0.274885492 | 0.882432786 | 0.954637888 | 13.6620742 |
| 6 | Sheet1 | CC_V_kurtosis | 807 | 807 | 0 | 0 | 0.0119064549 | 0.0485886386 | 0.476942164 | 0.974813791 | 0.664546043 |
| 6 | Sheet1 | CC_T_kurtosis | 807 | 807 | 0 | 0 | 0.219997083 | 2.51653809 | 0.519854992 | 0.938814998 | 9.62018059 |
| 6 | Sheet1 | CC_CCCT | 807 | 807 | 0 | 0 | 0.124657251 | 0.149735212 | 0.999193729 | 0.968630682 | 1.38376653 |
| 6 | Sheet1 | CC_entropy | 807 | 807 | 0 | 0 | 5.18012858 | 5.18014643 | 0.684703111 | 0.816393766 | 65.2671318 |
| 6 | Sheet1 | dV_energy | 807 | 807 | 0 | 0 | 0.019908944 | 0.0909135954 | 0.762385463 | 0.985963284 | 2.29534199 |
| 6 | Sheet1 | dV_Q | 807 | 807 | 0 | 0 | 0.00504393289 | 0.0230749273 | 0.762769509 | 0.986017832 | 2.29514557 |
| 6 | Sheet1 | dV_t_mean | 807 | 807 | 0 | 0 | 0.00465640733 | 0.00541298839 | 0.999973973 | 0.999673598 | 0.262945376 |
| 6 | Sheet1 | dV_V_mean | 807 | 807 | 0 | 0 | 0.000619267434 | 0.00220624788 | 0.678232756 | 0.985352641 | 0.0156900061 |
| 6 | Sheet1 | dV_T_mean | 807 | 807 | 0 | 0 | 0.00542438824 | 0.00689287632 | 0.999995972 | 0.999984599 | 0.0207571599 |
| 6 | Sheet1 | dV_V_std | 807 | 807 | 0 | 0 | 0.000109291506 | 0.00023458269 | 0.580133356 | 0.760772363 | 0.378416223 |
| 6 | Sheet1 | dV_T_std | 807 | 807 | 0 | 0 | 0.00679491199 | 0.024705596 | 0.986578943 | 0.996441976 | 2.50538107 |
| 6 | Sheet1 | dV_V_skewness | 807 | 807 | 0 | 0 | 0.0217095551 | 0.0941410811 | 0.66039512 | 0.988815366 | 16.4674258 |
| 6 | Sheet1 | dV_T_skewness | 807 | 807 | 0 | 0 | 0.120697884 | 0.727035206 | 0.414360636 | 0.858394828 | 44.6407496 |
| 6 | Sheet1 | dV_V_kurtosis | 807 | 807 | 0 | 0 | 0.0109394419 | 0.0436385915 | 0.349957542 | 0.921066828 | 0.601679119 |
| 6 | Sheet1 | dV_T_kurtosis | 807 | 807 | 0 | 0 | 0.566789337 | 8.98737453 | 0.118735282 | 0.717453418 | 26.8900209 |
| 6 | Sheet1 | dV_dV_devide_dt | 807 | 807 | 0 | 0 | 0.00165420004 | 0.00817813009 | 0.62437784 | 0.997746836 | 5.81541586 |
| 6 | Sheet1 | dV_entropy | 807 | 807 | 0 | 0 | 4.83498715 | 4.83652477 | 0.228020143 | -0.158874154 | 63.632169 |
| 6 | Sheet1 | CV_energy | 807 | 807 | 0 | 0 | 0.0203504257 | 0.0239566392 | 0.997597666 | 0.99218233 | 1.49934838 |
| 6 | Sheet1 | CV_Q | 807 | 807 | 0 | 0 | 0.00484529203 | 0.00570382208 | 0.997597251 | 0.992181029 | 1.49929373 |
| 6 | Sheet1 | CV_t_mean | 807 | 807 | 0 | 0 | 0.0435609498 | 0.0500702735 | 0.999828012 | 0.999777242 | 0.326897579 |
| 6 | Sheet1 | CV_C_mean | 807 | 807 | 0 | 0 | 0.00643715504 | 0.00743700402 | 0.997630031 | 0.979227187 | 0.881976986 |
| 6 | Sheet1 | CV_T_mean | 807 | 807 | 0 | 0 | 0.00910130082 | 0.010924775 | 0.999992477 | 0.999957028 | 0.038003343 |
| 6 | Sheet1 | CV_C_std | 807 | 807 | 0 | 0 | 0.0107281512 | 0.0123837515 | 0.996924021 | 0.909840615 | 1.31861021 |
| 6 | Sheet1 | CV_T_std | 807 | 807 | 0 | 0 | 0.0047311804 | 0.00580356922 | 0.999951022 | 0.999851746 | 0.241230401 |
| 6 | Sheet1 | CV_C_skewness | 807 | 807 | 0 | 0 | 0.0102591911 | 0.0118012152 | 0.998018805 | 0.993770428 | 0.585660487 |
| 6 | Sheet1 | CV_T_skewness | 807 | 807 | 0 | 0 | 0.0270128749 | 0.154442634 | 0.487468949 | 0.927374625 | 4.93844461 |
| 6 | Sheet1 | CV_C_kurtosis | 807 | 807 | 0 | 0 | 0.0480253359 | 0.055187791 | 0.997438729 | 0.993030916 | 0.885042217 |
| 6 | Sheet1 | CV_T_kurtosis | 807 | 807 | 0 | 0 | 0.0104889131 | 0.0278623349 | 0.967723797 | 0.98789157 | 0.552638949 |
| 6 | Sheet1 | CV_CVCT | 807 | 807 | 0 | 0 | 0.0793958227 | 0.0923005562 | 0.999839623 | 0.999785336 | 0.297998753 |
| 6 | Sheet1 | CV_entropy | 807 | 807 | 0 | 0 | 4.7679158 | 4.76828479 | 0.996397569 | 0.982720212 | 71.023044 |
| 6 | Sheet1 | dI_energy | 807 | 807 | 0 | 0 | 0.00127159984 | 0.00272423444 | 0.922257129 | 0.988702389 | 2.93985368 |
| 6 | Sheet1 | dI_Q | 807 | 807 | 0 | 0 | 0.000302772097 | 0.000648626806 | 0.92225038 | 0.988690676 | 2.93987107 |
| 6 | Sheet1 | dI_t_mean | 807 | 807 | 0 | 0 | 0.00950143459 | 0.0203898133 | 0.922891676 | 0.988815588 | 2.91739013 |
| 6 | Sheet1 | dI_C_mean | 807 | 807 | 0 | 0 | 0.000515540885 | 0.00065183673 | 0.38318882 | 0.338906488 | 0.0543381781 |
| 6 | Sheet1 | dI_T_mean | 807 | 807 | 0 | 0 | 0.0125733048 | 0.01558431 | 0.99996994 | 0.999890767 | 0.0491662081 |
| 6 | Sheet1 | dI_C_std | 807 | 807 | 0 | 0 | 0.00027991262 | 0.000349032405 | 0.129588461 | 0.0970545589 | 0.967387465 |
| 6 | Sheet1 | dI_T_std | 807 | 807 | 0 | 0 | 0.0115287044 | 0.0153991216 | 0.876745739 | 0.873472637 | 13.3122149 |
| 6 | Sheet1 | dI_C_skewness | 807 | 807 | 0 | 0 | 0.00964500925 | 0.0143510026 | 0.646263212 | 0.600789042 | 20.3619062 |
| 6 | Sheet1 | dI_T_skewness | 807 | 807 | 0 | 0 | 0.310148197 | 0.579925135 | 0.322369109 | 0.522439672 | 110.024368 |
| 6 | Sheet1 | dI_C_kurtosis | 807 | 807 | 0 | 0 | 0.007971463 | 0.00983877256 | 0.307526129 | 0.236950169 | 0.442573898 |
| 6 | Sheet1 | dI_T_kurtosis | 807 | 807 | 0 | 0 | 0.643534304 | 2.69456973 | 0.218201301 | 0.311238165 | 29.207144 |
| 6 | Sheet1 | dI_dI_devide_dt | 807 | 807 | 0 | 0 | 0.00114624076 | 0.00363339372 | 0.981333344 | 0.995334981 | 0.75552228 |
| 6 | Sheet1 | dI_entropy | 807 | 807 | 0 | 0 | 2.51562671 | 2.52196298 | 0.00717836675 | 0.0489170357 | 47.5827051 |
| 6 | Sheet1 | Charge_energy | 807 | 807 | 0 | 0 | 0.000270579813 | 0.000319209485 | 0.999999511 | 0.999994908 | 0.00760138985 |
| 6 | Sheet1 | Charge_Q | 807 | 807 | 0 | 0 | 6.24690653e-05 | 7.40986751e-05 | 0.999999557 | 0.999995593 | 0.00719196335 |
| 6 | Sheet1 | Charge_t_mean | 807 | 807 | 0 | 0 | 0.0059438826 | 0.00916857598 | 0.999988934 | 0.999978132 | 0.0333212796 |
| 6 | Sheet1 | Charge_V_mean | 807 | 807 | 0 | 0 | 0.000447759602 | 0.00132089139 | 0.983628643 | 0.998494147 | 0.0107655701 |
| 6 | Sheet1 | Charge_C_mean | 807 | 807 | 0 | 0 | 0.00193918504 | 0.00224196756 | 0.999977008 | 0.999821858 | 0.131565732 |
| 6 | Sheet1 | Charge_T_mean | 807 | 807 | 0 | 0 | 0.00321931193 | 0.00417514563 | 0.99999886 | 0.999992716 | 0.0130745701 |
| 6 | Sheet1 | Charge_C_std | 807 | 807 | 0 | 0 | 0.00140778238 | 0.0015267311 | 0.999997897 | 0.999780073 | 0.0950746554 |
| 6 | Sheet1 | Charge_V_std | 807 | 807 | 0 | 0 | 0.00111125666 | 0.00312975236 | 0.826905492 | 0.998282508 | 1.33779986 |
| 6 | Sheet1 | Charge_T_std | 807 | 807 | 0 | 0 | 0.00169123362 | 0.00219580804 | 0.999992944 | 0.999973788 | 0.0801682948 |
| 6 | Sheet1 | Charge_C_skewness | 807 | 807 | 0 | 0 | 0.00345452696 | 0.00376245053 | 0.999973536 | 0.99981245 | 0.523614373 |
| 6 | Sheet1 | Charge_V_skewness | 807 | 807 | 0 | 0 | 0.0138013239 | 0.0667080487 | 0.964923989 | 0.99953672 | 0.725709856 |
| 6 | Sheet1 | Charge_T_skewness | 807 | 807 | 0 | 0 | 0.0132262335 | 0.107064245 | 0.849918185 | 0.972388798 | 10.8102081 |
| 6 | Sheet1 | Charge_C_kurtosis | 807 | 807 | 0 | 0 | 0.00967477962 | 0.0423145707 | 0.981738815 | 0.999660817 | 0.564709535 |
| 6 | Sheet1 | Charge_V_kurtosis | 807 | 807 | 0 | 0 | 0.0943615779 | 0.484979619 | 0.887769759 | 0.999162443 | 1.8161846 |
| 6 | Sheet1 | Charge_T_kurtosis | 807 | 807 | 0 | 0 | 0.0189216391 | 0.138050287 | 0.626246651 | 0.967797602 | 1.31358324 |
| 6 | Sheet2 | CC_energy | 1036 | 1036 | 0 | 0 | 0.0481198439 | 0.105456283 | 0.802942692 | 0.956970935 | 2.186987 |
| 6 | Sheet2 | CC_Q | 1036 | 1036 | 0 | 0 | 0.0116846047 | 0.0263933588 | 0.803151241 | 0.960270734 | 2.14363697 |
| 6 | Sheet2 | CC_t_mean | 1036 | 1036 | 0 | 0 | 0.0643346518 | 0.0753803943 | 0.999265876 | 0.970774057 | 1.44096285 |
| 6 | Sheet2 | CC_V_mean | 1036 | 1036 | 0 | 0 | 0.00335727236 | 0.00606186293 | 0.635852977 | 0.924174315 | 0.0831741659 |
| 6 | Sheet2 | CC_T_mean | 1036 | 1036 | 0 | 0 | 0.0110250528 | 0.0157192849 | 0.999985078 | 0.999970754 | 0.0426297401 |
| 6 | Sheet2 | CC_V_std | 1036 | 1036 | 0 | 0 | 0.00182364979 | 0.00277256328 | 0.517366192 | 0.557996964 | 2.07864787 |
| 6 | Sheet2 | CC_T_std | 1036 | 1036 | 0 | 0 | 0.00961598055 | 0.0506675376 | 0.98327799 | 0.998844302 | 2.11948395 |
| 6 | Sheet2 | CC_V_skewness | 1036 | 1036 | 0 | 0 | 0.014553931 | 0.0680284254 | 0.670671803 | 0.967513748 | 8.2059196 |
| 6 | Sheet2 | CC_T_skewness | 1036 | 1036 | 0 | 0 | 0.0829066239 | 0.528852118 | 0.53365646 | 0.953114636 | 21.339642 |
| 6 | Sheet2 | CC_V_kurtosis | 1036 | 1036 | 0 | 0 | 0.0114731294 | 0.0500159531 | 0.468930649 | 0.978714668 | 0.637880098 |
| 6 | Sheet2 | CC_T_kurtosis | 1036 | 1036 | 0 | 0 | 0.268326685 | 3.02962535 | 0.63123683 | 0.962036759 | 12.3433414 |
| 6 | Sheet2 | CC_CCCT | 1036 | 1036 | 0 | 0 | 0.128579128 | 0.150533345 | 0.999272362 | 0.971003694 | 1.43996076 |
| 6 | Sheet2 | CC_entropy | 1036 | 1036 | 0 | 0 | 5.17891201 | 5.17893041 | 0.706804334 | 0.867937407 | 65.2653678 |
| 6 | Sheet2 | dV_energy | 1036 | 1036 | 0 | 0 | 0.0205908979 | 0.0927672141 | 0.730663273 | 0.984081384 | 2.38391229 |
| 6 | Sheet2 | dV_Q | 1036 | 1036 | 0 | 0 | 0.00521520294 | 0.0235461799 | 0.731151995 | 0.984169118 | 2.38304792 |
| 6 | Sheet2 | dV_t_mean | 1036 | 1036 | 0 | 0 | 0.00573945251 | 0.00639526259 | 0.99997493 | 0.999686349 | 0.32666352 |
| 6 | Sheet2 | dV_V_mean | 1036 | 1036 | 0 | 0 | 0.000681718173 | 0.00239113324 | 0.654066602 | 0.982664183 | 0.0172721591 |
| 6 | Sheet2 | dV_T_mean | 1036 | 1036 | 0 | 0 | 0.00546427392 | 0.00715436709 | 0.999995113 | 0.999983688 | 0.0215342189 |
| 6 | Sheet2 | dV_V_std | 1036 | 1036 | 0 | 0 | 0.000135548519 | 0.000283678632 | 0.533345819 | 0.712141806 | 0.469802598 |
| 6 | Sheet2 | dV_T_std | 1036 | 1036 | 0 | 0 | 0.00943754759 | 0.044363963 | 0.95178232 | 0.990213661 | 3.95542057 |
| 6 | Sheet2 | dV_V_skewness | 1036 | 1036 | 0 | 0 | 0.022985313 | 0.10177339 | 0.632301449 | 0.988011058 | 17.676714 |
| 6 | Sheet2 | dV_T_skewness | 1036 | 1036 | 0 | 0 | 0.113534109 | 0.350120958 | 0.74776787 | 0.897343197 | 40.8063192 |
| 6 | Sheet2 | dV_V_kurtosis | 1036 | 1036 | 0 | 0 | 0.0123719837 | 0.0512477839 | 0.362382615 | 0.921915515 | 0.680812414 |
| 6 | Sheet2 | dV_T_kurtosis | 1036 | 1036 | 0 | 0 | 0.358708027 | 2.72519689 | 0.157838967 | 0.84501986 | 16.856933 |
| 6 | Sheet2 | dV_dV_devide_dt | 1036 | 1036 | 0 | 0 | 0.00162983716 | 0.00840089976 | 0.597334257 | 0.996844051 | 5.68932469 |
| 6 | Sheet2 | dV_entropy | 1036 | 1036 | 0 | 0 | 4.82691331 | 4.82836448 | 0.245064745 | -0.175463376 | 63.5944596 |
| 6 | Sheet2 | CV_energy | 1036 | 1036 | 0 | 0 | 0.020805906 | 0.0244175609 | 0.997445631 | 0.99335905 | 1.54995427 |
| 6 | Sheet2 | CV_Q | 1036 | 1036 | 0 | 0 | 0.00495384991 | 0.00581371693 | 0.997445265 | 0.99335606 | 1.54990577 |
| 6 | Sheet2 | CV_t_mean | 1036 | 1036 | 0 | 0 | 0.044642017 | 0.0518033108 | 0.999833488 | 0.999803866 | 0.336508112 |
| 6 | Sheet2 | CV_C_mean | 1036 | 1036 | 0 | 0 | 0.00642383424 | 0.00750847552 | 0.997533008 | 0.970321991 | 0.885084826 |
| 6 | Sheet2 | CV_T_mean | 1036 | 1036 | 0 | 0 | 0.00861373732 | 0.010514392 | 0.999992224 | 0.99995286 | 0.0371237735 |
| 6 | Sheet2 | CV_C_std | 1036 | 1036 | 0 | 0 | 0.010618314 | 0.0124133857 | 0.997047144 | 0.841387546 | 1.29457138 |
| 6 | Sheet2 | CV_T_std | 1036 | 1036 | 0 | 0 | 0.00466288608 | 0.00658773809 | 0.999934424 | 0.999868014 | 0.253892305 |
| 6 | Sheet2 | CV_C_skewness | 1036 | 1036 | 0 | 0 | 0.00977516775 | 0.0178513425 | 0.9924971 | 0.990415 | 0.557728446 |
| 6 | Sheet2 | CV_T_skewness | 1036 | 1036 | 0 | 0 | 0.0120313703 | 0.129822358 | 0.580800762 | 0.994804499 | 2.07628204 |
| 6 | Sheet2 | CV_C_kurtosis | 1036 | 1036 | 0 | 0 | 0.0470485926 | 0.0888290292 | 0.987389335 | 0.988208584 | 0.873775711 |
| 6 | Sheet2 | CV_T_kurtosis | 1036 | 1036 | 0 | 0 | 0.0287474044 | 0.606028023 | 0.203212772 | 0.994571122 | 1.49333724 |
| 6 | Sheet2 | CV_CVCT | 1036 | 1036 | 0 | 0 | 0.0810357701 | 0.0939604846 | 0.999857623 | 0.999825696 | 0.305521653 |
| 6 | Sheet2 | CV_entropy | 1036 | 1036 | 0 | 0 | 4.75403124 | 4.75441524 | 0.996209869 | 0.980337943 | 71.1677893 |
| 6 | Sheet2 | dI_energy | 1036 | 1036 | 0 | 0 | 0.00102786857 | 0.00134279199 | 0.978764471 | 0.987830831 | 2.53959794 |
| 6 | Sheet2 | dI_Q | 1036 | 1036 | 0 | 0 | 0.00024473692 | 0.000319715283 | 0.97876277 | 0.987819327 | 2.53955232 |
| 6 | Sheet2 | dI_t_mean | 1036 | 1036 | 0 | 0 | 0.00767086811 | 0.0100757213 | 0.978522674 | 0.987156977 | 2.51700259 |
| 6 | Sheet2 | dI_C_mean | 1036 | 1036 | 0 | 0 | 0.000520721903 | 0.000645545526 | 0.241786568 | 0.184270737 | 0.0548910066 |
| 6 | Sheet2 | dI_T_mean | 1036 | 1036 | 0 | 0 | 0.0133732238 | 0.0164054055 | 0.999959178 | 0.999869703 | 0.0540903353 |
| 6 | Sheet2 | dI_C_std | 1036 | 1036 | 0 | 0 | 0.000275603732 | 0.000342030276 | 0.00327989235 | -0.00556768488 | 0.95245014 |
| 6 | Sheet2 | dI_T_std | 1036 | 1036 | 0 | 0 | 0.0113147825 | 0.0140683906 | 0.874294001 | 0.834502748 | 14.3855874 |
| 6 | Sheet2 | dI_C_skewness | 1036 | 1036 | 0 | 0 | 0.00646721739 | 0.00918758951 | 0.428804094 | 0.447725403 | 14.0714435 |
| 6 | Sheet2 | dI_T_skewness | 1036 | 1036 | 0 | 0 | 0.349430591 | 0.576582098 | 0.436437466 | 0.51381427 | 102.560352 |
| 6 | Sheet2 | dI_C_kurtosis | 1036 | 1036 | 0 | 0 | 0.00549632111 | 0.0069088907 | 0.263887318 | 0.231161738 | 0.30523036 |
| 6 | Sheet2 | dI_T_kurtosis | 1036 | 1036 | 0 | 0 | 0.655683481 | 1.93198486 | 0.105387837 | 0.332207286 | 29.2373852 |
| 6 | Sheet2 | dI_dI_devide_dt | 1036 | 1036 | 0 | 0 | 0.000675262377 | 0.00168719591 | 0.994454942 | 0.997878447 | 0.418218361 |
| 6 | Sheet2 | dI_entropy | 1036 | 1036 | 0 | 0 | 2.42083051 | 2.42504924 | -0.0803508944 | -0.0898792195 | 46.6244779 |
| 6 | Sheet2 | Charge_energy | 1036 | 1036 | 0 | 0 | 0.000800124452 | 0.0173379246 | 0.998301241 | 0.999994032 | 0.0226531073 |
| 6 | Sheet2 | Charge_Q | 1036 | 1036 | 0 | 0 | 0.000191218996 | 0.00421612132 | 0.998319986 | 0.999994194 | 0.0221839086 |
| 6 | Sheet2 | Charge_t_mean | 1036 | 1036 | 0 | 0 | 0.00575606339 | 0.00837959025 | 0.999992562 | 0.99998194 | 0.0324479481 |
| 6 | Sheet2 | Charge_V_mean | 1036 | 1036 | 0 | 0 | 0.000547608475 | 0.00199653397 | 0.958358254 | 0.998238312 | 0.0131660028 |
| 6 | Sheet2 | Charge_C_mean | 1036 | 1036 | 0 | 0 | 0.00195150713 | 0.00218432864 | 0.999982013 | 0.999837494 | 0.132544842 |
| 6 | Sheet2 | Charge_T_mean | 1036 | 1036 | 0 | 0 | 0.00284968607 | 0.00370177268 | 0.999998827 | 0.999993179 | 0.0119472738 |
| 6 | Sheet2 | Charge_C_std | 1036 | 1036 | 0 | 0 | 0.00140894061 | 0.00155333176 | 0.999996397 | 0.999702 | 0.0946385473 |
| 6 | Sheet2 | Charge_V_std | 1036 | 1036 | 0 | 0 | 0.00113871285 | 0.00327773302 | 0.802660939 | 0.998028515 | 1.37101969 |
| 6 | Sheet2 | Charge_T_std | 1036 | 1036 | 0 | 0 | 0.00150177405 | 0.00212592423 | 0.999992835 | 0.999978977 | 0.0752546755 |
| 6 | Sheet2 | Charge_C_skewness | 1036 | 1036 | 0 | 0 | 0.00405543013 | 0.0200727871 | 0.994751495 | 0.999740851 | 0.612466643 |
| 6 | Sheet2 | Charge_V_skewness | 1036 | 1036 | 0 | 0 | 0.0154063008 | 0.075958552 | 0.951673262 | 0.999481422 | 0.811178134 |
| 6 | Sheet2 | Charge_T_skewness | 1036 | 1036 | 0 | 0 | 0.00683307266 | 0.067540437 | 0.919131009 | 0.991416682 | 6.22301126 |
| 6 | Sheet2 | Charge_C_kurtosis | 1036 | 1036 | 0 | 0 | 0.00916151947 | 0.0410240066 | 0.981774303 | 0.999768339 | 0.535322349 |
| 6 | Sheet2 | Charge_V_kurtosis | 1036 | 1036 | 0 | 0 | 0.108155597 | 0.537198839 | 0.853752187 | 0.998497439 | 2.0903956 |
| 6 | Sheet2 | Charge_T_kurtosis | 1036 | 1036 | 0 | 0 | 0.00457732975 | 0.0522081773 | 0.897996594 | 0.997424476 | 0.323058063 |
| 6 | Sheet3 | CC_energy | 783 | 783 | 0 | 0 | 0.04705391 | 0.0985532479 | 0.874204294 | 0.956290512 | 2.13104218 |
| 6 | Sheet3 | CC_Q | 783 | 783 | 0 | 0 | 0.0113839837 | 0.0245480853 | 0.874227473 | 0.959613531 | 2.08164724 |
| 6 | Sheet3 | CC_t_mean | 783 | 783 | 0 | 0 | 0.0677698877 | 0.0811095755 | 0.999137199 | 0.967520341 | 1.4933149 |
| 6 | Sheet3 | CC_V_mean | 783 | 783 | 0 | 0 | 0.0032913145 | 0.00554270541 | 0.674886852 | 0.898777827 | 0.0815222273 |
| 6 | Sheet3 | CC_T_mean | 783 | 783 | 0 | 0 | 0.0101363797 | 0.0139568237 | 0.999988824 | 0.999961854 | 0.040051632 |
| 6 | Sheet3 | CC_V_std | 783 | 783 | 0 | 0 | 0.00181044174 | 0.00265209986 | 0.524083128 | 0.559675544 | 2.05654586 |
| 6 | Sheet3 | CC_T_std | 783 | 783 | 0 | 0 | 0.00509058946 | 0.00660025612 | 0.999696919 | 0.999495219 | 1.30379164 |
| 6 | Sheet3 | CC_V_skewness | 783 | 783 | 0 | 0 | 0.0152683588 | 0.0641915126 | 0.689908738 | 0.973690901 | 9.20738484 |
| 6 | Sheet3 | CC_T_skewness | 783 | 783 | 0 | 0 | 0.0895645598 | 0.518239889 | 0.667988975 | 0.939967247 | 21.4547737 |
| 6 | Sheet3 | CC_V_kurtosis | 783 | 783 | 0 | 0 | 0.0109959039 | 0.0436439207 | 0.505934645 | 0.97124592 | 0.615107594 |
| 6 | Sheet3 | CC_T_kurtosis | 783 | 783 | 0 | 0 | 0.276423217 | 2.3719939 | 0.782994864 | 0.956463413 | 11.4436756 |
| 6 | Sheet3 | CC_CCCT | 783 | 783 | 0 | 0 | 0.135323388 | 0.162069629 | 0.999137461 | 0.967576883 | 1.49095803 |
| 6 | Sheet3 | CC_entropy | 783 | 783 | 0 | 0 | 5.18107044 | 5.18108766 | 0.694765923 | 0.807009316 | 65.2620849 |
| 6 | Sheet3 | dV_energy | 783 | 783 | 0 | 0 | 0.0204518345 | 0.089837874 | 0.757847121 | 0.98552052 | 2.36709805 |
| 6 | Sheet3 | dV_Q | 783 | 783 | 0 | 0 | 0.0051836298 | 0.0228042065 | 0.758177911 | 0.985627522 | 2.36790534 |
| 6 | Sheet3 | dV_t_mean | 783 | 783 | 0 | 0 | 0.0041112421 | 0.00493915279 | 0.99997138 | 0.999607289 | 0.231411597 |
| 6 | Sheet3 | dV_V_mean | 783 | 783 | 0 | 0 | 0.000558054668 | 0.00203791258 | 0.688065982 | 0.979715849 | 0.0141388422 |
| 6 | Sheet3 | dV_T_mean | 783 | 783 | 0 | 0 | 0.00520463811 | 0.00672629491 | 0.999995446 | 0.999981321 | 0.0209088596 |
| 6 | Sheet3 | dV_V_std | 783 | 783 | 0 | 0 | 9.88519932e-05 | 0.000219344281 | 0.5828622 | 0.746730201 | 0.342078281 |
| 6 | Sheet3 | dV_T_std | 783 | 783 | 0 | 0 | 0.00554134632 | 0.0111593817 | 0.995167086 | 0.996890631 | 2.72089311 |
| 6 | Sheet3 | dV_V_skewness | 783 | 783 | 0 | 0 | 0.0197764788 | 0.0851521232 | 0.679854913 | 0.98557269 | 15.3330383 |
| 6 | Sheet3 | dV_T_skewness | 783 | 783 | 0 | 0 | 0.124265119 | 0.346777388 | 0.799616664 | 0.879560951 | 42.3040926 |
| 6 | Sheet3 | dV_V_kurtosis | 783 | 783 | 0 | 0 | 0.00949364745 | 0.0370945187 | 0.347261765 | 0.921271482 | 0.522435884 |
| 6 | Sheet3 | dV_T_kurtosis | 783 | 783 | 0 | 0 | 0.324978957 | 1.80045432 | 0.443126245 | 0.813178774 | 14.9781676 |
| 6 | Sheet3 | dV_dV_devide_dt | 783 | 783 | 0 | 0 | 0.00159782257 | 0.00766025904 | 0.650647769 | 0.998132729 | 5.63245755 |
| 6 | Sheet3 | dV_entropy | 783 | 783 | 0 | 0 | 4.83569986 | 4.83738452 | 0.229644296 | -0.134694486 | 63.6304186 |
| 6 | Sheet3 | CV_energy | 783 | 783 | 0 | 0 | 0.0158919346 | 0.02004736 | 0.998044205 | 0.994362338 | 1.17191541 |
| 6 | Sheet3 | CV_Q | 783 | 783 | 0 | 0 | 0.00378349676 | 0.00477268787 | 0.998044067 | 0.994360788 | 1.17185059 |
| 6 | Sheet3 | CV_t_mean | 783 | 783 | 0 | 0 | 0.0342844836 | 0.0416329052 | 0.999852916 | 0.999815743 | 0.256145109 |
| 6 | Sheet3 | CV_C_mean | 783 | 783 | 0 | 0 | 0.00520850398 | 0.00609406681 | 0.998006312 | 0.98051062 | 0.71804838 |
| 6 | Sheet3 | CV_T_mean | 783 | 783 | 0 | 0 | 0.00555851134 | 0.00697863533 | 0.99999587 | 0.999965653 | 0.0239320994 |
| 6 | Sheet3 | CV_C_std | 783 | 783 | 0 | 0 | 0.008917807 | 0.0103291179 | 0.997353839 | 0.916371021 | 1.1037186 |
| 6 | Sheet3 | CV_T_std | 783 | 783 | 0 | 0 | 0.00345175702 | 0.00431551727 | 0.999946385 | 0.999825117 | 0.236269469 |
| 6 | Sheet3 | CV_C_skewness | 783 | 783 | 0 | 0 | 0.00961309037 | 0.0273520399 | 0.989174359 | 0.991548518 | 0.544132025 |
| 6 | Sheet3 | CV_T_skewness | 783 | 783 | 0 | 0 | 0.0297622334 | 0.182146324 | 0.416648 | 0.923613073 | 5.03225274 |
| 6 | Sheet3 | CV_C_kurtosis | 783 | 783 | 0 | 0 | 0.0406342912 | 0.0470129078 | 0.998281097 | 0.995432406 | 0.738537387 |
| 6 | Sheet3 | CV_T_kurtosis | 783 | 783 | 0 | 0 | 0.00992221484 | 0.0196460931 | 0.988918081 | 0.994699779 | 0.509608523 |
| 6 | Sheet3 | CV_CVCT | 783 | 783 | 0 | 0 | 0.0620723689 | 0.0769827106 | 0.999860236 | 0.999814962 | 0.231938504 |
| 6 | Sheet3 | CV_entropy | 783 | 783 | 0 | 0 | 4.77338151 | 4.77380828 | 0.997124829 | 0.984723237 | 71.0875018 |
| 6 | Sheet3 | dI_energy | 783 | 783 | 0 | 0 | 0.00123972901 | 0.00196697924 | 0.967603384 | 0.99353337 | 2.85021394 |
| 6 | Sheet3 | dI_Q | 783 | 783 | 0 | 0 | 0.000295166899 | 0.000468317599 | 0.967603253 | 0.993532795 | 2.85021686 |
| 6 | Sheet3 | dI_t_mean | 783 | 783 | 0 | 0 | 0.00928427821 | 0.0147478436 | 0.967787296 | 0.993102607 | 2.83486305 |
| 6 | Sheet3 | dI_C_mean | 783 | 783 | 0 | 0 | 0.000457485547 | 0.000567934985 | 0.566598295 | 0.444783613 | 0.0482198637 |
| 6 | Sheet3 | dI_T_mean | 783 | 783 | 0 | 0 | 0.0122921306 | 0.0152701165 | 0.999970433 | 0.999848715 | 0.0502651487 |
| 6 | Sheet3 | dI_C_std | 783 | 783 | 0 | 0 | 0.000263798231 | 0.000324624091 | 0.0655729603 | 0.0304299881 | 0.914399445 |
| 6 | Sheet3 | dI_T_std | 783 | 783 | 0 | 0 | 0.0107196451 | 0.0135443106 | 0.877261408 | 0.873623502 | 15.700175 |
| 6 | Sheet3 | dI_C_skewness | 783 | 783 | 0 | 0 | 0.00750223551 | 0.0125400679 | 0.770595536 | 0.739606862 | 14.8222156 |
| 6 | Sheet3 | dI_T_skewness | 783 | 783 | 0 | 0 | 0.406867125 | 0.696332564 | 0.460896345 | 0.531073575 | 107.996718 |
| 6 | Sheet3 | dI_C_kurtosis | 783 | 783 | 0 | 0 | 0.00574643913 | 0.0073644404 | 0.42927585 | 0.376227303 | 0.318889059 |
| 6 | Sheet3 | dI_T_kurtosis | 783 | 783 | 0 | 0 | 0.876677874 | 3.38882706 | 0.221795605 | 0.307367572 | 38.2909417 |
| 6 | Sheet3 | dI_dI_devide_dt | 783 | 783 | 0 | 0 | 0.000634167374 | 0.00194921886 | 0.994649166 | 0.998989594 | 0.420422916 |
| 6 | Sheet3 | dI_entropy | 783 | 783 | 0 | 0 | 2.5224461 | 2.52898033 | -0.0616285203 | 0.167089036 | 47.6514027 |
| 6 | Sheet3 | Charge_energy | 783 | 783 | 0 | 0 | 0.000277465156 | 0.000329029157 | 0.999999519 | 0.9999953 | 0.00780154625 |
| 6 | Sheet3 | Charge_Q | 783 | 783 | 0 | 0 | 6.43451578e-05 | 7.66996204e-05 | 0.999999565 | 0.999995625 | 0.00741497819 |
| 6 | Sheet3 | Charge_t_mean | 783 | 783 | 0 | 0 | 0.0211347118 | 0.212923628 | 0.992811614 | 0.99971261 | 0.117962411 |
| 6 | Sheet3 | Charge_V_mean | 783 | 783 | 0 | 0 | 0.000421735648 | 0.000994458184 | 0.992274411 | 0.998872513 | 0.0101394835 |
| 6 | Sheet3 | Charge_C_mean | 783 | 783 | 0 | 0 | 0.00194180654 | 0.00235342492 | 0.999970727 | 0.999624063 | 0.132612259 |
| 6 | Sheet3 | Charge_T_mean | 783 | 783 | 0 | 0 | 0.0026153166 | 0.00332880355 | 0.999999136 | 0.999992676 | 0.0110182412 |
| 6 | Sheet3 | Charge_C_std | 783 | 783 | 0 | 0 | 0.00146483083 | 0.00160265361 | 0.999997665 | 0.999667458 | 0.0995452009 |
| 6 | Sheet3 | Charge_V_std | 783 | 783 | 0 | 0 | 0.00106978846 | 0.00293044582 | 0.851447803 | 0.997177282 | 1.28930705 |
| 6 | Sheet3 | Charge_T_std | 783 | 783 | 0 | 0 | 0.00157699135 | 0.00199089952 | 0.99998997 | 0.999966178 | 0.0996682693 |
| 6 | Sheet3 | Charge_C_skewness | 783 | 783 | 0 | 0 | 0.00344163177 | 0.003866355 | 0.999969882 | 0.999580892 | 0.521161809 |
| 6 | Sheet3 | Charge_V_skewness | 783 | 783 | 0 | 0 | 0.0124607913 | 0.0598109792 | 0.974086554 | 0.999384536 | 0.65371268 |
| 6 | Sheet3 | Charge_T_skewness | 783 | 783 | 0 | 0 | 0.0163024133 | 0.122674623 | 0.827303286 | 0.964109757 | 12.9386964 |
| 6 | Sheet3 | Charge_C_kurtosis | 783 | 783 | 0 | 0 | 0.00896245684 | 0.0399486777 | 0.984984385 | 0.999283721 | 0.521192616 |
| 6 | Sheet3 | Charge_V_kurtosis | 783 | 783 | 0 | 0 | 0.0860770633 | 0.445892176 | 0.908545873 | 0.998659809 | 1.64777859 |
| 6 | Sheet3 | Charge_T_kurtosis | 783 | 783 | 0 | 0 | 0.0231364337 | 0.164397977 | 0.564627293 | 0.978582787 | 1.61599305 |
| 6 | Sheet4 | CC_energy | 810 | 810 | 0 | 0 | 0.0475065078 | 0.0950344392 | 0.88364067 | 0.968194457 | 2.15997899 |
| 6 | Sheet4 | CC_Q | 810 | 810 | 0 | 0 | 0.0117982275 | 0.0246167688 | 0.872024387 | 0.969203596 | 2.16476948 |
| 6 | Sheet4 | CC_t_mean | 810 | 810 | 0 | 0 | 0.069697967 | 0.0804728865 | 0.999249291 | 0.977455096 | 1.55141081 |
| 6 | Sheet4 | CC_V_mean | 810 | 810 | 0 | 0 | 0.00339538343 | 0.0054790638 | 0.663177315 | 0.906559427 | 0.0840929934 |
| 6 | Sheet4 | CC_T_mean | 810 | 810 | 0 | 0 | 0.0127101752 | 0.0168596341 | 0.999987665 | 0.999964256 | 0.0487845416 |
| 6 | Sheet4 | CC_V_std | 810 | 810 | 0 | 0 | 0.00184626062 | 0.00256191269 | 0.54519232 | 0.601957248 | 2.09614686 |
| 6 | Sheet4 | CC_T_std | 810 | 810 | 0 | 0 | 0.00754392782 | 0.0327889955 | 0.992438855 | 0.99913164 | 1.5351864 |
| 6 | Sheet4 | CC_V_skewness | 810 | 810 | 0 | 0 | 0.0145268846 | 0.0610728563 | 0.694629141 | 0.9774035 | 9.00420501 |
| 6 | Sheet4 | CC_T_skewness | 810 | 810 | 0 | 0 | 0.0722897863 | 0.414617732 | 0.746998539 | 0.956799714 | 17.4019199 |
| 6 | Sheet4 | CC_V_kurtosis | 810 | 810 | 0 | 0 | 0.0109039897 | 0.0423856 | 0.506592332 | 0.969769919 | 0.611136181 |
| 6 | Sheet4 | CC_T_kurtosis | 810 | 810 | 0 | 0 | 0.278621704 | 3.06369403 | 0.708968116 | 0.940246667 | 11.2935914 |
| 6 | Sheet4 | CC_CCCT | 810 | 810 | 0 | 0 | 0.139192777 | 0.160740719 | 0.999250686 | 0.977466024 | 1.54918284 |
| 6 | Sheet4 | CC_entropy | 810 | 810 | 0 | 0 | 5.18101218 | 5.18102875 | 0.665472628 | 0.739445479 | 65.2561737 |
| 6 | Sheet4 | dV_energy | 810 | 810 | 0 | 0 | 0.0182187019 | 0.0842567125 | 0.773967501 | 0.987151194 | 2.12794223 |
| 6 | Sheet4 | dV_Q | 810 | 810 | 0 | 0 | 0.00461660753 | 0.0213855299 | 0.774291453 | 0.987212355 | 2.12824231 |
| 6 | Sheet4 | dV_t_mean | 810 | 810 | 0 | 0 | 0.00394874263 | 0.00479849942 | 0.999971048 | 0.999609363 | 0.225109341 |
| 6 | Sheet4 | dV_V_mean | 810 | 810 | 0 | 0 | 0.00053573197 | 0.00194734474 | 0.689735523 | 0.975724383 | 0.0135730932 |
| 6 | Sheet4 | dV_T_mean | 810 | 810 | 0 | 0 | 0.00545325577 | 0.00711043339 | 0.999995749 | 0.999981772 | 0.0213677728 |
| 6 | Sheet4 | dV_V_std | 810 | 810 | 0 | 0 | 9.51291917e-05 | 0.000211751494 | 0.566266277 | 0.725838123 | 0.329287384 |
| 6 | Sheet4 | dV_T_std | 810 | 810 | 0 | 0 | 0.00591373511 | 0.0115979183 | 0.996384206 | 0.997498344 | 2.32972531 |
| 6 | Sheet4 | dV_V_skewness | 810 | 810 | 0 | 0 | 0.0188979112 | 0.0817076452 | 0.681805755 | 0.984581685 | 14.7793604 |
| 6 | Sheet4 | dV_T_skewness | 810 | 810 | 0 | 0 | 0.124412197 | 0.446771736 | 0.7441051 | 0.828568128 | 45.3280767 |
| 6 | Sheet4 | dV_V_kurtosis | 810 | 810 | 0 | 0 | 0.00904891669 | 0.0352429332 | 0.332242807 | 0.908619798 | 0.498122431 |
| 6 | Sheet4 | dV_T_kurtosis | 810 | 810 | 0 | 0 | 0.402209838 | 2.48481446 | 0.853403155 | 0.768918935 | 16.650805 |
| 6 | Sheet4 | dV_dV_devide_dt | 810 | 810 | 0 | 0 | 0.00148214141 | 0.00730490382 | 0.661023727 | 0.998084632 | 5.15397391 |
| 6 | Sheet4 | dV_entropy | 810 | 810 | 0 | 0 | 4.8244651 | 4.82617026 | 0.213609997 | -0.161151684 | 63.5735728 |
| 6 | Sheet4 | CV_energy | 810 | 810 | 0 | 0 | 0.0169510779 | 0.0207735687 | 0.997987459 | 0.995276729 | 1.24864473 |
| 6 | Sheet4 | CV_Q | 810 | 810 | 0 | 0 | 0.00403570967 | 0.00494566305 | 0.997987304 | 0.995277632 | 1.24858465 |
| 6 | Sheet4 | CV_t_mean | 810 | 810 | 0 | 0 | 0.0375450737 | 0.044344103 | 0.999863429 | 0.999830988 | 0.277902452 |
| 6 | Sheet4 | CV_C_mean | 810 | 810 | 0 | 0 | 0.00511825946 | 0.00602166878 | 0.997905984 | 0.984687203 | 0.711072992 |
| 6 | Sheet4 | CV_T_mean | 810 | 810 | 0 | 0 | 0.00680786063 | 0.00847396911 | 0.999994718 | 0.999964075 | 0.0291440026 |
| 6 | Sheet4 | CV_C_std | 810 | 810 | 0 | 0 | 0.0087300136 | 0.0102560377 | 0.997349507 | 0.919274581 | 1.08361878 |
| 6 | Sheet4 | CV_T_std | 810 | 810 | 0 | 0 | 0.00390844628 | 0.00491046119 | 0.999955178 | 0.999831959 | 0.211464147 |
| 6 | Sheet4 | CV_C_skewness | 810 | 810 | 0 | 0 | 0.0087778286 | 0.0101572355 | 0.998666664 | 0.996067644 | 0.489166793 |
| 6 | Sheet4 | CV_T_skewness | 810 | 810 | 0 | 0 | 0.0151607799 | 0.0853211836 | 0.745845054 | 0.960471819 | 2.47354913 |
| 6 | Sheet4 | CV_C_kurtosis | 810 | 810 | 0 | 0 | 0.0416649852 | 0.0483276308 | 0.99836321 | 0.996009139 | 0.739759523 |
| 6 | Sheet4 | CV_T_kurtosis | 810 | 810 | 0 | 0 | 0.00861018439 | 0.0105674091 | 0.997125892 | 0.996527308 | 0.437091756 |
| 6 | Sheet4 | CV_CVCT | 810 | 810 | 0 | 0 | 0.0664289059 | 0.0801819195 | 0.999873944 | 0.999845789 | 0.245929474 |
| 6 | Sheet4 | CV_entropy | 810 | 810 | 0 | 0 | 4.76635147 | 4.76674402 | 0.997234851 | 0.987016308 | 71.1841365 |
| 6 | Sheet4 | dI_energy | 810 | 810 | 0 | 0 | 0.00124351915 | 0.00406260506 | 0.875607744 | 0.991800537 | 2.7599462 |
| 6 | Sheet4 | dI_Q | 810 | 810 | 0 | 0 | 0.000296071666 | 0.000967261892 | 0.875605894 | 0.991794734 | 2.75995165 |
| 6 | Sheet4 | dI_t_mean | 810 | 810 | 0 | 0 | 0.00938422397 | 0.0306470886 | 0.875131161 | 0.991604321 | 2.76668655 |
| 6 | Sheet4 | dI_C_mean | 810 | 810 | 0 | 0 | 0.000462455287 | 0.000610173357 | 0.65312851 | 0.605175139 | 0.0487409004 |
| 6 | Sheet4 | dI_T_mean | 810 | 810 | 0 | 0 | 0.0123405624 | 0.0152509302 | 0.999972173 | 0.999858558 | 0.0495534326 |
| 6 | Sheet4 | dI_C_std | 810 | 810 | 0 | 0 | 0.000273903492 | 0.000338111267 | 0.160014004 | 0.0903954479 | 0.944308836 |
| 6 | Sheet4 | dI_T_std | 810 | 810 | 0 | 0 | 0.0114107122 | 0.0156522018 | 0.862402555 | 0.852696651 | 13.0967889 |
| 6 | Sheet4 | dI_C_skewness | 810 | 810 | 0 | 0 | 0.00769114608 | 0.0152010237 | 0.847893667 | 0.845475894 | 15.8232239 |
| 6 | Sheet4 | dI_T_skewness | 810 | 810 | 0 | 0 | 0.288560743 | 0.446416188 | 0.452578935 | 0.513298174 | 100.488949 |
| 6 | Sheet4 | dI_C_kurtosis | 810 | 810 | 0 | 0 | 0.00616428153 | 0.00928332071 | 0.440283979 | 0.458354281 | 0.34207517 |
| 6 | Sheet4 | dI_T_kurtosis | 810 | 810 | 0 | 0 | 0.467160529 | 1.09114168 | 0.210196579 | 0.413630569 | 21.7369279 |
| 6 | Sheet4 | dI_dI_devide_dt | 810 | 810 | 0 | 0 | 0.000858054723 | 0.0046043049 | 0.978108764 | 0.99585978 | 0.582838371 |
| 6 | Sheet4 | dI_entropy | 810 | 810 | 0 | 0 | 2.56663195 | 2.5754049 | -0.0877487164 | 0.248312597 | 48.0857658 |
| 6 | Sheet4 | Charge_energy | 810 | 810 | 0 | 0 | 0.000279587873 | 0.00032923867 | 0.999999474 | 0.999995348 | 0.00787483767 |
| 6 | Sheet4 | Charge_Q | 810 | 810 | 0 | 0 | 6.4651286e-05 | 7.66386561e-05 | 0.999999522 | 0.999995868 | 0.00746381233 |
| 6 | Sheet4 | Charge_t_mean | 810 | 810 | 0 | 0 | 0.00618463439 | 0.00810490098 | 0.999992652 | 0.99998254 | 0.0343379612 |
| 6 | Sheet4 | Charge_V_mean | 810 | 810 | 0 | 0 | 0.000453426831 | 0.00132580612 | 0.984019666 | 0.998431831 | 0.0108997337 |
| 6 | Sheet4 | Charge_C_mean | 810 | 810 | 0 | 0 | 0.0020041818 | 0.00225912177 | 0.999981255 | 0.999843226 | 0.137737404 |
| 6 | Sheet4 | Charge_T_mean | 810 | 810 | 0 | 0 | 0.00276758912 | 0.00348245994 | 0.999999177 | 0.999992955 | 0.0115264438 |
| 6 | Sheet4 | Charge_C_std | 810 | 810 | 0 | 0 | 0.00146645069 | 0.00159328201 | 0.999997715 | 0.999778466 | 0.0994340375 |
| 6 | Sheet4 | Charge_V_std | 810 | 810 | 0 | 0 | 0.00102731679 | 0.00274776806 | 0.863829719 | 0.998189704 | 1.24654337 |
| 6 | Sheet4 | Charge_T_std | 810 | 810 | 0 | 0 | 0.00160613282 | 0.00200056228 | 0.999993404 | 0.999976201 | 0.0798619188 |
| 6 | Sheet4 | Charge_C_skewness | 810 | 810 | 0 | 0 | 0.00358470337 | 0.00386892382 | 0.999981025 | 0.999832546 | 0.525214578 |
| 6 | Sheet4 | Charge_V_skewness | 810 | 810 | 0 | 0 | 0.013006279 | 0.0604506223 | 0.972692967 | 0.999490705 | 0.673812373 |
| 6 | Sheet4 | Charge_T_skewness | 810 | 810 | 0 | 0 | 0.00390846855 | 0.035453024 | 0.981789005 | 0.99719961 | 2.94160046 |
| 6 | Sheet4 | Charge_C_kurtosis | 810 | 810 | 0 | 0 | 0.00845609792 | 0.0319705972 | 0.990832964 | 0.999763225 | 0.483511394 |
| 6 | Sheet4 | Charge_V_kurtosis | 810 | 810 | 0 | 0 | 0.0885044905 | 0.446662483 | 0.908303819 | 0.998995386 | 1.66360154 |
| 6 | Sheet4 | Charge_T_kurtosis | 810 | 810 | 0 | 0 | 0.00534103249 | 0.036612964 | 0.945486905 | 0.996478693 | 0.374076977 |
| 6 | Sheet5 | CC_energy | 1107 | 1107 | 0 | 0 | 0.0455230763 | 0.100641659 | 0.84906607 | 0.967879522 | 2.08010745 |
| 6 | Sheet5 | CC_Q | 1107 | 1107 | 0 | 0 | 0.0110296901 | 0.0250599471 | 0.849808619 | 0.969872234 | 2.03463086 |
| 6 | Sheet5 | CC_t_mean | 1107 | 1107 | 0 | 0 | 0.0634263313 | 0.0909542998 | 0.998062675 | 0.975083933 | 1.4235029 |
| 6 | Sheet5 | CC_V_mean | 1107 | 1107 | 0 | 0 | 0.00318994695 | 0.00582841347 | 0.635164401 | 0.923259694 | 0.0790192464 |
| 6 | Sheet5 | CC_T_mean | 1107 | 1107 | 0 | 0 | 0.0137838116 | 0.119754521 | 0.998297011 | 0.997970226 | 0.0551926681 |
| 6 | Sheet5 | CC_V_std | 1107 | 1107 | 0 | 0 | 0.0016973747 | 0.00248788191 | 0.54902552 | 0.595553946 | 1.9343037 |
| 6 | Sheet5 | CC_T_std | 1107 | 1107 | 0 | 0 | 0.0124251444 | 0.129135316 | 0.872604849 | 0.997981097 | 3.06267717 |
| 6 | Sheet5 | CC_V_skewness | 1107 | 1107 | 0 | 0 | 0.0142980338 | 0.0681560321 | 0.644225374 | 0.969142587 | 8.3954056 |
| 6 | Sheet5 | CC_T_skewness | 1107 | 1107 | 0 | 0 | 0.084528271 | 0.463715034 | 0.684717453 | 0.941361142 | 20.8537275 |
| 6 | Sheet5 | CC_V_kurtosis | 1107 | 1107 | 0 | 0 | 0.0098882131 | 0.0394279463 | 0.498946429 | 0.95066193 | 0.551005995 |
| 6 | Sheet5 | CC_T_kurtosis | 1107 | 1107 | 0 | 0 | 0.271307922 | 3.04631526 | 0.756006301 | 0.955506256 | 10.8612357 |
| 6 | Sheet5 | CC_CCCT | 1107 | 1106 | 0 | 1 | 0.123323995 | 0.146207543 | 0.999296267 | 0.97906232 | 1.38406991 |
| 6 | Sheet5 | CC_entropy | 1107 | 1107 | 0 | 0 | 5.17886158 | 5.17893537 | 0.199991413 | 0.830679222 | 65.2573593 |
| 6 | Sheet5 | dV_energy | 1107 | 1106 | 0 | 1 | 0.0180968687 | 0.0831202491 | 0.772714161 | 0.98686325 | 2.11549216 |
| 6 | Sheet5 | dV_Q | 1107 | 1106 | 0 | 1 | 0.00458520686 | 0.021098873 | 0.773009688 | 0.986986621 | 2.11557466 |
| 6 | Sheet5 | dV_t_mean | 1107 | 1106 | 0 | 1 | 0.00435183781 | 0.00518818694 | 0.999971974 | 0.999603799 | 0.248964505 |
| 6 | Sheet5 | dV_V_mean | 1107 | 1106 | 0 | 1 | 0.000566395286 | 0.00202391894 | 0.674209809 | 0.97149329 | 0.0143498397 |
| 6 | Sheet5 | dV_T_mean | 1107 | 1106 | 0 | 1 | 0.00489189134 | 0.00644666723 | 0.999995578 | 0.999984174 | 0.0199370622 |
| 6 | Sheet5 | dV_V_std | 1107 | 1106 | 0 | 1 | 0.000110658039 | 0.000250634169 | 0.508003342 | 0.707964679 | 0.382978418 |
| 6 | Sheet5 | dV_T_std | 1107 | 1106 | 0 | 1 | 0.00780032874 | 0.0328417996 | 0.96026904 | 0.988223018 | 3.74080974 |
| 6 | Sheet5 | dV_V_skewness | 1107 | 1106 | 0 | 1 | 0.0195228768 | 0.084574339 | 0.66748786 | 0.978605696 | 15.6332707 |
| 6 | Sheet5 | dV_T_skewness | 1107 | 1106 | 0 | 1 | 0.126504005 | 0.410182644 | 0.761992851 | 0.886596686 | 40.7908149 |
| 6 | Sheet5 | dV_V_kurtosis | 1107 | 1106 | 0 | 1 | 0.00986644313 | 0.0384091023 | 0.360038692 | 0.888302941 | 0.543427123 |
| 6 | Sheet5 | dV_T_kurtosis | 1107 | 1106 | 0 | 1 | 0.61407738 | 4.06540209 | 0.354517597 | 0.788327454 | 24.4995401 |
| 6 | Sheet5 | dV_dV_devide_dt | 1107 | 1106 | 0 | 1 | 0.00137798594 | 0.00708727437 | 0.667734183 | 0.997984073 | 4.76460893 |
| 6 | Sheet5 | dV_entropy | 1107 | 1106 | 0 | 1 | 4.82084058 | 4.82246342 | 0.261789981 | -0.149032191 | 63.5555753 |
| 6 | Sheet5 | CV_energy | 1107 | 1107 | 0 | 0 | 0.0216122647 | 0.0538910733 | 0.968084211 | 0.991324272 | 1.59253948 |
| 6 | Sheet5 | CV_Q | 1107 | 1107 | 0 | 0 | 0.00514569027 | 0.0128377963 | 0.968046564 | 0.991322609 | 1.59254219 |
| 6 | Sheet5 | CV_t_mean | 1107 | 1107 | 0 | 0 | 0.0436588953 | 0.0585620295 | 0.999646206 | 0.999835857 | 0.327860788 |
| 6 | Sheet5 | CV_C_mean | 1107 | 1107 | 0 | 0 | 0.00684151448 | 0.0355458584 | 0.915576644 | 0.962667949 | 0.936621268 |
| 6 | Sheet5 | CV_T_mean | 1107 | 1107 | 0 | 0 | 0.0209302098 | 0.466886313 | 0.971277192 | 0.995432498 | 0.0924672278 |
| 6 | Sheet5 | CV_C_std | 1107 | 1107 | 0 | 0 | 0.0104010711 | 0.0294119193 | 0.97574826 | 0.878284911 | 1.26938518 |
| 6 | Sheet5 | CV_T_std | 1107 | 1107 | 0 | 0 | 0.00884681817 | 0.163074523 | 0.941305236 | 0.998213274 | 0.557557539 |
| 6 | Sheet5 | CV_C_skewness | 1107 | 1107 | 0 | 0 | 0.0102270184 | 0.0399170162 | 0.969104679 | 0.989897953 | 0.583464505 |
| 6 | Sheet5 | CV_T_skewness | 1107 | 1107 | 0 | 0 | 0.00834321889 | 0.038166549 | 0.917363732 | 0.988018797 | 1.33171184 |
| 6 | Sheet5 | CV_C_kurtosis | 1107 | 1107 | 0 | 0 | 0.0474026515 | 0.121438521 | 0.981673269 | 0.988560578 | 0.876829319 |
| 6 | Sheet5 | CV_T_kurtosis | 1107 | 1107 | 0 | 0 | 0.0110967568 | 0.0219850757 | 0.983670893 | 0.994223176 | 0.559928035 |
| 6 | Sheet5 | CV_CVCT | 1107 | 1107 | 0 | 0 | 0.0790673359 | 0.108751874 | 0.999683847 | 0.999852451 | 0.29696183 |
| 6 | Sheet5 | CV_entropy | 1107 | 1107 | 0 | 0 | 4.76640657 | 4.76679448 | 0.994306656 | 0.977559495 | 71.0870251 |
| 6 | Sheet5 | dI_energy | 1107 | 1107 | 0 | 0 | 0.00111128246 | 0.00174216572 | 0.946744401 | 0.979918862 | 2.66484704 |
| 6 | Sheet5 | dI_Q | 1107 | 1107 | 0 | 0 | 0.000264586213 | 0.000414793042 | 0.946745093 | 0.979913537 | 2.66484818 |
| 6 | Sheet5 | dI_t_mean | 1107 | 1107 | 0 | 0 | 0.00835107099 | 0.0131090438 | 0.946696976 | 0.980098484 | 2.66003014 |
| 6 | Sheet5 | dI_C_mean | 1107 | 1107 | 0 | 0 | 0.000475483511 | 0.000584859871 | 0.328783238 | 0.227987507 | 0.0501149332 |
| 6 | Sheet5 | dI_T_mean | 1107 | 1107 | 0 | 0 | 0.0320671312 | 0.647903034 | 0.941248475 | 0.995748161 | 0.13407067 |
| 6 | Sheet5 | dI_C_std | 1107 | 1107 | 0 | 0 | 0.00027384211 | 0.000341064883 | -0.0153774431 | -0.0137555181 | 0.947068791 |
| 6 | Sheet5 | dI_T_std | 1107 | 1107 | 0 | 0 | 0.0123165189 | 0.017275334 | 0.766034301 | 0.786896087 | 16.6566309 |
| 6 | Sheet5 | dI_C_skewness | 1107 | 1107 | 0 | 0 | 0.00618261096 | 0.00827161168 | 0.692648681 | 0.546039491 | 12.7253299 |
| 6 | Sheet5 | dI_T_skewness | 1107 | 1107 | 0 | 0 | 0.386143451 | 0.75721488 | 0.309249653 | 0.464778215 | 119.322323 |
| 6 | Sheet5 | dI_C_kurtosis | 1107 | 1107 | 0 | 0 | 0.00532953798 | 0.00674250646 | 0.275443809 | 0.234139249 | 0.295894905 |
| 6 | Sheet5 | dI_T_kurtosis | 1107 | 1107 | 0 | 0 | 0.937381939 | 5.42844121 | 0.0427751548 | 0.327053071 | 42.3427138 |
| 6 | Sheet5 | dI_dI_devide_dt | 1107 | 1107 | 0 | 0 | 0.000752917924 | 0.00421695354 | 0.961603009 | 0.992928582 | 0.480706323 |
| 6 | Sheet5 | dI_entropy | 1107 | 1107 | 0 | 0 | 2.46241652 | 2.46631221 | -0.00768560089 | -0.0240236767 | 47.0494269 |
| 6 | Sheet5 | Charge_energy | 1107 | 1107 | 0 | 0 | 0.00302188361 | 0.0663124191 | 0.979403163 | 0.994852583 | 0.0854442331 |
| 6 | Sheet5 | Charge_Q | 1107 | 1107 | 0 | 0 | 0.000725813947 | 0.0159850888 | 0.979899142 | 0.994881651 | 0.0841135006 |
| 6 | Sheet5 | Charge_t_mean | 1107 | 1107 | 0 | 0 | 0.0282987318 | 0.231093494 | 0.993468749 | 0.999904746 | 0.159339506 |
| 6 | Sheet5 | Charge_V_mean | 1107 | 1107 | 0 | 0 | 0.000455432501 | 0.00135519597 | 0.98410651 | 0.999057715 | 0.0109489955 |
| 6 | Sheet5 | Charge_C_mean | 1107 | 1107 | 0 | 0 | 0.00306730395 | 0.037840809 | 0.975333307 | 0.995540754 | 0.208741478 |
| 6 | Sheet5 | Charge_T_mean | 1107 | 1107 | 0 | 0 | 0.0126168763 | 0.338182809 | 0.984883059 | 0.995574651 | 0.0543815438 |
| 6 | Sheet5 | Charge_C_std | 1107 | 1107 | 0 | 0 | 0.0014068599 | 0.00151535203 | 0.999998029 | 0.999719658 | 0.0949444731 |
| 6 | Sheet5 | Charge_V_std | 1107 | 1107 | 0 | 0 | 0.00091050689 | 0.0024347709 | 0.895457264 | 0.997925446 | 1.10195218 |
| 6 | Sheet5 | Charge_T_std | 1107 | 1107 | 0 | 0 | 0.0071960627 | 0.189935475 | 0.936527028 | 0.99828367 | 0.415430963 |
| 6 | Sheet5 | Charge_C_skewness | 1107 | 1107 | 0 | 0 | 0.00427219517 | 0.027756965 | 0.991459595 | 0.999585007 | 0.642592659 |
| 6 | Sheet5 | Charge_V_skewness | 1107 | 1107 | 0 | 0 | 0.0116374858 | 0.0563400385 | 0.976778879 | 0.999464263 | 0.607941201 |
| 6 | Sheet5 | Charge_T_skewness | 1107 | 1107 | 0 | 0 | 0.0047062797 | 0.0401036757 | 0.973605414 | 0.996501305 | 3.86463011 |
| 6 | Sheet5 | Charge_C_kurtosis | 1107 | 1107 | 0 | 0 | 0.00830602925 | 0.0340698219 | 0.989351708 | 0.999691572 | 0.481590358 |
| 6 | Sheet5 | Charge_V_kurtosis | 1107 | 1107 | 0 | 0 | 0.0823986644 | 0.437270783 | 0.912358513 | 0.998767769 | 1.56815307 |
| 6 | Sheet5 | Charge_T_kurtosis | 1107 | 1107 | 0 | 0 | 0.00569912325 | 0.0355994572 | 0.940237754 | 0.991572584 | 0.403660794 |
| 6 | Sheet6 | CC_energy | 909 | 909 | 0 | 0 | 0.053231001 | 0.11158546 | 0.830727802 | 0.964959512 | 2.4180825 |
| 6 | Sheet6 | CC_Q | 909 | 909 | 0 | 0 | 0.0129033044 | 0.0278706239 | 0.830552936 | 0.967028505 | 2.36627095 |
| 6 | Sheet6 | CC_t_mean | 909 | 909 | 0 | 0 | 0.0739511641 | 0.0844690612 | 0.999272437 | 0.977593511 | 1.64182941 |
| 6 | Sheet6 | CC_V_mean | 909 | 909 | 0 | 0 | 0.0036738137 | 0.00634643603 | 0.640693945 | 0.924734086 | 0.0910070108 |
| 6 | Sheet6 | CC_T_mean | 909 | 909 | 0 | 0 | 0.00992810224 | 0.0145445835 | 0.99998586 | 0.999973634 | 0.0399415444 |
| 6 | Sheet6 | CC_V_std | 909 | 909 | 0 | 0 | 0.00202183891 | 0.00292718534 | 0.508333449 | 0.546807761 | 2.30262767 |
| 6 | Sheet6 | CC_T_std | 909 | 909 | 0 | 0 | 0.00795399654 | 0.0401004637 | 0.983961665 | 0.998663543 | 2.22022181 |
| 6 | Sheet6 | CC_V_skewness | 909 | 909 | 0 | 0 | 0.0155740726 | 0.076663716 | 0.65508449 | 0.971032346 | 8.96040683 |
| 6 | Sheet6 | CC_T_skewness | 909 | 909 | 0 | 0 | 0.0846670852 | 0.457911667 | 0.71038365 | 0.942749804 | 18.4730341 |
| 6 | Sheet6 | CC_V_kurtosis | 909 | 909 | 0 | 0 | 0.00996803803 | 0.0704172503 | 0.486229321 | 0.974482076 | 0.554142193 |
| 6 | Sheet6 | CC_T_kurtosis | 909 | 909 | 0 | 0 | 0.262326268 | 1.95286272 | 0.732743403 | 0.935948792 | 11.3229615 |
| 6 | Sheet6 | CC_CCCT | 909 | 909 | 0 | 0 | 0.14761206 | 0.168560889 | 0.999277121 | 0.977746832 | 1.63865938 |
| 6 | Sheet6 | CC_entropy | 909 | 909 | 0 | 0 | 5.17887621 | 5.17890488 | 0.57144844 | 0.873494904 | 65.264908 |
| 6 | Sheet6 | dV_energy | 909 | 909 | 0 | 0 | 0.0196096313 | 0.0928532982 | 0.761037006 | 0.984486596 | 2.27463347 |
| 6 | Sheet6 | dV_Q | 909 | 909 | 0 | 0 | 0.00496728768 | 0.0235610753 | 0.761488107 | 0.984544922 | 2.27415772 |
| 6 | Sheet6 | dV_t_mean | 909 | 909 | 0 | 0 | 0.00596077598 | 0.0462893946 | 0.994123247 | 0.99947082 | 0.336689003 |
| 6 | Sheet6 | dV_V_mean | 909 | 909 | 0 | 0 | 0.000625128258 | 0.00228013655 | 0.649970241 | 0.978051767 | 0.0158379109 |
| 6 | Sheet6 | dV_T_mean | 909 | 909 | 0 | 0 | 0.00548189255 | 0.0146634919 | 0.999976803 | 0.999981742 | 0.0224012206 |
| 6 | Sheet6 | dV_V_std | 909 | 909 | 0 | 0 | 0.000112798802 | 0.000257951278 | 0.539719243 | 0.756037581 | 0.391059793 |
| 6 | Sheet6 | dV_T_std | 909 | 909 | 0 | 0 | 0.00859632887 | 0.0347945712 | 0.95500752 | 0.989595401 | 4.55484076 |
| 6 | Sheet6 | dV_V_skewness | 909 | 909 | 0 | 0 | 0.0217599648 | 0.0950144571 | 0.661651166 | 0.988006159 | 16.8302554 |
| 6 | Sheet6 | dV_T_skewness | 909 | 909 | 0 | 0 | 0.1440022 | 0.396334948 | 0.731085709 | 0.851784752 | 47.9215821 |
| 6 | Sheet6 | dV_V_kurtosis | 909 | 909 | 0 | 0 | 0.0113158588 | 0.0453072768 | 0.335521938 | 0.916449198 | 0.622474015 |
| 6 | Sheet6 | dV_T_kurtosis | 909 | 909 | 0 | 0 | 0.442451473 | 2.68009922 | 0.602287423 | 0.805481408 | 19.0618134 |
| 6 | Sheet6 | dV_dV_devide_dt | 909 | 909 | 0 | 0 | 0.00176765098 | 0.0108005396 | 0.541186512 | 0.997944571 | 6.17708641 |
| 6 | Sheet6 | dV_entropy | 909 | 909 | 0 | 0 | 4.82800556 | 4.82970967 | 0.247924265 | -0.143640481 | 63.5981798 |
| 6 | Sheet6 | CV_energy | 909 | 909 | 0 | 0 | 0.0233228762 | 0.0278018537 | 0.99739767 | 0.994227993 | 1.67195587 |
| 6 | Sheet6 | CV_Q | 909 | 909 | 0 | 0 | 0.00555346345 | 0.00661991877 | 0.997397363 | 0.994228425 | 1.67192517 |
| 6 | Sheet6 | CV_t_mean | 909 | 909 | 0 | 0 | 0.0499441546 | 0.0576100912 | 0.999867371 | 0.999846846 | 0.347191786 |
| 6 | Sheet6 | CV_C_mean | 909 | 909 | 0 | 0 | 0.00668222793 | 0.00804887131 | 0.997088406 | 0.978483676 | 0.960845633 |
| 6 | Sheet6 | CV_T_mean | 909 | 909 | 0 | 0 | 0.00739431062 | 0.0101591251 | 0.999990865 | 0.99995584 | 0.0327715178 |
| 6 | Sheet6 | CV_C_std | 909 | 909 | 0 | 0 | 0.0114165397 | 0.0137757044 | 0.996370915 | 0.887254994 | 1.43536054 |
| 6 | Sheet6 | CV_T_std | 909 | 909 | 0 | 0 | 0.00455349735 | 0.00585841454 | 0.999923637 | 0.999760188 | 0.313272757 |
| 6 | Sheet6 | CV_C_skewness | 909 | 909 | 0 | 0 | 0.0106527303 | 0.0125367187 | 0.998092563 | 0.994205067 | 0.579816686 |
| 6 | Sheet6 | CV_T_skewness | 909 | 909 | 0 | 0 | 0.0238621356 | 0.139623474 | 0.587148983 | 0.945666889 | 3.32559678 |
| 6 | Sheet6 | CV_C_kurtosis | 909 | 909 | 0 | 0 | 0.0515471714 | 0.0605356525 | 0.997530151 | 0.993193766 | 0.891362905 |
| 6 | Sheet6 | CV_T_kurtosis | 909 | 909 | 0 | 0 | 0.0138811426 | 0.0194494728 | 0.994801778 | 0.995249103 | 0.655440579 |
| 6 | Sheet6 | CV_CVCT | 909 | 909 | 0 | 0 | 0.0922275429 | 0.108210184 | 0.999869444 | 0.999855598 | 0.320652941 |
| 6 | Sheet6 | CV_entropy | 909 | 909 | 0 | 0 | 4.73129463 | 4.7317758 | 0.996481007 | 0.985287693 | 71.4977243 |
| 6 | Sheet6 | dI_energy | 909 | 909 | 0 | 0 | 0.00149331112 | 0.00309557174 | 0.918072549 | 0.990134015 | 3.41898635 |
| 6 | Sheet6 | dI_Q | 909 | 909 | 0 | 0 | 0.000355580893 | 0.000737096501 | 0.918063821 | 0.990122336 | 3.41897051 |
| 6 | Sheet6 | dI_t_mean | 909 | 909 | 0 | 0 | 0.0112323819 | 0.0232815325 | 0.918143081 | 0.989892861 | 3.41556281 |
| 6 | Sheet6 | dI_C_mean | 909 | 909 | 0 | 0 | 0.000461587938 | 0.000574961244 | 0.443366165 | 0.315612467 | 0.0486493915 |
| 6 | Sheet6 | dI_T_mean | 909 | 909 | 0 | 0 | 0.0129504808 | 0.0163560599 | 0.999961783 | 0.999862344 | 0.0543977828 |
| 6 | Sheet6 | dI_C_std | 909 | 909 | 0 | 0 | 0.000269513756 | 0.000330340097 | 0.0858325777 | 0.0676522602 | 0.933746099 |
| 6 | Sheet6 | dI_T_std | 909 | 909 | 0 | 0 | 0.0109466183 | 0.0138491254 | 0.875253892 | 0.872889343 | 15.4936647 |
| 6 | Sheet6 | dI_C_skewness | 909 | 909 | 0 | 0 | 0.0072521413 | 0.0130108943 | 0.651099982 | 0.621925554 | 15.2644348 |
| 6 | Sheet6 | dI_T_skewness | 909 | 909 | 0 | 0 | 0.427678087 | 0.869404006 | 0.308868942 | 0.464212331 | 116.87459 |
| 6 | Sheet6 | dI_C_kurtosis | 909 | 909 | 0 | 0 | 0.00529463044 | 0.00697174296 | 0.386914367 | 0.34093518 | 0.293928684 |
| 6 | Sheet6 | dI_T_kurtosis | 909 | 909 | 0 | 0 | 1.07193113 | 8.6262091 | 0.0696448581 | 0.316295122 | 46.370155 |
| 6 | Sheet6 | dI_dI_devide_dt | 909 | 909 | 0 | 0 | 0.000635239313 | 0.00186989253 | 0.99549745 | 0.999166238 | 0.423970964 |
| 6 | Sheet6 | dI_entropy | 909 | 909 | 0 | 0 | 2.52645923 | 2.53313095 | -0.125895988 | -0.0116878885 | 47.6901422 |
| 6 | Sheet6 | Charge_energy | 909 | 909 | 0 | 0 | 0.000292696436 | 0.000344192755 | 0.999999482 | 0.999996325 | 0.00816260871 |
| 6 | Sheet6 | Charge_Q | 909 | 909 | 0 | 0 | 6.72549628e-05 | 7.9723413e-05 | 0.99999953 | 0.999996357 | 0.0076885197 |
| 6 | Sheet6 | Charge_t_mean | 909 | 909 | 0 | 0 | 0.00579276809 | 0.0086307473 | 0.999993522 | 0.999985289 | 0.030652797 |
| 6 | Sheet6 | Charge_V_mean | 909 | 909 | 0 | 0 | 0.000551602455 | 0.00194748806 | 0.963521143 | 0.998177861 | 0.0132556666 |
| 6 | Sheet6 | Charge_C_mean | 909 | 909 | 0 | 0 | 0.00211363727 | 0.00245676815 | 0.999973609 | 0.999765796 | 0.150709838 |
| 6 | Sheet6 | Charge_T_mean | 909 | 909 | 0 | 0 | 0.00228026776 | 0.00457220633 | 0.999997353 | 0.999991692 | 0.0098746206 |
| 6 | Sheet6 | Charge_C_std | 909 | 909 | 0 | 0 | 0.00158127165 | 0.00178096943 | 0.999995534 | 0.99964982 | 0.108216504 |
| 6 | Sheet6 | Charge_V_std | 909 | 909 | 0 | 0 | 0.00106847924 | 0.00305672109 | 0.853170888 | 0.998130969 | 1.31899821 |
| 6 | Sheet6 | Charge_T_std | 909 | 909 | 0 | 0 | 0.00149919605 | 0.00237046106 | 0.999986073 | 0.999968622 | 0.0924133486 |
| 6 | Sheet6 | Charge_C_skewness | 909 | 909 | 0 | 0 | 0.00458443264 | 0.0223469085 | 0.994704395 | 0.999676613 | 0.617606459 |
| 6 | Sheet6 | Charge_V_skewness | 909 | 909 | 0 | 0 | 0.0160979438 | 0.0928968739 | 0.944686628 | 0.999418939 | 0.806128494 |
| 6 | Sheet6 | Charge_T_skewness | 909 | 909 | 0 | 0 | 0.0122940438 | 0.0967563346 | 0.87750343 | 0.982099484 | 7.19742508 |
| 6 | Sheet6 | Charge_C_kurtosis | 909 | 909 | 0 | 0 | 0.0112342217 | 0.0515361771 | 0.9825704 | 0.99961662 | 0.610711977 |
| 6 | Sheet6 | Charge_V_kurtosis | 909 | 909 | 0 | 0 | 0.111233736 | 0.735673655 | 0.829075598 | 0.99895788 | 1.98574834 |
| 6 | Sheet6 | Charge_T_kurtosis | 909 | 909 | 0 | 0 | 0.0120936766 | 0.092486979 | 0.803227124 | 0.985919508 | 0.855161587 |
| 6 | Sheet7 | CC_energy | 798 | 798 | 0 | 0 | 0.043771186 | 0.0940553014 | 0.893773819 | 0.968715387 | 1.98474368 |
| 6 | Sheet7 | CC_Q | 798 | 798 | 0 | 0 | 0.0105763891 | 0.0233937228 | 0.893765279 | 0.970677379 | 1.93661347 |
| 6 | Sheet7 | CC_t_mean | 798 | 798 | 0 | 0 | 0.0640588309 | 0.0766127942 | 0.999241883 | 0.978644491 | 1.41150628 |
| 6 | Sheet7 | CC_V_mean | 798 | 798 | 0 | 0 | 0.00309038066 | 0.00516113915 | 0.673811729 | 0.909867405 | 0.0765329595 |
| 6 | Sheet7 | CC_T_mean | 798 | 798 | 0 | 0 | 0.0109558935 | 0.0152045992 | 0.999988628 | 0.999960281 | 0.0425894507 |
| 6 | Sheet7 | CC_V_std | 798 | 798 | 0 | 0 | 0.00166283417 | 0.00242679917 | 0.573164891 | 0.674251426 | 1.88518563 |
| 6 | Sheet7 | CC_T_std | 798 | 798 | 0 | 0 | 0.0053235785 | 0.00697498043 | 0.999740059 | 0.999548662 | 1.21655176 |
| 6 | Sheet7 | CC_V_skewness | 798 | 798 | 0 | 0 | 0.0142792799 | 0.0601166783 | 0.701150799 | 0.982159755 | 9.02693705 |
| 6 | Sheet7 | CC_T_skewness | 798 | 798 | 0 | 0 | 0.0813601034 | 0.502719023 | 0.606041921 | 0.941277739 | 19.1886911 |
| 6 | Sheet7 | CC_V_kurtosis | 798 | 798 | 0 | 0 | 0.0104200545 | 0.0396799416 | 0.509523559 | 0.959274312 | 0.585150993 |
| 6 | Sheet7 | CC_T_kurtosis | 798 | 798 | 0 | 0 | 0.222009875 | 1.97498996 | 0.77772142 | 0.941120256 | 9.65544813 |
| 6 | Sheet7 | CC_CCCT | 798 | 798 | 0 | 0 | 0.12832835 | 0.153387225 | 0.999241939 | 0.978703997 | 1.41379562 |
| 6 | Sheet7 | CC_entropy | 798 | 798 | 0 | 0 | 5.18140394 | 5.1814212 | 0.672658374 | 0.712354873 | 65.253611 |
| 6 | Sheet7 | dV_energy | 798 | 798 | 0 | 0 | 0.0171661934 | 0.0811339803 | 0.792240772 | 0.986881579 | 2.00517955 |
| 6 | Sheet7 | dV_Q | 798 | 798 | 0 | 0 | 0.00434943124 | 0.0205923461 | 0.792483733 | 0.986925797 | 2.00525187 |
| 6 | Sheet7 | dV_t_mean | 798 | 798 | 0 | 0 | 0.00382385397 | 0.00457697746 | 0.999976411 | 0.99962931 | 0.216266824 |
| 6 | Sheet7 | dV_V_mean | 798 | 798 | 0 | 0 | 0.000507363972 | 0.00183908272 | 0.681714802 | 0.976226745 | 0.0128543652 |
| 6 | Sheet7 | dV_T_mean | 798 | 798 | 0 | 0 | 0.00527117551 | 0.00678485427 | 0.99999592 | 0.999981215 | 0.0208735693 |
| 6 | Sheet7 | dV_V_std | 798 | 798 | 0 | 0 | 9.50074855e-05 | 0.000215632686 | 0.521045519 | 0.71987555 | 0.328942112 |
| 6 | Sheet7 | dV_T_std | 798 | 798 | 0 | 0 | 0.00555290849 | 0.00701087851 | 0.998449474 | 0.997348492 | 2.44609883 |
| 6 | Sheet7 | dV_V_skewness | 798 | 798 | 0 | 0 | 0.0175357994 | 0.076118238 | 0.677921533 | 0.983126449 | 13.7827822 |
| 6 | Sheet7 | dV_T_skewness | 798 | 798 | 0 | 0 | 0.138142184 | 0.464712773 | 0.762093808 | 0.861585935 | 46.7783941 |
| 6 | Sheet7 | dV_V_kurtosis | 798 | 798 | 0 | 0 | 0.00801493741 | 0.0316266969 | 0.346989866 | 0.890647288 | 0.441278098 |
| 6 | Sheet7 | dV_T_kurtosis | 798 | 798 | 0 | 0 | 0.471914078 | 3.0145345 | 0.625267544 | 0.80131002 | 19.6290252 |
| 6 | Sheet7 | dV_dV_devide_dt | 798 | 798 | 0 | 0 | 0.00146580702 | 0.00707315001 | 0.676231069 | 0.998264887 | 5.13712629 |
| 6 | Sheet7 | dV_entropy | 798 | 798 | 0 | 0 | 4.82848431 | 4.83026508 | 0.232778855 | -0.124650232 | 63.5892658 |
| 6 | Sheet7 | CV_energy | 798 | 798 | 0 | 0 | 0.0206194865 | 0.0402804032 | 0.984228086 | 0.990303277 | 1.50871912 |
| 6 | Sheet7 | CV_Q | 798 | 798 | 0 | 0 | 0.00490907102 | 0.00959002052 | 0.98422682 | 0.990290384 | 1.50864364 |
| 6 | Sheet7 | CV_t_mean | 798 | 798 | 0 | 0 | 0.0410609071 | 0.0475171371 | 0.99986023 | 0.999795879 | 0.299132921 |
| 6 | Sheet7 | CV_C_mean | 798 | 798 | 0 | 0 | 0.00570790971 | 0.00661419445 | 0.997846145 | 0.982564549 | 0.800376408 |
| 6 | Sheet7 | CV_T_mean | 798 | 798 | 0 | 0 | 0.00713806957 | 0.00864279724 | 0.999995037 | 0.999950646 | 0.030781765 |
| 6 | Sheet7 | CV_C_std | 798 | 798 | 0 | 0 | 0.00982046479 | 0.0113547154 | 0.997252185 | 0.931646003 | 1.23241533 |
| 6 | Sheet7 | CV_T_std | 798 | 798 | 0 | 0 | 0.00447131335 | 0.0054393163 | 0.999940518 | 0.999697101 | 0.268926181 |
| 6 | Sheet7 | CV_C_skewness | 798 | 798 | 0 | 0 | 0.00988251518 | 0.0113202725 | 0.998845088 | 0.996875865 | 0.54580714 |
| 6 | Sheet7 | CV_T_skewness | 798 | 798 | 0 | 0 | 0.0211354422 | 0.143628514 | 0.556016089 | 0.95233457 | 3.09000521 |
| 6 | Sheet7 | CV_C_kurtosis | 798 | 798 | 0 | 0 | 0.0467478625 | 0.0538102121 | 0.998604915 | 0.996965481 | 0.81770667 |
| 6 | Sheet7 | CV_T_kurtosis | 798 | 798 | 0 | 0 | 0.0105234385 | 0.0127270189 | 0.997158944 | 0.996089323 | 0.509510981 |
| 6 | Sheet7 | CV_CVCT | 798 | 798 | 0 | 0 | 0.0739213683 | 0.0870134462 | 0.999867261 | 0.99981258 | 0.269347894 |
| 6 | Sheet7 | CV_entropy | 798 | 798 | 0 | 0 | 4.76611569 | 4.76655363 | 0.997012201 | 0.982949937 | 71.1796415 |
| 6 | Sheet7 | dI_energy | 798 | 798 | 0 | 0 | 0.00130268612 | 0.00382499354 | 0.923474373 | 0.997069147 | 2.80258771 |
| 6 | Sheet7 | dI_Q | 798 | 798 | 0 | 0 | 0.000310156694 | 0.000910672042 | 0.923470161 | 0.997065463 | 2.80257968 |
| 6 | Sheet7 | dI_t_mean | 798 | 798 | 0 | 0 | 0.00977994138 | 0.0287396778 | 0.923511546 | 0.996907195 | 2.79452615 |
| 6 | Sheet7 | dI_C_mean | 798 | 798 | 0 | 0 | 0.000501348761 | 0.000753742355 | 0.596150239 | 0.641676655 | 0.0528448638 |
| 6 | Sheet7 | dI_T_mean | 798 | 798 | 0 | 0 | 0.0130079048 | 0.0158220904 | 0.999971362 | 0.999826725 | 0.0529224505 |
| 6 | Sheet7 | dI_C_std | 798 | 798 | 0 | 0 | 0.000260817289 | 0.000329746217 | 0.0255391101 | 0.0396960739 | 0.902234537 |
| 6 | Sheet7 | dI_T_std | 798 | 798 | 0 | 0 | 0.0108929803 | 0.013934935 | 0.89745142 | 0.883612675 | 13.0721697 |
| 6 | Sheet7 | dI_C_skewness | 798 | 798 | 0 | 0 | 0.00936445958 | 0.0235897356 | 0.716628172 | 0.828481723 | 18.7272592 |
| 6 | Sheet7 | dI_T_skewness | 798 | 798 | 0 | 0 | 0.326505597 | 0.532506822 | 0.418920371 | 0.493287335 | 109.975762 |
| 6 | Sheet7 | dI_C_kurtosis | 798 | 798 | 0 | 0 | 0.00700277089 | 0.0118157121 | 0.440010421 | 0.502366444 | 0.388135888 |
| 6 | Sheet7 | dI_T_kurtosis | 798 | 798 | 0 | 0 | 0.604540461 | 1.76046242 | 0.126392781 | 0.38064355 | 27.7261483 |
| 6 | Sheet7 | dI_dI_devide_dt | 798 | 798 | 0 | 0 | 0.000743231071 | 0.00228187652 | 0.995893087 | 0.999363089 | 0.516973575 |
| 6 | Sheet7 | dI_entropy | 798 | 798 | 0 | 0 | 2.60300536 | 2.61513388 | -0.0787384165 | 0.221587696 | 48.4389378 |
| 6 | Sheet7 | Charge_energy | 798 | 798 | 0 | 0 | 0.000269582076 | 0.000318119352 | 0.999999582 | 0.999997284 | 0.00755648279 |
| 6 | Sheet7 | Charge_Q | 798 | 798 | 0 | 0 | 6.21760813e-05 | 7.38722438e-05 | 0.999999619 | 0.999997214 | 0.00714416051 |
| 6 | Sheet7 | Charge_t_mean | 798 | 798 | 0 | 0 | 0.00932073861 | 0.0947876559 | 0.998623801 | 0.999961822 | 0.0510172582 |
| 6 | Sheet7 | Charge_V_mean | 798 | 798 | 0 | 0 | 0.000419203963 | 0.000969332185 | 0.992661492 | 0.998983432 | 0.0100765314 |
| 6 | Sheet7 | Charge_C_mean | 798 | 798 | 0 | 0 | 0.00193828329 | 0.00218771752 | 0.99997896 | 0.999807544 | 0.134596684 |
| 6 | Sheet7 | Charge_T_mean | 798 | 798 | 0 | 0 | 0.00257789227 | 0.00328084273 | 0.999999237 | 0.999990672 | 0.0108323068 |
| 6 | Sheet7 | Charge_C_std | 798 | 798 | 0 | 0 | 0.00142379733 | 0.00155561594 | 0.99999758 | 0.999707113 | 0.0972548959 |
| 6 | Sheet7 | Charge_V_std | 798 | 798 | 0 | 0 | 0.000921248937 | 0.00240207672 | 0.899290462 | 0.998492375 | 1.12262737 |
| 6 | Sheet7 | Charge_T_std | 798 | 798 | 0 | 0 | 0.00150683976 | 0.0018738644 | 0.999993133 | 0.999962146 | 0.082007718 |
| 6 | Sheet7 | Charge_C_skewness | 798 | 798 | 0 | 0 | 0.00354685137 | 0.00383426553 | 0.999978296 | 0.999792431 | 0.512667997 |
| 6 | Sheet7 | Charge_V_skewness | 798 | 798 | 0 | 0 | 0.0121595941 | 0.0560894978 | 0.978018323 | 0.999478646 | 0.625654184 |
| 6 | Sheet7 | Charge_T_skewness | 798 | 798 | 0 | 0 | 0.0110297655 | 0.0949352535 | 0.882959848 | 0.976820489 | 7.17841382 |
| 6 | Sheet7 | Charge_C_kurtosis | 798 | 798 | 0 | 0 | 0.00657026573 | 0.00727949292 | 0.999956181 | 0.99975368 | 0.3715786 |
| 6 | Sheet7 | Charge_V_kurtosis | 798 | 798 | 0 | 0 | 0.0843830767 | 0.430610657 | 0.919302281 | 0.999046034 | 1.56852355 |
| 6 | Sheet7 | Charge_T_kurtosis | 798 | 798 | 0 | 0 | 0.0133067797 | 0.113610289 | 0.681536919 | 0.987096469 | 0.943020136 |
| 6 | Sheet8 | CC_energy | 879 | 879 | 0 | 0 | 0.0465597323 | 0.115596658 | 0.852142238 | 0.96550832 | 2.09860201 |
| 6 | Sheet8 | CC_Q | 879 | 879 | 0 | 0 | 0.0112653914 | 0.0287696632 | 0.852705243 | 0.967196022 | 2.0502515 |
| 6 | Sheet8 | CC_t_mean | 879 | 879 | 0 | 0 | 0.0687622642 | 0.145522338 | 0.992407948 | 0.975502425 | 1.51983198 |
| 6 | Sheet8 | CC_V_mean | 879 | 879 | 0 | 0 | 0.00322371345 | 0.00600778592 | 0.630393625 | 0.906620129 | 0.0798430508 |
| 6 | Sheet8 | CC_T_mean | 879 | 879 | 0 | 0 | 0.0169620645 | 0.159139691 | 0.997460852 | 0.999015812 | 0.0653487254 |
| 6 | Sheet8 | CC_V_std | 879 | 879 | 0 | 0 | 0.00170619055 | 0.00263448283 | 0.49349291 | 0.669849908 | 1.93447957 |
| 6 | Sheet8 | CC_T_std | 879 | 879 | 0 | 0 | 0.00571273538 | 0.0108241573 | 0.999283555 | 0.999073289 | 1.14131248 |
| 6 | Sheet8 | CC_V_skewness | 879 | 879 | 0 | 0 | 0.0154226432 | 0.07384616 | 0.651020935 | 0.983549421 | 9.45142094 |
| 6 | Sheet8 | CC_T_skewness | 879 | 879 | 0 | 0 | 0.0835396504 | 0.445260558 | 0.713316668 | 0.964823744 | 19.4446096 |
| 6 | Sheet8 | CC_V_kurtosis | 879 | 879 | 0 | 0 | 0.0123097925 | 0.0707565357 | 0.273293868 | 0.953065683 | 0.69047737 |
| 6 | Sheet8 | CC_T_kurtosis | 879 | 879 | 0 | 0 | 0.247511391 | 1.91511074 | 0.832683499 | 0.947150689 | 10.2490527 |
| 6 | Sheet8 | CC_CCCT | 879 | 879 | 0 | 0 | 0.137374002 | 0.290551107 | 0.992440857 | 0.975659763 | 1.51816749 |
| 6 | Sheet8 | CC_entropy | 879 | 879 | 0 | 0 | 5.18093905 | 5.1809628 | 0.405142618 | 0.703775564 | 65.2610694 |
| 6 | Sheet8 | dV_energy | 879 | 879 | 0 | 0 | 0.0178235681 | 0.0875185795 | 0.786992298 | 0.982730757 | 2.05770188 |
| 6 | Sheet8 | dV_Q | 879 | 879 | 0 | 0 | 0.00451678485 | 0.022207076 | 0.787294472 | 0.982766979 | 2.05809505 |
| 6 | Sheet8 | dV_t_mean | 879 | 879 | 0 | 0 | 0.00532940739 | 0.0608754572 | 0.988985307 | 0.995246262 | 0.300509486 |
| 6 | Sheet8 | dV_V_mean | 879 | 879 | 0 | 0 | 0.000509813083 | 0.00208730404 | 0.629292483 | 0.971715746 | 0.0129166361 |
| 6 | Sheet8 | dV_T_mean | 879 | 879 | 0 | 0 | 0.0105289602 | 0.150884022 | 0.997853296 | 0.998909863 | 0.041422279 |
| 6 | Sheet8 | dV_V_std | 879 | 879 | 0 | 0 | 0.000101880061 | 0.000585557883 | 0.240578134 | 0.759054157 | 0.352398851 |
| 6 | Sheet8 | dV_T_std | 879 | 879 | 0 | 0 | 0.00711777184 | 0.0199731428 | 0.98855186 | 0.996313672 | 2.75356834 |
| 6 | Sheet8 | dV_V_skewness | 879 | 879 | 0 | 0 | 0.0171335332 | 0.073985379 | 0.694382555 | 0.981590215 | 13.1703746 |
| 6 | Sheet8 | dV_T_skewness | 879 | 879 | 0 | 0 | 0.118867687 | 0.434458263 | 0.628625061 | 0.841856894 | 51.5096534 |
| 6 | Sheet8 | dV_V_kurtosis | 879 | 879 | 0 | 0 | 0.00714384161 | 0.0293727513 | 0.401270481 | 0.892655667 | 0.392996944 |
| 6 | Sheet8 | dV_T_kurtosis | 879 | 879 | 0 | 0 | 0.407615681 | 2.90912348 | 0.439602189 | 0.758194728 | 18.1776496 |
| 6 | Sheet8 | dV_dV_devide_dt | 879 | 879 | 0 | 0 | 0.00204541006 | 0.0178232969 | 0.32708326 | 0.993744697 | 7.19767795 |
| 6 | Sheet8 | dV_entropy | 879 | 879 | 0 | 0 | 4.83279286 | 4.83466992 | 0.172247083 | -0.151620424 | 63.6128056 |
| 6 | Sheet8 | CV_energy | 879 | 879 | 0 | 0 | 0.020487213 | 0.0248908957 | 0.997521521 | 0.993997072 | 1.47646473 |
| 6 | Sheet8 | CV_Q | 879 | 879 | 0 | 0 | 0.00487766279 | 0.00592606135 | 0.997521454 | 0.993998309 | 1.47639001 |
| 6 | Sheet8 | CV_t_mean | 879 | 879 | 0 | 0 | 0.0467949306 | 0.111798588 | 0.997530789 | 0.996857828 | 0.338495752 |
| 6 | Sheet8 | CV_C_mean | 879 | 879 | 0 | 0 | 0.00605761764 | 0.00742204749 | 0.997021894 | 0.977719209 | 0.843469018 |
| 6 | Sheet8 | CV_T_mean | 879 | 879 | 0 | 0 | 0.00920141061 | 0.0378217271 | 0.999821824 | 0.999804791 | 0.0395359503 |
| 6 | Sheet8 | CV_C_std | 879 | 879 | 0 | 0 | 0.01027031 | 0.0120534502 | 0.996786596 | 0.925007916 | 1.2792358 |
| 6 | Sheet8 | CV_T_std | 879 | 879 | 0 | 0 | 0.00621193951 | 0.0467109247 | 0.995084574 | 0.995782184 | 0.342242403 |
| 6 | Sheet8 | CV_C_skewness | 879 | 879 | 0 | 0 | 0.0105770053 | 0.0158836942 | 0.997047908 | 0.992588082 | 0.585352258 |
| 6 | Sheet8 | CV_T_skewness | 879 | 879 | 0 | 0 | 0.0202037371 | 0.138172492 | 0.584777739 | 0.970528226 | 3.13717313 |
| 6 | Sheet8 | CV_C_kurtosis | 879 | 879 | 0 | 0 | 0.0496668983 | 0.0747358769 | 0.99634176 | 0.992728799 | 0.871807199 |
| 6 | Sheet8 | CV_T_kurtosis | 879 | 879 | 0 | 0 | 0.0107706126 | 0.0222844038 | 0.987389977 | 0.990262542 | 0.534000322 |
| 6 | Sheet8 | CV_CVCT | 879 | 879 | 0 | 0 | 0.0855342048 | 0.219722061 | 0.997541582 | 0.996876844 | 0.309457438 |
| 6 | Sheet8 | CV_entropy | 879 | 879 | 0 | 0 | 4.76506528 | 4.76547237 | 0.996501071 | 0.977966811 | 71.1706472 |
| 6 | Sheet8 | dI_energy | 879 | 879 | 0 | 0 | 0.00136708209 | 0.00332469002 | 0.938940487 | 0.991876423 | 2.91832672 |
| 6 | Sheet8 | dI_Q | 879 | 879 | 0 | 0 | 0.000325495677 | 0.000791592902 | 0.938940458 | 0.991876423 | 2.91832623 |
| 6 | Sheet8 | dI_t_mean | 879 | 879 | 0 | 0 | 0.0103153805 | 0.0252359315 | 0.937989003 | 0.991737499 | 2.92487188 |
| 6 | Sheet8 | dI_C_mean | 879 | 879 | 0 | 0 | 0.000468824024 | 0.000666820587 | 0.733273554 | 0.689838487 | 0.0494160818 |
| 6 | Sheet8 | dI_T_mean | 879 | 879 | 0 | 0 | 0.0150908924 | 0.0771041517 | 0.999233326 | 0.999287006 | 0.0608862574 |
| 6 | Sheet8 | dI_C_std | 879 | 879 | 0 | 0 | 0.000271169702 | 0.000338052586 | 0.1310421 | 0.12627216 | 0.939914614 |
| 6 | Sheet8 | dI_T_std | 879 | 879 | 0 | 0 | 0.0103214972 | 0.0133488932 | 0.909699402 | 0.893337189 | 11.861335 |
| 6 | Sheet8 | dI_C_skewness | 879 | 879 | 0 | 0 | 0.00858073864 | 0.0202679132 | 0.851895572 | 0.889896349 | 17.0677363 |
| 6 | Sheet8 | dI_T_skewness | 879 | 879 | 0 | 0 | 0.3248549 | 0.535563186 | 0.418945559 | 0.522654976 | 103.770604 |
| 6 | Sheet8 | dI_C_kurtosis | 879 | 879 | 0 | 0 | 0.0070339786 | 0.0117738811 | 0.514967644 | 0.514159317 | 0.389966187 |
| 6 | Sheet8 | dI_T_kurtosis | 879 | 879 | 0 | 0 | 0.533074246 | 1.72110924 | 0.267294336 | 0.431578271 | 24.4289911 |
| 6 | Sheet8 | dI_dI_devide_dt | 879 | 879 | 0 | 0 | 0.000968578218 | 0.00458108003 | 0.982203262 | 0.994051652 | 0.682651201 |
| 6 | Sheet8 | dI_entropy | 879 | 879 | 0 | 0 | 2.61531471 | 2.62679859 | -0.180655366 | 0.179156794 | 48.5577724 |
| 6 | Sheet8 | Charge_energy | 879 | 879 | 0 | 0 | 0.0026442154 | 0.0703095471 | 0.979939351 | 0.994558933 | 0.0734523107 |
| 6 | Sheet8 | Charge_Q | 879 | 879 | 0 | 0 | 0.000651793858 | 0.017461153 | 0.979279675 | 0.994545928 | 0.0742192664 |
| 6 | Sheet8 | Charge_t_mean | 879 | 879 | 0 | 0 | 0.0134433515 | 0.220780038 | 0.992362973 | 0.995864058 | 0.0732314786 |
| 6 | Sheet8 | Charge_V_mean | 879 | 879 | 0 | 0 | 0.000487641022 | 0.00167470299 | 0.973133023 | 0.99787382 | 0.0117211273 |
| 6 | Sheet8 | Charge_C_mean | 879 | 879 | 0 | 0 | 0.00254457673 | 0.0152341478 | 0.995650065 | 0.999102249 | 0.176020266 |
| 6 | Sheet8 | Charge_T_mean | 879 | 879 | 0 | 0 | 0.00493939378 | 0.0644366075 | 0.999478324 | 0.999603399 | 0.0206531732 |
| 6 | Sheet8 | Charge_C_std | 879 | 879 | 0 | 0 | 0.00190832392 | 0.0125408216 | 0.998717712 | 0.998920151 | 0.129699575 |
| 6 | Sheet8 | Charge_V_std | 879 | 879 | 0 | 0 | 0.0010442139 | 0.00319863721 | 0.832643682 | 0.997625923 | 1.27262899 |
| 6 | Sheet8 | Charge_T_std | 879 | 879 | 0 | 0 | 0.00344931147 | 0.056125811 | 0.994433613 | 0.995126341 | 0.173769933 |
| 6 | Sheet8 | Charge_C_skewness | 879 | 879 | 0 | 0 | 0.00440895934 | 0.0220957174 | 0.994414261 | 0.999436584 | 0.631803053 |
| 6 | Sheet8 | Charge_V_skewness | 879 | 879 | 0 | 0 | 0.0170853016 | 0.152924296 | 0.860623062 | 0.99883094 | 0.87554305 |
| 6 | Sheet8 | Charge_T_skewness | 879 | 879 | 0 | 0 | 0.0130666734 | 0.106497845 | 0.850549311 | 0.983529596 | 9.22815068 |
| 6 | Sheet8 | Charge_C_kurtosis | 879 | 879 | 0 | 0 | 0.0102871461 | 0.0710513549 | 0.956530441 | 0.999247277 | 0.580264723 |
| 6 | Sheet8 | Charge_V_kurtosis | 879 | 879 | 0 | 0 | 0.142470421 | 1.47160894 | 0.561824289 | 0.998347777 | 2.63986195 |
| 6 | Sheet8 | Charge_T_kurtosis | 879 | 879 | 0 | 0 | 0.0141986571 | 0.122698519 | 0.652705098 | 0.987386414 | 0.996677597 |

## Original-reference benchmark reproduction

No original-reference implementation was created because no authoritative 67-column formula set or generating code was found. Accordingly, original-reference values and original-reference MAE, RMSE, correlation, relative error, and valid-pair counts are **not available**. The candidate tables above are kept separate and cannot be relabeled as original reproduction.

## Research gaps and next steps

1. Request from SOHbenchmark authors the exact script/notebook, source version, and preprocessing inputs that generated `batch-1_features.xlsx` through `batch-6_features.xlsx`, plus the mapping of workbook rows to raw cycles.
2. Request from XJTU dataset authors a source-authored mapping for each of the 67 columns: signal, units, stage/window thresholds, boundary interpolation, sampling/weights, integration/derivative estimator, statistical conventions, and entropy estimator.
3. Ask the XJTU authors to document the preprocessing between the release's stated 1 Hz acquisition data and the 128-point-per-cycle prepared MAT traces, including any resampling or selection.
4. If primary formulas/code are supplied, implement a separately named reference extractor in this isolated directory, retain the current candidate extractor unchanged, and compare the two independently against Excel only after validating cycle alignment.
5. Until then, retain Candidate / Unverified or Original Formula Unknown statuses and treat numerical agreement only as a candidate quality diagnostic.

## Reproducibility

From the repository root, run `scripts/member4_xjtu/original_verification/report.py` as a module to regenerate this report. This command reads the raw MAT files and feature workbooks, imports the existing candidate extractor and alignment helper without modifying them, and writes only this report file.
