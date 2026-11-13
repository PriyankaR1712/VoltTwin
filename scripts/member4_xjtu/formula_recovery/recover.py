from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from scripts.member4_xjtu.feature_definitions import (
    FEATURE_NAMES,
    FeatureDefinition,
    feature_definitions,
)


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = ROOT / "reports" / "member4_original_formula_recovery"
DEFAULT_REPORT = ROOT / "reports" / "member4_original_formula_recovery.md"

STATUSES = (
    "Source verified",
    "Partially verified",
    "Candidate/unverified",
    "Original formula unavailable",
)

SOURCES: tuple[dict[str, str], ...] = (
    {
        "id": "S1",
        "source": "SOHbenchmark author repository, pinned commit 62230dd9a857f5c05ac641227b52ec2ffbeb9e15",
        "url": "https://github.com/wang-fujin/SOHbenchmark/tree/62230dd9a857f5c05ac641227b52ec2ffbeb9e15",
        "location": "dataloader/XJTU_loader.py; repository history for data/XJTU/handcraft_features",
        "evidence": (
            "The loader reads and normalizes the prepared workbook. The "
            "feature-workbook history points to an uploaded data commit; the "
            "inspected repository history did not expose a workbook generator."
        ),
        "authority": "Authoritative for workbook consumption and repository contents; not a formula generator.",
    },
    {
        "id": "S2",
        "source": "SOHbenchmark feature workbook upload commit",
        "url": "https://github.com/wang-fujin/SOHbenchmark/commit/611bb5948fe4a7914486ded7be238db24faabb23",
        "location": "Commit adds data/XJTU/handcraft_features/batch-1_features.xlsx through batch-6_features.xlsx",
        "evidence": (
            "The commit records addition of precomputed workbook files, not "
            "the code that generated their values."
        ),
        "authority": "Author repository history; no formula implementation in the commit.",
    },
    {
        "id": "S3",
        "source": "XJTU authors' preprocessing library, pinned commit e986a74054fb64c0f5134f2cc97f4643cd7699d2",
        "url": "https://github.com/wang-fujin/Battery-dataset-preprocessing-code-library/tree/e986a74054fb64c0f5134f2cc97f4643cd7699d2",
        "location": "XJTUBatteryClass.py, get_CC_value/get_CV_value/get_IC_curve1/get_IC_curve2",
        "evidence": (
            "Documents charge-phase selectors and incremental-capacity "
            "(dQ/dV) helpers. No exact mapping to the 67 workbook columns "
            "or workbook-generation code was found."
        ),
        "authority": "Authoritative for the helper methods only; not for the 67 workbook equations.",
    },
    {
        "id": "S4",
        "source": "Official XJTU dataset site and Zenodo dataset record 10963339",
        "url": "https://zenodo.org/records/10963339",
        "location": "Dataset description; linked official site https://wang-fujin.github.io/",
        "evidence": (
            "Identifies the experiment, batch strategies, 1 Hz rate statement, "
            "dataset archive, and author preprocessing library. No 67-feature "
            "equation set or workbook join is provided in the inspected metadata."
        ),
        "authority": "Authoritative for release metadata; not for the workbook formulas.",
    },
    {
        "id": "S5",
        "source": "Wang et al., Physics-informed neural network for lithium-ion battery degradation stable modeling and prognosis",
        "url": "https://doi.org/10.1038/s41467-024-48779-z",
        "location": "Nature Communications 15, 4332 (2024); public full text https://pmc.ncbi.nlm.nih.gov/articles/PMC11109204/",
        "evidence": (
            "Describes statistical features extracted before full charge for "
            "the PINN method. The inspected article does not establish that "
            "its feature set generated the SOHbenchmark 67-column workbooks."
        ),
        "authority": "Authoritative for the paper's method; no evidence of identity with the 67 workbook columns.",
    },
    {
        "id": "S6",
        "source": "Wang et al., Open access dataset, code library and benchmarking deep learning approaches for SOH estimation",
        "url": "https://doi.org/10.1016/j.est.2023.109884",
        "location": "Journal of Energy Storage 77 (2024), 109884; supplied appendix PDF reference/SOHbenchmark/SOHbenchmark - Appendix.pdf",
        "evidence": (
            "The benchmark loader and supplied appendix concern consumption/"
            "benchmarking. The inspected appendix contains an Appendix B "
            "feature-engineering heading without equations for this schema."
        ),
        "authority": "Benchmark-associated source; no 67-feature equation or extraction implementation located.",
    },
    {
        "id": "S7",
        "source": "Member 4 candidate definitions and extractor",
        "url": "../scripts/member4_xjtu/feature_definitions.py",
        "location": "feature_definitions.py, extractor.py, segments.py",
        "evidence": (
            "Defines the current candidate equations, signal assumptions, "
            "units, and segment conventions used for diagnostic comparisons."
        ),
        "authority": "Implementation evidence for the candidate only; not an original source.",
    },
    {
        "id": "S8",
        "source": "OpenAlex literature-index queries",
        "url": "https://api.openalex.org/works?search=%22CC_CCCT%22&per-page=10",
        "location": "Exact quoted-name and XJTU/SOHbenchmark full-text searches",
        "evidence": (
            "The exact quoted CC_CCCT query returned no indexed works. "
            "Search results are incomplete and cannot prove that a term or "
            "source does not exist."
        ),
        "authority": "Discovery aid only; no formula evidence.",
    },
)

