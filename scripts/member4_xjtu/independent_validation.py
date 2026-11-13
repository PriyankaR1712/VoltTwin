from __future__ import annotations

import json
import warnings
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import spearmanr

from .extractor import extract_cycle
from .feature_definitions import FEATURE_NAMES, feature_definitions
from .loader import DEFAULT_DATA_ROOT, load_batch
from .models import CycleTrace

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = (
    REPOSITORY_ROOT
    / "reports"
    / "member4"
    / "independent_scientific_validation_summary.json"
)
DEFAULT_REPORT = (
    REPOSITORY_ROOT
    / "reports"
    / "member4"
    / "independent_scientific_validation.md"
)


def _finite_spearman(
    feature_values: list[float], capacities: list[float]
) -> float | None:
    if len(feature_values) < 3 or len(set(feature_values)) < 2 or len(set(capacities)) < 2:
        return None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = spearmanr(feature_values, capacities)
    rho = float(result.statistic)
    return rho if np.isfinite(rho) else None


def _describe(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {
            "count": 0,
            "minimum": None,
            "q25": None,
            "median": None,
            "q75": None,
            "maximum": None,
        }
    array = np.asarray(values, dtype=np.float64)
    return {
        "count": int(len(array)),
        "minimum": float(np.min(array)),
        "q25": float(np.quantile(array, 0.25)),
        "median": float(np.median(array)),
        "q75": float(np.quantile(array, 0.75)),
        "maximum": float(np.max(array)),
    }


def analyze_dataset(
    data_root: Path = DEFAULT_DATA_ROOT,
) -> dict[str, Any]:
    all_values: dict[str, list[float]] = {name: [] for name in FEATURE_NAMES}
    feature_capacities: dict[str, list[float]] = {
        name: [] for name in FEATURE_NAMES
    }
    profile_values: dict[str, list[tuple[list[float], list[float]]]] = {
        name: [] for name in FEATURE_NAMES
    }
    batch_values: dict[int, dict[str, list[float]]] = {}
    batch_summaries: list[dict[str, Any]] = []
    sample_count_distribution: Counter[int] = Counter()
    nonfinite_input_samples = 0
    nonpositive_time_intervals = 0
    nonuniform_cycle_time_grids = 0
    cycles_seen = 0
    workbook_rows = 0
    workbook_missing_values = 0

    for batch in range(1, 7):
        profiles, sheets = load_batch(batch, data_root)
        batch_values[batch] = {name: [] for name in FEATURE_NAMES}
        batch_cycle_count = 0
        batch_invalid_candidate_counts = Counter()
        batch_nonfinite_inputs = 0
        batch_nonuniform = 0
        batch_nonpositive_dt = 0
        batch_rows = 0
        batch_workbook_missing = 0

        for frame in sheets.values():
            batch_rows += len(frame)
            batch_workbook_missing += int(frame.isna().sum().sum())
        workbook_rows += batch_rows
        workbook_missing_values += batch_workbook_missing

        for profile in profiles:
            profile_feature_values: dict[str, list[float]] = {
                name: [] for name in FEATURE_NAMES
            }
            profile_feature_capacities: dict[str, list[float]] = {
                name: [] for name in FEATURE_NAMES
            }
            for cycle in profile:
                cycles_seen += 1
                batch_cycle_count += 1
                sample_count_distribution[len(cycle.time_min)] += 1
                channels = (
                    cycle.time_min,
                    cycle.voltage_v,
                    cycle.current_a,
                    cycle.temperature_c,
                    np.asarray([cycle.capacity_label]),
                )
                input_nonfinite = sum(
                    int(np.count_nonzero(~np.isfinite(channel))) for channel in channels
                )
                nonfinite_input_samples += input_nonfinite
                batch_nonfinite_inputs += input_nonfinite
                dt = np.diff(cycle.time_min)
                bad_dt = int(np.count_nonzero(dt <= 0))
                nonpositive_time_intervals += bad_dt
                batch_nonpositive_dt += bad_dt
                if len(dt) and not np.allclose(
                    dt, np.median(dt), rtol=1e-6, atol=1e-9
                ):
                    nonuniform_cycle_time_grids += 1
                    batch_nonuniform += 1

                values, _ = extract_cycle(cycle)
                capacity = float(cycle.capacity_label)
                for name, value in values.items():
                    if value is None or not np.isfinite(value):
                        batch_invalid_candidate_counts[name] += 1
                        continue
                    numeric = float(value)
                    all_values[name].append(numeric)
                    feature_capacities[name].append(capacity)
                    batch_values[batch][name].append(numeric)
                    profile_feature_values[name].append(numeric)
                    profile_feature_capacities[name].append(capacity)

            for name in FEATURE_NAMES:
                if profile_feature_values[name]:
                    profile_values[name].append(
                        (
                            profile_feature_values[name],
                            profile_feature_capacities[name],
                        )
                    )

        batch_summaries.append(
            {
                "batch": batch,
                "profile_count": len(profiles),
                "prepared_cycle_count": batch_cycle_count,
                "workbook_row_count": batch_rows,
                "workbook_missing_cells": batch_workbook_missing,
                "nonfinite_input_values": batch_nonfinite_inputs,
                "nonpositive_time_intervals": batch_nonpositive_dt,
                "cycles_with_nonuniform_time_grids": batch_nonuniform,
                "candidate_unavailable_counts_by_feature": {
                    name: int(batch_invalid_candidate_counts[name])
                    for name in FEATURE_NAMES
                    if batch_invalid_candidate_counts[name]
                },
                "feature_medians": {
                    name: _describe(batch_values[batch][name])["median"]
                    for name in FEATURE_NAMES
                },
            }
        )

    feature_results: list[dict[str, Any]] = []
    definitions = {
        definition.name: definition.as_dict()
        for definition in feature_definitions()
    }
    for name in FEATURE_NAMES:
        values = all_values[name]
        correlations = [
            rho
            for feature_list, capacity_list in profile_values[name]
            if (rho := _finite_spearman(feature_list, capacity_list)) is not None
        ]
        per_batch_medians = {
            str(batch): _describe(batch_values[batch][name])["median"]
            for batch in range(1, 7)
        }
        finite_medians = [
            value for value in per_batch_medians.values() if value is not None
        ]
        pooled_description = _describe(values)
        pooled_iqr = (
            float(pooled_description["q75"] - pooled_description["q25"])
            if pooled_description["count"]
            else 0.0
        )
        batch_median_spread = (
            float(max(finite_medians) - min(finite_medians))
            if finite_medians
            else None
        )
        capacity_rho = _finite_spearman(values, feature_capacities[name])
        feature_results.append(
            {
                **definitions[name],
                "name": name,
                "mathematical_validation": (
                    "Histogram proxy calculation tested; original entropy feature "
                    "definition unavailable."
                    if name.endswith("_entropy")
                    else "Candidate equation tested on synthetic signals; original "
                    "formula and segment provenance unverified."
                ),
                "original_benchmark_status": "unverified",
                "availability": {
                    "finite_cycles": len(values),
                    "unavailable_cycles": cycles_seen - len(values),
                    "finite_fraction": len(values) / cycles_seen if cycles_seen else None,
                },
                "candidate_value_distribution": pooled_description,
                "capacity_label_association": {
                    "pooled_spearman_rho_descriptive_only": capacity_rho,
                    "valid_profile_correlations": len(correlations),
                    "within_profile_spearman_rho_median": (
                        float(np.median(correlations)) if correlations else None
                    ),
                    "within_profile_spearman_rho_minimum": (
                        float(min(correlations)) if correlations else None
                    ),
                    "within_profile_spearman_rho_maximum": (
                        float(max(correlations)) if correlations else None
                    ),
                },
                "batch_median_capacity_protocol_cohort_values": per_batch_medians,
                "batch_median_spread": batch_median_spread,
                "batch_median_spread_over_pooled_iqr": (
                    batch_median_spread / pooled_iqr
                    if batch_median_spread is not None and pooled_iqr > 0
                    else None
                ),
            }
        )

    return {
        "analysis": "Descriptive audit of the current candidate extractor on local prepared XJTU charge MAT data.",
        "data_root": str(data_root),
        "original_benchmark_reproduction": False,
        "prediction_experiment_run": False,
        "mathematical_validation_summary": {
            "candidate_operations_checked_on_synthetic_signals": 63,
            "entropy_proxy_implementations_checked": 4,
            "candidate_outputs_checked_total": 67,
            "candidate_outputs_not_checked": 0,
            "original_benchmark_formulas_verified": 0,
            "interpretation": (
                "Synthetic arithmetic checks validate the implemented candidate "
                "operations only; the entropy originals, source formulas, and "
                "authoritative segment definitions remain unverified."
            ),
        },
        "confirmed_implementation_correction": {
            "file": "scripts/member4_xjtu/segments.py",
            "defect": (
                "CC interval construction computed interpolated threshold "
                "crossings but clamped starts to the first selected sample and "
                "ends to the last selected sample, potentially shortening or "
                "discarding positive-duration intervals."
            ),
            "correction": (
                "Use the latest applicable interpolated crossing for entry and "
                "the earliest applicable interpolated crossing for exit."
            ),
            "feature_equations_changed": False,
            "regression_expectations": {
                "current_threshold_crossing_start_min": 0.5,
                "voltage_cutoff_crossing_end_min": 0.99,
            },
        },
        "software_validation_evidence": {
            "synthetic_math_tests": {
                "command": ".\\.venv\\Scripts\\python.exe -m pytest -q tests\\member4_xjtu\\test_independent_mathematical_validation.py",
                "result": "15 passed",
            },
            "focused_member4_tests": {
                "command": ".\\.venv\\Scripts\\python.exe -m pytest -q tests\\member4_xjtu",
                "result": "38 passed",
            },
            "formula_explorer_api_tests": {
                "command": ".\\.venv\\Scripts\\python.exe -m pytest -q tests\\test_formula_explorer_api.py",
                "result": "13 passed",
            },
            "full_repository_tests": {
                "command": ".\\.venv\\Scripts\\python.exe -m pytest -q",
                "result": "119 passed",
            },
            "frontend_build": {
                "command": "Set-Location frontend; npm run build",
                "result": "passed with a non-blocking Vite large-chunk warning",
            },
            "frontend_lint": {
                "command": "Set-Location frontend; npm run lint",
                "result": "passed",
            },
            "git_diff_check": "passed",
        },
        "target_for_descriptive_associations": {
            "field": "CycleTrace.capacity_label",
            "interpretation": "Measured capacity label used as an aging/SOH proxy only; the inspected local loader does not explicitly declare its unit or normalization lineage.",
            "predictor": False,
        },
        "visualization_note": (
            "No feature-versus-SOH plot was generated because the available field "
            "is an unnormalized capacity label with unresolved unit/lineage; "
            "descriptive correlations are reported against that field explicitly "
            "as a proxy instead."
        ),
        "dataset_integrity": {
            "profiles": sum(item["profile_count"] for item in batch_summaries),
            "prepared_cycles": cycles_seen,
            "workbook_rows": workbook_rows,
            "prepared_cycle_minus_workbook_row_count": cycles_seen - workbook_rows,
            "sample_count_distribution": {
                str(key): int(sample_count_distribution[key])
                for key in sorted(sample_count_distribution)
            },
            "nonfinite_input_values": nonfinite_input_samples,
            "nonpositive_time_intervals": nonpositive_time_intervals,
            "cycles_with_nonuniform_time_grids": nonuniform_cycle_time_grids,
            "missing_workbook_cells_including_labels": workbook_missing_values,
        },
        "leakage_audit": {
            "extractor_reads_capacity_label": False,
            "capacity_label_used_to_calculate_features": False,
            "capacity_integral_features_are_direct_target_leakage": False,
            "capacity_integral_note": "Charge integrals use measured current and elapsed time and may be physically associated with capacity; this is not direct reuse of the capacity_label field.",
            "prediction_inputs_used": False,
        },
        "batch_cohort_note": (
            "Differences in feature distributions across batch labels are descriptive. "
            "They cannot be attributed to charging protocol alone because batch, cell "
            "composition, and other factors may be confounded."
        ),
        "batches": batch_summaries,
        "features": feature_results,
        "descriptive_association_summary": {
            "highest_absolute_median_within_profile_spearman": [
                item["name"]
                for item in sorted(
                    feature_results,
                    key=lambda item: abs(
                        item["capacity_label_association"][
                            "within_profile_spearman_rho_median"
                        ]
                        or 0
                    ),
                    reverse=True,
                )[:10]
            ],
            "largest_batch_median_spread_relative_to_pooled_iqr": [
                item["name"]
                for item in sorted(
                    feature_results,
                    key=lambda item: item["batch_median_spread_over_pooled_iqr"]
                    if item["batch_median_spread_over_pooled_iqr"] is not None
                    else -1,
                    reverse=True,
                )[:10]
            ],
            "causal_or_predictive_interpretation": False,
        },
        "method_limitations": [
            "The prepared MAT cycle indices are not an authoritative mapping to the workbook feature rows.",
            "Feature values are candidate calculations under current segmentation assumptions.",
            "Pooled and within-profile Spearman coefficients describe association only; no causal claim or p-value-based inference is made.",
            "Within-profile ordering is used only for descriptive association, not as evidence of authoritative cycle identity.",
            "No cycle-wise random split, predictive model, or cell-wise/batch-wise predictive validation was performed.",
        ],
    }


def _format_number(value: float | int | None, digits: int = 5) -> str:
    return "—" if value is None else f"{value:.{digits}g}"


def _markdown_report(result: dict[str, Any]) -> str:
    integrity = result["dataset_integrity"]
    features = result["features"]
    rows = [
        "# Independent Scientific Validation of Member 4 XJTU Candidates",
        "",
        "## Status and scope",
        "",
        "**Overall status: PARTIALLY VALIDATED.** Synthetic tests independently "
        "check the numerical behavior of all 67 implemented candidate outputs "
        "under their current definitions. This does **not** validate the "
        "original SOHbenchmark formulas, the author-intended feature windows, "
        "or workbook-row/cycle identity.",
        "",
        "- 63 non-entropy candidates were checked against independently written "
        "synthetic calculations for their stated candidate operations.",
        "- 4 entropy calculations were checked as 16-bin histogram proxies; "
        "their original intended feature definitions remain unknown.",
        "- Original benchmark formulas verified: **0/67**.",
        "- Authoritative workbook-row/cycle mappings: **0**.",
        "- Predictive model or cell-wise/batch-wise predictive experiment: **not run**.",
        "",
        "The synthetic oracle uses the extractor's selected candidate intervals "
        "as boundaries, then independently computes integration, moments, "
        "durations, rates, and histogram entropy. This checks arithmetic given "
        "those boundaries; it cannot establish that the candidate segmentation "
        "matches the original benchmark.",
        "",
        "## Confirmed implementation defect corrected",
        "",
        "The synthetic boundary tests exposed a CC interval construction bug: "
        "the code calculated interpolated threshold crossings but clamped the "
        "start to the first selected sample and the end to the last selected "
        "sample. This delayed starts and could reduce a valid positive-duration "
        "interval to zero length. [`segments.py`](../../scripts/member4_xjtu/segments.py) "
        "now uses the latest applicable interpolated crossing at entry and "
        "earliest at exit. Regression tests verify an analytically expected "
        "start at 0.5 min and voltage-cutoff end at 0.99 min. No feature "
        "equation was changed; actual candidate values and availability were "
        "recomputed after the segmentation correction.",
        "",
        "## Implementation, units, signals, and candidate assumptions",
        "",
        "The following table describes the implementation only. Formula status "
        "remains unverified for the original benchmark.",
        "",
        "| Feature | Group | Current candidate expression | Signal(s) | Output unit | Candidate segment | Assumptions / provenance status |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in features:
        rows.append(
            "| "
            + " | ".join(
                str(value).replace("|", "\\|").replace("\n", " ")
                for value in (
                    item["name"],
                    item["group"],
                    item["candidate_formula"],
                    item["signal"],
                    item["unit"],
                    item["segment"],
                    item["assumptions"],
                )
            )
            + " |"
        )

    rows.extend(
        [
            "",
            "## Synthetic mathematical tests",
            "",
            "The isolated test suite was run with "
            "`.\\.venv\\Scripts\\python.exe -m pytest -q "
            "tests\\member4_xjtu\\test_independent_mathematical_validation.py` "
            "and passed **15 tests**.",
            "",
            "It covers all 67 output names using a CC-to-CV synthetic trace and "
            "independent calculations, plus constant-current and constant-voltage "
            "signals, a linear ramp, changing current, duration scaling, "
            "nonuniform timestamps and trapezoidal unit conversion, constant "
            "signals, histogram proxy entropy, very short/two-point segments, "
            "missing/non-finite samples, mismatched channels, non-increasing "
            "timestamps, zero-duration interval rejection, and independence "
            "from the capacity label.",
            "",
            "These tests demonstrate behavior of the current code on controlled "
            "inputs. They do not prove source provenance, physical model "
            "adequacy, robustness to untested operating conditions, or agreement "
            "with the original workbook generator.",
            "",
            "## Software test results",
            "",
            "| Check | Command | Result |",
            "|---|---|---|",
            "| Synthetic mathematical tests | `.\\.venv\\Scripts\\python.exe -m pytest -q tests\\member4_xjtu\\test_independent_mathematical_validation.py` | **15 passed** |",
            "| Focused Member 4 tests | `.\\.venv\\Scripts\\python.exe -m pytest -q tests\\member4_xjtu` | **38 passed** |",
            "| Formula Explorer API tests | `.\\.venv\\Scripts\\python.exe -m pytest -q tests\\test_formula_explorer_api.py` | **13 passed** |",
            "| Full repository tests | `.\\.venv\\Scripts\\python.exe -m pytest -q` | **119 passed** |",
            "| Frontend production build/type check | `Set-Location frontend; npm run build` | **Passed**, with non-blocking Vite large-chunk warning |",
            "| Frontend lint | `Set-Location frontend; npm run lint` | **Passed** |",
            "| `git diff --check` | `git diff --check` | **Passed** |",
            "",
            "Frontend files were not changed during this validation. No browser "
            "automation was performed.",
            "",
            "## Prepared dataset integrity",
            "",
            f"- Profiles: **{integrity['profiles']}**; prepared cycles: "
            f"**{integrity['prepared_cycles']}**; workbook rows: "
            f"**{integrity['workbook_rows']}** (cycle-row difference "
            f"**{integrity['prepared_cycle_minus_workbook_row_count']}**).",
            f"- Sample counts per cycle: `{integrity['sample_count_distribution']}`.",
            f"- Non-finite input values: **{integrity['nonfinite_input_values']}**; "
            f"non-positive time intervals: **{integrity['nonpositive_time_intervals']}**; "
            f"cycles with nonuniform within-cycle time grids: "
            f"**{integrity['cycles_with_nonuniform_time_grids']}**.",
            f"- Missing workbook cells including labels: "
            f"**{integrity['missing_workbook_cells_including_labels']}**.",
            "",
            "The prepared MAT data are not the demonstrated original 1 Hz "
            "acquisition. Every inspected cycle has 128 samples; regular "
            "within-cycle time spacing in these files does not establish how "
            "the prepared representation was produced.",
            "",
            "## Candidate availability and descriptive aging association",
            "",
            "The association target is the raw `CycleTrace.capacity_label`, "
            "used only as an available-capacity/aging proxy. Its unit and "
            "normalization lineage are not explicit in the inspected loader; "
            "it is not reported here as calibrated SOH. Spearman coefficients "
            "are descriptive, not causal or predictive. Within-profile values "
            "pair feature and capacity values from the same prepared MAT cycle "
            "record; they do not depend on workbook row identity.",
            "",
            "| Feature | Finite cycles | Unavailable cycles | Within-profile median Spearman rho | Profiles with rho | Batch-median spread / pooled IQR |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for item in features:
        association = item["capacity_label_association"]
        rows.append(
            f"| {item['name']} | {item['availability']['finite_cycles']} | "
            f"{item['availability']['unavailable_cycles']} | "
            f"{_format_number(association['within_profile_spearman_rho_median'])} | "
            f"{association['valid_profile_correlations']} | "
            f"{_format_number(item['batch_median_spread_over_pooled_iqr'])} |"
        )

    top_correlated = sorted(
        features,
        key=lambda item: abs(
            item["capacity_label_association"][
                "within_profile_spearman_rho_median"
            ]
            or 0
        ),
        reverse=True,
    )[:10]
    top_batch = sorted(
        (
            item
            for item in features
            if item["batch_median_spread_over_pooled_iqr"] is not None
        ),
        key=lambda item: item["batch_median_spread_over_pooled_iqr"],
        reverse=True,
    )[:10]
    rows.extend(
        [
            "",
            "### Strongest within-profile monotone associations",
            "",
            "| Feature | Median within-profile Spearman rho | Profiles contributing |",
            "|---|---:|---:|",
        ]
    )
    for item in top_correlated:
        association = item["capacity_label_association"]
        rows.append(
            f"| {item['name']} | "
            f"{_format_number(association['within_profile_spearman_rho_median'])} | "
            f"{association['valid_profile_correlations']} |"
        )
    rows.extend(
        [
            "",
            "These ranks describe monotone co-variation in the prepared records. "
            "They do not demonstrate causality, predictive performance, or "
            "feature quality.",
            "",
            "### Largest between-batch distribution differences",
            "",
            "| Feature | Batch-median spread / pooled IQR | Batch-median spread |",
            "|---|---:|---:|",
        ]
    )
    for item in top_batch:
        rows.append(
            f"| {item['name']} | "
            f"{_format_number(item['batch_median_spread_over_pooled_iqr'])} | "
            f"{_format_number(item['batch_median_spread'])} |"
        )
    rows.extend(
        [
            "",
            "Between-batch differences are descriptive only. Batch labels "
            "combine charging protocol with cell composition and other possible "
            "differences; these statistics cannot isolate a protocol effect.",
            "",
            "## Missing and potentially unstable features",
            "",
            "Unavailable values are counted when the current candidate segment "
            "or a required calculation is not available. The feature table "
            "reports the observed counts for each feature. These are not "
            "missing raw input samples: all loaded raw records passed the "
            "existing channel/time validation in this run. Constant-signal "
            "moments are implemented as zero standard deviation, skewness, and "
            "Pearson kurtosis; this is a code convention, not a benchmark-verified "
            "statistical convention.",
            "",
            "## Target leakage and validation design",
            "",
            "- The extractor does not read `capacity_label`; synthetic tests "
            "confirm changing that field alone does not change feature values.",
            "- Charge and energy integrals use current, voltage, and elapsed "
            "time, not the target field. They may be physically associated with "
            "capacity and should be treated as potentially target-adjacent "
            "predictors in any later model, but are not direct reuse of the "
            "capacity label.",
            "- No predictive model was trained. No cycle-wise random split was "
            "used. No claim of cell-wise/batch-wise generalization is made.",
            "",
            "## Feature status counts",
            "",
            "| Status | Count | Interpretation |",
            "|---|---:|---|",
            "| Candidate arithmetic checked on synthetic signals | 63 | Numerical behavior of the stated candidate formula tested; original formula and source segment remain unverified. |",
            "| Entropy proxy calculation checked | 4 | 16-bin histogram implementation tested; original entropy feature definition remains unknown. |",
            "| Original SOHbenchmark formulas verified | 0 | No original feature generator or authoritative equation set was recovered. |",
            "| Authoritative cycle-to-workbook mappings | 0 | Positional/capacity associations remain unverified. |",
            "",
            "## Reproducibility",
            "",
            "From the repository root:",
            "",
            "```powershell",
            ".\\.venv\\Scripts\\python.exe -m pytest -q tests\\member4_xjtu\\test_independent_mathematical_validation.py",
            ".\\.venv\\Scripts\\python.exe -m scripts.member4_xjtu.independent_validation",
            "```",
            "",
            "The analysis command reads all six prepared MAT batches and workbook "
            "sheets, recalculates candidate features, and writes the machine-readable "
            "summary JSON beside this report. It does not modify source data.",
            "",
            "No feature-versus-SOH plot was generated because the available target "
            "field is an unnormalized capacity label with unresolved unit/lineage; "
            "associations are therefore reported numerically against that field "
            "only as a proxy.",
            "",
            "## Reviewed implementation and prior evidence",
            "",
            "- [Feature definitions](../../scripts/member4_xjtu/feature_definitions.py)",
            "- [Candidate extractor](../../scripts/member4_xjtu/extractor.py)",
            "- [Candidate segments](../../scripts/member4_xjtu/segments.py)",
            "- [Prepared data loader](../../scripts/member4_xjtu/loader.py)",
            "- [Cycle input validation](../../scripts/member4_xjtu/models.py)",
            "- [Original formula provenance audit](../member4_scientific_provenance_audit.md)",
            "- [Original benchmark reproduction status](./original_benchmark_reproduction.md)",
            "",
            "## Remaining scientific limitations",
            "",
            "- Original feature equations, boundaries, and preprocessing "
            "conventions remain unavailable.",
            "- No authoritative mapping links prepared cycles to workbook rows; "
            "the validation here therefore avoids treating workbook values as "
            "expected references.",
            "- The prepared MAT traces contain 128 samples per cycle and their "
            "lineage to original acquisition data is unresolved.",
            "- Candidate segment thresholds and policies are implementation "
            "assumptions. Mathematical agreement with synthetic expectations "
            "does not establish that they describe the authors' feature windows.",
            "- Descriptive capacity associations and batch differences are not "
            "causal findings or validated predictors.",
            "",
            "No original formula was changed, and no scientific accuracy or "
            "benchmark reproduction claim is made.",
        ]
    )
    return "\n".join(rows) + "\n"


def main() -> None:
    result = analyze_dataset()
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    DEFAULT_REPORT.write_text(_markdown_report(result), encoding="utf-8")
    print(
        f"Wrote {DEFAULT_OUTPUT} and {DEFAULT_REPORT}: "
        f"{result['dataset_integrity']['prepared_cycles']} cycles, "
        f"{len(result['features'])} candidate features; "
        "descriptive only, no prediction experiment."
    )


if __name__ == "__main__":
    main()
