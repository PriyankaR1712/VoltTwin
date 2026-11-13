from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from openpyxl import load_workbook
from scipy.stats import rankdata

from scripts.member4_xjtu.extractor import extract_cycle
from scripts.member4_xjtu.feature_definitions import (
    FEATURE_NAMES,
    FeatureDefinition,
    feature_definitions,
)
from scripts.member4_xjtu.loader import DEFAULT_DATA_ROOT, load_batch
from scripts.member4_xjtu.segments import SegmentationPolicy
from scripts.member4_xjtu.validation import _profile_pairs

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_REPORT = REPOSITORY_ROOT / "reports" / "member4_original_formula_verification.md"
BATCHES = tuple(range(1, 7))
INPUT_UNITS = {
    "voltage and current": "V, A",
    "current and time": "A, min",
    "elapsed time": "min",
    "voltage": "V",
    "temperature": "°C",
    "time": "min",
    "voltage and time": "V, min",
    "current and time": "A, min",
    "voltage proxy": "V",
    "current proxy": "A",
}


@dataclass
class FeaturePairs:
    aligned_pairs: int = 0
    workbook_invalid: int = 0
    candidate_invalid: int = 0
    workbook_values: list[float] = field(default_factory=list)
    candidate_values: list[float] = field(default_factory=list)

    def add(self, workbook_value: Any, candidate_value: Any) -> None:
        self.aligned_pairs += 1
        expected = _finite_number(workbook_value)
        candidate = _finite_number(candidate_value)
        if expected is None:
            self.workbook_invalid += 1
        if candidate is None:
            self.candidate_invalid += 1
        if expected is not None and candidate is not None:
            self.workbook_values.append(expected)
            self.candidate_values.append(candidate)


