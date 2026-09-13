from __future__ import annotations

from orion.core.engine import RuntimeEngine
from orion.core.events import Event, EventBus, EventType
from orion.voice import (
    AudioChunk,
    AudioFormat,
    AudioCapture,
    MicrophonePermissionState,
    SpeechRecognizer,
    SpeechSynthesizer,
    VoiceService,
    VoiceSessionState,
    VoiceTranscript,
    WakeWordDetector,
    WakeWordProfile,
)


class FakeCapture(AudioCapture):
    """Fake microphone used for deterministic tests."""

    def __init__(self) -> None:
        self.calls = 0

    def capture(
        self,
        duration_seconds: float,
    ) -> AudioChunk:
        self.calls += 1

        return AudioChunk(
            data=b"fake-audio",
            format=AudioFormat(),
        )


class FakeRecognizer(SpeechRecognizer):
    """Fake speech recognizer used for deterministic tests."""

    def __init__(
        self,
        transcript: str = "hello nova open calendar",
    ) -> None:
        self.transcript = transcript
        self.calls = 0

    def transcribe(
        self,
        audio: AudioChunk,
    ) -> VoiceTranscript:
        self.calls += 1

        return VoiceTranscript(
            text=self.transcript,
            language="en-US",
            confidence=0.95,
        )


class FakeSynthesizer(SpeechSynthesizer):
    """Fake TTS implementation used for deterministic tests."""

    def __init__(self) -> None:
        self.spoken = []

    def speak(
        self,
        text: str,
    ) -> None:
        self.spoken.append(text)


class FailingCapture(AudioCapture):
    """Fake microphone that always fails."""

    def capture(
        self,
        duration_seconds: float,
    ) -> AudioChunk:
        raise RuntimeError(
            "Microphone failure"
        )


class FailingSynthesizer(SpeechSynthesizer):
    """Fake TTS implementation that always fails."""

    def speak(
        self,
        text: str,
    ) -> None:
        raise RuntimeError(
            "TTS failure"
        )


def create_voice_service(
    *,
    transcript: str = "hello nova open calendar",
    synthesizer: SpeechSynthesizer | None = None,
    capture: AudioCapture | None = None,
) -> VoiceService:
    """Create a fully deterministic test voice service."""

    event_bus = EventBus()

    permission = MicrophonePermissionState()
    permission.grant()

    return VoiceService(
        event_bus=event_bus,
        capture=capture or FakeCapture(),
        recognizer=FakeRecognizer(
            transcript
        ),
        synthesizer=synthesizer,
        permission=permission,
        source="test",
        auto_speak_responses=True,
        default_capture_seconds=1.0,
    )


def test_wake_word_profile_normalizes_phrase():
    profile = WakeWordProfile(
        user_id="ayush",
        phrase="  Hello, Nova!  ",
    )

    assert profile.phrase == "hello nova"


def test_wake_word_detector_extracts_command():
    detector = WakeWordDetector(
        WakeWordProfile(
            "ayush",
            "hello nova",
        )
    )

    match = detector.detect(
        "Hello Nova, open calendar"
    )

    assert match is not None
    assert match.command == "open calendar"


def test_runtime_emits_wake_and_listening_expression():
    runtime = RuntimeEngine(
        WakeWordDetector(
            WakeWordProfile(
                "ayush",
                "hello nova",
            )
        )
    )

    wake_events = []
    expressions = []

    runtime.event_bus.subscribe(
        EventType.WAKE_WORD,
        wake_events.append,
    )

    runtime.event_bus.subscribe(
        EventType.AVATAR_EXPRESSION,
        expressions.append,
    )

    runtime.event_bus.publish(
        Event(
            type=EventType.VOICE_INPUT,
            payload={
                "text": (
                    "hello nova "
                    "what time is it"
                )
            },
            source="android",
        )
    )

    assert wake_events[0].payload["user_id"] == "ayush"

    assert (
        wake_events[0].payload["command"]
        == "what time is it"
    )

    assert (
        expressions[0].payload["state"]
        == "listening"
    )


def test_voice_service_starts_in_idle():
    service = create_voice_service()

    assert service.state == VoiceSessionState.IDLE
    assert service.is_running is False


def test_voice_service_start_sets_running():
    service = create_voice_service()

    service.start()

    assert service.is_running is True
    assert service.state == VoiceSessionState.IDLE


def test_voice_service_stop_returns_to_idle():
    service = create_voice_service()

    service.start()
    service.stop()

    assert service.is_running is False
    assert service.state == VoiceSessionState.IDLE


def test_voice_service_emits_session_states():
    service = create_voice_service()

    states = []

    service.event_bus.subscribe(
        EventType.VOICE_STATE,
        states.append,
    )

    service.start()

    service.listen_once()

    state_values = [
        event.payload["state"]
        for event in states
    ]

    assert (
        VoiceSessionState.ACTIVATING.value
        in state_values
    )

    assert (
        VoiceSessionState.LISTENING.value
        in state_values
    )

    assert (
        VoiceSessionState.TRANSCRIBING.value
        in state_values
    )

    assert (
        VoiceSessionState.THINKING.value
        in state_values
    )


