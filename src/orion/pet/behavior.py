from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict

from orion.brain.intent import IntentType
from orion.brain.reasoning import ReasoningResult


class AvatarState(str, Enum):
    """High-level visual state for an ORION pet interface."""

    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    HAPPY = "happy"
    ALERT = "alert"


class AvatarGesture(str, Enum):
    """Platform-neutral gesture names implemented by each UI client."""

    IDLE_BOB = "idle_bob"
    WAVE = "wave"
    NOD = "nod"
    HEAD_TILT = "head_tilt"
    FOCUS = "focus"
    CELEBRATE = "celebrate"


@dataclass(frozen=True)
class AvatarExpression:
    """An event-safe expression request for the animated pet."""

    state: AvatarState
    gesture: AvatarGesture
    duration_ms: int = 1200

    def __post_init__(self) -> None:
        if self.duration_ms <= 0:
            raise ValueError("Avatar expression duration must be positive.")

    def to_payload(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "gesture": self.gesture.value,
            "duration_ms": self.duration_ms,
        }


class AvatarBehavior:
    """Maps brain outcomes to expressions without depending on a UI toolkit."""

    def for_wake_word(self) -> AvatarExpression:
        return AvatarExpression(
            state=AvatarState.LISTENING,
            gesture=AvatarGesture.HEAD_TILT,
        )

    def for_reasoning(
        self,
        intent: IntentType,
        result: ReasoningResult,
    ) -> AvatarExpression:
        if intent == IntentType.MEMORY_REQUEST:
            return AvatarExpression(
                state=AvatarState.HAPPY,
                gesture=AvatarGesture.NOD,
            )

        if intent == IntentType.TOOL_REQUEST:
            return AvatarExpression(
                state=AvatarState.THINKING,
                gesture=AvatarGesture.FOCUS,
            )

        if intent == IntentType.QUESTION:
            return AvatarExpression(
                state=AvatarState.THINKING,
                gesture=AvatarGesture.HEAD_TILT,
            )

        if result.confidence >= 0.5:
            return AvatarExpression(
                state=AvatarState.HAPPY,
                gesture=AvatarGesture.WAVE,
            )

        return AvatarExpression(
            state=AvatarState.IDLE,
            gesture=AvatarGesture.IDLE_BOB,
        )
