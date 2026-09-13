from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class VoiceError(Exception):
    """Raised when a voice component cannot complete its operation."""


class VoicePermissionError(VoiceError):
    """Raised when microphone use is attempted without permission."""


class MicrophonePermission(str, Enum):
    """Application-level microphone permission state."""

    UNKNOWN = "unknown"
    GRANTED = "granted"
    DENIED = "denied"


@dataclass
class MicrophonePermissionState:
    """Application-level record of microphone permission state."""

    status: MicrophonePermission = MicrophonePermission.UNKNOWN

    @property
    def can_record(self) -> bool:
        """Return True only when microphone recording is permitted."""
        return self.status == MicrophonePermission.GRANTED

    @property
    def is_denied(self) -> bool:
        """Return True when microphone access has been explicitly denied."""
        return self.status == MicrophonePermission.DENIED

    @property
    def is_unknown(self) -> bool:
        """Return True when permission has not been established."""
        return self.status == MicrophonePermission.UNKNOWN

    def grant(self) -> None:
        """Mark microphone permission as granted."""
        self.status = MicrophonePermission.GRANTED

    def deny(self) -> None:
        """Mark microphone permission as denied."""
        self.status = MicrophonePermission.DENIED

    def reset(self) -> None:
        """Return permission state to unknown."""
        self.status = MicrophonePermission.UNKNOWN

    def require_recording_permission(self) -> None:
        """
        Require microphone permission before recording.

        Both UNKNOWN and DENIED are rejected because the application
        must never assume that microphone access is available.
        """

        if self.status == MicrophonePermission.GRANTED:
            return

        if self.status == MicrophonePermission.DENIED:
            raise VoicePermissionError(
                "Microphone permission has been denied."
            )

        raise VoicePermissionError(
            "Microphone permission has not been granted."
        )


class VoiceSessionState(str, Enum):
    """
    High-level state of an ORION voice interaction.

    The state machine is platform-independent so Windows and
    Android clients can use the same states to drive their
    respective pet animations.
    """

    IDLE = "idle"
    ACTIVATING = "activating"
    LISTENING = "listening"
    TRANSCRIBING = "transcribing"
    THINKING = "thinking"
    SPEAKING = "speaking"
    ERROR = "error"


@dataclass(frozen=True)
class AudioFormat:
    """PCM audio format shared by capture and recognition providers."""

    sample_rate: int = 16000
    channels: int = 1
    sample_width_bytes: int = 2

    def __post_init__(self) -> None:
        if self.sample_rate <= 0:
            raise ValueError(
                "Audio sample rate must be positive."
            )

        if self.channels <= 0:
            raise ValueError(
                "Audio channel count must be positive."
            )

        if self.sample_width_bytes <= 0:
            raise ValueError(
                "Audio sample width must be positive."
            )


@dataclass(frozen=True)
class AudioChunk:
    """A short, captured block of raw PCM audio."""

    data: bytes
    format: AudioFormat

    def __post_init__(self) -> None:
        if not self.data:
            raise ValueError(
                "Audio chunk cannot be empty."
            )


@dataclass(frozen=True)
class VoiceTranscript:
    """Final speech-recognition output before wake-word processing."""

    text: str
    language: str = "en-US"
    confidence: Optional[float] = None

    def __post_init__(self) -> None:
        if (
            self.confidence is not None
            and not 0.0 <= self.confidence <= 1.0
        ):
            raise ValueError(
                "Transcript confidence must be between 0 and 1."
            )


class AudioCapture(ABC):
    """Captures a bounded audio segment from a platform microphone."""

    @abstractmethod
    def capture(
        self,
        duration_seconds: float,
    ) -> AudioChunk:
        """Capture and return one PCM audio segment."""


class SpeechRecognizer(ABC):
    """Converts PCM audio into a final transcript."""

    @abstractmethod
    def transcribe(
        self,
        audio: AudioChunk,
    ) -> VoiceTranscript:
        """Transcribe one captured audio segment."""


class SpeechSynthesizer(ABC):
    """Speaks plain text through a platform output provider."""

    @abstractmethod
    def speak(
        self,
        text: str,
    ) -> None:
        """Speak a non-empty response."""