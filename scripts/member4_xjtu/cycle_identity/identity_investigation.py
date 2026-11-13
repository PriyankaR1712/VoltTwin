from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.io import loadmat

from scripts.member4_xjtu.loader import DEFAULT_DATA_ROOT
from scripts.member4_xjtu.validation import _profile_pairs


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = ROOT / "reports" / "member4_cycle_identity_investigation"
CAPACITY_TOLERANCE = 1e-6
LABEL_TOLERANCES = (1e-6, 5e-4, 1e-3)

MAPPING_EVIDENCE = (
    {
        "method": "explicit_cycle_id",
        "classification": "Unsupported",
        "scope": "cycle-level",
        "evidence": (
            "The prepared MAT cycle structs expose relative_time_min, "
            "voltage_V, current_A, temperature_C, and capacity; the feature "
            "sheets expose the feature columns and label. No explicit cycle "
            "identifier column or field was observed."
        ),
        "limitation": (
            "Absence in these prepared files does not establish that IDs are "
            "absent from the original released acquisition files."
        ),
    },
    {
        "method": "author_provided_workbook_mapping",
        "classification": "Unsupported",
        "scope": "cycle-level",
        "evidence": (
            "No author-provided mapping file or workbook-generation join was "
            "located in the inspected repository/source material. The "
            "SOHbenchmark loader reads prepared feature sheets."
        ),
        "limitation": (
            "The public dataset archive and inaccessible/private author "
            "materials may contain additional provenance."
        ),
    },
    {
        "method": "filename_and_profile_ordinal",
        "classification": "Independently corroborated (profile level only)",
        "scope": "batch/profile",
        "evidence": (
            "MAT filenames identify the batch. The SOHbenchmark loader "
            "assigns 1-based battery IDs from MAT array order and uses the "
            "same ordinal for feature workbook sheets."
        ),
        "limitation": (
            "This is an ordinal loader convention, not a physical battery "
            "identifier or a cycle-row mapping."
        ),
    },
    {
        "method": "timestamp",
        "classification": "Unsupported in prepared MAT/workbooks",
        "scope": "cycle-level",
        "evidence": (
            "No absolute timestamp is present in the inspected prepared MAT "
            "cycle structs or workbook columns. The author preprocessing "
            "reader documents system_time in its separate source-cycle "
            "representation."
        ),
        "limitation": (
            "No documented transformation connects source system_time to "
            "the prepared MAT and feature workbook rows."
        ),
    },
    {
        "method": "charge_discharge_event_sequence",
        "classification": "Diagnostic only",
        "scope": "batch/profile",
        "evidence": (
            "The official dataset documentation describes six batch-level "
            "cycling strategies; prepared charge MAT data contains ordered "
            "charge traces. Workbook rows contain no event sequence key."
        ),
        "limitation": (
            "Batch protocol agreement cannot identify a particular workbook "
            "row as a particular prepared cycle."
        ),
    },
    {
        "method": "capacity_label",
        "classification": "Diagnostic only; ambiguous where repeated",
        "scope": "cycle-level",
        "evidence": (
            "The prepared MAT has a scalar capacity per cycle and each "
            "workbook row has a label. Capacity matching is not a unique "
            "cycle identifier and can be affected by label precision."
        ),
        "limitation": (
            "Exact or near-exact capacity agreement alone does not establish "
            "identity, especially for duplicate capacities or skipped rows."
        ),
    },
    {
        "method": "same_count_positional",
        "classification": "Diagnostic only",
        "scope": "cycle-level",
        "evidence": (
            "For equal-count profiles the existing validator pairs equal "
            "array/row indices. Matching counts do not prove that the two "
            "sequences share a cycle origin or have no omissions."
        ),
        "limitation": (
            "Workbook row order is not explicitly documented as raw MAT "
            "cycle order."
        ),
    },
)


def _items(value: Any) -> list[Any]:
    return list(np.atleast_1d(value))


def _field_names(value: Any) -> list[str]:
    fields = getattr(value, "_fieldnames", None)
    if fields is not None:
        return [str(field) for field in fields]
    if isinstance(value, dict):
        return [str(field) for field in value]
    return []


