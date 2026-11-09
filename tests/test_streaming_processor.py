import pytest
import json
import os
from copy import deepcopy
from threading import Barrier, Event, Thread
from pathlib import Path

import numpy as np
import torch

from backend.twin_registry import TwinRegistry
from backend.streaming.stream_processor import (
    StreamProcessingError,
    StreamProcessor,
)
from backend.streaming.stream_reader import XJTUBatchReader
from digital_twin.twin_manager import TwinManager


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
        self._version = 0
        self.prediction_history = []

    def process_observation(self, features, observation_index=None):
        self.calls.append(observation_index)

        if self.should_fail:
            raise RuntimeError("Simulated CNN processing failure")

        self.last_observation_index = observation_index
        self._version += 1
        self.prediction_history.append({
            "observation_index": observation_index,
            "predicted_soh": 0.91,
        })

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

    def get_snapshot(self):
        return {
            "battery_id": "TEST-BATTERY",
            "version": self._version,
            "state": {
                "battery_id": "TEST-BATTERY",
                "last_observation_index": self.last_observation_index,
                "prediction_count": len(self.prediction_history),
                "state_source": "cnn_prediction",
                "twin_state": {
                    "battery_id": "TEST-BATTERY",
                    "soh": 0.91 if self.prediction_history else 1.0,
                },
            },
            "history": {
                "battery_id": "TEST-BATTERY",
                "prediction_history": deepcopy(self.prediction_history),
                "observation_history": [],
                "state_source": "cnn_prediction",
            },
            "simulation_assumptions": {},
            "_manager_identity": id(self),
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


def test_post_commit_failure_advances_cursor_and_never_replays_duplicate(
    monkeypatch,
):
    predictor = ConstantPredictor()
    registry, manager = create_registered_manager(monkeypatch, predictor)
    processor = StreamProcessor(
        battery_id="TEST-BATTERY",
        registry=registry,
        reader=FakeReader(),
    )
    original = manager.process_observation
    failed_after_commit = False

    def commit_then_fail(features, observation_index=None):
        nonlocal failed_after_commit
        result = original(features, observation_index)
        if not failed_after_commit:
            failed_after_commit = True
            raise RuntimeError("failure after twin commit")
        return result

    monkeypatch.setattr(manager, "process_observation", commit_then_fail)
    processor.start()

    with pytest.raises(StreamProcessingError) as error:
        processor.process_next()

    assert error.value.commit_status == "committed"
    assert processor.get_status()["current_index"] == 1
    assert processor.get_status()["processing_error"]["commit_status"] == "committed"
    assert manager.get_snapshot()["state"]["prediction_count"] == 1

    with pytest.raises(StreamProcessingError):
        processor.process_next()

    assert predictor.calls == 1
    assert processor.resume()["status"] == "running"
    result = processor.process_next()
    assert result["observation_index"] == 1
    assert predictor.calls == 2
    assert [
        item["observation_index"]
        for item in manager.get_snapshot()["history"]["prediction_history"]
    ] == [0, 1]


def test_unknown_commit_outcome_blocks_retry_without_losing_error_state(
    monkeypatch,
):
    manager = FakeTwinManager()
    processor = create_processor(manager)
    original_process = manager.process_observation
    original_snapshot = manager.get_snapshot
    snapshot_calls = 0

    def commit_then_fail(features, observation_index=None):
        original_process(features, observation_index)
        raise RuntimeError("post-commit response failure")

    def fail_outcome_snapshot():
        nonlocal snapshot_calls
        snapshot_calls += 1
        if snapshot_calls == 1:
            raise RuntimeError("snapshot temporarily unavailable")
        return original_snapshot()

    monkeypatch.setattr(manager, "process_observation", commit_then_fail)
    monkeypatch.setattr(manager, "get_snapshot", fail_outcome_snapshot)
    processor.start()

    with pytest.raises(StreamProcessingError) as error:
        processor.process_next()

    assert error.value.commit_status == "unknown"
    assert processor.get_status()["status"] == "error"
    assert processor.get_status()["processing_error"]["commit_status"] == "unknown"
    assert processor.resume()["status"] == "error"
    with pytest.raises(StreamProcessingError):
        processor.process_next()
    assert manager.calls == [0]

    monkeypatch.setattr(manager, "get_snapshot", original_snapshot)
    assert manager.get_snapshot()["state"]["prediction_count"] == 1
    assert processor.get_status()["current_index"] == 0


class ConstantPredictor:
    def __init__(self, value=0.93):
        self.value = value
        self.calls = 0

    def predict(self, features):
        self.calls += 1
        assert tuple(features.shape) == (1, 67)
        return torch.tensor([self.value], dtype=torch.float32)


def create_registered_manager(monkeypatch, predictor):
    import backend.twin_registry as registry_module

    monkeypatch.setattr(
        registry_module,
        "TwinManager",
        lambda battery_id, initial_soh=1.0: TwinManager(
            battery_id=battery_id,
            initial_soh=initial_soh,
            predictor=predictor,
        ),
    )
    registry = TwinRegistry()
    manager = registry.initialize("TEST-BATTERY")
    return registry, manager


def test_processor_reuses_registered_twin_manager_and_prediction_pipeline(
    monkeypatch,
):
    predictor = ConstantPredictor()
    registry, manager = create_registered_manager(monkeypatch, predictor)
    original_twin = manager.twin
    processor = StreamProcessor(
        batch_number=1,
        sheet_name="Sheet1",
        battery_id="TEST-BATTERY",
        registry=registry,
        reader=FakeReader(),
    )

    assert processor.twin_manager is manager
    assert processor.start()["status"] == "running"
    result = processor.process_next()
    snapshot = manager.get_snapshot()

    assert predictor.calls == 1
    assert registry.get("TEST-BATTERY") is manager
    assert registry.list_batteries() == ["TEST-BATTERY"]
    assert manager.twin is original_twin
    assert result["state_source"] == "cnn_prediction"
    assert result["observation_index"] == 0
    assert result["actual_soh"] == pytest.approx(0.9)
    assert result["predicted_soh"] == pytest.approx(0.93)
    assert snapshot["version"] == 1
    assert snapshot["state"]["last_observation_index"] == 0
    assert snapshot["state"]["prediction_count"] == 1
    assert snapshot["state"]["twin_state"]["soh"] == pytest.approx(0.93)
    assert snapshot["history"]["prediction_history"][0][
        "observation_index"
    ] == 0
    assert snapshot["history"]["state_source"] == "cnn_prediction"
    assert snapshot["history"]["observation_history"] == []


def test_processor_uses_trained_cnn_when_checkpoint_is_available():
    repo_root = Path(__file__).resolve().parents[1]
    checkpoint = repo_root / "models" / "soh_cnn_xjtu_batch1_clean.pt"
    if not checkpoint.is_file():
        pytest.skip("The trained XJTU CNN checkpoint is not present in this worktree.")
    default_workbook = (
        repo_root
        / "reference"
        / "SOHbenchmark"
        / "data"
        / "XJTU"
        / "handcraft_features"
        / "batch-1_features.xlsx"
    )
    workbook = Path(os.environ.get("VOLTTWIN_XJTU_WORKBOOK", default_workbook))
    if not workbook.is_file():
        pytest.skip("The XJTU workbook is not available for trained-CNN inference.")

    registry = TwinRegistry()
    manager = registry.initialize("trained-cnn-battery")
    processor = StreamProcessor(
        battery_id="trained-cnn-battery",
        registry=registry,
        reader=XJTUBatchReader(
            batch_number=1,
            sheet_name="Sheet1",
            workbook_path=workbook,
        ),
    )
    processor.start()
    result = processor.process_next()
    snapshot = manager.get_snapshot()

    assert result["state_source"] == "cnn_prediction"
    assert result["prediction_count"] == 1
    assert snapshot["state"]["prediction_count"] == 1
    assert snapshot["state"]["last_observation_index"] == 0
    assert snapshot["history"]["prediction_history"][0][
        "predicted_soh"
    ] == pytest.approx(result["predicted_soh"])


def test_two_processors_cannot_commit_same_observation_twice(monkeypatch):
    predictor = ConstantPredictor()
    registry, manager = create_registered_manager(monkeypatch, predictor)
    processors = [
        StreamProcessor(
            batch_number=1,
            sheet_name="Sheet1",
            battery_id="TEST-BATTERY",
            registry=registry,
            reader=FakeReader(),
        )
        for _ in range(2)
    ]
    for processor in processors:
        processor.start()

    barrier = Barrier(2)
    results = []

    def run(processor):
        barrier.wait()
        try:
            results.append(("ok", processor.process_next()))
        except Exception as exc:
            results.append(("error", exc))

    threads = [Thread(target=run, args=(item,)) for item in processors]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)

    assert all(not thread.is_alive() for thread in threads)
    assert sum(kind == "ok" for kind, _ in results) == 1
    failures = [value for kind, value in results if kind == "error"]
    assert len(failures) == 1
    assert isinstance(failures[0], StreamProcessingError)
    assert failures[0].commit_status == "already_committed"
    snapshot = manager.get_snapshot()
    assert predictor.calls == 1
    assert snapshot["state"]["prediction_count"] == 1
    assert snapshot["history"]["prediction_history"][0][
        "observation_index"
    ] == 0


