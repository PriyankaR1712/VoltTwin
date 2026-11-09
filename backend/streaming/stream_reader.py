
from pathlib import Path

import numpy as np
import pandas as pd


class XJTUBatchReader:
    """Read XJTU observations with strict Feature Explorer validation."""

    FEATURE_NAMES = (
        "CC_energy", "CC_Q", "CC_t_mean", "CC_V_mean", "CC_T_mean",
        "CC_V_std", "CC_T_std", "CC_V_skewness", "CC_T_skewness",
        "CC_V_kurtosis", "CC_T_kurtosis", "CC_CCCT", "CC_entropy",
        "dV_energy", "dV_Q", "dV_t_mean", "dV_V_mean", "dV_T_mean",
        "dV_V_std", "dV_T_std", "dV_V_skewness", "dV_T_skewness",
        "dV_V_kurtosis", "dV_T_kurtosis", "dV_dV_devide_dt",
        "dV_entropy",
        "CV_energy", "CV_Q", "CV_t_mean", "CV_C_mean", "CV_T_mean",
        "CV_C_std", "CV_T_std", "CV_C_skewness", "CV_T_skewness",
        "CV_C_kurtosis", "CV_T_kurtosis", "CV_CVCT", "CV_entropy",
        "dI_energy", "dI_Q", "dI_t_mean", "dI_C_mean", "dI_T_mean",
        "dI_C_std", "dI_T_std", "dI_C_skewness", "dI_T_skewness",
        "dI_C_kurtosis", "dI_T_kurtosis", "dI_dI_devide_dt",
        "dI_entropy",
        "Charge_energy", "Charge_Q", "Charge_t_mean",
        "Charge_V_mean", "Charge_C_mean", "Charge_T_mean",
        "Charge_C_std", "Charge_V_std", "Charge_T_std",
        "Charge_C_skewness", "Charge_V_skewness",
        "Charge_T_skewness", "Charge_C_kurtosis",
        "Charge_V_kurtosis", "Charge_T_kurtosis",
    )

    FEATURE_COUNT = 67
    LABEL_COLUMN = "label"

    def __init__(self, batch_number=1, sheet_name="Sheet1", workbook_path=None):
        if (
            isinstance(batch_number, bool)
            or not isinstance(batch_number, int)
            or batch_number < 1
        ):
            raise ValueError("Batch number must be a positive integer.")

        project_root = Path(__file__).resolve().parents[2]

        self.workbook_path = (
            Path(workbook_path)
            if workbook_path is not None
            else (
                project_root
                / "reference"
                / "SOHbenchmark"
                / "data"
                / "XJTU"
                / "handcraft_features"
                / f"batch-{batch_number}_features.xlsx"
            )
        )
        self.sheet_name = sheet_name

        if not self.workbook_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {self.workbook_path}"
            )

        self.data = pd.read_excel(
            self.workbook_path,
            sheet_name=sheet_name,
        )

        if not isinstance(self.data, pd.DataFrame):
            raise ValueError("The selected workbook sheet is invalid.")

        actual_features = tuple(self.data.columns[:-1])

        if len(self.data.columns) != self.FEATURE_COUNT + 1:
            raise ValueError(
                f"Expected 67 features and 1 label column; "
                f"found {len(self.data.columns)} columns."
            )

        if actual_features != self.FEATURE_NAMES:
            mismatches = [
                f"position {i + 1}: expected '{expected}', "
                f"found '{actual}'"
                for i, (expected, actual) in enumerate(
                    zip(self.FEATURE_NAMES, actual_features)
                )
                if expected != actual
            ]

            raise ValueError(
                "Dataset feature names/order do not match "
                "Feature Explorer schema. "
                + "; ".join(mismatches[:10])
            )

        if self.data.columns[-1] != self.LABEL_COLUMN:
            raise ValueError(
                f"Expected '{self.LABEL_COLUMN}' as the final column."
            )

        if self.data.empty:
            raise ValueError("The selected dataset sheet is empty.")

        self.feature_names = list(self.FEATURE_NAMES)

        self.features = self.data.loc[
            :, self.feature_names
        ].to_numpy(dtype=np.float32)

        self.labels = self.data[self.LABEL_COLUMN].to_numpy(
            dtype=np.float32
        )

        if not np.isfinite(self.features).all():
            raise ValueError("Dataset features contain invalid values.")

        if not np.isfinite(self.labels).all():
            raise ValueError("Dataset labels contain invalid values.")

        self.total_observations = len(self.data)

    def read_observation(self, index):
        """Return one observation without mixing features and label."""

        if (
            isinstance(index, bool)
            or not isinstance(index, int)
            or index < 0
            or index >= self.total_observations
        ):
            raise IndexError(
                f"Observation index must be between 0 and "
                f"{self.total_observations - 1}."
            )

        return {
            "observation_index": index,
            "features": self.features[index].tolist(),
            "label": float(self.labels[index]),
        }
