from __future__ import annotations

from typing import Dict, List

from orion.tools.base import BaseTool, ToolError


class ToolRegistry:
    """
    Registry for discovering and managing ORION tools.
    """

    def __init__(self) -> None:
        self._tools: Dict[str, BaseTool] = {}

    def register(
        self,
        tool: BaseTool,
    ) -> None:
        if not isinstance(tool, BaseTool):
            raise TypeError(
                "Only BaseTool instances can be registered."
            )

        if tool.name in self._tools:
            raise ToolError(
                f"Tool already registered: {tool.name}"
            )

        self._tools[tool.name] = tool

    def unregister(
        self,
        name: str,
    ) -> None:
        self._tools.pop(name, None)

    def get(
        self,
        name: str,
    ) -> BaseTool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolError(
                f"Tool not found: {name}"
            ) from exc

    def has(
        self,
        name: str,
    ) -> bool:
        return name in self._tools

    def names(self) -> List[str]:
        return list(self._tools.keys())

    def count(self) -> int:
        return len(self._tools)

    def clear(self) -> None:
        self._tools.clear()