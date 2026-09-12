from __future__ import annotations

from typing import Optional

from orion.brain.local_model import OllamaModelProvider
from orion.brain.model import BaseModelProvider


def create_model_provider(
    provider_name: str,
    model_name: str,
    endpoint: str,
    timeout_seconds: float = 120.0,
) -> Optional[BaseModelProvider]:
    """Create a configured provider, or deterministic mode when model is blank."""

    normalized_provider = provider_name.strip().lower()
    normalized_model = model_name.strip()

    if normalized_provider in {"", "none", "deterministic"}:
        return None

    if normalized_provider in {"local", "ollama"}:
        if not normalized_model:
            return None

        return OllamaModelProvider(
            model=normalized_model,
            endpoint=endpoint,
            timeout_seconds=timeout_seconds,
        )

    raise ValueError(
        f"Unsupported model provider: {provider_name}"
    )
