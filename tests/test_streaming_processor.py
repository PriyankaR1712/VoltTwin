import pytest

from backend.streaming.stream_processor import StreamProcessor


class FakeReader:
    total_observations = 2

    def read_observation(self, index):
        return {
            "observation_index": index,
            "features": [0.1] * 67,
            "label": 1.8,
        }


class FakeTwinManager:
    def __init__(self, should_fail=False):
        self.last_observation_index = None
        self.calls = []
        self.should_fail = should_fail

    def process_observation(self, features, observation_index=None):
        self.calls.append(observation_index)

        if self.should_fail:
            raise RuntimeError("Simulated CNN processing failure")

        self.last_observation_index = observation_index

        return {
            "prediction": {
                "predicted_soh": 0.91,
                "predicted_soh_percent": 91.0,
            },
            "twin_state": {"soh": 0.91},
            "degradation": {},
            "rul": {},
            "prediction_count": len(self.calls),
            "state_source": "cnn_prediction",
        }


def create_processor(manager):
    return StreamProcessor(
        batch_number=1,
        sheet_name="Sheet1",
        battery_id="TEST-BATTERY",
        twin_manager=manager,
        reader=FakeReader(),
    )


def test_manager_called_exactly_once():
    manager = FakeTwinManager()
    processor = create_processor(manager)

    processor.start()
    result = processor.process_next()

    assert manager.calls == [0]
    assert result["observation_index"] == 0
    assert result["state_source"] == "cnn_prediction"
    assert processor.get_status()["current_index"] == 1


def test_failed_processing_does_not_advance_cursor():
    manager = FakeTwinManager(should_fail=True)
    processor = create_processor(manager)

    processor.start()

    with pytest.raises(RuntimeError):
        processor.process_next()

    assert manager.calls == [0]
    assert processor.get_status()["current_index"] == 0


def test_reset_does_not_reset_registered_manager():
    manager = FakeTwinManager()
    processor = create_processor(manager)

    processor.start()
    processor.process_next()

    previous_index = manager.last_observation_index
    previous_calls = len(manager.calls)

    result = processor.reset()

    assert result["replay_requires_new_twin"] is True
    assert manager.last_observation_index == previous_index
    assert len(manager.calls) == previous_calls
    assert processor.get_status()["current_index"] == 0

    with pytest.raises(RuntimeError, match="Replay is blocked"):
        processor.start()
        processor.process_next()

    assert len(manager.calls) == previous_calls