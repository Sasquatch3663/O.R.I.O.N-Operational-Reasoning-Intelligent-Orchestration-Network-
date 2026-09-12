from __future__ import annotations

import re
from dataclasses import dataclass


def _normalize(text: str) -> str:
    return " ".join(re.findall(r"[\w']+", text.lower()))


@dataclass(frozen=True)
class WakeWordProfile:
    """A user-owned wake phrase configuration, independent of audio hardware."""

    user_id: str
    phrase: str
    enabled: bool = True

    def __post_init__(self) -> None:
        if not self.user_id.strip():
            raise ValueError("Wake-word user ID cannot be empty.")

        normalized = _normalize(self.phrase)

        if len(normalized.split()) < 2:
            raise ValueError(
                "Wake phrase must contain at least two words."
            )

        object.__setattr__(self, "phrase", normalized)


@dataclass(frozen=True)
class WakeWordMatch:
    """Result of matching a transcript against a user's wake phrase."""

    profile: WakeWordProfile
    transcript: str
    command: str


class WakeWordDetector:
    """Text-level wake-word matcher for platform-specific audio adapters."""

    def __init__(self, profile: WakeWordProfile) -> None:
        self.profile = profile

    def detect(self, transcript: str) -> WakeWordMatch | None:
        if not self.profile.enabled:
            return None

        normalized = _normalize(transcript)
        phrase = self.profile.phrase

        if not normalized.startswith(phrase):
            return None

        command = normalized[len(phrase):].strip()

        return WakeWordMatch(
            profile=self.profile,
            transcript=transcript,
            command=command,
        )
