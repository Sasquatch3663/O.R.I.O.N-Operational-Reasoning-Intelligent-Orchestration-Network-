from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from orion.brain.intent import Intent
from orion.brain.input import UserInput


@dataclass
class ReasoningContext:
    """Context supplied to the reasoning engine."""

    user_input: UserInput
    intent: Intent

    memories: List[Any] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ReasoningResult:
    """Result produced by the reasoning engine."""

    response: str
    actions: List[Dict[str, Any]] = field(
        default_factory=list
    )

    confidence: float = 0.0


class ReasoningEngine:
    """
    Initial deterministic reasoning engine.

    Advanced model-based reasoning will be added later.
    """

    def reason(
        self,
        context: ReasoningContext,
    ) -> ReasoningResult:

        intent = context.intent

        if intent.type.value == "question":
            return ReasoningResult(
                response=(
                    "I understand that you are "
                    "asking a question."
                ),
                confidence=0.5,
            )

        if intent.type.value == "memory_request":
            return ReasoningResult(
                response=(
                    "I understand that you want "
                    "me to remember something."
                ),
                confidence=0.7,
            )

        if intent.type.value == "tool_request":
            return ReasoningResult(
                response=(
                    "I understand that you want "
                    "me to perform an action."
                ),
                actions=[
                    {
                        "type": "tool_request",
                        "parameters": intent.parameters,
                    }
                ],
                confidence=0.6,
            )

        return ReasoningResult(
            response=(
                "I understand your request."
            ),
            confidence=0.4,
        )