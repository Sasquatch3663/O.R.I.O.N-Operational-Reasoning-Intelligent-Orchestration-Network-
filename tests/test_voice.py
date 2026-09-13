from __future__ import annotations

from time import monotonic, sleep

from orion.core.engine import RuntimeEngine
from orion.core.events import Event, EventBus, EventType
from orion.voice import (
    AudioCapture,
    AudioChunk,
    AudioFormat,
    MicrophonePermissionState,
    SpeechRecognizer,
    SpeechSynthesizer,
    VoiceRuntime,
    VoiceService,
    VoiceSessionState,
    VoiceTranscript,
    WakeWordDetector,
    WakeWordProfile,
)
from orion.voice.service import VoiceService

# ============================================================
# TEST DOUBLES
# ============================================================


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
        self.spoken: list[str] = []

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


# ============================================================
# VOICE SERVICE TEST HELPERS
# ============================================================


def create_voice_service(
    *,
    transcript: str = "hello nova open calendar",
    synthesizer: SpeechSynthesizer | None = None,
    capture: AudioCapture | None = None,
) -> VoiceService:
    """
    Create a fully deterministic VoiceService for tests.
    """

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
        default_capture_seconds=0.01,
    )


# ============================================================
# WAKE WORD TESTS
# ============================================================


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


def test_wake_word_detector_ignores_non_matching_transcript():
    detector = WakeWordDetector(
        WakeWordProfile(
            "ayush",
            "hello nova",
        )
    )

    match = detector.detect(
        "good morning"
    )

    assert match is None


def test_wake_word_detector_accepts_exact_phrase():
    detector = WakeWordDetector(
        WakeWordProfile(
            "ayush",
            "hello nova",
        )
    )

    match = detector.detect(
        "hello nova"
    )

    assert match is not None
    assert match.command == ""


# ============================================================
# RUNTIME ENGINE + WAKE WORD TESTS
# ============================================================


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

    assert len(wake_events) == 1

    assert (
        wake_events[0].payload["user_id"]
        == "ayush"
    )

    assert (
        wake_events[0].payload["command"]
        == "what time is it"
    )

    assert len(expressions) >= 1

    assert (
        expressions[0].payload["state"]
        == "listening"
    )


def test_runtime_ignores_voice_input_without_wake_word():
    runtime = RuntimeEngine(
        WakeWordDetector(
            WakeWordProfile(
                "ayush",
                "hello nova",
            )
        )
    )

    wake_events = []
    user_inputs = []

    runtime.event_bus.subscribe(
        EventType.WAKE_WORD,
        wake_events.append,
    )

    runtime.event_bus.subscribe(
        EventType.USER_INPUT,
        user_inputs.append,
    )

    runtime.event_bus.publish(
        Event(
            type=EventType.VOICE_INPUT,
            payload={
                "text": "open calendar"
            },
            source="voice",
        )
    )

    assert wake_events == []
    assert user_inputs == []


def test_runtime_publishes_user_input_after_wake_word():
    runtime = RuntimeEngine(
        WakeWordDetector(
            WakeWordProfile(
                "ayush",
                "hello nova",
            )
        )
    )

    user_inputs = []

    runtime.event_bus.subscribe(
        EventType.USER_INPUT,
        user_inputs.append,
    )

    runtime.event_bus.publish(
        Event(
            type=EventType.VOICE_INPUT,
            payload={
                "text": (
                    "hello nova "
                    "open calendar"
                )
            },
            source="voice",
        )
    )

    assert len(user_inputs) == 1

    assert (
        user_inputs[0].payload["text"]
        == "open calendar"
    )


# ============================================================
# VOICE SERVICE LIFECYCLE TESTS
# ============================================================


def test_voice_service_starts_in_idle():
    service = create_voice_service()

    assert (
        service.state
        == VoiceSessionState.IDLE
    )

    assert service.is_running is False


def test_voice_service_start_sets_running():
    service = create_voice_service()

    service.start()

    assert service.is_running is True

    assert (
        service.state
        == VoiceSessionState.IDLE
    )