SEARCH_LOG: tuple[dict[str, str], ...] = (
    {
        "scope": "local repository",
        "query": "Exact workbook names; candidate names; entropy, feature engineering, SOHbenchmark, XJTU",
        "result": "No original generator found in local scripts, reports, notebooks, metadata, or supplied benchmark code.",
        "interpretation": "Bounded to the files and versions present in this workspace.",
    },
    {
        "scope": "SOHbenchmark GitHub repository",
        "query": "Commit history for dataloader/XJTU_loader.py and data/XJTU/handcraft_features",
        "result": (
            "Loader first appears in the 2023 repository history; workbook path "
            "is added as prepared data in commit 611bb5948fe4a7914486ded7be238db24faabb23."
        ),
        "interpretation": (
            "The reachable inspected history does not contain a feature "
            "generator; this does not exclude unpushed/private/removed sources."
        ),
    },
    {
        "scope": "author GitHub repositories",
        "query": (
            "Repository-scoped exact searches for CC_energy, CC_CCCT, "
            "dV_dV_devide_dt, dI_dI_devide_dt, Charge_energy, and entropy names"
        ),
        "result": "No feature-generation code matches in the two inspected author repositories.",
        "interpretation": (
            "GitHub code search is indexed and incomplete. Feature-value "
            "mirrors are not formula implementations."
        ),
    },
    {
        "scope": "public GitHub code search",
        "query": (
            "Exact derivative spellings and exact feature names, including "
            "CC_CCCT, Charge_energy, CC_energy, and entropy columns"
        ),
        "result": (
            "Exact derivative-name searches returned no implementation. "
            "Some common feature-name hits were downstream CSV/value mirrors "
            "or unrelated symbols."
        ),
        "interpretation": (
            "A value table does not establish signal selection, estimator, "
            "boundaries, units, or provenance."
        ),
    },
    {
        "scope": "literature discovery",
        "query": (
            "OpenAlex full-text search for XJTU battery entropy handcrafted "
            "SOH and exact quoted CC_CCCT"
        ),
        "result": (
            "The exact quoted CC_CCCT query returned zero works; broad search "
            "returned records but did not identify an authoritative equation "
            "source tied to the 67 workbook columns."
        ),
        "interpretation": (
            "Index coverage and full-text access are incomplete; this is not "
            "evidence that no related paper exists."
        ),
    },
    {
        "scope": "SOHbenchmark supplied materials",
        "query": "Appendix, workbooks, metadata, and XJTU loader",
        "result": (
            "Workbook formulas/comments/defined names and supplied appendix "
            "did not provide the 67 equations; loader reads the existing sheet."
        ),
        "interpretation": "Confirms prepared-data consumption, not feature generation.",
    },
    {
        "scope": "2024 XJTU dataset paper",
        "query": "Full-text feature method; supplementary-file link/retrieval",
        "result": (
            "The paper describes its own pre-full-charge statistical-feature "
            "method; no mapping to the SOHbenchmark 67-column schema was found. "
            "The linked supplementary PDF could not be retrieved as readable "
            "content through the available source endpoint."
        ),
        "interpretation": (
            "Do not substitute that distinct feature set for the benchmark "
            "workbook; supplementary contents remain uninspected."
        ),
    },
)

