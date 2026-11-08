
import pytest

from backend.twin_registry import TwinRegistry


class FakeTwinManager:
    def __init__(self, battery_id, initial_soh=1.0):
        self.battery_id = battery_id
        self.initial_soh = initial_soh


@pytest.fixture
def registry(monkeypatch):
    monkeypatch.setattr(
        "backend.twin_registry.TwinManager",
        FakeTwinManager,
    )
    return TwinRegistry()


def test_registry_initializes_battery(registry):
    twin = registry.initialize("battery-1", 0.95)

    assert twin.battery_id == "battery-1"
    assert twin.initial_soh == pytest.approx(0.95)
    assert registry.exists("battery-1")


def test_registry_returns_existing_twin(registry):
    created = registry.initialize("battery-1")
    retrieved = registry.get("battery-1")

    assert retrieved is created


def test_registry_keeps_batteries_separate(registry):
    first = registry.initialize("battery-1", 0.95)
    second = registry.initialize("battery-2", 0.85)

    assert first is not second
    assert registry.get("battery-1").initial_soh == pytest.approx(0.95)
    assert registry.get("battery-2").initial_soh == pytest.approx(0.85)


def test_registry_rejects_duplicate_battery(registry):
    registry.initialize("battery-1")

    with pytest.raises(ValueError, match="already exists"):
        registry.initialize("battery-1")


def test_registry_rejects_unknown_battery(registry):
    with pytest.raises(KeyError, match="No Digital Twin initialized"):
        registry.get("unknown-battery")


def test_registry_removes_battery(registry):
    registry.initialize("battery-1")

    assert registry.remove("battery-1") is True
    assert registry.exists("battery-1") is False
    assert registry.remove("battery-1") is False


def test_registry_lists_batteries(registry):
    registry.initialize("battery-1")
    registry.initialize("battery-2")

    assert registry.list_batteries() == ["battery-1", "battery-2"]
