import pytest

from orion.core.engine import RuntimeEngine
from orion.core.events import Event, EventBus, EventType
from orion.interface.voice import VoiceInterface
from orion.voice import (
    AudioCapture,
    AudioChunk,
    AudioFormat,
    MicrophonePermissionState,
    SpeechRecognizer,
    SpeechSynthesizer,
    VoiceError,
    VoiceService,
    VoiceTranscript,
    WakeWordDetector,
    WakeWordProfile,
    WindowsSpeechSynthesizer,
    create_windows_voice_service,
)


class FakeCapture(AudioCapture):
    def __init__(self) -> None:
        self.durations = []

    def capture(self, duration_seconds: float) -> AudioChunk:
        self.durations.append(duration_seconds)
        return AudioChunk(b"audio", AudioFormat())


class FakeRecognizer(SpeechRecognizer):
    def __init__(self, text: str) -> None:
        self.text = text

    def transcribe(self, audio: AudioChunk) -> VoiceTranscript:
        return VoiceTranscript(self.text, confidence=0.8)


class FakeSynthesizer(SpeechSynthesizer):
    def __init__(self) -> None:
        self.messages = []

    def speak(self, text: str) -> None:
        self.messages.append(text)


class FailingSynthesizer(SpeechSynthesizer):
    def speak(self, text: str) -> None:
        raise VoiceError("Speaker is unavailable.")


def test_voice_service_routes_audio_through_wake_brain_and_speech():
    runtime = RuntimeEngine(
        wake_word_detector=WakeWordDetector(
            WakeWordProfile("ayush", "hello nova")
        )
    )
    permission = MicrophonePermissionState()
    capture = FakeCapture()
    speaker = FakeSynthesizer()
    service = VoiceService(
        event_bus=runtime.event_bus,
        capture=capture,
        recognizer=FakeRecognizer("hello nova what time is it"),
        synthesizer=speaker,
        permission=permission,
        default_capture_seconds=3,
    )
    voice_events = []
    expressions = []

    runtime.event_bus.subscribe(EventType.VOICE_INPUT, voice_events.append)
    runtime.event_bus.subscribe(
        EventType.AVATAR_EXPRESSION,
        expressions.append,
    )

    permission.grant()
    service.start()
    transcript = service.listen_once()

    assert transcript is not None
    assert capture.durations == [3]
    assert voice_events[0].payload["text"] == "hello nova what time is it"
    assert speaker.messages == [
        "I understand that you are asking a question."
    ]
    assert expressions[0].payload["state"] == "listening"
    assert expressions[-1].payload["state"] == "thinking"


def test_voice_service_denied_permission_reports_error_without_capture():
    bus = EventBus()
    capture = FakeCapture()
    service = VoiceService(
        event_bus=bus,
        capture=capture,
        recognizer=FakeRecognizer("hello nova"),
    )
    errors = []

    bus.subscribe(EventType.VOICE_ERROR, errors.append)
    service.start()

    assert service.listen_once() is None
    assert capture.durations == []
    assert "permission" in errors[0].payload["message"].lower()


def test_voice_service_does_not_publish_empty_transcript():
    bus = EventBus()
    permission = MicrophonePermissionState()
    service = VoiceService(
        event_bus=bus,
        capture=FakeCapture(),
        recognizer=FakeRecognizer(""),
        permission=permission,
    )
    inputs = []

    bus.subscribe(EventType.VOICE_INPUT, inputs.append)
    permission.grant()
    service.start()

    assert service.listen_once() is not None
    assert inputs == []


def test_voice_service_reports_speech_output_errors_and_stops_state():
    bus = EventBus()
    service = VoiceService(
        event_bus=bus,
        capture=FakeCapture(),
        recognizer=FakeRecognizer(""),
        synthesizer=FailingSynthesizer(),
    )
    states = []
    errors = []

    bus.subscribe(EventType.VOICE_SPEAKING, states.append)
    bus.subscribe(EventType.VOICE_ERROR, errors.append)

    assert service.speak("Hello") is False
    assert [event.payload["active"] for event in states] == [True, False]
    assert errors[0].payload["message"] == "Speaker is unavailable."


def test_voice_interface_uses_voice_service():
    bus = EventBus()
    permission = MicrophonePermissionState()
    service = VoiceService(
        event_bus=bus,
        capture=FakeCapture(),
        recognizer=FakeRecognizer("hello nova"),
        permission=permission,
    )
    interface = VoiceInterface(bus, service)

    permission.grant()
    interface.start()

    assert interface.receive() == "hello nova"

    interface.stop()
    assert interface.is_running is False


def test_windows_synthesizer_uses_encoded_text(monkeypatch):
    commands = []
    synthesizer = WindowsSpeechSynthesizer(
        runner=lambda *args, **kwargs: commands.append((args, kwargs))
    )

    monkeypatch.setattr("orion.voice.windows.sys.platform", "win32")
    synthesizer.speak("Hello; Remove-Item")

    script = commands[0][0][0][-1]
    assert "Hello; Remove-Item" not in script
    assert "FromBase64String" in script


def test_voice_factory_requires_vosk_model_path():
    with pytest.raises(VoiceError, match="Vosk model path"):
        create_windows_voice_service(EventBus(), "")