def test_voice_service_listen_once_publishes_voice_input():
    service = create_voice_service()

    inputs = []

    service.event_bus.subscribe(
        EventType.VOICE_INPUT,
        inputs.append,
    )

    service.start()

    transcript = service.listen_once()

    assert transcript is not None
    assert transcript.text == (
        "hello nova open calendar"
    )

    assert len(inputs) == 1

    assert (
        inputs[0].payload["text"]
        == "hello nova open calendar"
    )

    assert (
        inputs[0].payload["language"]
        == "en-US"
    )

    assert (
        inputs[0].payload["confidence"]
        == 0.95
    )


def test_voice_service_returns_to_idle_for_empty_transcript():
    service = create_voice_service(
        transcript=""
    )

    service.start()

    transcript = service.listen_once()

    assert transcript is not None
    assert transcript.text == ""

    assert (
        service.state
        == VoiceSessionState.IDLE
    )


def test_voice_service_speaks_response():
    synthesizer = FakeSynthesizer()

    service = create_voice_service(
        synthesizer=synthesizer
    )

    states = []

    service.event_bus.subscribe(
        EventType.VOICE_STATE,
        states.append,
    )

    service.start()

    result = service.speak(
        "Hello, Ayush."
    )

    assert result is True

    assert synthesizer.spoken == [
        "Hello, Ayush."
    ]

    state_values = [
        event.payload["state"]
        for event in states
    ]

    assert (
        VoiceSessionState.SPEAKING.value
        in state_values
    )

    assert (
        service.state
        == VoiceSessionState.IDLE
    )


def test_voice_service_handles_brain_response():
    synthesizer = FakeSynthesizer()

    service = create_voice_service(
        synthesizer=synthesizer
    )

    service.start()

    service.event_bus.publish(
        Event(
            type=EventType.BRAIN_RESPONSE,
            payload={
                "response": "The time is 10 AM."
            },
            source="brain",
        )
    )

    assert synthesizer.spoken == [
        "The time is 10 AM."
    ]

    assert (
        service.state
        == VoiceSessionState.IDLE
    )


def test_voice_service_microphone_error_recovers_to_idle():
    service = create_voice_service(
        capture=FailingCapture()
    )

    errors = []
    states = []

    service.event_bus.subscribe(
        EventType.VOICE_ERROR,
        errors.append,
    )

    service.event_bus.subscribe(
        EventType.VOICE_STATE,
        states.append,
    )

    service.start()

    result = service.listen_once()

    assert result is None

    assert len(errors) == 1

    assert (
        "Microphone failure"
        in errors[0].payload["message"]
    )

    state_values = [
        event.payload["state"]
        for event in states
    ]

    assert (
        VoiceSessionState.ERROR.value
        in state_values
    )

    assert (
        service.state
        == VoiceSessionState.IDLE
    )


def test_voice_service_tts_error_recovers_to_idle():
    service = create_voice_service(
        synthesizer=FailingSynthesizer()
    )

    errors = []

    service.event_bus.subscribe(
        EventType.VOICE_ERROR,
        errors.append,
    )

    service.start()

    result = service.speak(
        "This will fail."
    )

    assert result is False

    assert len(errors) == 1

    assert (
        "TTS failure"
        in errors[0].payload["message"]
    )

    assert (
        service.state
        == VoiceSessionState.IDLE
    )


def test_voice_service_requires_running_state():
    service = create_voice_service()

    try:
        service.listen_once()
    except Exception as exc:
        assert (
            "not running"
            in str(exc).lower()
        )
    else:
        raise AssertionError(
            "listen_once() should fail "
            "when the service is not running."
        )


def test_voice_service_publishes_listening_lifecycle():
    service = create_voice_service()

    listening_events = []

    service.event_bus.subscribe(
        EventType.VOICE_LISTENING,
        listening_events.append,
    )

    service.start()
    service.listen_once()

    values = [
        event.payload["active"]
        for event in listening_events
    ]

    assert values == [
        True,
        False,
    ]


def test_voice_service_avatar_follows_voice_state():
    service = create_voice_service()

    expressions = []

    service.event_bus.subscribe(
        EventType.AVATAR_EXPRESSION,
        expressions.append,
    )

    service.start()
    service.listen_once()

    states = [
        event.payload["state"]
        for event in expressions
    ]

    assert "listening" in states
    assert "thinking" in states


def test_voice_service_rejects_invalid_capture_duration():
    service = create_voice_service()

    service.start()

    try:
        service.listen_once(
            duration_seconds=0
        )
    except ValueError as exc:
        assert (
            "duration"
            in str(exc).lower()
        )
    else:
        raise AssertionError(
            "Invalid capture duration "
            "should raise ValueError."
        )