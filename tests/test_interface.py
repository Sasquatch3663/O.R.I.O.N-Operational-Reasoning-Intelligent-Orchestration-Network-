import pytest

from orion.core.events import (
    Event,
    EventBus,
    EventType,
)
from orion.interface.base import (
    BaseInterface,
)
from orion.interface.cli import (
    CLIInterface,
)
from orion.interface.manager import (
    InterfaceManager,
)
from orion.interface.output import (
    ConsoleOutput,
)


class MockInterface(BaseInterface):
    """Test interface implementation."""

    def __init__(
        self,
        event_bus: EventBus,
    ) -> None:

        super().__init__(
            "mock",
            event_bus,
        )

        self.sent_messages = []

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def receive(self):
        return "hello"

    def send(self, message: str) -> None:
        self.sent_messages.append(message)


def test_interface_initial_state() -> None:
    bus = EventBus()

    interface = MockInterface(bus)

    assert interface.name == "mock"
    assert interface.is_running is False


def test_interface_start_stop() -> None:
    bus = EventBus()

    interface = MockInterface(bus)

    interface.start()

    assert interface.is_running is True

    interface.stop()

    assert interface.is_running is False


def test_interface_publishes_input() -> None:
    bus = EventBus()

    interface = MockInterface(bus)

    received = []

    def handler(event: Event) -> None:
        received.append(event)

    bus.subscribe(
        EventType.USER_INPUT,
        handler,
    )

    interface.publish_input(
        "hello"
    )

    assert len(received) == 1
    assert (
        received[0].type
        == EventType.USER_INPUT
    )
    assert (
        received[0].payload["text"]
        == "hello"
    )
    assert (
        received[0].source
        == "mock"
    )


def test_interface_manager() -> None:
    bus = EventBus()

    manager = InterfaceManager()

    interface = MockInterface(bus)

    manager.register(interface)

    assert manager.count() == 1
    assert "mock" in manager.names()

    manager.start("mock")

    assert interface.is_running is True

    manager.stop("mock")

    assert interface.is_running is False


def test_interface_duplicate_registration() -> None:
    bus = EventBus()

    manager = InterfaceManager()

    interface = MockInterface(bus)

    manager.register(interface)

    with pytest.raises(ValueError):
        manager.register(interface)


def test_interface_output() -> None:
    output = ConsoleOutput()

    assert output is not None

def test_cli_interface_start_stop() -> None:
    bus = EventBus()

    cli = CLIInterface(bus)

    assert cli.is_running is False

    cli.start()

    assert cli.is_running is True

    cli.stop()

    assert cli.is_running is False

def test_cli_interface_input_event(
    monkeypatch,
) -> None:

    bus = EventBus()

    cli = CLIInterface(bus)

    cli.start()

    received = []

    def handler(event: Event) -> None:
        received.append(event)

    bus.subscribe(
        EventType.USER_INPUT,
        handler,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "hello ORION",
    )

    command = cli.receive()

    cli.publish_input(command)

    assert len(received) == 1
    assert (
        received[0].payload["text"]
        == "hello ORION"
    )