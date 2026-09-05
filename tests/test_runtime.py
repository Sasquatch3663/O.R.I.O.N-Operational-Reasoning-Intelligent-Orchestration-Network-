from pathlib import Path

from orion.core.assistant import OrionAssistant
from orion.core.engine import RuntimeEngine
from orion.core.events import Event, EventType
from orion.core.state import RuntimeState
from orion.interface.base import BaseInterface
from orion.utils.config import Config
from orion.utils.logger import setup_logging


class MockRuntimeInterface(BaseInterface):
    """Mock interface used for runtime tests."""

    def __init__(self, event_bus):
        super().__init__(
            "test",
            event_bus,
        )

        self.commands = [
            "hello",
            "exit",
        ]

    def start(self):
        self._running = True

    def stop(self):
        self._running = False

    def receive(self):
        if self.commands:
            return self.commands.pop(0)

        return "exit"

    def send(self, message):
        pass


def test_runtime_initial_state() -> None:
    engine = RuntimeEngine()

    assert engine.state == RuntimeState.CREATED
    assert engine.is_running is False


def test_runtime_initialization() -> None:
    engine = RuntimeEngine()

    engine.initialize()

    assert engine.state == RuntimeState.INITIALIZING


def test_runtime_start() -> None:
    engine = RuntimeEngine()

    engine.initialize()
    engine.start()

    assert engine.state == RuntimeState.RUNNING
    assert engine.is_running is True

    engine.stop()

    assert engine.state == RuntimeState.STOPPED
    assert engine.is_running is False


def test_runtime_shutdown() -> None:
    engine = RuntimeEngine()

    engine.initialize()
    engine.start()
    engine.shutdown()

    assert engine.state == RuntimeState.STOPPED


def test_assistant_runtime(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]

    config = Config(root)

    setup_logging(
        config_path=(
            root
            / "config"
            / "logging.yaml"
        ),
        log_directory=tmp_path / "logs",
        level="DEBUG",
    )

    assistant = OrionAssistant(config)

    assistant.initialize()

    assert assistant.initialized is True

    assert (
        assistant.engine.state
        == RuntimeState.INITIALIZING
    )

    assistant.start()

    assert (
        assistant.engine.state
        == RuntimeState.RUNNING
    )

    status = assistant.status()

    assert status["initialized"] is True
    assert status["running"] is True
    assert status["runtime_state"] == "running"

    assistant.shutdown()

    assert (
        assistant.engine.state
        == RuntimeState.STOPPED
    )

    assert assistant.initialized is False


def test_runtime_publishes_startup_event() -> None:
    engine = RuntimeEngine()

    received = []

    def handler(event: Event) -> None:
        received.append(event)

    engine.event_bus.subscribe(
        EventType.STARTUP,
        handler,
    )

    engine.initialize()

    assert len(received) == 1
    assert received[0].type == EventType.STARTUP
    assert received[0].source == "runtime"


def test_runtime_interface_loop() -> None:
    engine = RuntimeEngine()

    engine.initialize()
    engine.start()

    interface = MockRuntimeInterface(
        engine.event_bus
    )

    interface.start()

    received = []

    def handler(event):
        received.append(event)

    engine.event_bus.subscribe(
        EventType.USER_INPUT,
        handler,
    )

    engine.run(interface)

    assert len(received) == 1

    assert (
        received[0].payload["text"]
        == "hello"
    )

    assert (
        engine.state
        == RuntimeState.STOPPED
    )