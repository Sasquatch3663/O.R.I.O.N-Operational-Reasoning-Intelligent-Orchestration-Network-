from __future__ import annotations

import json
from typing import Any, Callable, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from orion.brain.model import (
    BaseModelProvider,
    ModelProviderError,
    ModelRequest,
    ModelResponse,
)


LocalModelTransport = Callable[[Dict[str, Any]], Dict[str, Any]]


class OllamaModelProvider(BaseModelProvider):
    """Adapter for an Ollama model running on the user's own device."""

    def __init__(
        self,
        model: str,
        endpoint: str = "http://127.0.0.1:11434/api/generate",
        timeout_seconds: float = 120.0,
        transport: Optional[LocalModelTransport] = None,
    ) -> None:
        if not model.strip():
            raise ValueError("Local model name cannot be empty.")

        if not endpoint.startswith(("http://", "https://")):
            raise ValueError("Local model endpoint must be an HTTP URL.")

        if timeout_seconds <= 0:
            raise ValueError("Local model timeout must be positive.")

        self.model = model.strip()
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds
        self._transport = transport

    def generate(self, request: ModelRequest) -> ModelResponse:
        payload = {
            "model": self.model,
            "prompt": request.prompt(),
            "stream": False,
        }

        response_data = self._request(payload)
        text = response_data.get("response")

        if not isinstance(text, str) or not text.strip():
            raise ModelProviderError(
                "Local model returned no response text."
            )

        return ModelResponse(
            text=text,
            metadata={
                "provider": "ollama",
                "model": response_data.get("model", self.model),
                "total_duration_ns": response_data.get(
                    "total_duration"
                ),
                "eval_count": response_data.get("eval_count"),
            },
        )

    def _request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if self._transport is not None:
            return self._transport(payload)

        request = Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, OSError) as exc:
            raise ModelProviderError(
                "Unable to reach the local model service."
            ) from exc
        except json.JSONDecodeError as exc:
            raise ModelProviderError(
                "Local model returned invalid JSON."
            ) from exc

        if not isinstance(data, dict):
            raise ModelProviderError(
                "Local model returned an invalid response payload."
            )

        return data
