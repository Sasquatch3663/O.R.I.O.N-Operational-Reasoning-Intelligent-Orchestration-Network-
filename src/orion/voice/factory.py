from __future__ import annotations

from pathlib import Path

from orion.core.events import EventBus
from orion.voice.contracts import (
    AudioFormat,
    MicrophonePermissionState,
    VoiceError,
)
from orion.voice.service import VoiceService
from orion.voice.windows import (
    SoundDeviceMicrophoneCapture,
    VoskSpeechRecognizer,
    WindowsSpeechSynthesizer,
)


def create_windows_voice_service(
    event_bus: EventBus,
    model_path: str,
    sample_rate: int = 16000,
    default_capture_seconds: float = 5.0,
    auto_speak_responses: bool = True,
) -> VoiceService:
    """Create the optional Windows local-voice stack from configuration."""

    if not model_path.strip():
        raise VoiceError(
            "A local Vosk model path is required when voice is enabled."
        )

    audio_format = AudioFormat(sample_rate=sample_rate)

    return VoiceService(
        event_bus=event_bus,
        capture=SoundDeviceMicrophoneCapture(audio_format),
        recognizer=VoskSpeechRecognizer(Path(model_path)),
        synthesizer=WindowsSpeechSynthesizer(),
        permission=MicrophonePermissionState(),
        default_capture_seconds=default_capture_seconds,
        auto_speak_responses=auto_speak_responses,
    )