def test_voice_service_start_is_idempotent():
    service = create_voice_service()

    service.start()
    service.start()

    assert service.is_running is True

    assert (
        service.state
        == VoiceSessionState.IDLE
    )


def test_voice_service_stop_returns_to_idle():
    service = create_voice_service()

    service.start()
    service.stop()

    assert service.is_running is False

    assert (
        service.state
        == VoiceSessionState.IDLE
    )


def test_voice_service_stop_is_idempotent():
    service = create_voice_service()

    service.stop()
    service.stop()

    assert service.is_running is False

    assert (
        service.state
        == VoiceSessionState.IDLE
    )


# ============================================================
# VOICE SERVICE STATE MACHINE TESTS
# ============================================================


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


def test_voice_service_state_events_include_reason():
    service = create_voice_service()

    states = []

    service.event_bus.subscribe(
        EventType.VOICE_STATE,
        states.append,
    )

    service.start()
    service.listen_once()

    assert len(states) > 0

    for event in states:
        assert (
            "previous_state"
            in event.payload
        )

        assert (
            "state"
            in event.payload
        )

        assert (
            "reason"
            in event.payload
        )


def test_voice_service_returns_to_idle_after_empty_transcript():
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


def test_voice_service_returns_to_idle_when_no_wake_word_is_detected():
    """
    A transcript by itself should not leave the voice service
    permanently stuck in THINKING.

    RuntimeEngine is responsible for deciding whether the
    wake word exists.
    """

    service = create_voice_service(
        transcript="open calendar"
    )

    service.start()

    transcript = service.listen_once()

    assert transcript is not None

    assert transcript.text == (
        "open calendar"
    )

    assert (
        service.state
        == VoiceSessionState.IDLE
    )


# ============================================================
# VOICE INPUT TESTS
# ============================================================


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


def test_voice_service_calls_capture():
    capture = FakeCapture()

    service = create_voice_service(
        capture=capture
    )

    service.start()
    service.listen_once()

    assert capture.calls == 1


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


def test_voice_service_rejects_negative_capture_duration():
    service = create_voice_service()

    service.start()

    try:
        service.listen_once(
            duration_seconds=-1
        )

    except ValueError as exc:
        assert (
            "duration"
            in str(exc).lower()
        )

    else:
        raise AssertionError(
            "Negative capture duration "
            "should raise ValueError."
        )


# ============================================================
# LISTENING EVENT TESTS
# ============================================================


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


# ============================================================
# AVATAR TESTS
# ============================================================


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


def test_voice_service_publishes_thinking_avatar_after_wake_word():
    service = create_voice_service()

    expressions = []

    service.event_bus.subscribe(
        EventType.AVATAR_EXPRESSION,
        expressions.append,
    )

    service.start()

    service.event_bus.publish(
        Event(
            type=EventType.WAKE_WORD,
            payload={
                "user_id": "ayush",
                "phrase": "hello nova",
                "command": "open calendar",
            },
            source="voice",
        )
    )

    states = [
        event.payload["state"]
        for event in expressions
    ]

    assert "thinking" in states


# ============================================================
# TTS TESTS
# ============================================================


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


def test_voice_service_returns_false_without_synthesizer():
    service = create_voice_service()

    service.start()

    result = service.speak(
        "Hello."
    )

    assert result is False

    assert (
        service.state
        == VoiceSessionState.IDLE
    )


def test_voice_service_returns_false_for_empty_speech():
    synthesizer = FakeSynthesizer()

    service = create_voice_service(
        synthesizer=synthesizer
    )

    service.start()

    result = service.speak(
        "   "
    )

    assert result is False

    assert synthesizer.spoken == []

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
                "response": (
                    "The time is 10 AM."
                )
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


def test_voice_service_ignores_invalid_brain_response():
    synthesizer = FakeSynthesizer()

    service = create_voice_service(
        synthesizer=synthesizer
    )

    service.start()

    service.event_bus.publish(
        Event(
            type=EventType.BRAIN_RESPONSE,
            payload={
                "response": None
            },
            source="brain",
        )
    )

    assert synthesizer.spoken == []


