from threading import RLock

from backend.streaming.stream_reader import XJTUBatchReader


class StreamController:
    def __init__(self, batch_number=1, sheet_name="Sheet1", reader=None):
        self.reader = reader or XJTUBatchReader(
            batch_number=batch_number,
            sheet_name=sheet_name
        )

        self.current_index = 0
        self.status = "stopped"
        self._lock = RLock()

    def start(self):
        with self._lock:
            if self.status == "completed":
                return {
                    "status": self.status,
                    "message": "Stream completed. Reset before starting again."
                }

            self.status = "running"
            return {
                "status": self.status,
                "message": "Stream started."
            }

    def pause(self):
        with self._lock:
            if self.status != "running":
                return {
                    "status": self.status,
                    "message": "Stream is not running."
                }

            self.status = "paused"
            return {
                "status": self.status,
                "message": "Stream paused."
            }

    def resume(self):
        with self._lock:
            if self.status != "paused":
                return {
                    "status": self.status,
                    "message": "Stream is not paused."
                }

            self.status = "running"
            return {
                "status": self.status,
                "message": "Stream resumed."
            }

    def reset(self):
        with self._lock:
            self.current_index = 0
            self.status = "stopped"

            return {
                "status": self.status,
                "current_index": self.current_index,
                "message": "Stream cursor reset."
            }

    def peek_observation(self):
        """
        Read the current observation without advancing the cursor.

        The cursor advances only after successful TwinManager processing
        through commit_observation().
        """
        with self._lock:
            if self.status != "running":
                return None

            if self.current_index >= self.reader.total_observations:
                self.status = "completed"
                return None

            return self.reader.read_observation(self.current_index)

    def commit_observation(self, observation_index):
        """
        Commit a successfully processed observation and advance the cursor.
        """
        with self._lock:
            if self.status != "running":
                raise RuntimeError(
                    "Cannot commit an observation when the stream is not running."
                )

            if observation_index != self.current_index:
                raise ValueError(
                    f"Cannot commit observation {observation_index}. "
                    f"Expected observation {self.current_index}."
                )

            self.current_index += 1

            if self.current_index >= self.reader.total_observations:
                self.status = "completed"

            return self.get_status()

    def get_status(self):
        with self._lock:
            total = self.reader.total_observations

            return {
                "status": self.status,
                "current_index": self.current_index,
                "total_observations": total,
                "remaining_observations": max(
                    0, total - self.current_index
                )
            }