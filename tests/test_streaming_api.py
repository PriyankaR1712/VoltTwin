import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from backend.main import app
from backend.streaming import stream_routes
from backend.streaming.stream_processor import StreamProcessingError


class StubStreamProcessor:
    def __init__(self, **kwargs):
        self.status = "stopped"
        self.interval_calls = []
        self.fail_next = False

    def get_status(self):
        return {
            "status": self.status,
            "current_index": 0,
            "total_observations": 1,
            "remaining_observations": 1,
        }

    def start(self):
        self.status = "running"
        return {"status": self.status, "message": "started"}

    def pause(self):
        self.status = "paused"
        return {"status": self.status, "message": "paused"}

    def resume(self):
        self.status = "running"
        return {"status": self.status, "message": "resumed"}

    def reset(self):
        self.status = "stopped"
        return {"status": self.status, "current_index": 0}

    def process_next(self):
        if self.fail_next:
            self.status = "error"
            raise StreamProcessingError(
                "test commit outcome is not known", "unknown"
            )
        return None


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(stream_routes, "StreamProcessor", StubStreamProcessor)
    with stream_routes._active_lock:
        stream_routes._active_batteries.clear()
    with TestClient(app) as test_client:
        yield test_client
    with stream_routes._active_lock:
        stream_routes._active_batteries.clear()


def test_stream_websocket_route_is_registered_and_handles_lifecycle(client):
    battery_id = "websocket-lifecycle-test"
    with client.websocket_connect(
        f"/ws/stream?battery_id={battery_id}"
    ) as websocket:
        connected = websocket.receive_json()
        assert connected["event"] == "connected"
        assert connected["battery_id"] == battery_id

        websocket.send_json({"action": "start"})
        assert websocket.receive_json()["data"]["status"] == "running"

        websocket.send_json({"action": "pause"})
        assert websocket.receive_json()["data"]["status"] == "paused"

        websocket.send_json({"action": "resume"})
        assert websocket.receive_json()["data"]["status"] == "running"

        websocket.send_json({"action": "pause"})
        assert websocket.receive_json()["data"]["status"] == "paused"

        websocket.send_json({"action": "status"})
        status = websocket.receive_json()["data"]
        assert status["status"] == "paused"

    assert battery_id not in stream_routes._active_batteries


def test_second_websocket_cannot_claim_same_battery(client):
    battery_id = "websocket-duplicate-test"
    url = f"/ws/stream?battery_id={battery_id}"
    with client.websocket_connect(url) as first:
        assert first.receive_json()["event"] == "connected"
        with client.websocket_connect(url) as second:
            rejection = second.receive_json()
            assert rejection["event"] == "error"
            with pytest.raises(WebSocketDisconnect) as disconnect:
                second.receive_json()
        assert disconnect.value.code == 4409

    assert battery_id not in stream_routes._active_batteries


def test_processing_error_is_reported_without_replaying_automatically(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        stream_routes,
        "StreamProcessor",
        lambda **kwargs: _FailingProcessor(),
    )
    with client.websocket_connect(
        "/ws/stream?battery_id=websocket-error-test"
    ) as websocket:
        assert websocket.receive_json()["event"] == "connected"
        websocket.send_json({"action": "set_interval", "interval": 0.1})
        assert websocket.receive_json()["event"] == "command_response"
        websocket.send_json({"action": "start"})
        assert websocket.receive_json()["event"] == "command_response"

        error = websocket.receive_json()
        assert error["event"] == "error"
        assert error["commit_status"] == "unknown"
        assert error["status"]["status"] == "error"

        websocket.send_json({"action": "status"})
        assert websocket.receive_json()["data"]["status"] == "error"


class _FailingProcessor(StubStreamProcessor):
    def __init__(self):
        super().__init__()
        self.fail_next = True
