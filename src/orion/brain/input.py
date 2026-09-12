from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserInput:
    """Normalized user input."""

    text: str
    source: str = "unknown"

    def __post_init__(self) -> None:
        self.text = self.text.strip()

        if not self.text:
            raise ValueError(
                "User input cannot be empty."
            )

        if not self.source:
            self.source = "unknown"