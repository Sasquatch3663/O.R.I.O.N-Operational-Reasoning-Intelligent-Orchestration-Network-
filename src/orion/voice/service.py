from __future__ import annotations

from typing import Optional

from orion.core.events import Event, EventBus, EventType
from orion.pet import AvatarExpression, AvatarGesture, AvatarState
from orion.voice.contracts import (
    AudioCapture,
    MicrophonePermissionState,
    SpeechRecognizer,
    SpeechSynthesizer,
    VoiceError,
    VoiceTranscript,
)


class VoiceService:
    """Coordinates capture, transcription, voice output, and voice events."""

    def __init__(
        self,
        event_bus: EventBus,
        capture: AudioCapture,
        recognizer: SpeechRecognizer,
        synthesizer: Optional[SpeechSynthesizer] = None,
        permission: Optional[MicrophonePermissionState] = None,
        source: str = "voice",
        auto_speak_responses: bool = True,
        default_capture_seconds: float = 5.0,
    ) -> None:
        self.event_bus = event_bus
        self.capture = capture
        self.recognizer = recognizer
        self.synthesizer = synthesizer
        self.permission = permission or MicrophonePermissionState()
        self.source = source
        self.auto_speak_responses = auto_speak_responses
        self.default_capture_seconds = default_capture_seconds
        self._running = False

        if self.default_capture_seconds <= 0:
            raise ValueError("Default capture duration must be positive.")

        if self.auto_speak_responses and self.synthesizer is not None:
            self.event_bus.subscribe(
                EventType.BRAIN_RESPONSE,
                self.handle_brain_response,
            )

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def listen_once(
        self,
        duration_seconds: Optional[float] = None,
    ) -> Optional[VoiceTranscript]:
        """Capture one utterance and publish it as `VOICE_INPUT`."""

        if not self._running:
            raise VoiceError("Voice service is not running.")

        if duration_seconds is None:
            duration_seconds = self.default_capture_seconds

        if duration_seconds <= 0:
            raise ValueError("Capture duration must be positive.")

        self._publish_listening(True)

        try:
            self.permission.require_recording_permission()
            audio = self.capture.capture(duration_seconds)
            transcript = self.recognizer.transcribe(audio)
        except VoiceError as exc:
            self._publish_error(str(exc))
            return None
        finally:
            self._publish_listening(False)

        text = transcript.text.strip()

        if not text:
            return transcript

        self.event_bus.publish(
            Event(
                type=EventType.VOICE_INPUT,
                payload={
                    "text": text,
                    "language": transcript.language,
                    "confidence": transcript.confidence,
                },
                source=self.source,
            )
        )

        return transcript

    def speak(self, text: str) -> bool:
        """Speak a response and publish lifecycle events when output is enabled."""

        if self.synthesizer is None or not text.strip():
            return False

        self.event_bus.publish(
            Event(
                type=EventType.VOICE_SPEAKING,
                payload={"active": True, "text": text},
                source=self.source,
            )
        )

        try:
            self.synthesizer.speak(text)
        except VoiceError as exc:
            self._publish_error(str(exc))
            return False
        finally:
            self.event_bus.publish(
                Event(
                    type=EventType.VOICE_SPEAKING,
                    payload={"active": False},
                    source=self.source,
                )
            )

        return True

    def handle_brain_response(self, event: Event) -> None:
        response = event.payload.get("response")

        if isinstance(response, str):
            self.speak(response)

    def _publish_listening(self, active: bool) -> None:
        self.event_bus.publish(
            Event(
                type=EventType.VOICE_LISTENING,
                payload={"active": active},
                source=self.source,
            )
        )

        if active:
            expression = AvatarExpression(
                state=AvatarState.LISTENING,
                gesture=AvatarGesture.HEAD_TILT,
            )
            self.event_bus.publish(
                Event(
                    type=EventType.AVATAR_EXPRESSION,
                    payload=expression.to_payload(),
                    source=self.source,
                )
            )

    def _publish_error(self, message: str) -> None:
        self.event_bus.publish(
            Event(
                type=EventType.VOICE_ERROR,
                payload={"message": message},
                source=self.source,
            )
        )
