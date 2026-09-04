from __future__ import annotations

import threading
from typing import Optional

from orion.core.state import RuntimeState
from orion.utils.logger import get_logger


class RuntimeEngine:
    """
    Controls the lifecycle of the ORION runtime.

    The engine is intentionally independent of the AI brain,
    voice system, tools, and memory system.
    """

    def __init__(self) -> None:
        self.logger = get_logger("orion.core.engine")

        self._state = RuntimeState.CREATED
        self._stop_event = threading.Event()

    @property
    def state(self) -> RuntimeState:
        """Return the current runtime state."""
        return self._state

    @property
    def is_running(self) -> bool:
        """Return True when ORION is actively running."""
        return self._state == RuntimeState.RUNNING

    def initialize(self) -> None:
        """Initialize runtime components."""

        if self._state != RuntimeState.CREATED:
            self.logger.warning(
                "Runtime initialization requested from state: %s",
                self._state.value,
            )
            return

        self.logger.info("Initializing ORION runtime.")

        self._state = RuntimeState.INITIALIZING
        self._stop_event.clear()

        self.logger.info("ORION runtime initialized.")

    def start(self) -> None:
        """Start the runtime loop."""

        if self._state == RuntimeState.CREATED:
            self.initialize()

        if self._state != RuntimeState.INITIALIZING:
            raise RuntimeError(
                f"Cannot start runtime from state: {self._state.value}"
            )

        self._state = RuntimeState.RUNNING

        self.logger.info("ORION runtime started.")

    def run(self) -> None:
        """
        Run the main ORION runtime loop.

        The runtime currently accepts simple console commands.
        Future phases will replace this with the event system.
        """

        if not self.is_running:
            raise RuntimeError(
                f"Cannot run runtime from state: {self._state.value}"
            )

        self.logger.info("ORION runtime loop entered.")

        try:
            while self.is_running:
                command = input("ORION > ").strip().lower()

                if command in {"exit", "quit", "shutdown"}:
                    self.logger.info(
                        "Shutdown command received: %s",
                        command,
                    )
                    self.stop()
                    break

                if command:
                    self.logger.info(
                        "Received runtime command: %s",
                        command,
                    )
                    print(
                        f"ORION received: {command}"
                    )

        except EOFError:
            self.logger.info(
                "Input stream closed."
            )
            self.stop()

        except KeyboardInterrupt:
            self.logger.info(
                "Keyboard interrupt received."
            )
            self.stop()

        self.logger.info("ORION runtime loop exited.")

    def stop(self) -> None:
        """Request runtime shutdown."""

        if self._state not in {
            RuntimeState.RUNNING,
            RuntimeState.INITIALIZING,
        }:
            return

        self.logger.info("Stopping ORION runtime.")

        self._state = RuntimeState.STOPPING
        self._stop_event.set()

        self._state = RuntimeState.STOPPED

        self.logger.info("ORION runtime stopped.")

    def shutdown(self) -> None:
        """Perform final runtime cleanup."""

        if self._state == RuntimeState.RUNNING:
            self.stop()

        if self._state == RuntimeState.STOPPING:
            self._state = RuntimeState.STOPPED

        self.logger.info("ORION runtime shutdown completed.")