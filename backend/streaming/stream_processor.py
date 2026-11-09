from threading import RLock

from backend.streaming.stream_controller import StreamController


class StreamProcessingError(RuntimeError):
    """A stream error with an explicit Digital Twin commit outcome."""

    def __init__(self, message, commit_status):
        super().__init__(message)
        self.commit_status = commit_status


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
        self._processing_error = None

        # The manager enforces strictly increasing observation indices.
        # Do not replay from index zero into a manager that has already
        # processed observations.
        self._replay_blocked = (
            self.twin_manager.get_snapshot()["state"][
                "last_observation_index"
            ] is not None
        )

    def start(self):
        with self._lock:
            return self.controller.start()

    def pause(self):
        with self._lock:
            return self.controller.pause()

    def resume(self):
        with self._lock:
            if self._processing_error is not None:
                if self._processing_error["commit_status"] in (
                    "unknown",
                    "already_committed",
                ):
                    return {
                        "status": "error",
                        "message": (
                            "The observation outcome is not safe to retry. "
                            "Inspect the registered twin and select a new "
                            "battery ID if replay must restart."
                        ),
                        "commit_status": self._processing_error[
                            "commit_status"
                        ],
                    }
                self._processing_error = None
                return self.controller.recover_from_error()
            return self.controller.resume()

    def reset(self):
        with self._lock:
            if self._processing_error is not None:
                return {
                    **self.controller.get_status(),
                    "processing_error": dict(self._processing_error),
                    "message": (
                        "Resolve the current processing error before resetting."
                    ),
                }
            result = self.controller.reset()

            last_index = self.twin_manager.get_snapshot()["state"][
                "last_observation_index"
            ]

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
            if self._processing_error is not None:
                raise StreamProcessingError(
                    "Stream is paused in a processing error state; "
                    "inspect status and explicitly resume if safe.",
                    self._processing_error["commit_status"],
                )
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
            try:
                manager_result = self.twin_manager.process_observation(
                    features,
                    observation_index=observation_index,
                )
            except Exception as exc:
                commit_status = self._classify_failed_observation(
                    observation_index,
                    exc,
                )
                if commit_status == "committed":
                    try:
                        self.controller.commit_observation(observation_index)
                    except Exception:
                        commit_status = "unknown"

                self._processing_error = {
                    "observation_index": observation_index,
                    "commit_status": commit_status,
                    "message": str(exc),
                }
                self.controller.set_error(
                    "Observation processing failed; inspect commit_status before recovery."
                )
                raise StreamProcessingError(
                    f"Observation {observation_index} failed: {exc}",
                    commit_status,
                ) from exc

            # Advance only after TwinManager processing succeeds.
            try:
                stream_status = self.controller.commit_observation(
                    observation_index
                )
            except Exception as exc:
                self._processing_error = {
                    "observation_index": observation_index,
                    "commit_status": "committed",
                    "message": str(exc),
                }
                self.controller.set_error(
                    "Digital Twin committed this observation, but the stream cursor could not advance."
                )
                raise StreamProcessingError(
                    f"Observation {observation_index} was committed to the Digital Twin, "
                    "but the stream cursor did not advance.",
                    "committed",
                ) from exc

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
        status = self.controller.get_status()
        processing_error = self._processing_error
        if processing_error is not None:
            status["processing_error"] = dict(processing_error)
        return status

    def _classify_failed_observation(self, observation_index, error):
        """Use one atomic snapshot to classify a failed manager call."""
        try:
            snapshot = self.twin_manager.get_snapshot()
            state = snapshot["state"]
            history = snapshot["history"]["prediction_history"]
            count = state["prediction_count"]
            last_index = state["last_observation_index"]

            if (
                snapshot["version"] != count
                or len(history) != count
                or (history and history[-1]["observation_index"] != last_index)
            ):
                return "unknown"

            if (
                isinstance(error, ValueError)
                and "greater than the previous index" in str(error)
                and any(
                    item["observation_index"] == observation_index
                    for item in history
                )
            ):
                return "already_committed"

            if last_index == observation_index and history:
                return "committed"

            if (
                last_index is None and count == 0
            ) or (
                isinstance(last_index, int)
                and last_index < observation_index
            ):
                return "not_committed"
        except Exception:
            pass
        return "unknown"