ENTROPY_NAMES = ("CC_entropy", "dV_entropy", "CV_entropy", "dI_entropy")


def _feature_status(definition: FeatureDefinition) -> str:
    if definition.name in ENTROPY_NAMES:
        return "Original formula unavailable"
    return "Candidate/unverified"


def feature_evidence_rows() -> list[dict[str, str]]:
    definitions = feature_definitions()
    if tuple(item.name for item in definitions) != FEATURE_NAMES:
        raise ValueError("Candidate definitions do not match the canonical 67-feature schema.")
    rows = []
    for definition in definitions:
        group_note = {
            "CC": (
                "Author code documents a related CC selector, but no source "
                "maps it or this feature to the workbook column."
            ),
            "CV": (
                "Author code documents a related CV selector, but no source "
                "maps it or this feature to the workbook column."
            ),
            "dV": (
                "No workbook formula located. Author dQ/dV helpers are a "
                "different quantity and do not define this feature."
            ),
            "dI": "No workbook formula or derivative/entropy definition located.",
            "Charge": "No original charge-window or full-charge statistic definition located.",
        }[definition.group]
        related_source = {
            "CC": "S3",
            "CV": "S3",
            "dV": "S3; S8",
            "dI": "S8",
            "Charge": "S1; S6",
        }[definition.group]
        rows.append(
            {
                "feature": definition.name,
                "group": definition.group,
                "status": _feature_status(definition),
                "original_formula": "Not located in inspected authoritative sources.",
                "original_signal": "Unknown",
                "original_segment": "Unknown",
                "original_input_units": "Unknown",
                "original_output_units": "Unknown",
                "original_integration_or_statistic_convention": "Unknown",
                "original_time_unit": "Unknown",
                "original_boundary_and_preprocessing": "Unknown",
                "source_equation_reference": "",
                "candidate_formula_only": definition.candidate_formula,
                "candidate_signal_only": definition.signal,
                "candidate_segment_only": definition.segment,
                "candidate_output_unit_only": definition.unit,
                "candidate_assumptions": definition.assumptions,
                "evidence_note": group_note,
                "candidate_implementation_reference": "S7",
                "related_source_reference": related_source,
            }
        )
    return rows


