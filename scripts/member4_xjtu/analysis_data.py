from __future__ import annotations

from pathlib import Path

import pandas as pd

from .extractor import extract_cycle
from .feature_definitions import FEATURE_NAMES
from .loader import DEFAULT_DATA_ROOT, load_batch


def load_candidate_frame(
    data_root: Path = DEFAULT_DATA_ROOT,
) -> tuple[pd.DataFrame, dict[str, int]]:
    records: list[dict[str, object]] = []
    workbook_rows = 0
    for batch in range(1, 7):
        profiles, sheets = load_batch(batch, data_root)
        workbook_rows += sum(len(frame) for frame in sheets.values())
        for profile in profiles:
            for cycle in profile:
                values, _ = extract_cycle(cycle)
                records.append(
                    {
                        "batch": cycle.batch,
                        "profile": cycle.profile,
                        "cell_id": f"batch-{cycle.batch}:{cycle.profile}",
                        "cycle_index": cycle.cycle_index,
                        "capacity_label": cycle.capacity_label,
                        **values,
                    }
                )
    frame = pd.DataFrame.from_records(records)
    if tuple(name for name in FEATURE_NAMES if name in frame.columns) != FEATURE_NAMES:
        raise ValueError("Extracted candidate features do not match the 67-feature registry.")
    return frame, {
        "profiles": int(frame["cell_id"].nunique()),
        "prepared_cycles": len(frame),
        "workbook_rows": workbook_rows,
    }
