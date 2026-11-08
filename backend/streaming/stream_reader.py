
from pathlib import Path

import numpy as np
import pandas as pd


class XJTUBatchReader:
    """
    Reads XJTU battery data one observation at a time.
    Keeps the 67 CNN features separate from the capacity label.
    """

    FEATURE_COUNT = 67
    LABEL_COLUMN = "label"

    def __init__(self, batch_number=1, sheet_name="Sheet1"):

        # Locate the project root directory
        project_root = Path(__file__).resolve().parents[2]

        self.workbook_path = (
            project_root
            / "reference"
            / "SOHbenchmark"
            / "data"
            / "XJTU"
            / "handcraft_features"
            / f"batch-{batch_number}_features.xlsx"
        )

        if not self.workbook_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {self.workbook_path}"
            )

        # Load the selected battery's data
        self.data = pd.read_excel(
            self.workbook_path,
            sheet_name=sheet_name
        )

        # Validate dataset structure
        if self.data.shape[1] != self.FEATURE_COUNT + 1:
            raise ValueError(
                f"Expected 68 columns, found {self.data.shape[1]}"
            )

        if self.data.columns[-1] != self.LABEL_COLUMN:
            raise ValueError(
                "Expected 'label' as the last column."
            )

        # Preserve original feature order
        self.feature_names = list(self.data.columns[:-1])

        # Keep CNN features and capacity labels separate
        self.features = self.data.iloc[:, :-1].to_numpy(
            dtype=np.float32
        )

        self.labels = self.data[self.LABEL_COLUMN].to_numpy(
            dtype=np.float32
        )

        # Validate values
        if not np.isfinite(self.features).all():
            raise ValueError("Features contain invalid values.")

        if not np.isfinite(self.labels).all():
            raise ValueError("Labels contain invalid values.")

        self.total_observations = len(self.data)

    def read_observation(self, index):
        """
        Returns one observation using its zero-based row index.
        """

        if index < 0 or index >= self.total_observations:
            raise IndexError(
                f"Observation index must be between 0 and "
                f"{self.total_observations - 1}"
            )

        return {
            "observation_index": index,
            "features": self.features[index].tolist(),
            "label": float(self.labels[index])
        }
