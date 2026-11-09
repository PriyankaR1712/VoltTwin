from threading import RLock

from backend.streaming.stream_controller import StreamController


class StreamProcessor:
    def __init__(
        self,
        batch_number=1,
        sheet_name="Sheet1",
        battery_id=None,
        twin_manager=None,
        registry=None,
        reader=None,
    ):
        self.batch_number = batch_number
        self.sheet_name = sheet_name

        self.battery_id = battery_id or (
            f"XJTU-B{batch_number}-{sheet_name}"
        )

        self.controller = StreamController(
            batch_number=batch_number,
            sheet_name=sheet_name,
            reader=reader,
        )

        # Use the existing registered TwinManager.
        # Never create another predictor or BatteryTwin here.
        if twin_manager is None:
            if registry is None:
                try:
                    from backend.twin_registry import twin_registry
                    registry = twin_registry
                except ImportError as exc:
                    raise RuntimeError(
                        "The shared TwinRegistry is not available in this "
                        "branch yet. Integrate the approved TwinRegistry "
                        "baseline before starting the stream."
                    ) from exc

            try:
                twin_manager = registry.get(self.battery_id)
            except KeyError as exc:
                raise ValueError(
                    f"No registered Digital Twin found for "
                    f"'{self.battery_id}'. Register this battery before "
                    f"starting its stream."
                ) from exc

        self.twin_manager = twin_manager
        self._lock = RLock()

        # The manager enforces strictly increasing observation indices.
        # Do not replay from index zero into a manager that has already
        # processed observations.
        self._replay_blocked = (
            getattr(self.twin_manager, "last_observation_index", None)
            is not None
        )

    def start(self):
        return self.controller.start()

    def pause(self):
        return self.controller.pause()

    def resume(self):
        return self.controller.resume()

    def reset(self):
        with self._lock:
            result = self.controller.reset()

            last_index = getattr(
                self.twin_manager,
                "last_observation_index",
                None,
            )

            self._replay_blocked = last_index is not None

            if self._replay_blocked:
                result["replay_requires_new_twin"] = True
                result["message"] = (
                    "Replay cursor reset. This registered TwinManager "
                    "has already processed observations and cannot safely "
                    "replay from index 0. Register a new battery ID to "
                    "start a fresh replay."
                )

            return result

    def process_next(self):
        with self._lock:
            if self._replay_blocked:
                raise RuntimeError(
                    "Replay is blocked because this TwinManager has already "
                    "processed observations. Use a newly registered battery "
                    "ID for a fresh replay."
                )

            # Read without advancing the cursor.
            observation = self.controller.peek_observation()

            if observation is None:
                return None

            observation_index = observation["observation_index"]
            features = observation["features"]
            capacity = float(observation["label"])

            # Actual dataset SOH is only for comparison/output.
            # It is never passed to TwinManager.
            actual_soh = capacity / 2.0

            if not 0.0 <= actual_soh <= 1.0:
                raise ValueError(
                    f"Invalid actual SOH comparison value: {actual_soh}"
                )

            # Exactly one call per successfully processed observation.
            # TwinManager performs CNN inference and updates the registered
            # operational Digital Twin from the CNN prediction.
            manager_result = self.twin_manager.process_observation(
                features,
                observation_index=observation_index,
            )

            # Advance only after TwinManager processing succeeds.
            stream_status = self.controller.commit_observation(
                observation_index
            )

            prediction = manager_result["prediction"]

            return {
                "battery_id": self.battery_id,
                "observation_index": observation_index,
                "capacity": capacity,
                "actual_soh": actual_soh,
                "actual_soh_percent": round(actual_soh * 100, 2),
                "prediction": prediction,
                "predicted_soh": prediction["predicted_soh"],
                "predicted_soh_percent": prediction[
                    "predicted_soh_percent"
                ],
                "twin_state": manager_result["twin_state"],
                "degradation": manager_result["degradation"],
                "rul": manager_result["rul"],
                "prediction_count": manager_result["prediction_count"],
                "state_source": manager_result["state_source"],
                "stream_status": stream_status,
            }

    def get_status(self):
        return self.controller.get_status()