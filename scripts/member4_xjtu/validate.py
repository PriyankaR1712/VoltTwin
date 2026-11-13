from __future__ import annotations

import argparse
from pathlib import Path

from .loader import DEFAULT_DATA_ROOT
from .segments import SegmentationPolicy
from .validation import validate_batches, write_validation_outputs

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract explicitly unverified XJTU feature candidates and compare with workbooks."
    )
    parser.add_argument("--batches", nargs="+", type=int, default=list(range(1, 7)))
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument(
        "--cc-method",
        choices=("adaptive_candidate", "author_documented"),
        default="adaptive_candidate",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=REPOSITORY_ROOT / "reports" / "member4_candidate_validation.csv",
    )
    parser.add_argument(
        "--output-report",
        type=Path,
        default=REPOSITORY_ROOT / "reports" / "member4_candidate_validation.md",
    )
    args = parser.parse_args()
    policy = SegmentationPolicy(cc_method=args.cc_method)
    rows = validate_batches(args.batches, args.data_root, policy)
    write_validation_outputs(rows, args.output_csv, args.output_report, policy)
    print(
        f"Wrote {len(rows)} feature-scope rows to {args.output_csv} "
        f"and {args.output_report}."
    )


if __name__ == "__main__":
    main()
