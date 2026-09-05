from __future__ import annotations

from abc import ABC, abstractmethod


class OutputInterface(ABC):
    """Abstract output destination."""

    @abstractmethod
    def send(self, message: str) -> None:
        """Send a message."""


class ConsoleOutput(OutputInterface):
    """Standard console output."""

    def send(self, message: str) -> None:
        print(message)