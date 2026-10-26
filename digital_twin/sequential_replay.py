
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from digital_twin.rul_estimator import RULEstimator
from digital_twin.battery_twin import BatteryState, BatteryTwin
from models.soh_predictor import SOHPredictor


def replay_battery(
    workbook_path: str | Path,
    sheet_name: str,
    battery_id: str,
    checkpoint_path: str | Path | None = None,
) -> dict:
    """
    Replay one battery's recorded observations in their existing order.

    Each row is predicted independently using the trained CNN.
    The prediction is evaluated against label / 2.0, then the
    Digital Twin state is updated to the observed SOH.

    Workbook row indices are observation indices, not verified
    physical cycle counts.
    """
    path = Path(workbook_path)

    if not path.is_file():
        raise FileNotFoundError(f"Workbook not found: {path}")

    if not battery_id.strip():
        raise ValueError("Battery ID cannot be empty.")

    sheets = pd.read_excel(path, sheet_name=None)

    if sheet_name not in sheets:
        raise ValueError(f"Sheet '{sheet_name}' was not found.")

    frame = sheets[sheet_name]

    if "label" not in frame.columns:
        raise ValueError(f"Sheet '{sheet_name}' has no 'label' column.")

    if len(frame) < 1:
        raise ValueError("The selected sheet contains no observations.")

    feature_columns = list(frame.columns[:-1])

    if len(feature_columns) != 67:
        raise ValueError(
            f"Expected 67 feature columns, found {len(feature_columns)}."
        )

    features = frame.loc[:, feature_columns].to_numpy(dtype=np.float32)
    capacity = frame["label"].to_numpy(dtype=np.float64)

    if not np.isfinite(features).all():
        raise ValueError("Features contain NaN or infinite values.")

    if not np.isfinite(capacity).all():
        raise ValueError("Capacity labels contain NaN or infinite values.")

    actual_soh = capacity / 2.0

    if np.any((actual_soh < 0.0) | (actual_soh > 1.0)):
        raise ValueError("Actual SOH labels must convert to values in [0, 1].")

    predictor = SOHPredictor(checkpoint_path=checkpoint_path)

    feature_tensor = torch.as_tensor(features, dtype=torch.float32)

    # Predictions are generated using the same saved scaler and feature
    # order as the original training pipeline.
    predictions = predictor.predict(feature_tensor).cpu().numpy().reshape(-1)

    if not np.isfinite(predictions).all():
        raise ValueError("The model produced non-finite predictions.")

    absolute_errors = np.abs(predictions - actual_soh)
    squared_errors = (predictions - actual_soh) ** 2

    twin = BatteryTwin(
        state=BatteryState(
            battery_id=battery_id,
            soh=float(actual_soh[0]),
            cycle_count=0,
        )
    )

    observations = []

    for index, (prediction, actual) in enumerate(
        zip(predictions, actual_soh)
        
    ):
        twin.record_prediction(
            predicted_soh=float(prediction),
            observation_index=index,
        )
        # Update the twin with the observed SOH after evaluating
        # the model prediction for this observation.
        twin.update_from_observation(
        observed_soh=float(actual),
        observation_index=index,
)

        observations.append(
            {
                "observation_index": index,
                "predicted_soh": round(float(prediction), 6),
                "predicted_soh_percent": round(float(prediction) * 100, 2),
                "actual_soh": round(float(actual), 6),
                "actual_soh_percent": round(float(actual) * 100, 2),
                "absolute_error": round(float(abs(prediction - actual)), 6),
                "twin_state": twin.get_state(),
            }
        )
        rul_estimator = RULEstimator(eol_threshold=0.80)
        rul_result = rul_estimator.estimate(actual_soh.tolist())
    return {
        "battery_id": battery_id,
        "sheet_name": sheet_name,
        "observation_count": int(len(observations)),
        "mae": round(float(np.mean(absolute_errors)), 6),
        "mae_percentage_points": round(
            float(np.mean(absolute_errors) * 100), 4
        ),
        "rmse": round(float(np.sqrt(np.mean(squared_errors))), 6),
        "rmse_percentage_points": round(
            float(np.sqrt(np.mean(squared_errors)) * 100), 4
        ),
        "observations": observations,
        "prediction_history": twin.prediction_history,
        "final_twin_state": twin.get_state(),
        "rul_estimate": rul_result,
        "evaluation_type": "sequential_observation_replay",
        "observation_order_is_verified_physical_cycle_order": False,
    }
