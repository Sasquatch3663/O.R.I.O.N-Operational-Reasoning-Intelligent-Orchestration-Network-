from orion.voice.wake_word import (
    WakeWordDetector,
    WakeWordMatch,
    WakeWordProfile,
)

from orion.voice.contracts import (
    AudioCapture,
    AudioChunk,
    AudioFormat,
    MicrophonePermission,
    MicrophonePermissionState,
    SpeechRecognizer,
    SpeechSynthesizer,
    VoiceError,
    VoicePermissionError,
    VoiceSessionState,
    VoiceTranscript,
)

from orion.voice.service import VoiceService

from orion.voice.windows import (
    SoundDeviceMicrophoneCapture,
    VoskSpeechRecognizer,
    WindowsSpeechSynthesizer,
)

from orion.voice.factory import (
    create_windows_voice_service,
)


__all__ = [
    "WakeWordDetector",
    "WakeWordMatch",
    "WakeWordProfile",
    "AudioCapture",
    "AudioChunk",
    "AudioFormat",
    "MicrophonePermission",
    "MicrophonePermissionState",
    "SpeechRecognizer",
    "SpeechSynthesizer",
    "VoiceError",
    "VoicePermissionError",
    "VoiceSessionState",
    "VoiceTranscript",
    "VoiceService",
    "SoundDeviceMicrophoneCapture",
    "VoskSpeechRecognizer",
    "WindowsSpeechSynthesizer",
    "create_windows_voice_service",
]