def test_voice_service_publishes_speaking_lifecycle():
    synthesizer = FakeSynthesizer()

    service = create_voice_service(
        synthesizer=synthesizer
    )

    speaking_events = []

    service.event_bus.subscribe(
        EventType.VOICE_SPEAKING,
        speaking_events.append,
    )

    service.start()

    service.speak(
        "Hello."
    )

    assert len(speaking_events) == 2

    assert (
        speaking_events[0].payload["active"]
        is True
    )

    assert (
        speaking_events[1].payload["active"]
        is False
    )


# ============================================================
# ERROR HANDLING TESTS
# ============================================================


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


# ============================================================
# VOICE RUNTIME TEST DOUBLES
# ============================================================


class RuntimeTestCapture(AudioCapture):
    """
    Fast fake microphone.

    Each capture increments the counter so the background
    runtime can be verified without a real microphone.
    """

    def __init__(self) -> None:
        self.calls = 0

    def capture(
        self,
        duration_seconds: float,
    ) -> AudioChunk:
        self.calls += 1

        return AudioChunk(
            data=b"runtime-audio",
            format=AudioFormat(),
        )


class RuntimeTestRecognizer(SpeechRecognizer):
    """Fast recognizer for VoiceRuntime tests."""

    def __init__(
        self,
        transcript: str = "",
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
            confidence=0.9,
        )


class RuntimeFailingCapture(AudioCapture):
    """Fake capture device that always fails."""

    def __init__(self) -> None:
        self.calls = 0

    def capture(
        self,
        duration_seconds: float,
    ) -> AudioChunk:
        self.calls += 1

        raise RuntimeError(
            "Runtime microphone failure"
        )


# ============================================================
# VOICE RUNTIME TEST HELPER
# ============================================================


def create_runtime_test_service(
    *,
    transcript: str = "",
    capture: AudioCapture | None = None,
):
    """
    Create a VoiceRuntime with fast deterministic components.
    """

    event_bus = EventBus()

    permission = MicrophonePermissionState()
    permission.grant()

    actual_capture = (
        capture
        if capture is not None
        else RuntimeTestCapture()
    )

    service = VoiceService(
        event_bus=event_bus,
        capture=actual_capture,
        recognizer=RuntimeTestRecognizer(
            transcript=transcript
        ),
        synthesizer=None,
        permission=permission,
        source="test-runtime",
        auto_speak_responses=False,
        default_capture_seconds=0.01,
    )

    runtime = VoiceRuntime(
        service=service,
        event_bus=event_bus,
        capture_interval_seconds=0.01,
        error_retry_delay_seconds=0.01,
        join_timeout_seconds=1.0,
    )

    return runtime, actual_capture, service


# ============================================================
# VOICE RUNTIME LIFECYCLE TESTS
# ============================================================


def test_voice_runtime_starts_background_worker():
    runtime, capture, service = (
        create_runtime_test_service()
    )

    runtime.start()

    deadline = monotonic() + 1.0

    while (
        capture.calls == 0
        and monotonic() < deadline
    ):
        sleep(0.01)

    assert runtime.is_running is True

    assert runtime.thread is not None

    assert (
        service.is_running
        is True
    )

    runtime.stop()

    assert runtime.is_running is False

    assert runtime.thread is None

    assert (
        service.is_running
        is False
    )


def test_voice_runtime_continuously_captures():
    runtime, capture, service = (
        create_runtime_test_service()
    )

    runtime.start()

    deadline = monotonic() + 1.0

    while (
        capture.calls < 2
        and monotonic() < deadline
    ):
        sleep(0.01)

    runtime.stop()

    assert capture.calls >= 2

    assert (
        service.is_running
        is False
    )


def test_voice_runtime_continuously_processes_audio():
    runtime, capture, service = (
        create_runtime_test_service()
    )

    runtime.start()

    deadline = monotonic() + 1.0

    while (
        capture.calls < 3
        and monotonic() < deadline
    ):
        sleep(0.01)

    runtime.stop()

    assert capture.calls >= 3


def test_voice_runtime_start_is_idempotent():
    runtime, _, _ = (
        create_runtime_test_service()
    )

    runtime.start()

    first_thread = runtime.thread

    runtime.start()

    second_thread = runtime.thread

    assert first_thread is second_thread

    runtime.stop()