def capacity_label_agreement(
    raw_capacities: np.ndarray | list[float],
    workbook_labels: np.ndarray | list[float],
    tolerances: tuple[float, ...] = LABEL_TOLERANCES,
) -> dict[str, Any]:
    """Summarize same-index label agreement only when counts are equal.

    The result is corroborating label evidence, never a cycle-identity verdict.
    Unequal-length sequences deliberately return no positional comparison.
    """
    raw = np.asarray(raw_capacities, dtype=np.float64).reshape(-1)
    labels = np.asarray(workbook_labels, dtype=np.float64).reshape(-1)
    result: dict[str, Any] = {
        "counts_equal": len(raw) == len(labels),
        "compared_pairs": 0,
        "mean_abs_label_delta": None,
        "median_abs_label_delta": None,
        "max_abs_label_delta": None,
    }
    for tolerance in tolerances:
        result[f"matches_within_{tolerance:g}"] = None
    if len(raw) != len(labels):
        return result
    if not np.isfinite(raw).all() or not np.isfinite(labels).all():
        raise ValueError("Capacity values and workbook labels must be finite.")

    deltas = np.abs(raw - labels)
    result.update(
        compared_pairs=len(deltas),
        mean_abs_label_delta=float(np.mean(deltas)) if len(deltas) else None,
        median_abs_label_delta=float(np.median(deltas)) if len(deltas) else None,
        max_abs_label_delta=float(np.max(deltas)) if len(deltas) else None,
    )
    for tolerance in tolerances:
        result[f"matches_within_{tolerance:g}"] = int(
            np.count_nonzero(deltas <= tolerance)
        )
    return result


def _identifier_columns(columns: list[Any]) -> list[str]:
    patterns = re.compile(
        r"(^|[_\s-])(cycle(_?id|_?index|_?number|_?no)?|"
        r"timestamp|datetime|system_time|absolute_time|time|date|"
        r"battery(_?id|_?number)?)([_\s-]|$)",
        re.IGNORECASE,
    )
    results = []
    for column in columns:
        name = str(column)
        if name.lower().startswith(("relative_time", "elapsed_time")):
            continue
        if patterns.search(name):
            results.append(name)
    return results


def _read_mat_profiles(mat_path: Path) -> tuple[list[Any], dict[str, Any]]:
    data = loadmat(mat_path, squeeze_me=True, struct_as_record=False)
    if "battery" not in data:
        raise ValueError(f"{mat_path} has no 'battery' array.")
    batteries = _items(data["battery"])
    return batteries, data


