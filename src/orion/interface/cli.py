from __future__ import annotations

from typing import Optional

from orion.core.events import EventBus
from orion.interface.base import BaseInterface
from orion.utils.logger import get_logger


class CLIInterface(BaseInterface):
    """Command-line interface for ORION."""

    def __init__(self, event_bus: EventBus) -> None:
        super().__init__(
            "cli",
            event_bus,
        )

        self.logger = get_logger(
            "orion.interface.cli"
        )

    def start(self) -> None:
        """Start the CLI interface."""

        if self._running:
            self.logger.warning(
                "CLI interface is already running."
            )
            return

        self._running = True

        self.logger.info(
            "CLI interface started."
        )

    def stop(self) -> None:
        """Stop the CLI interface."""

        if not self._running:
            return

        self._running = False

        self.logger.info(
            "CLI interface stopped."
        )

    def receive(self) -> Optional[str]:
        """Receive input from the command line."""

        if not self._running:
            raise RuntimeError(
                "CLI interface is not running."
            )

        try:
            command = input("ORION > ")
        except EOFError:
            self.logger.info(
                "CLI input stream closed."
            )
            return None

        return command.strip()

    def send(self, message: str) -> None:
        """Send output to the command line."""

        if not self._running:
            raise RuntimeError(
                "CLI interface is not running."
            )

        print(message)