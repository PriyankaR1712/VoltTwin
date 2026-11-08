
from backend.streaming.stream_reader import XJTUBatchReader


class StreamController:
    """
    Controls sequential replay of XJTU battery observations.
    """

    def __init__(self, batch_number=1, sheet_name="Sheet1"):

        self.reader = XJTUBatchReader(
            batch_number=batch_number,
            sheet_name=sheet_name
        )

        self.current_index = 0
        self.status = "stopped"

    def start(self):
        """Start streaming observations."""

        if self.status == "completed":
            return {
                "status": self.status,
                "message": "Stream completed. Reset before starting again."
            }

        self.status = "running"

        return {
            "status": self.status,
            "message": "Streaming started."
        }

    def pause(self):
        """Pause the stream."""

        if self.status != "running":
            return {
                "status": self.status,
                "message": "Stream is not running."
            }

        self.status = "paused"

        return {
            "status": self.status,
            "message": "Streaming paused."
        }

    def resume(self):
        """Resume a paused stream."""

        if self.status != "paused":
            return {
                "status": self.status,
                "message": "Stream is not paused."
            }

        self.status = "running"

        return {
            "status": self.status,
            "message": "Streaming resumed."
        }

    def reset(self):
        """Reset the stream to the first observation."""

        self.current_index = 0
        self.status = "stopped"

        return {
            "status": self.status,
            "message": "Stream reset."
        }

    def next_observation(self):
        """Read and return the next observation."""

        if self.status != "running":
            return None

        if self.current_index >= self.reader.total_observations:
            self.status = "completed"
            return None

        observation = self.reader.read_observation(
            self.current_index
        )

        self.current_index += 1

        if self.current_index >= self.reader.total_observations:
            self.status = "completed"

        return observation

    def get_status(self):
        """Return the current streaming status."""

        return {
            "status": self.status,
            "current_index": self.current_index,
            "total_observations": self.reader.total_observations,
            "remaining_observations": (
                self.reader.total_observations - self.current_index
            )
        }
