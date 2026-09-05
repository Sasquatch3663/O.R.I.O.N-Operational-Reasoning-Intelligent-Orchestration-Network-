from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from orion.core.events import Event, EventBus, EventType


class InterfaceError(Exception):
    """Raised when an ORION interface encounters an error."""


class BaseInterface(ABC):
    """Abstract base class for ORION interfaces."""

    def __init__(
        self,
        name: str,
        event_bus: EventBus,
    ) -> None:
        if not name:
            raise ValueError("Interface name cannot be empty.")

        self.name = name
        self.event_bus = event_bus
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    def publish_input(self, text: str) -> None:
        if not text:
            return

        self.event_bus.publish(
            Event(
                type=EventType.USER_INPUT,
                payload={"text": text},
                source=self.name,
            )
        )

    def publish_shutdown(self, command: str) -> None:
        self.event_bus.publish(
            Event(
                type=EventType.SHUTDOWN,
                payload={"command": command},
                source=self.name,
            )
        )

    @abstractmethod
    def start(self) -> None:
        ...

    @abstractmethod
    def stop(self) -> None:
        ...

    @abstractmethod
    def receive(self) -> Optional[str]:
        ...

    @abstractmethod
    def send(self, message: str) -> None:
        ...