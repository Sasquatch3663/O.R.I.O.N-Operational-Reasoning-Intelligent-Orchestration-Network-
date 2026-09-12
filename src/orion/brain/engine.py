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
from orion.memory import MemoryManager
from orion.security import (
    PermissionLevel,
    SecurityRequest,
    SecurityValidator,
)
from orion.tools import ToolRegistry


@dataclass
class BrainResult:
    """Complete result of brain processing."""

    reasoning: ReasoningResult
    plan: Plan
    context: ReasoningContext


class BrainEngine:
    """
    Coordinates ORION's core intelligence pipeline.
    """

    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        memory_manager: Optional[MemoryManager] = None,
        tool_registry: Optional[ToolRegistry] = None,
        security_validator: Optional[SecurityValidator] = None,
    ) -> None:
        self.intent_analyzer = IntentAnalyzer()
        self.reasoning_engine = ReasoningEngine()
        self.planner = Planner()
        self.event_bus = event_bus
        self.memory_manager = memory_manager
        self.tool_registry = tool_registry
        self.security_validator = security_validator
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
            memories=self._find_memories(user_input.text),
            metadata=self._context_metadata(),
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
            context=context,
        )

        self.last_result = result

        return result

    def validate_plan(
        self,
        plan: Plan,
        granted: Optional[PermissionLevel] = None,
    ) -> None:
        """Validate every planned action against the configured policy."""

        if self.security_validator is None:
            return

        for step in plan.steps:
            self.security_validator.validate(
                SecurityRequest(
                    action=step.action,
                    permission=step.permission,
                    parameters=step.parameters,
                ),
                granted=granted,
            )

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
            "memories_used": len(result.context.memories),
            "plan": [
                {
                    "step_id": step.step_id,
                    "action": step.action,
                    "parameters": step.parameters,
                    "permission": step.permission.name.lower(),
                    "requires_confirmation": (
                        step.requires_confirmation
                    ),
                }
                for step in result.plan.steps
            ],
        }

    def _find_memories(self, query: str) -> list[Any]:
        """Retrieve relevant memories when a memory provider is available."""

        if self.memory_manager is None:
            return []

        return self.memory_manager.search(query)

    def _context_metadata(self) -> Dict[str, Any]:
        """Expose available capabilities to reasoning without executing them."""

        if self.tool_registry is None:
            return {}

        return {"available_tools": self.tool_registry.names()}
