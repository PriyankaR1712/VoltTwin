
import torch

from backend.streaming.stream_controller import StreamController
from models.soh_predictor import SOHPredictor
from digital_twin.battery_twin import BatteryState, BatteryTwin


class StreamProcessor:
    """
    Processes each streamed battery observation through
    the CNN and updates the Digital Twin.
    """

    def __init__(
        self,
        batch_number=1,
        sheet_name="Sheet1",
        battery_id=None,
    ):
        self.controller = StreamController(
            batch_number=batch_number,
            sheet_name=sheet_name,
        )

        self.predictor = SOHPredictor()

        self.battery_id = (
            battery_id or f"XJTU-B{batch_number}-{sheet_name}"
        )

        # Initialize the twin using the first observation's actual SOH.
        first_observation = self.controller.reader.read_observation(0)
        initial_soh = first_observation["label"] / 2.0

        self.twin = BatteryTwin(
            state=BatteryState(
                battery_id=self.battery_id,
                soh=initial_soh,
                cycle_count=0,
            )
        )

    def start(self):
        return self.controller.start()

    def pause(self):
        return self.controller.pause()

    def resume(self):
        return self.controller.resume()

    def reset(self):
        result = self.controller.reset()

        first_observation = self.controller.reader.read_observation(0)
        initial_soh = first_observation["label"] / 2.0

        self.twin = BatteryTwin(
            state=BatteryState(
                battery_id=self.battery_id,
                soh=initial_soh,
                cycle_count=0,
            )
        )

        return result

    def process_next(self):
        """
        Process one observation and return its prediction
        and updated Digital Twin state.
        """

        observation = self.controller.next_observation()

        if observation is None:
            return None

        index = observation["observation_index"]
        features = observation["features"]
        capacity = observation["label"]

        # Convert raw features to a PyTorch tensor.
        feature_tensor = torch.tensor(
            [features],
            dtype=torch.float32,
        )

        # CNN applies its own saved checkpoint normalization.
        prediction = self.predictor.predict(feature_tensor)

        predicted_soh = float(prediction.item())

        # Match the existing sequential replay conversion.
        actual_soh = float(capacity / 2.0)

        if not 0.0 <= actual_soh <= 1.0:
            raise ValueError(
                f"Invalid actual SOH at observation {index}: "
                f"{actual_soh}"
            )

        # Record prediction separately from observed SOH.
        prediction_record = self.twin.record_prediction(
            predicted_soh=predicted_soh,
            observation_index=index,
        )

        observation_record = self.twin.update_from_observation(
            observed_soh=actual_soh,
            observation_index=index,
        )

        return {
            "battery_id": self.battery_id,
            "observation_index": index,
            "capacity": capacity,
            "predicted_soh": prediction_record["predicted_soh"],
            "predicted_soh_percent": (
                prediction_record["predicted_soh_percent"]
            ),
            "actual_soh": observation_record["observed_soh"],
            "actual_soh_percent": (
                observation_record["observed_soh_percent"]
            ),
            "twin_state": self.twin.get_state(),
            "stream_status": self.controller.get_status(),
        }

    def get_status(self):
        return self.controller.get_status()
