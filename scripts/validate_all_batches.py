"""Run candidate-feature validation across all XJTU batches and write a CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

from validate_features import print_diagnostics, validate_batches, write_results


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "reports" / "feature_validation_results.csv"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"CSV output path (default: {DEFAULT_OUTPUT}).",
    )
    args = parser.parse_args()

    rows, feature_names, diagnostics = validate_batches(list(range(1, 7)))
    print_diagnostics(diagnostics)
    write_results(rows, args.output)
    print(
        f"Wrote {len(rows)} rows ({len(feature_names)} features across "
        f"overall and per-batch scopes) to {args.output}"
    )


if __name__ == "__main__":
    main()