def _profile_audit(
    batch: int,
    profile_ordinal: int,
    sheet_name: str,
    battery: Any,
    frame: pd.DataFrame,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    if not hasattr(battery, "cycles"):
        raise ValueError(f"Batch {batch}, profile {profile_ordinal}: missing cycles.")
    cycles = _items(battery.cycles)
    raw_capacities = np.asarray(
        [
            float(np.asarray(getattr(cycle, "capacity")).reshape(-1)[0])
            for cycle in cycles
        ],
        dtype=np.float64,
    )
    raw_fields = sorted(set().union(*(_field_names(cycle) for cycle in cycles)))
    workbook_columns = [str(column) for column in frame.columns]
    workbook_ids = _identifier_columns(workbook_columns)
    raw_ids = _identifier_columns(raw_fields)

    if "label" not in frame.columns:
        raise ValueError(f"Batch {batch}, sheet {sheet_name}: missing label.")
    labels = frame["label"].to_numpy(dtype=np.float64)
    pairs, method, unmatched, ambiguous = _profile_pairs(
        [
            _CapacityCycle(value)
            for value in raw_capacities
        ],
        frame,
    )
    used_raw = {raw_index for raw_index, _ in pairs}
    unmatched_raw = sorted(set(range(len(cycles))) - used_raw)
    agreement = capacity_label_agreement(raw_capacities, labels)
    sample_lengths = [
        len(np.asarray(getattr(cycle, "relative_time_min")).reshape(-1))
        for cycle in cycles
    ]
    row = {
        "batch": batch,
        "profile_ordinal": profile_ordinal,
        "profile_key": f"Sheet{profile_ordinal}",
        "sheet_name": sheet_name,
        "raw_cycle_count": len(cycles),
        "workbook_row_count": len(frame),
        "counts_equal": len(cycles) == len(frame),
        "existing_alignment_method": method,
        "existing_helper_matched_pairs": len(pairs),
        "unmatched_workbook_rows": len(unmatched),
        "ambiguous_workbook_rows": len(ambiguous),
        "unmatched_raw_cycles": len(unmatched_raw),
        "raw_cycle_fields": "|".join(raw_fields),
        "workbook_columns": "|".join(workbook_columns),
        "raw_explicit_identifier_fields": "|".join(raw_ids),
        "workbook_explicit_identifier_columns": "|".join(workbook_ids),
        "sample_count_min": min(sample_lengths) if sample_lengths else None,
        "sample_count_median": (
            float(np.median(sample_lengths)) if sample_lengths else None
        ),
        "sample_count_max": max(sample_lengths) if sample_lengths else None,
        **agreement,
    }
    schema_rows = [
        {
            "batch": batch,
            "profile_ordinal": profile_ordinal,
            "container": "prepared_mat_cycle",
            "field": field,
            "observed": True,
            "evidence_note": "Field observed in local prepared MAT struct.",
        }
        for field in raw_fields
    ]
    schema_rows.extend(
        {
            "batch": batch,
            "profile_ordinal": profile_ordinal,
            "container": "feature_workbook",
            "field": column,
            "observed": True,
            "evidence_note": "Column observed in local workbook sheet.",
        }
        for column in workbook_columns
    )
    unmatched_rows = [
        {
            "batch": batch,
            "profile_ordinal": profile_ordinal,
            "sheet_name": sheet_name,
            "alignment_method": method,
            "row_or_cycle_kind": (
                "ambiguous_workbook_row"
                if index in set(ambiguous)
                else "unmatched_workbook_row"
            ),
            "index_1based": index + 1,
            "capacity_or_label": float(labels[index]),
        }
        for index in unmatched
    ]
    unmatched_rows.extend(
        {
            "batch": batch,
            "profile_ordinal": profile_ordinal,
            "sheet_name": sheet_name,
            "alignment_method": method,
            "row_or_cycle_kind": "unmatched_raw_cycle",
            "index_1based": index + 1,
            "capacity_or_label": float(raw_capacities[index]),
        }
        for index in unmatched_raw
    )
    return row, schema_rows, unmatched_rows


class _CapacityCycle:
    """Minimal read-only adapter for the existing capacity alignment helper."""

    def __init__(self, capacity_label: float) -> None:
        self.capacity_label = capacity_label


def run_identity_audit(
    data_root: Path = DEFAULT_DATA_ROOT,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    batches: tuple[int, ...] = tuple(range(1, 7)),
) -> dict[str, Any]:
    """Audit local cycle/workbook evidence without changing alignment policy."""
    data_root = Path(data_root)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    profile_rows: list[dict[str, Any]] = []
    schema_rows: list[dict[str, Any]] = []
    unmatched_rows: list[dict[str, Any]] = []

    for batch in batches:
        mat_path = data_root / "charge" / f"batch-{batch}.mat"
        workbook_path = (
            data_root / "handcraft_features" / f"batch-{batch}_features.xlsx"
        )
        batteries, _ = _read_mat_profiles(mat_path)
        sheets = pd.read_excel(workbook_path, sheet_name=None)
        if len(batteries) != len(sheets):
            raise ValueError(
                f"Batch {batch}: MAT profile count {len(batteries)} differs from "
                f"workbook sheet count {len(sheets)}."
            )
        for profile_ordinal, ((sheet_name, frame), battery) in enumerate(
            zip(sheets.items(), batteries), start=1
        ):
            profile_row, schema, unmatched = _profile_audit(
                batch, profile_ordinal, sheet_name, battery, frame
            )
            profile_rows.append(profile_row)
            schema_rows.extend(schema)
            unmatched_rows.extend(unmatched)

    mapping_rows = [dict(row) for row in MAPPING_EVIDENCE]
    profile_df = pd.DataFrame(profile_rows)
    profile_df.to_csv(output_dir / "profile_audit.csv", index=False)
    pd.DataFrame(schema_rows).to_csv(output_dir / "schema_inventory.csv", index=False)
    pd.DataFrame(unmatched_rows).to_csv(
        output_dir / "unmatched_rows_and_cycles.csv", index=False
    )
    pd.DataFrame(mapping_rows).to_csv(
        output_dir / "mapping_evidence.csv", index=False
    )

    summary = {
        "profiles": len(profile_rows),
        "raw_cycles": int(profile_df["raw_cycle_count"].sum()),
        "workbook_rows": int(profile_df["workbook_row_count"].sum()),
        "helper_matched_pairs": int(
            profile_df["existing_helper_matched_pairs"].sum()
        ),
        "unmatched_workbook_rows": int(
            profile_df["unmatched_workbook_rows"].sum()
        ),
        "ambiguous_workbook_rows": int(
            profile_df["ambiguous_workbook_rows"].sum()
        ),
        "unmatched_raw_cycles": int(profile_df["unmatched_raw_cycles"].sum()),
        "equal_count_profiles": int(profile_df["counts_equal"].sum()),
        "same_index_capacity_matches_within_1e-6": int(
            profile_df["matches_within_1e-06"].fillna(0).sum()
        ),
        "same_index_capacity_comparison_profiles": int(
            profile_df["counts_equal"].sum()
        ),
        "positional_unverified_pairs": int(
            profile_df.loc[
                profile_df["existing_alignment_method"]
                == "positional_unverified_equal_counts",
                "existing_helper_matched_pairs",
            ].sum()
        ),
        "capacity_match_diagnostic_pairs": int(
            profile_df.loc[
                profile_df["existing_alignment_method"]
                == "unique_monotone_capacity_diagnostic",
                "existing_helper_matched_pairs",
            ].sum()
        ),
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit XJTU cycle-to-workbook identity evidence (read-only)."
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=DEFAULT_DATA_ROOT,
        help="SOHbenchmark XJTU data directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for generated CSV/JSON audit tables.",
    )
    args = parser.parse_args()
    summary = run_identity_audit(args.data_root, args.output_dir)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
