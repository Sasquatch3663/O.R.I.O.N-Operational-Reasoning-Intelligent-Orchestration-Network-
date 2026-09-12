from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from orion.brain.input import UserInput
from orion.brain.intent import IntentAnalyzer
from orion.brain.planner import Plan, Planner
from orion.brain.reasoning import (
    ReasoningContext,
    ReasoningEngine,
    ReasoningResult,
)
from orion.core.events import Event, EventBus, EventType


@dataclass
class BrainResult:
    """Complete result of brain processing."""

    reasoning: ReasoningResult
    plan: Plan


class BrainEngine:
    """
    Coordinates ORION's core intelligence pipeline.
    """

    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self.intent_analyzer = IntentAnalyzer()
        self.reasoning_engine = ReasoningEngine()
        self.planner = Planner()
        self.event_bus = event_bus
        self.last_result: Optional[BrainResult] = None

        if self.event_bus is not None:
            self.event_bus.subscribe(
                EventType.USER_INPUT,
                self.handle_user_input,
            )

    def process(
        self,
        user_input: UserInput,
    ) -> BrainResult:

        intent = self.intent_analyzer.analyze(
            user_input.text
        )

        context = ReasoningContext(
            user_input=user_input,
            intent=intent,
        )

        reasoning = self.reasoning_engine.reason(
            context
        )

        plan = self.planner.create_plan(
            reasoning
        )

        result = BrainResult(
            reasoning=reasoning,
            plan=plan,
        )

        self.last_result = result

        return result

    def handle_user_input(
        self,
        event: Event,
    ) -> None:
        """Process a user-input event and publish the brain response."""

        text = event.payload.get("text")

        if not isinstance(text, str):
            raise TypeError(
                "USER_INPUT events must include text as a string."
            )

        result = self.process(
            UserInput(
                text=text,
                source=event.source or "unknown",
            )
        )

        if self.event_bus is None:
            return

        self.event_bus.publish(
            Event(
                type=EventType.BRAIN_RESPONSE,
                payload=self._response_payload(result),
                source="brain",
            )
        )

    @staticmethod
    def _response_payload(
        result: BrainResult,
    ) -> Dict[str, Any]:
        """Convert a brain result into an event-safe payload."""

        return {
            "response": result.reasoning.response,
            "actions": result.reasoning.actions,
            "confidence": result.reasoning.confidence,
            "plan": [
                {
                    "step_id": step.step_id,
                    "action": step.action,
                    "parameters": step.parameters,
                }
                for step in result.plan.steps
            ],
        }
