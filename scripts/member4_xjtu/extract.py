from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

from .feature_definitions import FEATURE_NAMES, feature_definitions
from .loader import DEFAULT_DATA_ROOT, load_batch
from .segments import SegmentationPolicy
from .extractor import extract_cycle

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def extract_batches(
    batches: list[int],
    output_path: Path,
    data_root: Path = DEFAULT_DATA_ROOT,
    policy: SegmentationPolicy = SegmentationPolicy(),
) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "batch",
        "profile",
        "cycle_index",
        "capacity_label",
        "cc_method",
        "formula_status",
        "entropy_status",
        *FEATURE_NAMES,
        *(
            f"{group}_{field}"
            for group in ("CC", "dV", "CV", "dI", "Charge")
            for field in (
                "interval_count",
                "interval_start_min",
                "interval_end_min",
                "selection_method",
                "selection_state",
            )
        ),
    ]
    definitions = feature_definitions()
    unknown_entropy = any(
        definition.evidence_class == "unknown_original_definition"
        for definition in definitions
    )
    written = 0
    with output_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for batch in batches:
            profiles, _ = load_batch(batch, data_root)
            for cycles in profiles:
                for cycle in cycles:
                    values, segments = extract_cycle(cycle, policy)
                    row: dict[str, Any] = {
                        "batch": cycle.batch,
                        "profile": cycle.profile,
                        "cycle_index": cycle.cycle_index,
                        "capacity_label": cycle.capacity_label,
                        "cc_method": policy.cc_method,
                        "formula_status": "candidate_only_unverified",
                        "entropy_status": (
                            "unknown_original_formula_proxy_only"
                            if unknown_entropy
                            else "not_applicable"
                        ),
                        **values,
                    }
                    for group, segment in segments.items():
                        row[f"{group}_interval_count"] = len(segment.intervals)
                        row[f"{group}_interval_start_min"] = (
                            segment.intervals[0].start_min
                            if len(segment.intervals) == 1
                            else None
                        )
                        row[f"{group}_interval_end_min"] = (
                            segment.intervals[0].end_min
                            if len(segment.intervals) == 1
                            else None
                        )
                        row[f"{group}_selection_method"] = segment.selection_method
                        row[f"{group}_selection_state"] = (
                            "candidate_selected"
                            if segment.intervals
                            else "unavailable_candidate_segment"
                        )
                    writer.writerow(row)
                    written += 1
    return written


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract explicitly unverified XJTU feature candidates to CSV."
    )
    parser.add_argument("--batches", nargs="+", type=int, default=list(range(1, 7)))
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument(
        "--cc-method",
        choices=("adaptive_candidate", "author_documented"),
        default="adaptive_candidate",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=REPOSITORY_ROOT / "reports" / "member4_candidate_features.csv",
    )
    args = parser.parse_args()
    count = extract_batches(
        args.batches,
        args.output,
        args.data_root,
        SegmentationPolicy(cc_method=args.cc_method),
    )
    print(f"Wrote {count} raw cycles of candidate features to {args.output}.")


if __name__ == "__main__":
    main()
