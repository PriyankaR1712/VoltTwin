
from digital_twin.twin_manager import TwinManager


class TwinRegistry:
    """
    Maintains one operational TwinManager per battery.

    Registry is in-memory: state persists while the backend
    process is running, but is lost when the process restarts.
    """

    def __init__(self):
        self._twins: dict[str, TwinManager] = {}

    def initialize(
        self,
        battery_id: str,
        initial_soh: float = 1.0,
    ) -> TwinManager:
        if not isinstance(battery_id, str) or not battery_id.strip():
            raise ValueError("Battery ID cannot be empty.")

        if battery_id in self._twins:
            raise ValueError(
                f"Twin already exists for battery '{battery_id}'."
            )

        twin = TwinManager(
            battery_id=battery_id,
            initial_soh=initial_soh,
        )

        self._twins[battery_id] = twin
        return twin

    def get(self, battery_id: str) -> TwinManager:
        twin = self._twins.get(battery_id)

        if twin is None:
            raise KeyError(
                f"No Digital Twin initialized for battery '{battery_id}'."
            )

        return twin

    def exists(self, battery_id: str) -> bool:
        return battery_id in self._twins

    def remove(self, battery_id: str) -> bool:
        return self._twins.pop(battery_id, None) is not None

    def list_batteries(self) -> list[str]:
        return list(self._twins.keys())


# Shared registry instance for the FastAPI application.
twin_registry = TwinRegistry()
