from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import numpy as np

from .loader import DEFAULT_DATA_ROOT, load_batch
from .models import CycleTrace

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = (
    REPOSITORY_ROOT / "reports" / "member4" / "paper_validation_results.csv"
)

@dataclass(frozen=True)
class PaperWindow:
    window_id: str
    signal: Literal["voltage", "current"]
    lower: float
    upper: float
    unit: str
    source_definition: str
    phase_filter: str


WINDOWS = (
    PaperWindow(
        "paper_xjtu_voltage",
        "voltage",
        4.0,
        4.2,
        "V",
        "XJTU V_end=4.2 V; select [V_end-0.2, V_end].",
        "none; value-window coverage only",
    ),
    PaperWindow(
        "paper_current_band",
        "current",
        0.1,
        0.5,
        "A",
        "Paper prints current between 0.5 A and 0.1 A.",
        "not applied; authoritative CV phase boundary unavailable",
    ),
)


def _sample_counts(
    profiles: list[list[CycleTrace]],
    signal: Literal["voltage", "current"],
    lower: float,
    upper: float,
) -> tuple[list[int], int]:
    counts: list[int] = []
    sample_total = 0
    for profile in profiles:
        for cycle in profile:
            values = cycle.voltage_v if signal == "voltage" else cycle.current_a
            count = int(np.count_nonzero((values >= lower) & (values <= upper)))
            counts.append(count)
            sample_total += count
    return counts, sample_total


def build_rows(data_root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for batch in range(1, 7):
        profiles, _ = load_batch(batch, data_root)
        profile_count = len(profiles)
        for window in WINDOWS:
            counts, sample_total = _sample_counts(
                profiles,
                window.signal,
                window.lower,
                window.upper,
            )
            cycle_count = len(counts)
            cycles_with_samples = sum(count > 0 for count in counts)
            rows.append(
                {
                    "comparison_scope": "window_coverage_only_not_feature_validation",
                    "batch": batch,
                    "profile_count": profile_count,
                    "cycle_count": cycle_count,
                    "window_id": window.window_id,
                    "signal": window.signal,
                    "lower_inclusive": window.lower,
                    "upper_inclusive": window.upper,
                    "signal_unit": window.unit,
                    "source_definition": window.source_definition,
                    "phase_filter": window.phase_filter,
                    "cycles_with_at_least_one_sample": cycles_with_samples,
                    "coverage_percent": (
                        100.0 * cycles_with_samples / cycle_count
                        if cycle_count
                        else None
                    ),
                    "cycles_with_at_least_two_samples": sum(
                        count >= 2 for count in counts
                    ),
                    "samples_per_cycle_min": min(counts) if counts else None,
                    "samples_per_cycle_median": (
                        float(np.median(counts)) if counts else None
                    ),
                    "samples_per_cycle_max": max(counts) if counts else None,
                    "selected_sample_total": sample_total,
                    "feature_values_computed": False,
                }
            )
    return rows


def write_rows(rows: list[dict[str, object]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("No paper-window coverage rows were produced.")
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Audit whether prepared XJTU traces contain samples in the paper's "
            "value windows; this does not validate feature values."
        )
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=DEFAULT_DATA_ROOT,
        help="Root containing charge/ and handcraft_features/.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    rows = build_rows(args.data_root)
    write_rows(rows, args.output)
    total_cycles = sum(
        int(row["cycle_count"])
        for row in rows
        if row["window_id"] == WINDOWS[0].window_id
    )
    print(f"Wrote {len(rows)} window-coverage rows to {args.output}")
    print(f"Inspected {total_cycles} prepared cycles; no feature values were compared.")


if __name__ == "__main__":
    main()