def test_snapshot_waits_for_inflight_prediction_then_returns_consistent_state():
    started = Event()
    release = Event()

    class BlockingPredictor(ConstantPredictor):
        def predict(self, features):
            self.calls += 1
            started.set()
            assert release.wait(timeout=5)
            return torch.tensor([0.92], dtype=torch.float32)

    manager = TwinManager(
        "snapshot-battery",
        predictor=BlockingPredictor(),
    )
    registry = TwinRegistry()
    registry._twins["snapshot-battery"] = manager
    processor = StreamProcessor(
        battery_id="snapshot-battery",
        registry=registry,
        reader=FakeReader(),
    )
    processor.start()
    process_thread = Thread(target=processor.process_next)
    process_thread.start()
    assert started.wait(timeout=5)

    captured = []
    snapshot_done = Event()

    def capture():
        captured.append(manager.get_snapshot())
        snapshot_done.set()

    snapshot_thread = Thread(target=capture)
    snapshot_thread.start()
    assert not snapshot_done.wait(timeout=0.05)
    release.set()
    process_thread.join(timeout=5)
    snapshot_thread.join(timeout=5)

    assert not process_thread.is_alive()
    assert not snapshot_thread.is_alive()
    snapshot = captured[0]
    assert snapshot["version"] == 1
    assert snapshot["state"]["prediction_count"] == 1
    assert snapshot["state"]["last_observation_index"] == 0
    assert len(snapshot["history"]["prediction_history"]) == 1
    assert snapshot["history"]["prediction_history"][0][
        "observation_index"
    ] == snapshot["state"]["last_observation_index"]
    assert snapshot["state"]["twin_state"]["soh"] == pytest.approx(0.92)