def _finite_number(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _correlation(left: np.ndarray, right: np.ndarray) -> tuple[float | None, float | None]:
    if len(left) < 2:
        return None, None
    left_ranks = rankdata(left, method="average")
    right_ranks = rankdata(right, method="average")
    if np.ptp(left) == 0 or np.ptp(right) == 0:
        pearson = None
    else:
        pearson = float(np.corrcoef(left, right)[0, 1])
    if np.ptp(left_ranks) == 0 or np.ptp(right_ranks) == 0:
        spearman = None
    else:
        spearman = float(np.corrcoef(left_ranks, right_ranks)[0, 1])
    return pearson, spearman


def summarize_pairs(pairs: FeaturePairs) -> dict[str, int | float | None]:
    actual = np.asarray(pairs.workbook_values, dtype=np.float64)
    candidate = np.asarray(pairs.candidate_values, dtype=np.float64)
    if len(actual):
        errors = candidate - actual
        mae = float(np.mean(np.abs(errors)))
        rmse = float(np.sqrt(np.mean(errors**2)))
        reference_scale = float(np.mean(np.abs(actual)))
        relative_error = (
            float(mae / reference_scale * 100) if reference_scale > 0 else None
        )
        pearson, spearman = _correlation(actual, candidate)
    else:
        mae = rmse = relative_error = pearson = spearman = None
    return {
        "aligned_pairs": pairs.aligned_pairs,
        "valid_pairs": len(actual),
        "workbook_invalid": pairs.workbook_invalid,
        "candidate_invalid": pairs.candidate_invalid,
        "mae": mae,
        "rmse": rmse,
        "pearson_r": pearson,
        "spearman_rho": spearman,
        "relative_error_pct": relative_error,
    }


def _new_pairs() -> dict[str, FeaturePairs]:
    return {name: FeaturePairs() for name in FEATURE_NAMES}


def _alignment_rows(
    batches: Iterable[int],
    data_root: Path,
) -> tuple[
    list[dict[str, Any]],
    dict[str, dict[str, FeaturePairs]],
    dict[str, FeaturePairs],
    dict[str, Any],
]:
    profile_rows: list[dict[str, Any]] = []
    batch_pairs: dict[str, dict[str, FeaturePairs]] = {}
    overall_pairs = _new_pairs()
    sampling = {
        "cycles": 0,
        "nonuniform_cycles": 0,
        "min_samples": None,
        "max_samples": 0,
        "min_delta_min": math.inf,
        "max_delta_min": 0.0,
        "median_delta_min_by_cycle": [],
        "maximum_relative_step_deviation": 0.0,
    }

    for batch in batches:
        profiles, sheets = load_batch(batch, data_root)
        scope = f"batch-{batch}"
        batch_pairs[scope] = _new_pairs()
        for (sheet_name, frame), cycles in zip(sheets.items(), profiles):
            profile_pairs = _new_pairs()
            paired, method, unmatched_rows, ambiguous_rows = _profile_pairs(
                cycles, frame
            )
            used_cycles = {cycle_index for cycle_index, _ in paired}
            label_differences: list[float] = []
            for trace in cycles:
                delta_time = np.diff(trace.time_min)
                sampling["cycles"] += 1
                sampling["min_samples"] = (
                    len(trace.time_min)
                    if sampling["min_samples"] is None
                    else min(sampling["min_samples"], len(trace.time_min))
                )
                sampling["max_samples"] = max(
                    sampling["max_samples"], len(trace.time_min)
                )
                median_delta = float(np.median(delta_time))
                sampling["median_delta_min_by_cycle"].append(median_delta)
                sampling["min_delta_min"] = min(
                    sampling["min_delta_min"], float(np.min(delta_time))
                )
                sampling["max_delta_min"] = max(
                    sampling["max_delta_min"], float(np.max(delta_time))
                )
                relative_deviation = float(
                    np.max(np.abs(delta_time - median_delta)) / abs(median_delta)
                )
                sampling["maximum_relative_step_deviation"] = max(
                    sampling["maximum_relative_step_deviation"], relative_deviation
                )
                if not np.allclose(
                    delta_time, median_delta, rtol=1e-6, atol=1e-9
                ):
                    sampling["nonuniform_cycles"] += 1

            for cycle_index, row_index in paired:
                trace = cycles[cycle_index]
                expected_row = frame.iloc[row_index]
                label_differences.append(
                    abs(
                        trace.capacity_label
                        - float(expected_row["label"])
                    )
                )
                candidate_values, _ = extract_cycle(trace, SegmentationPolicy())
                for name in FEATURE_NAMES:
                    workbook_value = expected_row[name]
                    candidate_value = candidate_values[name]
                    profile_pairs[name].add(workbook_value, candidate_value)
                    batch_pairs[scope][name].add(workbook_value, candidate_value)
                    overall_pairs[name].add(workbook_value, candidate_value)

            profile_rows.append(
                {
                    "batch": batch,
                    "profile": sheet_name,
                    "raw_cycles": len(cycles),
                    "workbook_rows": len(frame),
                    "matched_pairs": len(paired),
                    "unmatched_workbook_rows": len(unmatched_rows),
                    "ambiguous_workbook_rows": len(ambiguous_rows),
                    "unmatched_raw_cycles": len(cycles) - len(used_cycles),
                    "alignment_method": method,
                    "mean_abs_label_difference": (
                        float(np.mean(label_differences)) if label_differences else None
                    ),
                }
            )
            profile_rows.extend(
                {
                    "batch": batch,
                    "profile": sheet_name,
                    "feature": name,
                    **summarize_pairs(pairs),
                }
                for name, pairs in profile_pairs.items()
            )

    median_deltas = sampling.pop("median_delta_min_by_cycle")
    sampling["median_delta_min_across_cycles"] = (
        float(np.median(median_deltas)) if median_deltas else None
    )
    return profile_rows, batch_pairs, overall_pairs, {
        "alignment": profile_rows,
        "sampling": sampling,
    }


def _workbook_formula_audit(data_root: Path, batches: Iterable[int]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for batch in batches:
        path = data_root / "handcraft_features" / f"batch-{batch}_features.xlsx"
        workbook = load_workbook(path, data_only=False, read_only=False)
        formula_count = 0
        comment_count = 0
        for worksheet in workbook.worksheets:
            for row in worksheet.iter_rows():
                for cell in row:
                    if isinstance(cell.value, str) and cell.value.startswith("="):
                        formula_count += 1
                    if cell.comment is not None:
                        comment_count += 1
        records.append(
            {
                "batch": batch,
                "sheet_count": len(workbook.worksheets),
                "formula_cells": formula_count,
                "commented_cells": comment_count,
                "defined_names": len(workbook.defined_names),
                "feature_columns": (
                    workbook.worksheets[0].max_column - 1
                    if workbook.worksheets
                    else 0
                ),
            }
        )
        workbook.close()
    return records


def _feature_status(definition: FeatureDefinition) -> str:
    if definition.evidence_class == "unknown_original_definition":
        return "Original Formula Unknown"
    return "Candidate / Unverified"


def _segment_evidence(group: str) -> str:
    return {
        "CC": (
            "The XJTU author helper documents a CC sample selector (charging stage, "
            "I ≥ 3.9 A and V ≤ 4.199 V by default); no source links that selector "
            "to this Excel column. Candidate extractor instead uses an adaptive "
            "current threshold and V ceiling."
        ),
        "CV": (
            "The XJTU author helper documents a CV selector (V ≥ 4.199 V by "
            "default); no source links it to this Excel column. Candidate extractor "
            "uses the first rising crossing through the recorded endpoint."
        ),
        "dV": (
            "The author helper has CC-window dQ/dV incremental-capacity routines; "
            "they do not define this workbook column or its candidate voltage window."
        ),
        "dI": (
            "No source definition for the workbook's dI interval or this column was "
            "located; the falling-current window is candidate-only."
        ),
        "Charge": (
            "No source defines the workbook's full-charge start/end limits; the "
            "candidate uses the full stored charge trace."
        ),
    }[group]


def _format(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)):
        if not math.isfinite(float(value)):
            return "—"
        return f"{float(value):.9g}"
    return str(value).replace("|", "\\|").replace("\n", " ")


def _markdown_table(
    rows: Iterable[dict[str, Any]],
    columns: list[tuple[str, str]],
) -> list[str]:
    lines = [
        "| " + " | ".join(title for title, _ in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(_format(row.get(key)) for _, key in columns)
            + " |"
        )
    return lines


def _metric_rows(
    pairs_by_feature: dict[str, FeaturePairs],
    *,
    batch: int | None = None,
    profile: str | None = None,
) -> list[dict[str, Any]]:
    rows = []
    for definition in feature_definitions():
        rows.append(
            {
                "batch": batch,
                "profile": profile,
                "feature": definition.name,
                **summarize_pairs(pairs_by_feature[definition.name]),
            }
        )
    return rows


def _candidate_metric_columns(
    include_scope: str,
) -> list[tuple[str, str]]:
    columns = []
    if include_scope == "profile":
        columns.extend((("Batch", "batch"), ("Profile", "profile")))
    elif include_scope == "batch":
        columns.append(("Batch", "batch"))
    columns.extend(
        [
            ("Feature", "feature"),
            ("Aligned", "aligned_pairs"),
            ("Valid", "valid_pairs"),
            ("Workbook invalid", "workbook_invalid"),
            ("Candidate invalid", "candidate_invalid"),
            ("MAE", "mae"),
            ("RMSE", "rmse"),
            ("Pearson r", "pearson_r"),
            ("Spearman ρ", "spearman_rho"),
            ("Relative MAE (%)", "relative_error_pct"),
        ]
    )
    return columns


def _profile_alignment_table(
    profile_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            key: row[key]
            for key in (
                "batch",
                "profile",
                "raw_cycles",
                "workbook_rows",
                "matched_pairs",
                "unmatched_workbook_rows",
                "ambiguous_workbook_rows",
                "unmatched_raw_cycles",
                "alignment_method",
                "mean_abs_label_difference",
            )
        }
        for row in profile_rows
        if "feature" not in row
    ]


def _render_feature_table() -> list[str]:
    rows = []
    for order, definition in enumerate(feature_definitions(), start=1):
        group_note = _segment_evidence(definition.group)
        rows.append(
            {
                "order": order,
                "name": definition.name,
                "candidate": definition.candidate_formula,
                "signal": definition.signal,
                "input_units": INPUT_UNITS.get(definition.signal, "not specified"),
                "candidate_output_unit": definition.unit,
                "candidate_segment": definition.segment,
                "source_status": _feature_status(definition),
                "source_evidence": group_note,
                "original_formula": "Not located; no original equation or implementation verified.",
            }
        )
    return _markdown_table(
        rows,
        [
            ("#", "order"),
            ("Feature", "name"),
            ("Candidate interpretation only", "candidate"),
            ("Candidate input signal", "signal"),
            ("Candidate input units", "input_units"),
            ("Candidate output unit", "candidate_output_unit"),
            ("Candidate segment", "candidate_segment"),
            ("Status", "source_status"),
            ("Feature-specific source evidence", "source_evidence"),
            ("Original benchmark formula", "original_formula"),
        ],
    )


def _render_report(
    profile_rows: list[dict[str, Any]],
    batch_pairs: dict[str, dict[str, FeaturePairs]],
    overall_pairs: dict[str, FeaturePairs],
    workbook_audit: list[dict[str, Any]],
    sampling: dict[str, Any],
) -> str:
    profile_alignment = _profile_alignment_table(profile_rows)
    profile_metrics = [row for row in profile_rows if "feature" in row]
    batch_metrics: list[dict[str, Any]] = []
    for scope, pairs in batch_pairs.items():
        batch_number = int(scope.split("-")[1])
        batch_metrics.extend(
            _metric_rows(pairs, batch=batch_number)
        )
    overall_metrics = _metric_rows(overall_pairs)
    definitions = feature_definitions()
    status_counts = {
        "Source Verified": sum(_feature_status(item) == "Source Verified" for item in definitions),
        "Partially Verified": sum(_feature_status(item) == "Partially Verified" for item in definitions),
        "Candidate / Unverified": sum(_feature_status(item) == "Candidate / Unverified" for item in definitions),
        "Original Formula Unknown": sum(_feature_status(item) == "Original Formula Unknown" for item in definitions),
    }
    batch_alignment = []
    for batch in BATCHES:
        members = [row for row in profile_alignment if row["batch"] == batch]
        batch_alignment.append(
            {
                "batch": batch,
                "profiles": len(members),
                "raw_cycles": sum(row["raw_cycles"] for row in members),
                "workbook_rows": sum(row["workbook_rows"] for row in members),
                "matched_pairs": sum(row["matched_pairs"] for row in members),
                "unmatched_workbook_rows": sum(
                    row["unmatched_workbook_rows"] for row in members
                ),
                "ambiguous_workbook_rows": sum(
                    row["ambiguous_workbook_rows"] for row in members
                ),
                "unmatched_raw_cycles": sum(
                    row["unmatched_raw_cycles"] for row in members
                ),
                "alignment_methods": "; ".join(
                    sorted({row["alignment_method"] for row in members})
                ),
            }
        )

    lines = [
        "# XJTU Original Formula Verification and Benchmark Reproduction",
        "",
        "## Executive summary",
        "",
        "No authoritative source was located that maps the 67 `handcraft_features` "
        "workbook columns to exact equations or a generating implementation. The "
        "author-provided XJTU helper code documents CC/CV selectors and incremental-"
        "capacity (`dQ/dV`) routines, but does not state that it generated these "
        "workbooks. The SOHbenchmark loader consumes the prepared Excel data rather "
        "than extracting the 67 features from raw traces.",
        "",
        f"Feature status counts: **{status_counts['Source Verified']} Source Verified**, "
        f"**{status_counts['Partially Verified']} Partially Verified**, "
        f"**{status_counts['Candidate / Unverified']} Candidate / Unverified**, "
        f"**{status_counts['Original Formula Unknown']} Original Formula Unknown**. "
        "No feature is promoted based on candidate-to-Excel numerical agreement.",
        "",
        "**Genuine original benchmark reproduction is not currently possible.** "
        "There is no verified original equation/code against which an original-"
        "reference output can be generated. This report therefore keeps the "
        "existing candidate extractor comparison separate and labels every such "
        "metric candidate-only.",
        "",
        "## Research methodology",
        "",
        "- Inspected the existing Member 4 formula research, candidate validation, "
        "author-CC diagnostic reports, candidate definitions, segmentation and "
        "extractor code, and the SOHbenchmark loader and README.",
        "- Inspected the pinned XJTU authors' preprocessing repository and the "
        "`XJTUBatteryClass.py` helper methods. The author's notebook/search work "
        "described in the prior report was treated as discovery evidence, not as "
        "a formula source.",
        "- Inspected the complete supplied SOHbenchmark appendix PDF (22 pages), "
        "including a visual review of page 1. Page 1 prints the headings "
        "`Appendix A. Dataset`, `Appendix B. Feature engineering`, then immediately "
        "`Appendix C. Results`; the remaining pages are benchmark results. No "
        "feature equations are present in this supplied appendix.",
        "- Scanned all six workbooks with formulas enabled for formula cells, "
        "comments, and defined names; none were found. Column headers and the 67 "
        "feature order were compared with the canonical schema.",
        "- Searched exact feature spellings in local source and public GitHub code "
        "search. Exact-name hits that were recognizable as feature-value CSV "
        "mirrors were not treated as formula provenance. A search miss is not proof "
        "that private, deleted, unindexed, or inaccessible source code does not exist.",
        "- Compared candidate values from the unchanged candidate extractor against "
        "workbook values using the existing `_profile_pairs` alignment rules without "
        "changing them. Equal-count profiles remain positional and explicitly "
        "unverified; batch-6 capacity matches remain diagnostic and ambiguous rows "
        "remain excluded.",
        "- Consulted the 2024 Nature Communications article through its public "
        "PubMed Central full text (PMC11109204), and retrieved Zenodo record "
        "metadata and file listings through the Zenodo API. The article describes "
        "statistical features from a short pre-full-charge period, but does not "
        "establish that its feature set generated these 67 Excel columns.",
        "- The Zenodo records are distinct: 10963339 is the XJTU dataset record, "
        "while 11046967 is the PINN4SOH software archive. The XJTU class docstring "
        "labels the latter as a dataset link; the Zenodo metadata identifies it "
        "as software. No feature formula is inferred from either record.",
        "- Consulted OpenAlex records only to cross-check article titles, DOIs, "
        "publication dates, and the 2024 article's PMC identifier; no formula "
        "evidence is inferred from bibliographic metadata.",
        "",
        "## Sources inspected",
        "",
        "| Source | Evidence inspected | Authority for the 67 workbook formulas? |",
        "|---|---|---|",
        "| [XJTU author preprocessing repository at commit `e986a740`](https://github.com/wang-fujin/Battery-dataset-preprocessing-code-library/tree/e986a74054fb64c0f5134f2cc97f4643cd7699d2) and [`XJTUBatteryClass.py`](https://github.com/wang-fujin/Battery-dataset-preprocessing-code-library/blob/e986a74054fb64c0f5134f2cc97f4643cd7699d2/XJTUBatteryClass.py#L165-L276) | `get_CC_value` (lines 165–187) selects charging-stage values using current ≥3.9 A and voltage ≤4.199 V by default; `get_CV_value` (lines 189–205) selects voltage ≥4.199 V by default. `get_IC_curve1/2` (lines 225–276) implement dQ/dV using resampling and/or `I·dt/dV`. | Authoritative for those helper operations only. No link to these 67 columns or workbook generation was found. The dQ/dV helper is not the Excel column `dV_dV_devide_dt` or `dI_dI_devide_dt`. |",
        "| [Author repository README at the same commit](https://github.com/wang-fujin/Battery-dataset-preprocessing-code-library/blob/e986a74054fb64c0f5134f2cc97f4643cd7699d2/README.md) | Identifies the code as a public-dataset reading/preprocessing library and cites Wang et al., *Nature Communications* 15, 4332 (2024), [DOI](https://doi.org/10.1038/s41467-024-48779-z). README links dataset record 10963339; the XJTU class docstring links 11046967 but labels it as a dataset. Zenodo metadata resolves the record types: 10963339 is the dataset, and 11046967 is the PINN4SOH software archive. The docstring's record type is mislabeled; this is not an unresolved Zenodo record conflict. | Dataset/code provenance, not a feature-generation specification. |",
        "| [Zenodo XJTU dataset record 10963339](https://zenodo.org/records/10963339) and [record API metadata](https://zenodo.org/api/records/10963339) | The record identifies itself as a dataset, names the 55-cell experiment, refers to `Data Introduction.pdf` for further details, links the author preprocessing code, and states that the data sampling frequency is 1 Hz. Its file listing contains `Battery Dataset.zip`. | Authoritative for release metadata and the stated acquisition rate, not for the 67 workbook formulas or the transformation into the prepared MAT traces inspected here. |",
        "| [Zenodo PINN4SOH software record 11046967](https://zenodo.org/records/11046967) and [record API metadata](https://zenodo.org/api/records/11046967) | The record identifies itself as software, describes `wang-fujin/PINN4SOH`, and archives `PINN4SOH-v1.zip`. | Authoritative for the software archive's identity, not for the 67 workbook formulas. |",
        "| [Wang et al., *Nature Communications* 15, 4332 (2024)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11109204/) | The article describes extracting statistical features from a short period before full charge and reports a 55-cell XJTU dataset. It does not map that method to the 67-column SOHbenchmark workbooks. | Authoritative for the paper's described method and dataset; no evidence that its feature set is the Excel 67-feature schema or generator. |",
        "| [OpenAlex record for the 2024 article](https://api.openalex.org/works/https://doi.org/10.1038/s41467-024-48779-z) and [OpenAlex record for the SOHbenchmark paper](https://api.openalex.org/works/https://doi.org/10.1016/j.est.2023.109884) | Cross-checks the article titles, publication dates, DOIs, and the 2024 article's PMCID. | Bibliographic metadata only; not formula or workbook-generation evidence. |",
        "| [SOHbenchmark author repository at commit `62230dd`](https://github.com/wang-fujin/SOHbenchmark/tree/62230dd9a857f5c05ac641227b52ec2ffbeb9e15), [`XJTU_loader.py`](https://github.com/wang-fujin/SOHbenchmark/blob/62230dd9a857f5c05ac641227b52ec2ffbeb9e15/dataloader/XJTU_loader.py#L146-L170), and [README](https://github.com/wang-fujin/SOHbenchmark/blob/62230dd9a857f5c05ac641227b52ec2ffbeb9e15/README.md) | `get_features` reads `batch-*_features.xlsx`, parses feature columns and labels, then normalizes them. README describes the data under `data` as preprocessed and points to the XJTU dataset site/code. The paper is Wang et al., *Journal of Energy Storage* 77 (2024), 109884, [DOI](https://doi.org/10.1016/j.est.2023.109884). | Authoritative for consuming prepared features; not a raw-to-67 feature implementation. |",
        "| [Supplied SOHbenchmark appendix PDF](../reference/SOHbenchmark/SOHbenchmark%20-%20Appendix.pdf), page 1 | Visually inspected; Appendix B appears as a heading only before Appendix C results. PDF text extraction covers 22 pages. | No equations or specific generator for the 67 columns in this supplied appendix. |",
        "| Local XJTU workbooks and raw MAT traces under `reference/SOHbenchmark/data/XJTU/` | Six Excel workbooks, 55 sheets, 67 named feature columns plus `label`; formula/comment/name audit is summarized below. MAT traces contain raw time, voltage, current, temperature, and capacity labels. | Primary values/signals, but no embedded formula provenance. |",
        "| [Member 4 candidate extractor](../scripts/member4_xjtu/extractor.py), [feature definitions](../scripts/member4_xjtu/feature_definitions.py), and existing [candidate validation report](./member4_candidate_validation.md) | Candidate intervals and calculations, prior candidate-vs-Excel errors, and explicit alignment caveats. | Not authoritative; metrics describe approximations only. |",
        "| [XJTU author papers-summary repository](https://github.com/wang-fujin/XJTU-Battery-Dataset-Papers-Summary) | Bibliographic discovery resource. Exact target names and feature-workbook generator were not located. | Not a formula specification. |",
        "",
        "### Exact-name source search findings",
        "",
        "- The misspelled exact names `dV_dV_devide_dt` and `dI_dI_devide_dt` did not yield an authoritative implementation in the searched source/code indexes.",
        "- Searches for `CC_energy`, `Charge_energy`, `CC_CCCT`, `CV_CVCT`, and entropy names produced no target implementation in the XJTU author preprocessing library. Some global hits were downstream CSV feature values; they document neither equations nor provenance.",
        "- The checked-out author preprocessing source is pinned locally at commit `e986a74054fb64c0f5134f2cc97f4643cd7699d2`; SOHbenchmark source was checked at `62230dd9a857f5c05ac641227b52ec2ffbeb9e15`. These are explicit versions, not a claim that no later/private implementation exists.",
        "",
        "## Original formula evidence and status rules",
        "",
        "No exact original equation or generating implementation for any of the 67 "
        "Excel feature columns was found. The author helper's CC/CV selector and "
        "dQ/dV code are useful contextual evidence, but there is no authoritative "
        "mapping from those helpers to these workbook columns. Therefore no feature "
        "is marked Partially Verified: doing so would imply a feature-to-generator "
        "connection that the sources do not establish. The 63 non-entropy columns "
        "remain Candidate / Unverified; the four entropy columns are Original "
        "Formula Unknown because even their estimator and signal are not identified.",
        "",
        "The 2024 Nature Communications paper and its XJTU dataset must not be used "
        "to silently substitute another feature set. No source was found that maps "
        "the paper's reported feature list to this 67-column Excel schema. Similar "
        "names or physical plausibility are not that mapping.",
        "",
        "## Feature-by-feature verification table",
        "",
        "All formulas below are the current candidate interpretation solely to "
        "describe what was compared. `Candidate input units`, `Candidate output "
        "unit`, and segment are not original-source-verified workbook attributes. "
        "For every row, the original benchmark equation remains not located.",
        "",
    ]
    lines.extend(_render_feature_table())
    lines.extend(
        [
            "",
            "## Workbook formula audit",
            "",
            *_markdown_table(
                workbook_audit,
                [
                    ("Batch", "batch"),
                    ("Sheets", "sheet_count"),
                    ("Feature columns (excluding label)", "feature_columns"),
                    ("Formula cells", "formula_cells"),
                    ("Commented cells", "commented_cells"),
                    ("Defined names", "defined_names"),
                ],
            ),
            "",
            "The workbooks contain values but no embedded formulas, comments, or "
            "defined names that expose their calculation provenance.",
            "",
            "## Raw sampling and segmentation evidence",
            "",
            f"- Loaded {sampling['cycles']:,} raw cycles; samples per cycle ranged "
            f"from {sampling['min_samples']} to {sampling['max_samples']}.",
            f"- Using `rtol=1e-6, atol=1e-9` against each cycle's median Δt, "
            f"{sampling['nonuniform_cycles']:,} cycles were classified nonuniform. "
            f"The maximum relative Δt deviation from a cycle median was "
            f"{sampling['maximum_relative_step_deviation']:.3g}; the median cycle "
            f"step was {sampling['median_delta_min_across_cycles']:.9g} min "
            f"(global interval range {sampling['min_delta_min']:.9g}–"
            f"{sampling['max_delta_min']:.9g} min).",
            "- The XJTU dataset record states a 1 Hz sampling frequency "
            "([Zenodo record 10963339](https://zenodo.org/records/10963339)). "
            "The MAT traces analyzed here have only 128 timestamped samples per "
            "cycle; measured intervals range from "
            f"{sampling['min_delta_min']:.9g} to "
            f"{sampling['max_delta_min']:.9g} min (median per-cycle interval "
            f"{sampling['median_delta_min_across_cycles']:.9g} min), much coarser "
            "than 1 s. The source-to-MAT transformation is not established by the "
            "available evidence; do not treat these prepared traces as a verified "
            "1 Hz raw stream.",
            "- This contradicts older Member 4 documentation that described these "
            "prepared 128-point traces as nonuniform. The new observation is for "
            "the exact loaded MAT files and tolerance stated above; prior reports "
            "were not edited.",
            "- Candidate extraction defaults: adaptive CC current plateau with a "
            "4.199 V ceiling; CV first rising 4.199 V crossing to trace end; dV "
            "rising 3.9–4.0 V within candidate CC; dI falling 1.0–0.9 A within "
            "candidate CV; Charge is the complete stored trace. None of these exact "
            "workbook boundary conventions is verified.",
            "- Candidate integrals use trapezoids over stored timestamps and "
            "interpolated endpoints. Candidate moments use a 257-point uniform-time "
            "grid; candidate entropy is a 16-bin histogram proxy. These describe "
            "candidate code behavior only.",
            "",
            "## Alignment limitations and coverage",
            "",
            "Alignment decisions reuse `scripts.member4_xjtu.validation._profile_pairs` "
            "unchanged. Equal-count profiles are paired by row position and remain "
            "unverified. When counts differ, the existing unique monotone capacity "
            "match with tolerance 1e-6 is used; ambiguous rows are excluded. The "
            "ambiguous count is a subset of unmatched workbook rows and is not added "
            "again. Unmatched raw cycles are separately reported here.",
            "",
            *_markdown_table(
                batch_alignment,
                [
                    ("Batch", "batch"),
                    ("Profiles", "profiles"),
                    ("Raw cycles", "raw_cycles"),
                    ("Workbook rows", "workbook_rows"),
                    ("Matched pairs", "matched_pairs"),
                    ("Unmatched workbook rows", "unmatched_workbook_rows"),
                    ("Ambiguous rows (subset)", "ambiguous_workbook_rows"),
                    ("Unmatched raw cycles", "unmatched_raw_cycles"),
                    ("Alignment method", "alignment_methods"),
                ],
            ),
            "",
            "### Per-profile alignment accounting",
            "",
            *_markdown_table(
                profile_alignment,
                [
                    ("Batch", "batch"),
                    ("Profile", "profile"),
                    ("Raw cycles", "raw_cycles"),
                    ("Workbook rows", "workbook_rows"),
                    ("Matched pairs", "matched_pairs"),
                    ("Unmatched workbook rows", "unmatched_workbook_rows"),
                    ("Ambiguous rows", "ambiguous_workbook_rows"),
                    ("Unmatched raw cycles", "unmatched_raw_cycles"),
                    ("Method", "alignment_method"),
                    ("Mean abs label Δ", "mean_abs_label_difference"),
                ],
            ),
            "",
            "## Candidate comparison results (not original reproduction)",
            "",
            "Metrics compare the existing default candidate extractor with workbook "
            "values under the preserved alignment rules. They are **not** original-"
            "reference results and do not establish formula provenance. Valid "
            "matched cycles require finite workbook and candidate values. Workbook "
            "invalid and candidate invalid counts are reported independently among "
            "aligned rows. Relative error is defined as "
            "`MAE / mean(abs(workbook values)) × 100`; it is unavailable when that "
            "denominator is zero. Pearson and Spearman are undefined for fewer than "
            "two valid pairs or constant input.",
            "",
            "### Overall feature-wise candidate metrics (67 rows)",
            "",
            *_markdown_table(
                overall_metrics, _candidate_metric_columns("overall")
            ),
            "",
            "### Batch-wise feature candidate metrics (6 × 67 rows)",
            "",
            *_markdown_table(batch_metrics, _candidate_metric_columns("batch")),
            "",
            "### Profile-wise feature candidate metrics (55 × 67 rows)",
            "",
            "Each row below is one workbook profile × feature pair. The profile IDs "
            "are the workbook sheet names; equal-count positional identity is still "
            "not verified.",
            "",
            *_markdown_table(profile_metrics, _candidate_metric_columns("profile")),
            "",
            "## Original-reference benchmark reproduction",
            "",
            "No original-reference implementation was created because no "
            "authoritative 67-column formula set or generating code was found. "
            "Accordingly, original-reference values and original-reference MAE, "
            "RMSE, correlation, relative error, and valid-pair counts are **not "
            "available**. The candidate tables above are kept separate and cannot "
            "be relabeled as original reproduction.",
            "",
            "## Research gaps and next steps",
            "",
            "1. Request from SOHbenchmark authors the exact script/notebook, source "
            "version, and preprocessing inputs that generated `batch-1_features.xlsx` "
            "through `batch-6_features.xlsx`, plus the mapping of workbook rows to "
            "raw cycles.",
            "2. Request from XJTU dataset authors a source-authored mapping for each "
            "of the 67 columns: signal, units, stage/window thresholds, boundary "
            "interpolation, sampling/weights, integration/derivative estimator, "
            "statistical conventions, and entropy estimator.",
            "3. Ask the XJTU authors to document the preprocessing between the "
            "release's stated 1 Hz acquisition data and the 128-point-per-cycle "
            "prepared MAT traces, including any resampling or selection.",
            "4. If primary formulas/code are supplied, implement a separately named "
            "reference extractor in this isolated directory, retain the current "
            "candidate extractor unchanged, and compare the two independently "
            "against Excel only after validating cycle alignment.",
            "5. Until then, retain Candidate / Unverified or Original Formula "
            "Unknown statuses and treat numerical agreement only as a candidate "
            "quality diagnostic.",
            "",
            "## Reproducibility",
            "",
            f"From the repository root, run "
            f"`{Path('scripts/member4_xjtu/original_verification/report.py').as_posix()}` "
            "as a module to regenerate this report. This command reads the raw MAT "
            "files and feature workbooks, imports the existing candidate extractor "
            "and alignment helper without modifying them, and writes only this "
            "report file.",
            "",
        ]
    )
    return "\n".join(lines)


def generate_report(
    data_root: Path = DEFAULT_DATA_ROOT,
    report_path: Path = DEFAULT_REPORT,
    batches: Iterable[int] = BATCHES,
) -> int:
    selected_batches = tuple(batches)
    definitions = feature_definitions()
    if len(definitions) != 67 or tuple(item.name for item in definitions) != FEATURE_NAMES:
        raise RuntimeError("The canonical XJTU feature schema is not the expected 67-feature order.")

    profile_rows, batch_pairs, overall_pairs, details = _alignment_rows(
        selected_batches, data_root
    )
    workbook_audit = _workbook_formula_audit(data_root, selected_batches)
    report = _render_report(
        profile_rows,
        batch_pairs,
        overall_pairs,
        workbook_audit,
        details["sampling"],
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    return sum("feature" not in row for row in profile_rows)


def main() -> None:
    profiles = generate_report()
    print(f"Wrote original formula verification report for {profiles} profiles.")


if __name__ == "__main__":
    main()