def test_voice_runtime_stop_is_idempotent():
    runtime, _, _ = (
        create_runtime_test_service()
    )

    runtime.start()

    runtime.stop()
    runtime.stop()

    assert runtime.is_running is False

    assert runtime.thread is None


def test_voice_runtime_can_restart_after_stop():
    runtime, capture, service = (
        create_runtime_test_service()
    )

    runtime.start()

    deadline = monotonic() + 1.0

    while (
        capture.calls < 1
        and monotonic() < deadline
    ):
        sleep(0.01)

    runtime.stop()

    first_calls = capture.calls

    runtime.start()

    deadline = monotonic() + 1.0

    while (
        capture.calls <= first_calls
        and monotonic() < deadline
    ):
        sleep(0.01)

    runtime.stop()

    assert capture.calls > first_calls

    assert (
        service.is_running
        is False
    )


# ============================================================
# VOICE RUNTIME EVENT TESTS
# ============================================================


def test_voice_runtime_publishes_start_event():
    runtime, _, _ = (
        create_runtime_test_service()
    )

    events = []

    runtime.event_bus.subscribe(
        EventType.SYSTEM_EVENT,
        events.append,
    )

    runtime.start()

    deadline = monotonic() + 1.0

    while (
        not events
        and monotonic() < deadline
    ):
        sleep(0.01)

    runtime.stop()

    runtime_events = [
        event
        for event in events
        if event.payload.get(
            "component"
        ) == "voice_runtime"
    ]

    assert any(
        event.payload.get("event")
        == "started"
        for event in runtime_events
    )


def test_voice_runtime_publishes_stop_event():
    runtime, _, _ = (
        create_runtime_test_service()
    )

    events = []

    runtime.event_bus.subscribe(
        EventType.SYSTEM_EVENT,
        events.append,
    )

    runtime.start()
    runtime.stop()

    runtime_events = [
        event
        for event in events
        if event.payload.get(
            "component"
        ) == "voice_runtime"
    ]

    assert any(
        event.payload.get("event")
        == "stopped"
        for event in runtime_events
    )


def test_voice_runtime_publishes_start_and_stop_events():
    runtime, _, _ = (
        create_runtime_test_service()
    )

    events = []

    runtime.event_bus.subscribe(
        EventType.SYSTEM_EVENT,
        events.append,
    )

    runtime.start()

    deadline = monotonic() + 1.0

    while (
        not any(
            event.payload.get("event")
            == "started"
            for event in events
        )
        and monotonic() < deadline
    ):
        sleep(0.01)

    runtime.stop()

    runtime_events = [
        event.payload["event"]
        for event in events
        if event.payload.get(
            "component"
        ) == "voice_runtime"
    ]

    assert "started" in runtime_events
    assert "stopped" in runtime_events


# ============================================================
# VOICE RUNTIME ERROR RECOVERY TESTS
# ============================================================


def test_voice_runtime_survives_capture_errors():
    capture = RuntimeFailingCapture()

    runtime, _, service = (
        create_runtime_test_service(
            capture=capture
        )
    )

    errors = []

    runtime.event_bus.subscribe(
        EventType.VOICE_ERROR,
        errors.append,
    )

    runtime.start()

    deadline = monotonic() + 1.0

    while (
        len(errors) == 0
        and monotonic() < deadline
    ):
        sleep(0.01)

    runtime.stop()

    assert capture.calls >= 1

    assert len(errors) >= 1

    assert runtime.is_running is False

    assert (
        service.is_running
        is False
    )


# ============================================================
# NON-BLOCKING TESTS
# ============================================================


def test_voice_runtime_start_does_not_block_application():
    runtime, capture, _ = (
        create_runtime_test_service()
    )

    start = monotonic()

    runtime.start()

    elapsed = monotonic() - start

    runtime.stop()

    assert elapsed < 0.5

    assert capture.calls >= 0