def test_failure_during_concurrent_snapshot_capture_is_not_committed():
    started = Event()
    release = Event()

    class FailOncePredictor:
        def __init__(self):
            self.calls = 0

        def predict(self, features):
            self.calls += 1
            if self.calls == 1:
                started.set()
                assert release.wait(timeout=5)
                raise RuntimeError("CNN failed before twin update")
            return torch.tensor([0.9], dtype=torch.float32)

    predictor = FailOncePredictor()
    manager = TwinManager("failure-battery", predictor=predictor)
    registry = TwinRegistry()
    registry._twins["failure-battery"] = manager
    processor = StreamProcessor(
        battery_id="failure-battery",
        registry=registry,
        reader=FakeReader(),
    )
    processor.start()
    errors = []

    def process():
        try:
            processor.process_next()
        except StreamProcessingError as exc:
            errors.append(exc)

    process_thread = Thread(target=process)
    process_thread.start()
    assert started.wait(timeout=5)
    snapshots = []
    snapshot_started = Event()
    snapshot_done = Event()

    def capture_snapshot():
        snapshot_started.set()
        snapshots.append(manager.get_snapshot())
        snapshot_done.set()

    snapshot_thread = Thread(target=capture_snapshot)
    snapshot_thread.start()
    assert snapshot_started.wait(timeout=5)
    assert not snapshot_done.wait(timeout=0.05)
    release.set()
    process_thread.join(timeout=5)
    snapshot_thread.join(timeout=5)

    assert not process_thread.is_alive()
    assert not snapshot_thread.is_alive()
    assert len(errors) == 1
    assert errors[0].commit_status == "not_committed"
    assert processor.get_status()["status"] == "error"
    assert processor.get_status()["current_index"] == 0
    assert snapshots[0]["version"] == 0
    assert snapshots[0]["state"]["prediction_count"] == 0
    assert snapshots[0]["history"]["prediction_history"] == []

    assert processor.resume()["status"] == "running"
    result = processor.process_next()
    assert result["observation_index"] == 0
    assert predictor.calls == 2
    assert manager.get_snapshot()["state"]["prediction_count"] == 1


def test_real_xjtu_reader_matches_approved_feature_metadata():
    repo_root = Path(__file__).resolve().parents[1]
    default_workbook = (
        repo_root
        / "reference"
        / "SOHbenchmark"
        / "data"
        / "XJTU"
        / "handcraft_features"
        / "batch-1_features.xlsx"
    )
    workbook = Path(
        os.environ.get("VOLTTWIN_XJTU_WORKBOOK", default_workbook)
    )
    if not workbook.is_file():
        pytest.skip("The ignored XJTU workbook is not available in this worktree.")

    reader = XJTUBatchReader(
        batch_number=1,
        sheet_name="Sheet1",
        workbook_path=workbook,
    )
    metadata_path = repo_root / "frontend" / "src" / "data" / "feature_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    expected_names = [item["name"] for item in sorted(metadata, key=lambda x: x["order"])]
    observation = reader.read_observation(0)

    assert reader.workbook_path.name == "batch-1_features.xlsx"
    assert reader.sheet_name == "Sheet1"
    assert reader.total_observations > 0
    assert reader.feature_names == expected_names
    assert len(observation["features"]) == 67
    assert np.isfinite(observation["features"]).all()
    assert observation["label"] == float(reader.labels[0])
