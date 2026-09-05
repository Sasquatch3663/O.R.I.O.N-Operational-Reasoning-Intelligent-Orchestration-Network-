from __future__ import annotations

import threading

from orion.core.events import (
    Event,
    EventBus,
    EventType,
)
from orion.core.state import RuntimeState
from orion.utils.logger import get_logger
from orion.interface.base import BaseInterface


class RuntimeEngine:
    """
    Controls the lifecycle of the ORION runtime.
    """

    def __init__(self) -> None:
        self.logger = get_logger(
            "orion.core.engine"
        )

        self._state = RuntimeState.CREATED

        self._stop_event = threading.Event()

        self.event_bus = EventBus()

    @property
    def state(self) -> RuntimeState:
        """Return current runtime state."""

        return self._state

    @property
    def is_running(self) -> bool:
        """Return True when runtime is active."""

        return (
            self._state
            == RuntimeState.RUNNING
        )

    def initialize(self) -> None:
        """Initialize runtime."""

        if self._state != RuntimeState.CREATED:
            self.logger.warning(
                "Runtime initialization requested "
                "from state: %s",
                self._state.value,
            )
            return

        self.logger.info(
            "Initializing ORION runtime."
        )

        self._state = RuntimeState.INITIALIZING

        self._stop_event.clear()

        self.logger.info(
            "ORION runtime initialized."
        )

        self.event_bus.publish(
            Event(
                type=EventType.STARTUP,
                source="runtime",
            )
        )

    def start(self) -> None:
        """Start runtime."""

        if self._state == RuntimeState.CREATED:
            self.initialize()

        if (
            self._state
            != RuntimeState.INITIALIZING
        ):
            raise RuntimeError(
                "Cannot start runtime from state: "
                f"{self._state.value}"
            )

        self._state = RuntimeState.RUNNING

        self.logger.info(
            "ORION runtime started."
        )

    def run_interface(
        self,
        interface: BaseInterface,
    ) -> None:
        """Run ORION through an abstract interface."""

        if not self.is_running:
            raise RuntimeError(
                "Runtime must be running before "
                "an interface can be used."
            )

        self.logger.info(
            "Runtime using interface: %s",
            interface.name,
        )

        try:
            while self.is_running:
                command = interface.receive()

                if command is None:
                    self.stop()
                    break

                if not command:
                    continue

                normalized = command.lower()

                if normalized in {
                    "exit",
                    "quit",
                    "shutdown",
                }:
                    interface.publish_shutdown(
                        normalized
                    )

                    self.stop()
                    break

                interface.publish_input(
                    command
                )

        except KeyboardInterrupt:
            self.logger.info(
                "Keyboard interrupt received."
            )

            self.stop()

        except EOFError:
            self.logger.info(
                "Interface input closed."
            )

            self.stop()

    def run(
        self,
        interface: BaseInterface,
    ) -> None:
        """Run ORION using an abstract interface."""

        if not self.is_running:
            raise RuntimeError(
                "Cannot run runtime from state: "
                f"{self._state.value}"
            )

        self.logger.info(
            "ORION runtime loop entered."
        )

        self.run_interface(interface)

        self.logger.info(
            "ORION runtime loop exited."
        )

    def stop(self) -> None:
        """Request runtime shutdown."""

        if self._state not in {
            RuntimeState.RUNNING,
            RuntimeState.INITIALIZING,
        }:
            return

        self.logger.info(
            "Stopping ORION runtime."
        )

        self._state = RuntimeState.STOPPING

        self._stop_event.set()

        self._state = RuntimeState.STOPPED

        self.logger.info(
            "ORION runtime stopped."
        )

    def shutdown(self) -> None:
        """Perform final runtime cleanup."""

        if self._state == RuntimeState.RUNNING:
            self.stop()

        if self._state == RuntimeState.STOPPING:
            self._state = RuntimeState.STOPPED

        self.event_bus.clear()

        self.logger.info(
            "ORION runtime shutdown completed."
        )