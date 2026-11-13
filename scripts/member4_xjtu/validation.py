from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .extractor import extract_cycle
from .feature_definitions import FEATURE_NAMES, feature_definitions
from .loader import DEFAULT_DATA_ROOT, load_batch
from .models import CycleTrace
from .segments import SegmentationPolicy

CAPACITY_TOLERANCE = 1e-6


def _unique_monotone_capacity_pairs(
    cycles: list[CycleTrace], labels: np.ndarray
) -> tuple[list[tuple[int, int]], list[int], list[int]]:
    pairs: list[tuple[int, int]] = []
    unmatched: list[int] = []
    ambiguous: list[int] = []
    cursor = 0
    capacities = np.asarray([cycle.capacity_label for cycle in cycles])
    for row_index, label in enumerate(labels):
        candidates = np.flatnonzero(
            np.abs(capacities[cursor:] - label) <= CAPACITY_TOLERANCE
        ) + cursor
        if len(candidates) == 1:
            cycle_index = int(candidates[0])
            pairs.append((cycle_index, row_index))
            cursor = cycle_index + 1
        elif len(candidates) > 1:
            ambiguous.append(row_index)
            unmatched.append(row_index)
        else:
            unmatched.append(row_index)
    return pairs, unmatched, ambiguous


def _profile_pairs(
    cycles: list[CycleTrace], frame: pd.DataFrame
) -> tuple[list[tuple[int, int]], str, list[int], list[int]]:
    labels = frame["label"].to_numpy(dtype=np.float64)
    if not np.isfinite(labels).all():
        raise ValueError("Workbook labels contain non-finite values.")
    if len(cycles) == len(frame):
        return (
            [(index, index) for index in range(len(frame))],
            "positional_unverified_equal_counts",
            [],
            [],
        )
    if len(cycles) < len(frame):
        return [], "unmatched_raw_cycle_shortage", list(range(len(frame))), []
    pairs, unmatched, ambiguous = _unique_monotone_capacity_pairs(cycles, labels)
    return pairs, "unique_monotone_capacity_diagnostic", unmatched, ambiguous


