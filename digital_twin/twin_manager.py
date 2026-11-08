
import math
from copy import deepcopy
from threading import RLock

import numpy as np
import torch

from digital_twin.battery_twin import BatteryState, BatteryTwin
from digital_twin.degradation_estimator import DegradationEstimator
from digital_twin.rul_estimator import RULEstimator
from models.soh_predictor import SOHPredictor


class TwinManager:
    """
    Coordinates CNN predictions and the operational Battery Digital Twin.

    Incoming feature observations are processed by the CNN.
    Predicted SOH updates the operational twin.

    Degradation and RUL are estimated from prediction history.
    Observation indices represent dataset positions, not verified
    physical battery cycle counts.
    """

    def __init__(
        self,
        battery_id: str,
        initial_soh: float = 1.0,
        checkpoint_path=None,
        eol_threshold: float = 0.80,
        window_size: int = 25,
        predictor=None,
    ):
        if not isinstance(battery_id, str) or not battery_id.strip():
            raise ValueError("Battery ID cannot be empty.")

        self.predictor = predictor or SOHPredictor(
            checkpoint_path=checkpoint_path
        )

        self.twin = BatteryTwin(
            state=BatteryState(
                battery_id=battery_id,
                soh=initial_soh,
            )
        )

        self.degradation_estimator = DegradationEstimator(
            window_size=window_size
        )

        self.rul_estimator = RULEstimator(
            eol_threshold=eol_threshold,
            window_size=window_size,
        )

        self.last_observation_index = None
        self._lock = RLock()
        self._version = 0
        self._state_cache_key = None
        self._state_cache_value = None

    def process_observation(
        self,
        feature_values,
        observation_index=None,
    ) -> dict:
        """Atomically process one observation and update the registered twin."""
        with self._lock:
            return self._process_observation_locked(
                feature_values,
                observation_index=observation_index,
            )

    def _process_observation_locked(
        self,
        feature_values,
        observation_index=None,
    ) -> dict:
        """
        Process one incoming observation containing exactly 67 features.

        Returns the CNN prediction, updated twin state,
        degradation estimate, and RUL estimate.
        """

        if observation_index is not None:
            if (
                not isinstance(observation_index, int)
                or isinstance(observation_index, bool)
                or observation_index < 0
            ):
                raise ValueError(
                    "Observation index must be a non-negative integer."
                )

            if (
                self.last_observation_index is not None
                and observation_index <= self.last_observation_index
            ):
                raise ValueError(
                    "Observation index must be greater than the previous index."
                )

        features = np.asarray(feature_values, dtype=np.float32)

        if features.shape != (67,):
            raise ValueError(
                f"Expected 67 features, received shape {features.shape}."
            )

        if not np.isfinite(features).all():
            raise ValueError(
                "Feature values must be finite."
            )

        feature_tensor = torch.as_tensor(
            features,
            dtype=torch.float32,
        ).reshape(1, 67)

        prediction = self.predictor.predict(feature_tensor)

        if isinstance(prediction, torch.Tensor):
            prediction = prediction.detach().cpu().numpy()

        prediction = np.asarray(prediction, dtype=np.float64)

        if prediction.size != 1:
            raise ValueError(
                "CNN must return exactly one SOH prediction per observation."
            )

        predicted_soh = float(prediction.reshape(-1)[0])

        if not math.isfinite(predicted_soh):
            raise ValueError("CNN returned a non-finite SOH prediction.")

        if not 0.0 <= predicted_soh <= 1.0:
            raise ValueError(
                f"CNN prediction {predicted_soh} is outside the valid SOH range."
            )

        # Update operational twin using the CNN prediction.
        update = self.twin.update_from_prediction(
            predicted_soh=predicted_soh,
            observation_index=observation_index,
        )
        self._version += 1

        if observation_index is not None:
            self.last_observation_index = observation_index

        prediction_history = [
            item["predicted_soh"]
            for item in self.twin.prediction_history
        ]

        degradation = {
            "status": "insufficient_observations",
            "required_observations": 3,
            "available_observations": len(prediction_history),
        }

        rul = {
            "status": "insufficient_observations",
            "rul_observations": None,
            "unit": "observations",
            "is_physically_validated": False,
        }

        # Both estimators require at least 3 observations.
        if len(prediction_history) >= 3:
            degradation = self.degradation_estimator.estimate(
                prediction_history
            )

            rul = self.rul_estimator.estimate(
                prediction_history
            )

        return {
            "battery_id": self.twin.state.battery_id,
            "observation_index": observation_index,
            "prediction": {
                "predicted_soh": predicted_soh,
                "predicted_soh_percent": round(
                    predicted_soh * 100, 2
                ),
            },
            "twin_state": self.twin.get_state(),
            "state_source": update["state_source"],
            "degradation": degradation,
            "rul": rul,
            "prediction_count": len(prediction_history),
        }

    def get_state(self) -> dict:
        """Return the latest operational Digital Twin state."""
        with self._lock:
            return self._get_state_locked()

    def _get_state_locked(self) -> dict:
        twin_state = self.twin.get_state()
        prediction_records = self.twin.prediction_history
        cache_key = (
            self.last_observation_index,
            twin_state["battery_id"],
            twin_state["soh"],
            twin_state["cycle_count"],
            tuple(
                (
                    item.get("observation_index"),
                    item.get("predicted_soh"),
                )
                for item in prediction_records
            ),
        )
        if cache_key == self._state_cache_key:
            return deepcopy(self._state_cache_value)

        prediction_history = [
            item["predicted_soh"]
            for item in prediction_records
        ]

        degradation = None
        rul = None
        if len(prediction_history) >= 3:
            degradation = self.degradation_estimator.estimate(
                prediction_history
            )
            rul = self.rul_estimator.estimate(prediction_history)

        state = {
            "battery_id": self.twin.state.battery_id,
            "twin_state": twin_state,
            "last_observation_index": self.last_observation_index,
            "prediction_count": len(prediction_history),
            "degradation": degradation,
            "rul": rul,
            "state_source": "cnn_prediction",
            "rul_unit": "observations",
            "is_physically_validated": False,
        }
        self._state_cache_key = cache_key
        self._state_cache_value = deepcopy(state)
        return state

    def get_history(self) -> dict:
        """Return prediction and observation history."""
        with self._lock:
            return self._get_history_locked()

    def _get_history_locked(self) -> dict:
        return {
            "battery_id": self.twin.state.battery_id,
            "prediction_history": list(
                self.twin.prediction_history
            ),
            "observation_history": list(
                self.twin.observation_history
            ),
            "observation_count": len(
                self.twin.prediction_history
            ),
            "state_source": "cnn_prediction",
        }

    def get_snapshot(self) -> dict:
        """Capture state, histories, metadata and assumptions atomically."""
        with self._lock:
            snapshot = {
                "battery_id": self.twin.state.battery_id,
                "version": self._version,
                "state": self._get_state_locked(),
                "history": self._get_history_locked(),
                "simulation_assumptions": {
                    "degradation_per_cycle": (
                        self.twin.assumptions.degradation_per_cycle
                    ),
                    "maintenance_recovery": (
                        self.twin.assumptions.maintenance_recovery
                    ),
                },
                "_manager_identity": id(self),
            }
            return deepcopy(snapshot)
