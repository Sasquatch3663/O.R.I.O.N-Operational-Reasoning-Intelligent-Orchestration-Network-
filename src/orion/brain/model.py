from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List


class ModelProviderError(Exception):
    """Raised when a model provider cannot complete a request."""


@dataclass
class ModelRequest:
    """Provider-neutral input for a model-backed brain response."""

    text: str
    intent: str
    memories: List[Any] = field(default_factory=list)
    available_tools: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.text:
            raise ValueError("Model request text cannot be empty.")

        if not self.intent:
            raise ValueError("Model request intent cannot be empty.")

    def prompt(self) -> str:
        """Build a simple, portable prompt for provider adapters."""

        return (
            "You are ORION, a helpful local assistant.\n"
            f"User request: {self.text}\n"
            f"Detected intent: {self.intent}\n"
            f"Available tools: {', '.join(self.available_tools) or 'none'}\n"
            "Respond clearly and concisely."
        )


@dataclass
class ModelResponse:
    """Provider-neutral model output."""

    text: str
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("Model response text cannot be empty.")

        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "Model response confidence must be between 0 and 1."
            )

        if not isinstance(self.metadata, dict):
            raise TypeError("Model response metadata must be a dictionary.")


class BaseModelProvider(ABC):
    """Abstract contract implemented by local or remote model adapters."""

    @abstractmethod
    def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate one response for a normalized model request."""
