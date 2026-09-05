from __future__ import annotations

from typing import Optional

from orion.core.events import EventBus
from orion.interface.base import BaseInterface
from orion.utils.logger import get_logger


class VoiceInterface(BaseInterface):
    """
    Placeholder for the future ORION voice interface.

    Actual speech recognition and speech synthesis will be
    implemented during the Voice phase.
    """

    def __init__(self, event_bus: EventBus) -> None:
        super().__init__("voice")

        self.event_bus = event_bus

        self.logger = get_logger(
            "orion.interface.voice"
        )

    def start(self) -> None:
        """Start the voice interface."""

        self._running = True

        self.logger.info(
            "Voice interface started."
        )

    def stop(self) -> None:
        """Stop the voice interface."""

        self._running = False

        self.logger.info(
            "Voice interface stopped."
        )

    def receive(self) -> Optional[str]:
        """
        Receive voice input.

        Not implemented until the Voice phase.
        """

        raise NotImplementedError(
            "Voice input will be implemented "
            "in the ORION Voice phase."
        )

    def send(self, message: str) -> None:
        """
        Send voice output.

        Not implemented until the Voice phase.
        """

        raise NotImplementedError(
            "Voice output will be implemented "
            "in the ORION Voice phase."
        )