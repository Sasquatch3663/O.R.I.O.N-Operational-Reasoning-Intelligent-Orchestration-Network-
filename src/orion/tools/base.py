from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class ToolError(Exception):
    """Raised when an ORION tool encounters an error."""


class ToolContext:
    """
    Context provided to a tool during execution.
    """

    def __init__(
        self,
        source: str = "unknown",
    ) -> None:
        self.source = source


class BaseTool(ABC):
    """
    Abstract base class for all ORION tools.
    """

    def __init__(
        self,
        name: str,
        description: str,
    ) -> None:
        if not name:
            raise ValueError(
                "Tool name cannot be empty."
            )

        if not description:
            raise ValueError(
                "Tool description cannot be empty."
            )

        self.name = name
        self.description = description

    @abstractmethod
    def execute(
        self,
        parameters: Dict[str, Any],
        context: ToolContext,
    ) -> Any:
        """
        Execute the tool.

        Args:
            parameters: Input parameters for the tool.
            context: Execution context.

        Returns:
            Tool execution result.
        """

    def metadata(self) -> Dict[str, Any]:
        """
        Return tool metadata.
        """

        return {
            "name": self.name,
            "description": self.description,
        }