def entropy_evidence_rows() -> list[dict[str, str]]:
    rows = []
    for feature in ENTROPY_NAMES:
        definition = next(
            item for item in feature_definitions() if item.name == feature
        )
        rows.append(
            {
                "feature": feature,
                "status": "Original formula unavailable",
                "original_signal": "Unknown",
                "original_estimator": "Unknown",
                "original_binning_or_probability_definition": "Unknown",
                "original_normalization": "Unknown",
                "original_log_base": "Unknown",
                "original_segment": "Unknown",
                "candidate_proxy_only": definition.candidate_formula,
                "candidate_signal_only": definition.signal,
                "candidate_segment_only": definition.segment,
                "search_evidence": (
                    "Exact author-repository entropy-name search produced no "
                    "formula implementation; broader exact-name searches were "
                    "not sufficient to establish a source."
                ),
                "source_reference": "S3; S6; S8",
            }
        )
    return rows


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write an empty evidence file: {path}")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_report(
    feature_rows: list[dict[str, str]],
    entropy_rows: list[dict[str, str]],
) -> str:
    counts = Counter(row["status"] for row in feature_rows)
    lines = [
        "# Original XJTU 67-Feature Formula Recovery",
        "",
        "## Executive summary",
        "",
        "No original source implementation or authoritative equation set for the 67 SOHbenchmark XJTU workbook columns was located in the inspected sources. No exact original equations were recovered. This is a bounded research conclusion, not proof that private, deleted, inaccessible, or unindexed material does not exist.",
        "",
        f"Feature status counts: **{counts['Source verified']} Source verified**, **{counts['Partially verified']} Partially verified**, **{counts['Candidate/unverified']} Candidate/unverified**, and **{counts['Original formula unavailable']} Original formula unavailable**.",
        "",
        "The candidate extractor remains a separate, unverified implementation. Candidate formulas, signals, units, and segment labels in the evidence table describe that implementation only; they are not statements about the original Excel calculation. Numerical agreement is not used to assign provenance.",
        "",
        "The four entropy columns have no located original estimator, signal, probability definition, binning, normalization, or logarithm base. The 16-bin histogram implementation is retained only as a candidate diagnostic proxy.",
        "",
        "## Method and evidence rules",
        "",
        "- Inspected prior Member 4 reports, candidate definitions/extractor/segments, local metadata, XJTU workbooks, SOHbenchmark sources and history, the author preprocessing library and history, official XJTU dataset information, the 2024 XJTU paper, the supplied SOHbenchmark appendix, and indexed exact-name searches.",
        "- A source equation is marked verified only when a source directly ties that equation or implementation to a feature in this exact 67-column workbook schema. A related CC/CV helper, generic statistical convention, copied feature-value CSV, or a differently scoped feature set is insufficient.",
        "- `Candidate/unverified` means a candidate interpretation exists in the existing extractor, but its original formula/provenance is not established. `Original formula unavailable` is used for the four entropy features, for which even the original estimator is unidentified.",
        "- Original-scope formula, signal, segment, input/output units, time units, numerical convention, preprocessing, and boundary fields remain explicitly unknown unless supported by a direct source. A blank source equation reference means none was found.",
        "- Literature and code-search misses are recorded as search outcomes, not proof of nonexistence.",
        "",
        "## Feature-wise evidence table",
        "",
        "| # | Feature | Status | Original formula/source equation | Original signal/segment/units/conventions | Candidate interpretation only | Evidence note |",
        "|---:|---|---|---|---|---|---|",
    ]
    for index, row in enumerate(feature_rows, start=1):
        original = "Not located; no feature-specific original equation."
        original_details = (
            f"Signal: {row['original_signal']}; segment: {row['original_segment']}; "
            f"units: {row['original_input_units']} → {row['original_output_units']}; "
            f"convention/time/boundaries: unknown."
        )
        candidate = (
            f"{row['candidate_formula_only']} "
            f"(signal: {row['candidate_signal_only']}; segment: "
            f"{row['candidate_segment_only']}; unit: "
            f"{row['candidate_output_unit_only']})"
        )
        lines.append(
            f"| {index} | `{row['feature']}` | {row['status']} | {original} | "
            f"{original_details} | {candidate} | {row['evidence_note']} |"
        )
    lines.extend(
        [
            "",
            "The full machine-readable table in `member4_original_formula_recovery/feature_evidence.csv` also separates original unknowns from candidate implementation assumptions field by field.",
            "",
            "## Sources inspected",
            "",
            "| ID | Source | Evidence and scope | Formula authority for this schema |",
            "|---|---|---|---|",
        ]
    )
    for source in SOURCES:
        lines.append(
            f"| {source['id']} | [{source['source']}]({source['url']}) | "
            f"{source['evidence']} Location: {source['location']}. | "
            f"{source['authority']} |"
        )
    lines.extend(
        [
            "",
            "## Repository history and exact-name search",
            "",
            "The inspected SOHbenchmark history shows the XJTU loader and precomputed workbook data, but no feature-generation program in the reachable history checked. The workbook upload commit is evidence of data publication, not evidence of how the values were calculated. Author-repository exact-name searches did not locate implementations of `CC_energy`, `CC_CCCT`, `dV_dV_devide_dt`, `dI_dI_devide_dt`, `Charge_energy`, or the four entropy columns. Public code search also returns downstream value tables and unrelated name collisions; those are not formula sources.",
            "",
            "The 2024 Nature Communications article describes its own statistical features from a short pre-full-charge interval. No source establishes that its feature set, sample window, or equations produced the SOHbenchmark 67-column workbook. It is not substituted for the benchmark schema.",
            "",
            "The article full text was checked, but its linked supplementary PDF could not be retrieved as readable content through the available source endpoint. Supplementary contents are therefore uninspected, not presumed empty.",
            "",
            "The complete query/scope/result record is in `member4_original_formula_recovery/search_log.csv`. Search availability, repository history visibility, literature indexing, and full-text access are limitations; no search miss is treated as proof of absence.",
            "",
            "## Entropy investigation",
            "",
            "| Feature | Original signal | Estimator | Probability/binning | Normalization | Log base | Candidate proxy only | Status |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in entropy_rows:
        lines.append(
            f"| `{row['feature']}` | Unknown | Unknown | Unknown | Unknown | Unknown | "
            f"{row['candidate_proxy_only']} | {row['status']} |"
        )
    lines.extend(
        [
            "",
            "The original entropy equation cannot be inferred from column names or numerical values. Different entropy estimators and probability constructions are not interchangeable. The candidate histogram is not presented as an original formula.",
            "",
            "## Formula status and implementation implications",
            "",
            "- **Source verified:** none.",
            "- **Partially verified:** none. Author helper CC/CV selectors are not linked to any named workbook feature, and the author dQ/dV helpers calculate a different quantity from the misspelled derivative columns.",
            f"- **Candidate/unverified:** {counts['Candidate/unverified']} features. Keep the existing candidate implementation distinct and labeled.",
            f"- **Original formula unavailable:** {counts['Original formula unavailable']} entropy features.",
            "- Exact benchmark reproduction of the 67 values is not currently supportable from the located evidence. Do not implement conjectural formulas as original-reference equations.",
            "- Future formula status changes require new direct evidence: author-supplied feature-generation code, a workbook-generation notebook/script with an explicit schema mapping, or an authoritative supplement giving exact feature-specific equations and conventions.",
            "",
            "## Remaining unknowns",
            "",
            "For all features, the original source signal and feature-to-column mapping remain unverified. Depending on feature family, unresolved details include CC/CV/dV/dI/full-charge boundaries; whether disjoint intervals are joined or summed; capacity versus current integration; power/energy units and signs; elapsed-time origin; timestamp and resampling rules; trapezoidal versus discrete integration; endpoint interpolation/inclusion; time units; point-weighted versus time-weighted statistics; sample/population standard deviation; skewness correction; Pearson versus excess kurtosis; derivative estimator; and preprocessing/filtering. For entropy, the estimator and all probability construction details are unknown.",
            "",
            "## Recommended next steps",
            "",
            "1. Request the exact feature workbook generator and its version/commit from SOHbenchmark authors, with a direct mapping from output columns to code.",
            "2. Request the original feature-generation manuscript/supplement or `Data Introduction.pdf` and verify whether it specifies the 67 columns, not merely a different XJTU feature set.",
            "3. Obtain any missing archived branches, tags, or source bundles from the benchmark authors. Do not derive equations from benchmark-value correlations.",
            "4. Once direct source evidence is available, implement a separately named original-reference extractor, write feature-specific tests against source examples, and compare only against authoritatively mapped cycles.",
            "5. Until then, preserve candidate outputs and uncertainty statuses; do not mark formulas verified based on low MAE or correlation.",
            "",
            "## Reproducibility",
            "",
            "Generate the evidence CSVs and this report from the repository root:",
            "",
            "```powershell",
            r".\.venv\Scripts\python.exe -m scripts.member4_xjtu.formula_recovery.recover",
            "```",
            "",
            "The generator reads the existing candidate definitions as candidate-only descriptions. It does not modify extraction code, metadata, prior reports, alignment behavior, models, or datasets.",
            "",
        ]
    )
    return "\n".join(lines)


def generate_outputs(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    report_path: Path = DEFAULT_REPORT,
) -> dict[str, int]:
    output_dir = Path(output_dir)
    report_path = Path(report_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    feature_rows = feature_evidence_rows()
    entropy_rows = entropy_evidence_rows()
    _write_csv(output_dir / "feature_evidence.csv", feature_rows)
    _write_csv(output_dir / "entropy_evidence.csv", entropy_rows)
    _write_csv(output_dir / "source_evidence.csv", list(SOURCES))
    _write_csv(output_dir / "search_log.csv", list(SEARCH_LOG))

    counts = Counter(row["status"] for row in feature_rows)
    summary = {
        "feature_count": len(feature_rows),
        "entropy_feature_count": len(entropy_rows),
        "status_counts": {status: counts.get(status, 0) for status in STATUSES},
        "source_verified_features": [
            row["feature"]
            for row in feature_rows
            if row["status"] == "Source verified"
        ],
        "original_equations_recovered": 0,
    }
    (output_dir / "status_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    report_path.write_text(build_report(feature_rows, entropy_rows), encoding="utf-8")
    return {
        "features": len(feature_rows),
        "sources": len(SOURCES),
        "searches": len(SEARCH_LOG),
        "entropy_features": len(entropy_rows),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate the isolated XJTU original-formula evidence ledger."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    print(json.dumps(generate_outputs(args.output_dir, args.report), indent=2))


if __name__ == "__main__":
    main()