def _metric_rows(
    rows_by_scope: dict[str, dict[str, list[tuple[float, float]]]],
    invalid_by_scope: dict[str, dict[str, int]],
    diagnostic_by_scope: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for scope, features in rows_by_scope.items():
        for definition in feature_definitions():
            pairs = features.get(definition.name, [])
            if pairs:
                expected = np.asarray([pair[0] for pair in pairs], dtype=float)
                candidate = np.asarray([pair[1] for pair in pairs], dtype=float)
                errors = candidate - expected
                mean_abs_reference = float(np.mean(np.abs(expected)))
                relative_error = (
                    float(np.mean(np.abs(errors)) / mean_abs_reference * 100)
                    if mean_abs_reference > 0
                    else None
                )
                mae = float(np.mean(np.abs(errors)))
                rmse = float(np.sqrt(np.mean(errors**2)))
                max_error = float(np.max(np.abs(errors)))
            else:
                mean_abs_reference = mae = rmse = max_error = relative_error = None
            output.append(
                {
                    "scope": scope,
                    **definition.as_dict(),
                    "valid_pairs": len(pairs),
                    "invalid_candidate_pairs": invalid_by_scope[scope].get(
                        definition.name, 0
                    ),
                    "mean_abs_reference": mean_abs_reference,
                    "mae": mae,
                    "rmse": rmse,
                    "max_abs_error": max_error,
                    "relative_error_pct": relative_error,
                    **diagnostic_by_scope[scope],
                }
            )
    return output


def validate_batches(
    batches: list[int] = list(range(1, 7)),
    data_root: Path = DEFAULT_DATA_ROOT,
    policy: SegmentationPolicy = SegmentationPolicy(),
) -> list[dict[str, Any]]:
    rows_by_scope: dict[str, dict[str, list[tuple[float, float]]]] = {
        "overall": defaultdict(list)
    }
    invalid_by_scope: dict[str, dict[str, int]] = {
        "overall": defaultdict(int)
    }
    diagnostics: dict[str, dict[str, Any]] = {
        "overall": {
            "paired_rows": 0,
            "unmatched_workbook_rows": 0,
            "ambiguous_workbook_rows": 0,
            "alignment_methods": set(),
            "mean_abs_label_difference": None,
        }
    }
    batch_label_differences: dict[str, list[float]] = defaultdict(list)

    for batch in batches:
        profiles, sheets = load_batch(batch, data_root)
        scope = f"batch-{batch}"
        rows_by_scope[scope] = defaultdict(list)
        invalid_by_scope[scope] = defaultdict(int)
        diagnostics[scope] = {
            "paired_rows": 0,
            "unmatched_workbook_rows": 0,
            "ambiguous_workbook_rows": 0,
            "alignment_methods": set(),
            "mean_abs_label_difference": None,
        }
        for (sheet_name, frame), cycles in zip(sheets.items(), profiles):
            features = [name for name in frame.columns if name != "label"]
            if tuple(features) != FEATURE_NAMES:
                raise ValueError(
                    f"Batch {batch}/{sheet_name}: workbook feature columns/order "
                    "do not match the 67-feature schema."
                )
            pairs, method, unmatched, ambiguous = _profile_pairs(cycles, frame)
            diagnostics[scope]["alignment_methods"].add(method)
            diagnostics[scope]["unmatched_workbook_rows"] += len(unmatched)
            diagnostics[scope]["ambiguous_workbook_rows"] += len(ambiguous)
            diagnostics["overall"]["alignment_methods"].add(method)
            diagnostics["overall"]["unmatched_workbook_rows"] += len(unmatched)
            diagnostics["overall"]["ambiguous_workbook_rows"] += len(ambiguous)
            for cycle_index, row_index in pairs:
                cycle = cycles[cycle_index]
                expected_row = frame.iloc[row_index]
                label_delta = abs(cycle.capacity_label - float(expected_row["label"]))
                batch_label_differences[scope].append(label_delta)
                batch_label_differences["overall"].append(label_delta)
                candidate_values, _ = extract_cycle(cycle, policy)
                diagnostics[scope]["paired_rows"] += 1
                diagnostics["overall"]["paired_rows"] += 1
                for feature in FEATURE_NAMES:
                    actual = float(expected_row[feature])
                    candidate = candidate_values[feature]
                    if candidate is None or not math.isfinite(candidate):
                        invalid_by_scope[scope][feature] += 1
                        invalid_by_scope["overall"][feature] += 1
                        continue
                    rows_by_scope[scope][feature].append((actual, candidate))
                    rows_by_scope["overall"][feature].append((actual, candidate))

    for scope, values in batch_label_differences.items():
        diagnostics[scope]["mean_abs_label_difference"] = (
            float(np.mean(values)) if values else None
        )
        diagnostics[scope]["alignment_methods"] = "; ".join(
            sorted(diagnostics[scope]["alignment_methods"])
        )
    rows = _metric_rows(rows_by_scope, invalid_by_scope, diagnostics)
    for row in rows:
        row["cc_method"] = policy.cc_method
        row["cv_voltage_threshold_v"] = policy.cv_voltage_threshold_v
        row["dv_voltage_range_v"] = "-".join(
            f"{value:g}" for value in policy.dv_voltage_range_v
        )
        row["di_current_range_a"] = "-".join(
            f"{value:g}" for value in policy.di_current_range_a
        )
    return rows


def write_validation_outputs(
    rows: list[dict[str, Any]],
    csv_path: Path,
    report_path: Path,
    policy: SegmentationPolicy,
) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    overall = [row for row in rows if row["scope"] == "overall"]
    valid_feature_count = sum(
        row["valid_pairs"] > 0 for row in overall
    )
    batch_rows = [
        row
        for row in rows
        if row["scope"].startswith("batch-") and row["name"] == FEATURE_NAMES[0]
    ]
    report_lines = [
        "# Member 4 XJTU Candidate Extraction and Validation",
        "",
        "## Status",
        "",
        "All reported values are candidate approximations. The original workbook "
        "feature-generation source was not located; numerical agreement does not "
        "verify a formula.",
        "",
        f"- Features with at least one valid comparison: {valid_feature_count}/67.",
        "- No feature is source-verified. The four entropy columns have unknown "
        "original definitions; their histogram values are diagnostics only.",
        f"- CC selection method: `{policy.cc_method}`.",
        f"- CV begins at the first rising {policy.cv_voltage_threshold_v:g} V crossing.",
        f"- Candidate dV window: {policy.dv_voltage_range_v[0]:g}-"
        f"{policy.dv_voltage_range_v[1]:g} V; candidate dI window: "
        f"{policy.di_current_range_a[0]:g}-{policy.di_current_range_a[1]:g} A.",
        "- The optional author-documented CC selector uses current >= 3.9 A and "
        "voltage <= 4.199 V; it is not evidence that the workbook used that rule.",
        "- Statistics use a 257-point uniform-time interpolation grid; integrals "
        "use trapezoidal integration over stored timestamps and interpolated boundaries.",
        "- Entropy is an explicitly diagnostic 16-bin histogram proxy; the original "
        "entropy definition remains unknown.",
        "",
        "## Alignment and limitations",
        "",
        "Equal-count profiles are compared positionally and labeled "
        "`positional_unverified_equal_counts`; this does not prove cycle identity. "
        "Unequal-count profiles use unique monotone capacity-label matches only. "
        "Ambiguous or unmatched rows are excluded and reported in the CSV.",
        "The benchmark MAT traces contain 128 samples per cycle with nonuniform "
        "`relative_time_min` spacing. No resampling is assumed to recover the "
        "original acquisition samples.",
        "",
        "## Batch alignment coverage",
        "",
        "| Batch | Paired rows | Unmatched workbook rows | Ambiguous rows | Alignment method | Mean absolute label difference |",
        "|---|---:|---:|---:|---|---:|",
    ]
    for row in batch_rows:
        mean_label_error = row["mean_abs_label_difference"]
        report_lines.append(
            "| "
            + " | ".join(
                (
                    row["scope"],
                    str(row["paired_rows"]),
                    str(row["unmatched_workbook_rows"]),
                    str(row["ambiguous_workbook_rows"]),
                    row["alignment_methods"],
                    "" if mean_label_error is None else f"{mean_label_error:.6g}",
                )
            )
            + " |"
        )
    report_lines.extend(
        [
            "",
            "Capacity-label agreement does not prove cycle identity; equal-count "
            "profiles remain positional and unequal-count matches are conservative "
            "diagnostics only.",
            "",
        "## Overall candidate metrics",
        "",
        "| Feature | Status | Valid pairs | Invalid candidates | MAE | RMSE | Max abs error | Relative error (%) |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in overall:
        def display(value: Any) -> str:
            return "" if value is None else f"{value:.6g}" if isinstance(value, float) else str(value)
        report_lines.append(
            "| "
            + " | ".join(
                (
                    row["name"],
                    row["formula_status"],
                    str(row["valid_pairs"]),
                    str(row["invalid_candidate_pairs"]),
                    display(row["mae"]),
                    display(row["rmse"]),
                    display(row["max_abs_error"]),
                    display(row["relative_error_pct"]),
                )
            )
            + " |"
        )
    report_lines.append("")
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