def test_voice_runtime_stop_is_bounded():
    runtime, _, _ = (
        create_runtime_test_service()
    )

    runtime.start()

    start = monotonic()

    runtime.stop()

    elapsed = monotonic() - start

    assert elapsed < 2.0


# ============================================================
# VALIDATION TESTS
# ============================================================


def test_voice_runtime_rejects_negative_capture_interval():
    runtime, _, _ = (
        create_runtime_test_service()
    )

    try:
        VoiceRuntime(
            service=runtime.service,
            event_bus=runtime.event_bus,
            capture_interval_seconds=-1.0,
        )

    except ValueError as exc:
        assert (
            "interval"
            in str(exc).lower()
        )

    else:
        raise AssertionError(
            "Negative capture interval "
            "should raise ValueError."
        )


def test_voice_runtime_rejects_negative_retry_delay():
    runtime, _, _ = (
        create_runtime_test_service()
    )

    try:
        VoiceRuntime(
            service=runtime.service,
            event_bus=runtime.event_bus,
            error_retry_delay_seconds=-1.0,
        )

    except ValueError as exc:
        assert (
            "retry"
            in str(exc).lower()
        )

    else:
        raise AssertionError(
            "Negative retry delay "
            "should raise ValueError."
        )


def test_voice_runtime_rejects_invalid_join_timeout():
    runtime, _, _ = (
        create_runtime_test_service()
    )

    try:
        VoiceRuntime(
            service=runtime.service,
            event_bus=runtime.event_bus,
            join_timeout_seconds=0,
        )

    except ValueError as exc:
        assert (
            "join timeout"
            in str(exc).lower()
        )

    else:
        raise AssertionError(
            "Invalid join timeout "
            "should raise ValueError."
        )

class FakeAudioCapture:
    def __init__(self):
        self.calls = 0

    def capture(self, duration_seconds):
        self.calls += 1
        return AudioChunk(
            data=b"\x00\x00",
            format=AudioFormat(),
        )


class FakeSpeechRecognizer:
    def transcribe(self, audio):
        return VoiceTranscript(text="hello orion")

def test_unknown_microphone_permission_is_rejected():
    event_bus = EventBus()

    capture = FakeAudioCapture()
    recognizer = FakeSpeechRecognizer()

    permission = MicrophonePermissionState()

    service = VoiceService(
        event_bus=event_bus,
        capture=capture,
        recognizer=recognizer,
        permission=permission,
    )

    errors = []

    event_bus.subscribe(
        EventType.VOICE_ERROR,
        errors.append,
    )

    service.start()

    result = service.listen_once()

    assert result is None
    assert service.state == VoiceSessionState.IDLE
    assert len(errors) == 1
    assert (
        "not been granted"
        in errors[0].payload["message"]
    )
    assert capture.calls == 0

def test_denied_microphone_permission_is_rejected():
    event_bus = EventBus()

    capture = FakeAudioCapture()
    recognizer = FakeSpeechRecognizer()

    permission = MicrophonePermissionState()
    permission.deny()

    service = VoiceService(
        event_bus=event_bus,
        capture=capture,
        recognizer=recognizer,
        permission=permission,
    )

    errors = []

    event_bus.subscribe(
        EventType.VOICE_ERROR,
        errors.append,
    )

    service.start()

    result = service.listen_once()

    assert result is None
    assert service.state == VoiceSessionState.IDLE
    assert len(errors) == 1
    assert (
        "denied"
        in errors[0].payload["message"]
    )
    assert capture.calls == 0

def test_permission_failure_does_not_publish_active_listening():
    event_bus = EventBus()

    capture = FakeAudioCapture()
    recognizer = FakeSpeechRecognizer()

    permission = MicrophonePermissionState()
    permission.deny()

    service = VoiceService(
        event_bus=event_bus,
        capture=capture,
        recognizer=recognizer,
        permission=permission,
    )

    listening_events = []

    event_bus.subscribe(
        EventType.VOICE_LISTENING,
        listening_events.append,
    )

    service.start()
    result = service.listen_once()

    assert result is None
    assert service.state == VoiceSessionState.IDLE
    assert all(
        event.payload["active"] is False
        for event in listening_events
    )
    assert capture.calls == 0