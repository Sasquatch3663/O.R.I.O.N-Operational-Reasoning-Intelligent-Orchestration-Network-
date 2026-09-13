from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict


class IntentType(str, Enum):
    UNKNOWN = "unknown"
    INFORMATION = "information"
    COMMAND = "command"
    QUESTION = "question"
    CONVERSATION = "conversation"
    TOOL_REQUEST = "tool_request"
    MEMORY_REQUEST = "memory_request"


@dataclass
class Intent:
    """Represents the interpreted intent of a request."""

    type: IntentType
    confidence: float
    parameters: Dict[str, Any]

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Intent confidence must be between 0 and 1."
            )

        if not isinstance(self.parameters, dict):
            raise TypeError(
                "Intent parameters must be a dictionary."
            )


class IntentAnalyzer:
    """
    Initial rule-based intent analyzer.

    This is intentionally provider-independent.
    A model-based analyzer can replace or extend it later.
    """

    def analyze(self, text: str) -> Intent:
        normalized = text.strip().lower()

        if not normalized:
            return Intent(
                type=IntentType.UNKNOWN,
                confidence=0.0,
                parameters={},
            )

        if normalized.endswith("?") or normalized.startswith(
            (
                "what ",
                "when ",
                "where ",
                "who ",
                "why ",
                "how ",
                "can ",
                "could ",
                "would ",
                "do ",
                "does ",
                "is ",
                "are ",
                "will ",
            )
        ):
            return Intent(
                type=IntentType.QUESTION,
                confidence=0.8,
                parameters={},
            )

        if normalized.startswith(
            ("remember ", "remember that ")
        ):
            return Intent(
                type=IntentType.MEMORY_REQUEST,
                confidence=0.9,
                parameters={
                    "text": text,
                },
            )

        if normalized.startswith(
            (
                "calculate ",
                "open ",
                "run ",
                "search ",
            )
        ):
            return Intent(
                type=IntentType.TOOL_REQUEST,
                confidence=0.7,
                parameters={
                    "text": text,
                },
            )

        return Intent(
            type=IntentType.CONVERSATION,
            confidence=0.5,
            parameters={},
        )
