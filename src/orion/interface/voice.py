from __future__ import annotations

from typing import Optional

from orion.core.events import EventBus
from orion.interface.base import BaseInterface
from orion.utils.logger import get_logger
from orion.voice import VoiceService


class VoiceInterface(BaseInterface):
    """
    Event-driven voice interface backed by a VoiceService.
    """

    def __init__(
        self,
        event_bus: EventBus,
        service: VoiceService,
    ) -> None:
        super().__init__("voice", event_bus)

        self.service = service

        self.logger = get_logger(
            "orion.interface.voice"
        )

    def start(self) -> None:
        """Start the voice interface."""

        self._running = True
        self.service.start()

        self.logger.info(
            "Voice interface started."
        )

    def stop(self) -> None:
        """Stop the voice interface."""

        self._running = False
        self.service.stop()

        self.logger.info(
            "Voice interface stopped."
        )

    def receive(self) -> Optional[str]:
        """
        Capture and transcribe a single voice turn.
        """

        if not self._running:
            raise RuntimeError("Voice interface is not running.")

        transcript = self.service.listen_once()

        if transcript is None:
            return None

        return transcript.text or None

    def send(self, message: str) -> None:
        """
        Speak voice output through the configured synthesizer.
        """

        self.service.speak(message)
