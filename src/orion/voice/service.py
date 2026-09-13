from __future__ import annotations

from threading import Lock
from typing import Optional

from orion.core.events import Event, EventBus, EventType
from orion.pet import AvatarExpression, AvatarGesture, AvatarState
from orion.voice.contracts import (
    AudioCapture,
    MicrophonePermissionState,
    SpeechRecognizer,
    SpeechSynthesizer,
    VoiceError,
    VoiceSessionState,
    VoiceTranscript,
)


class VoiceService:
    """
    Coordinates one voice interaction.

    VoiceRuntime is responsible for repeatedly calling this
    service in the background.

    VoiceService itself remains platform-independent.
    """

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

        self.permission = (
            permission
            or MicrophonePermissionState()
        )

        self.source = source
        self.auto_speak_responses = (
            auto_speak_responses
        )
        self.default_capture_seconds = (
            default_capture_seconds
        )

        self._running = False
        self._state = VoiceSessionState.IDLE
        self._state_lock = Lock()

        if self.default_capture_seconds <= 0:
            raise ValueError(
                "Default capture duration must be positive."
            )

        if (
            self.auto_speak_responses
            and self.synthesizer is not None
        ):
            self.event_bus.subscribe(
                EventType.BRAIN_RESPONSE,
                self.handle_brain_response,
            )

        self.event_bus.subscribe(
            EventType.WAKE_WORD,
            self.handle_wake_word,
        )

    # =========================================================
    # STATUS
    # =========================================================

    @property
    def is_running(self) -> bool:
        """Return True when the voice service is active."""
        return self._running

    @property
    def state(self) -> VoiceSessionState:
        """Return the current voice-session state."""
        with self._state_lock:
            return self._state

    # =========================================================
    # LIFECYCLE
    # =========================================================

    def start(self) -> None:
        """Start the voice service."""

        if self._running:
            return

        self._running = True

        self._set_state(
            VoiceSessionState.IDLE,
            reason="voice service started",
        )

    def stop(self) -> None:
        """Stop the voice service."""

        self._running = False

        self._publish_listening(False)

        self._set_state(
            VoiceSessionState.IDLE,
            reason="voice service stopped",
        )

    # =========================================================
    # LISTENING
    # =========================================================

    def listen_once(
        self,
        duration_seconds: Optional[float] = None,
    ) -> Optional[VoiceTranscript]:
        """
        Capture one utterance and publish it as VOICE_INPUT.

        This method performs exactly one capture cycle.

        VoiceRuntime is responsible for repeatedly calling it.
        """

        if not self._running:
            raise VoiceError(
                "Voice service is not running."
            )

        if duration_seconds is None:
            duration_seconds = (
                self.default_capture_seconds
            )

        if duration_seconds <= 0:
            raise ValueError(
                "Capture duration must be positive."
            )

        try:
            # ---------------------------------------------
            # ACTIVATING
            # ---------------------------------------------

            self._set_state(
                VoiceSessionState.ACTIVATING,
                reason="voice session starting",
            )

            # ---------------------------------------------
            # PERMISSION CHECK
            # ---------------------------------------------

            # Permission is checked BEFORE entering
            # LISTENING so denied/unknown microphone access
            # never produces a false listening state.
            self.permission.require_recording_permission()

            # ---------------------------------------------
            # LISTENING
            # ---------------------------------------------

            self._set_state(
                VoiceSessionState.LISTENING,
                reason="capturing microphone audio",
            )

            self._publish_listening(True)

            audio = self.capture.capture(
                duration_seconds
            )

            # ---------------------------------------------
            # TRANSCRIBING
            # ---------------------------------------------

            self._set_state(
                VoiceSessionState.TRANSCRIBING,
                reason="converting speech to text",
            )

            transcript = self.recognizer.transcribe(
                audio
            )

        except VoiceError as exc:
            self._handle_error(
                str(exc)
            )
            return None

        except Exception as exc:
            self._handle_error(
                f"Unexpected voice error: {exc}"
            )
            return None

        finally:
            self._publish_listening(False)

        text = transcript.text.strip()

        # ---------------------------------------------
        # NOTHING WAS HEARD
        # ---------------------------------------------

        if not text:
            self._set_state(
                VoiceSessionState.IDLE,
                reason="no speech detected",
            )

            return transcript

        # ---------------------------------------------
        # PUBLISH RAW VOICE INPUT
        # ---------------------------------------------

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

        # RuntimeEngine determines whether the transcript
        # contains the configured wake phrase.

        if self.state != VoiceSessionState.THINKING:
            self._set_state(
                VoiceSessionState.IDLE,
                reason="voice input did not activate ORION",
            )

        return transcript

    # =========================================================
    # WAKE WORD
    # =========================================================

    def handle_wake_word(
        self,
        event: Event,
    ) -> None:
        """
        Handle successful wake-word detection.

        RuntimeEngine owns wake-word matching. VoiceService
        only reacts to the resulting event.
        """

        self._set_state(
            VoiceSessionState.THINKING,
            reason="wake word detected",
        )

    # =========================================================
    # SPEECH
    # =========================================================

    def speak(
        self,
        text: str,
    ) -> bool:
        """
        Speak a response and publish lifecycle events.
        """

        if self.synthesizer is None:
            return False

        if not text.strip():
            return False

        self._set_state(
            VoiceSessionState.SPEAKING,
            reason="speaking response",
        )

        self.event_bus.publish(
            Event(
                type=EventType.VOICE_SPEAKING,
                payload={
                    "active": True,
                    "text": text,
                },
                source=self.source,
            )
        )

        try:
            self.synthesizer.speak(
                text
            )

        except VoiceError as exc:
            self._handle_error(
                str(exc)
            )
            return False

        except Exception as exc:
            self._handle_error(
                f"Unexpected speech synthesis error: {exc}"
            )
            return False

        finally:
            self.event_bus.publish(
                Event(
                    type=EventType.VOICE_SPEAKING,
                    payload={
                        "active": False,
                    },
                    source=self.source,
                )
            )

        self._set_state(
            VoiceSessionState.IDLE,
            reason="speech completed",
        )

        return True

    def handle_brain_response(
        self,
        event: Event,
    ) -> None:
        """Speak a brain response when automatic TTS is enabled."""

        response = event.payload.get(
            "response"
        )

        if not isinstance(response, str):
            return

        if not response.strip():
            return

        self.speak(
            response
        )

    # =========================================================
    # STATE
    # =========================================================

    def _set_state(
        self,
        new_state: VoiceSessionState,
        reason: str = "",
    ) -> None:
        """Update and publish the voice-session state."""

        with self._state_lock:
            previous_state = self._state

            if previous_state == new_state:
                return

            self._state = new_state

        self.event_bus.publish(
            Event(
                type=EventType.VOICE_STATE,
                payload={
                    "previous_state": previous_state.value,
                    "state": new_state.value,
                    "reason": reason,
                },
                source=self.source,
            )
        )

        self._publish_avatar_for_state(
            new_state
        )

    # =========================================================
    # AVATAR
    # =========================================================

    def _publish_avatar_for_state(
        self,
        state: VoiceSessionState,
    ) -> None:
        """Convert voice state into a platform-neutral avatar expression."""

        expression: AvatarExpression | None = None

        if state == VoiceSessionState.IDLE:
            expression = AvatarExpression(
                state=AvatarState.IDLE,
                gesture=AvatarGesture.IDLE_BOB,
            )

        elif state == VoiceSessionState.ACTIVATING:
            expression = AvatarExpression(
                state=AvatarState.LISTENING,
                gesture=AvatarGesture.HEAD_TILT,
            )

        elif state == VoiceSessionState.LISTENING:
            expression = AvatarExpression(
                state=AvatarState.LISTENING,
                gesture=AvatarGesture.HEAD_TILT,
            )

        elif state == VoiceSessionState.TRANSCRIBING:
            expression = AvatarExpression(
                state=AvatarState.LISTENING,
                gesture=AvatarGesture.FOCUS,
            )

        elif state == VoiceSessionState.THINKING:
            expression = AvatarExpression(
                state=AvatarState.THINKING,
                gesture=AvatarGesture.FOCUS,
            )

        elif state == VoiceSessionState.SPEAKING:
            expression = AvatarExpression(
                state=AvatarState.HAPPY,
                gesture=AvatarGesture.NOD,
            )

        elif state == VoiceSessionState.ERROR:
            expression = AvatarExpression(
                state=AvatarState.ALERT,
                gesture=AvatarGesture.HEAD_TILT,
            )

        if expression is None:
            return

        self.event_bus.publish(
            Event(
                type=EventType.AVATAR_EXPRESSION,
                payload=expression.to_payload(),
                source=self.source,
            )
        )

    # =========================================================
    # EVENTS
    # =========================================================

    def _publish_listening(
        self,
        active: bool,
    ) -> None:
        """Publish microphone listening state."""

        self.event_bus.publish(
            Event(
                type=EventType.VOICE_LISTENING,
                payload={
                    "active": active,
                },
                source=self.source,
            )
        )

    def _handle_error(
        self,
        message: str,
    ) -> None:
        """Enter ERROR state and recover to IDLE."""

        self._set_state(
            VoiceSessionState.ERROR,
            reason=message,
        )

        self._publish_error(
            message
        )

        self._set_state(
            VoiceSessionState.IDLE,
            reason="voice error recovered",
        )

    def _publish_error(
        self,
        message: str,
    ) -> None:
        """Publish a voice error event."""

        self.event_bus.publish(
            Event(
                type=EventType.VOICE_ERROR,
                payload={
                    "message": message,
                },
                source=self.source,
            )
        )