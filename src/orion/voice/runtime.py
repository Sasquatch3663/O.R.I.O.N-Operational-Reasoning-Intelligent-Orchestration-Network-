from __future__ import annotations

from threading import Event as ThreadEvent
from threading import Lock, Thread
from typing import Optional

from orion.core.events import Event, EventBus, EventType
from orion.voice.service import VoiceService


class VoiceRuntime:
    """
    Runs the ORION voice service continuously in a background worker.

    VoiceService handles one voice interaction.
    VoiceRuntime owns the continuous background lifecycle.
    """

    def __init__(
        self,
        *,
        service: VoiceService,
        event_bus: EventBus,
        capture_interval_seconds: float = 0.0,
        error_retry_delay_seconds: float = 2.0,
        join_timeout_seconds: float = 3.0,
    ) -> None:
        """
        Initialize the continuous voice runtime.

        Args:
            service:
                VoiceService responsible for one voice interaction.

            event_bus:
                ORION EventBus used for lifecycle and error events.

            capture_interval_seconds:
                Optional delay between successful capture cycles.

            error_retry_delay_seconds:
                Delay before retrying after a runtime-level error.

            join_timeout_seconds:
                Maximum time to wait for the worker thread to stop.
        """

        if capture_interval_seconds < 0:
            raise ValueError(
                "Capture interval cannot be negative."
            )

        if error_retry_delay_seconds < 0:
            raise ValueError(
                "Error retry delay cannot be negative."
            )

        if join_timeout_seconds <= 0:
            raise ValueError(
                "Join timeout must be positive."
            )

        self.service = service
        self.event_bus = event_bus

        self.capture_interval_seconds = (
            capture_interval_seconds
        )

        self.error_retry_delay_seconds = (
            error_retry_delay_seconds
        )

        self.join_timeout_seconds = (
            join_timeout_seconds
        )

        self._stop_event = ThreadEvent()
        self._lock = Lock()

        self._thread: Optional[Thread] = None
        self._running = False

    @property
    def is_running(self) -> bool:
        """Return True when the background worker is running."""

        with self._lock:
            return self._running

    @property
    def thread(self) -> Optional[Thread]:
        """Return the current worker thread, if one exists."""

        with self._lock:
            return self._thread

    def start(self) -> None:
        """
        Start the continuous voice runtime.

        This method is non-blocking.

        Calling start() multiple times is safe and does not
        create multiple worker threads.
        """

        with self._lock:
            if self._running:
                return

            self._stop_event.clear()

            # Start the underlying voice service first.
            self.service.start()

            self._thread = Thread(
                target=self._run,
                name="orion-voice-runtime",
                daemon=False,
            )

            self._running = True

            self._thread.start()

        self._publish_system_event(
            event="started"
        )

    def stop(self) -> None:
        """
        Stop the continuous voice runtime.

        The worker receives a shutdown signal and is given
        a bounded amount of time to exit.
        """

        with self._lock:
            if not self._running:
                self.service.stop()
                return

            self._stop_event.set()

            thread = self._thread

        if thread is not None:
            thread.join(
                timeout=self.join_timeout_seconds
            )

        self.service.stop()

        with self._lock:
            self._running = False
            self._thread = None

        self._publish_system_event(
            event="stopped"
        )

    def _run(self) -> None:
        """
        Execute the continuous background voice loop.
        """

        try:
            while not self._stop_event.is_set():

                try:
                    self.service.listen_once()

                except Exception as exc:
                    self._publish_voice_error(
                        f"Voice runtime error: {exc}"
                    )

                    if self._stop_event.wait(
                        self.error_retry_delay_seconds
                    ):
                        break

                    continue

                if self.capture_interval_seconds > 0:
                    if self._stop_event.wait(
                        self.capture_interval_seconds
                    ):
                        break

        finally:
            with self._lock:
                self._running = False

    def _publish_system_event(
        self,
        *,
        event: str,
    ) -> None:
        """
        Publish a voice-runtime lifecycle event.

        The payload intentionally uses the ``event`` field
        because this is the public lifecycle-event contract
        consumed by the voice runtime tests and callers.
        """

        self.event_bus.publish(
            Event(
                type=EventType.SYSTEM_EVENT,
                payload={
                    "event": event,
                    "component": "voice_runtime",
                },
                source="voice_runtime",
            )
        )

    def _publish_voice_error(
        self,
        message: str,
    ) -> None:
        """
        Publish a runtime-level voice error.
        """

        self.event_bus.publish(
            Event(
                type=EventType.VOICE_ERROR,
                payload={
                    "message": message,
                    "component": "voice_runtime",
                },
                source="voice_runtime",
            )
        )