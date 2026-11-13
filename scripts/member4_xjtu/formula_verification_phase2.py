"""Build the Phase 2 original-formula evidence artifacts.

This report generator deliberately keeps the source-backed 16-feature method
separate from the 67-column SOHbenchmark workbook provenance.  It consumes the
existing feature registry and prior recovery ledger; it does not change any
candidate formula implementation.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "reports" / "member4"
SOURCE_CSV = REPORT_DIR / "original_formula_recovery.csv"
RELATED_CSV = (
    ROOT / "reports" / "member4_supplementary_pdf_inspection" / "feature_mapping.csv"
)
OUTPUT_CSV = REPORT_DIR / "formula_verification_phase2.csv"
OUTPUT_JSON = REPORT_DIR / "formula_verification_phase2_summary.json"
OUTPUT_MD = REPORT_DIR / "formula_verification_phase2.md"

SUPPLEMENT_URL = (
    "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-024-48779-z/"
    "MediaObjects/41467_2024_48779_MOESM1_ESM.pdf"
)
SOHBENCHMARK_URL = (
    "https://github.com/wang-fujin/SOHbenchmark/tree/"
    "62230dd9a857f5c05ac641227b52ec2ffbeb9e15"
)
WORKBOOK_COMMIT_URL = (
    "https://github.com/wang-fujin/SOHbenchmark/commit/"
    "611bb5948fe4a7914486ded7be238db24faabb23"
)
PREPROCESSING_URL = (
    "https://github.com/wang-fujin/Battery-dataset-preprocessing-code-library/"
    "blob/e986a74054fb64c0f5134f2cc97f4643cd7699d2/XJTUBatteryClass.py"
)
NOTEBOOK_URL = (
    "https://github.com/wang-fujin/Battery-dataset-preprocessing-code-library/"
    "blob/e986a74054fb64c0f5134f2cc97f4643cd7699d2/"
    "XJTU%E6%95%B0%E6%8D%AE%E9%9B%86%E5%88%86%E6%9E%90.ipynb"
)

FIELDS = (
    "feature",
    "group",
    "original_formula",
    "evidence_status",
    "source_url",
    "source_file",
    "source_page",
    "source_section",
    "implementation_formula",
    "equivalence",
    "discrepancy",
    "notes",
)


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _group(feature: str) -> str:
    return feature.split("_", 1)[0]


def _source_context(
    feature: str, related: str
) -> tuple[str, str, str, str, str, str]:
    """Return source/evidence context without implying an original mapping."""
    if related == "Related methodology only":
        source_url = f"{SUPPLEMENT_URL}; {NOTEBOOK_URL}; {PREPROCESSING_URL}"
        source_file = (
            "Publisher supplementary PDF; XJTU数据集分析.ipynb; "
            "XJTUBatteryClass.py"
        )
        source_page = "6 (supplement); notebook cells 19/21"
        source_section = "Supplementary Note 2, Eqs. (1)-(8); CC/CV plotting helpers"
        if feature.endswith("_entropy"):
            evidence = "ORIGINAL_FORMULA_UNKNOWN"
        else:
            evidence = "RELATED_METHOD_ONLY"
        discrepancy = (
            "The source defines a related paper method or selector, but does not "
            "identify this SOHbenchmark workbook column, its row/cycle, or all "
            "sampling and numerical conventions."
        )
        return source_url, source_file, source_page, source_section, evidence, discrepancy

    source_url = f"{SOHBENCHMARK_URL}; {WORKBOOK_COMMIT_URL}; {NOTEBOOK_URL}"
    source_file = (
        "dataloader/XJTU_loader.py; data/XJTU/handcraft_features/"
        "batch-*_features.xlsx; XJTU数据集分析.ipynb"
    )
    source_page = "README Dataset section; loader get_features; notebook cells 19/21"
    source_section = "Prepared handcraft_features consumption; no generator/export found"
    discrepancy = (
        "No source equation or feature-generation implementation was found for "
        "this workbook column. Candidate semantics remain unverified."
    )
    return source_url, source_file, source_page, source_section, "CANDIDATE_UNVERIFIED", discrepancy


def build_rows() -> list[dict[str, str]]:
    source_rows = _read_rows(SOURCE_CSV)
    related_rows = {
        row["feature"]: row for row in _read_rows(RELATED_CSV)
    }
    result: list[dict[str, str]] = []
    for row in source_rows:
        feature = row["feature_name"]
        related = related_rows[feature]["pdf_match_classification"]
        source_url, source_file, source_page, source_section, status, discrepancy = (
            _source_context(feature, related)
        )
        original_formula = ""
        if status == "ORIGINAL_FORMULA_UNKNOWN":
            equivalence = (
                "Related-method entropy expression only; original workbook entropy "
                "estimator remains unknown."
            )
        elif status == "RELATED_METHOD_ONLY":
            equivalence = (
                "No exact equivalence; related method/selector evidence only."
            )
        else:
            equivalence = "No related formula correspondence located."
        notes = (
            "The current implementation is a VoltTwin candidate, not an original "
            "benchmark recovery. Formula Explorer provenance warning is preserved. "
            f"Prior audit status: {row['verification_status']}."
        )
        result.append(
            {
                "feature": feature,
                "group": row["group"],
                "original_formula": original_formula,
                "evidence_status": status,
                "source_url": source_url,
                "source_file": source_file,
                "source_page": source_page,
                "source_section": source_section,
                "implementation_formula": row["candidate_formula"],
                "equivalence": equivalence,
                "discrepancy": discrepancy,
                "notes": notes,
            }
        )
    return result


def _summary(rows: list[dict[str, str]]) -> dict[str, object]:
    counts = Counter(row["evidence_status"] for row in rows)
    original_counts = {
        "SOURCE_VERIFIED": 0,
        "PARTIALLY_VERIFIED": 0,
        "CANDIDATE_UNVERIFIED": 63,
        "ORIGINAL_FORMULA_UNKNOWN": 4,
    }
    return {
        "title": "VoltTwin Original Benchmark Formula Verification - Deep Research Phase 2",
        "audit_date": "2026-11-10",
        "feature_count": len(rows),
        "phase2_evidence_status_counts": {
            status: counts.get(status, 0)
            for status in (
                "SOURCE_VERIFIED",
                "PARTIALLY_VERIFIED",
                "RELATED_METHOD_ONLY",
                "CANDIDATE_UNVERIFIED",
                "ORIGINAL_FORMULA_UNKNOWN",
            )
        },
        "original_formula_provenance_counts": original_counts,
        "original_formulas_recovered": 0,
        "exact_67_feature_source_found": False,
        "candidate_formulas_modified": False,
        "formula_explorer_modified": False,
        "related_method": {
            "paper": "Wang et al., Nature Communications 15, 4332 (2024)",
            "supplement_url": SUPPLEMENT_URL,
            "scope": "Separate 16-feature selected-window method; no 67-column mapping.",
            "rows_classified_related_method_only": counts.get("RELATED_METHOD_ONLY", 0),
        },
        "author_source_investigation": {
            "sohbenchmark_commit": SOHBENCHMARK_URL,
            "workbook_upload_commit": WORKBOOK_COMMIT_URL,
            "preprocessing_commit": PREPROCESSING_URL,
            "xjtu_notebook": NOTEBOOK_URL,
            "author_pinn4soh": "https://github.com/wang-fujin/PINN4SOH",
            "author_papers_summary": (
                "https://github.com/wang-fujin/XJTU-Battery-Dataset-Papers-Summary"
            ),
            "forks_checked": [
                "https://github.com/rosyeeBen/SOHbenchmark2",
                "https://github.com/armand00000/SOHbenchmarkT",
                "https://github.com/Yike-Lin/SOH-Baseline-test",
            ],
        },
        "findings": [
            "SOHbenchmark loader consumes precomputed Excel handcraft_features; no generator was found in the pinned repository history.",
            "The author SOHbenchmark repository exposes only its main branch and no releases/tags in the inspected GitHub navigation; its six-commit history contains the loader and workbook upload but no feature exporter.",
            "The workbook upload commit adds prepared sheets without formulas, comments, defined names, or a row-to-cycle crosswalk.",
            "The current preprocessing notebook demonstrates CC [3.8,4.0] V and CV [1.0,0.5] A selectors for visualization only; it does not export the 67 workbook columns.",
            "PINN4SOH and its CSVs expose a separate 16-feature schema plus capacity; the supplementary equations do not map to the workbook schema.",
        ],
        "limitations": [
            "No source-verified or partially verified original formula was recovered.",
            "Related-method classifications are not evidence of workbook equivalence and do not change Formula Explorer status.",
            "The four entropy features remain original-formula-unknown; the candidate histogram is diagnostic only.",
            "An author-provided generator/specification and workbook-row-to-cycle crosswalk are still required for scientific reproduction.",
        ],
        "source_urls": [
            SOHBENCHMARK_URL,
            WORKBOOK_COMMIT_URL,
            PREPROCESSING_URL,
            NOTEBOOK_URL,
            "https://zenodo.org/records/10963339",
            "https://doi.org/10.1016/j.est.2023.109884",
            "https://doi.org/10.1038/s41467-024-48779-z",
            SUPPLEMENT_URL,
            "https://github.com/wang-fujin/PINN4SOH",
            "https://github.com/wang-fujin/XJTU-Battery-Dataset-Papers-Summary",
        ],
    }


def _markdown(rows: list[dict[str, str]], summary: dict[str, object]) -> str:
    counts = summary["phase2_evidence_status_counts"]
    lines = [
        "# Original Benchmark Formula Verification — Deep Research Phase 2",
        "",
        "## Result",
        "",
        "No authoritative generator, equation table, or workbook-row/cycle crosswalk for the 67 SOHbenchmark XJTU columns was recovered. The candidate equations and Formula Explorer provenance warning were left unchanged.",
        "",
        "The Phase 2 evidence taxonomy separates related-method evidence from original-formula provenance:",
        "",
        "| Evidence status | Features | Interpretation |",
        "|---|---:|---|",
        f"| `SOURCE_VERIFIED` | {counts['SOURCE_VERIFIED']} | Exact original workbook definition tied to an authoritative source |",
        f"| `PARTIALLY_VERIFIED` | {counts['PARTIALLY_VERIFIED']} | Source-backed partial definition with an explicit workbook mapping |",
        f"| `RELATED_METHOD_ONLY` | {counts['RELATED_METHOD_ONLY']} | Similar operation/window in a separate author method; not a workbook mapping |",
        f"| `CANDIDATE_UNVERIFIED` | {counts['CANDIDATE_UNVERIFIED']} | No feature-specific original equation or related method correspondence located |",
        f"| `ORIGINAL_FORMULA_UNKNOWN` | {counts['ORIGINAL_FORMULA_UNKNOWN']} | Entropy estimator/signal/conventions remain unidentified |",
        "",
        "The original-provenance status used by the existing Formula Explorer remains `SOURCE_VERIFIED=0`, `PARTIALLY_VERIFIED=0`, `CANDIDATE_UNVERIFIED=63`, and `ORIGINAL_FORMULA_UNKNOWN=4`. `RELATED_METHOD_ONLY` is a Phase 2 evidence label and does not promote a candidate to verified.",
        "",
        "## Sources investigated",
        "",
        f"- [SOHbenchmark at pinned commit]({SOHBENCHMARK_URL}) and [workbook upload commit]({WORKBOOK_COMMIT_URL}): the loader reads precomputed `handcraft_features` workbooks; the inspected history contains no feature generator.",
        "- The public SOHbenchmark navigation exposed one `main` branch and no releases/tags; the six-commit history was checked as a bounded public history search.",
        f"- [Current XJTU preprocessing class]({PREPROCESSING_URL}) and [XJTU analysis notebook]({NOTEBOOK_URL}): the notebook uses CC `[3.8, 4.0] V` and CV `[1.0, 0.5] A` selectors for plots, and the class provides CC/CV helpers and dQ/dV routines. Neither maps helper output to any of the 67 workbook columns or exports feature sheets.",
        "- Author `PINN4SOH`, the linked CSV schema, the official XJTU/Zenodo documentation, and the supplied SOHbenchmark appendix were checked. PINN4SOH exposes a separate 16-feature paper schema plus capacity; no 67-column generator is present.",
        "- Author repository inventory and forks `rosyeeBen/SOHbenchmark2`, `armand00000/SOHbenchmarkT`, and `Yike-Lin/SOH-Baseline-test` were checked as discovery sources. Their trees retain the prepared-data benchmark layout and do not add a 67-feature generator.",
        "- The Nature Communications supplementary PDF, Supplementary Note 2 p. 6, supplies equations for the separate 16-feature method (mean, sample standard deviation, skewness, kurtosis, duration, accumulated charge, voltage slope, and generic entropy). No equation is claimed as a SOHbenchmark workbook formula.",
        "",
        "## Feature-level records",
        "",
        "The machine-readable [Phase 2 CSV](./formula_verification_phase2.csv) contains exactly one row per registry feature with the original formula field intentionally blank when it was not recovered. Candidate implementation formulas are copied from the existing audit ledger and are not promoted by this report.",
        "",
        "| Group | Features | Related-method evidence | Original formula recovered |",
        "|---|---:|---:|---:|",
    ]
    for group in ("CC", "dV", "CV", "dI", "Charge"):
        group_rows = [row for row in rows if row["group"] == group]
        lines.append(
            f"| `{group}` | {len(group_rows)} | {sum(row['evidence_status'] == 'RELATED_METHOD_ONLY' for row in group_rows)} | 0 |"
        )
    lines.extend(
        [
            "",
            "## Scientific interpretation",
            "",
            "- No candidate formula was edited. No source-backed regression test could be added because no original equation and no authoritative row/cycle identity were recovered.",
            "- The notebook's `[3.8,4.0] V` and `[1.0,0.5] A` examples are useful provenance for related selectors, but they do not justify changing VoltTwin's candidate windows or declaring a workbook match.",
            "- The 16-feature paper equations specify sample standard deviation (`n-1`) and a generic `-sum(p_i log p_i)` entropy, while VoltTwin candidates use different candidate windows/conventions. These differences are recorded rather than silently reconciled.",
            "- The four entropy columns remain scientifically unresolved. The existing 16-bin histogram is explicitly diagnostic and not an original formula claim.",
            "",
            "## Required next evidence",
            "",
            "Obtain from the benchmark authors a versioned 67-feature generator or a source-authored table specifying each signal, phase/window, units, sampling/interpolation, integration/derivative estimator, statistical convention, entropy estimator, and workbook-row-to-cycle key. Until then, keep all 67 formulas candidate-only in the application.",
            "",
            "## Verification",
            "",
            "- Phase 2 rows: 67 (one per feature).",
            "- Original formulas recovered: 0.",
            "- Candidate implementation formulas modified: no.",
            "- Formula Explorer modified: no.",
            "- Existing formula recovery audit and Formula Explorer provenance tests remain applicable.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    rows = build_rows()
    if len(rows) != 67 or len({row["feature"] for row in rows}) != 67:
        raise RuntimeError("Phase 2 report must contain exactly 67 unique features")
    with OUTPUT_CSV.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    summary = _summary(rows)
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(_markdown(rows, summary), encoding="utf-8")


if __name__ == "__main__":
    main()
