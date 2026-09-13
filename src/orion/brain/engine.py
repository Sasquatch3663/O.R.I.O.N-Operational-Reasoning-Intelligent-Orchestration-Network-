from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from orion.brain.input import UserInput
from orion.brain.intent import IntentAnalyzer
from orion.brain.model import (
    BaseModelProvider,
    ModelProviderError,
    ModelRequest,
    ModelResponse,
)
from orion.brain.planner import Plan, Planner
from orion.brain.reasoning import (
    ReasoningContext,
    ReasoningEngine,
    ReasoningResult,
)
from orion.core.events import Event, EventBus, EventType
from orion.memory import MemoryManager
from orion.pet.behavior import AvatarBehavior, AvatarExpression
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
    model_response: Optional[ModelResponse] = None
    model_error: Optional[str] = None
    avatar_expression: Optional[AvatarExpression] = None


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
        model_provider: Optional[BaseModelProvider] = None,
        avatar_behavior: Optional[AvatarBehavior] = None,
    ) -> None:
        self.intent_analyzer = IntentAnalyzer()
        self.reasoning_engine = ReasoningEngine()
        self.planner = Planner()
        self.event_bus = event_bus
        self.memory_manager = memory_manager
        self.tool_registry = tool_registry
        self.security_validator = security_validator
        self.model_provider = model_provider
        self.avatar_behavior = avatar_behavior or AvatarBehavior()
        self.last_result: Optional[BrainResult] = None

        if self.event_bus is not None:
            self.event_bus.subscribe(
            EventType.USER_INPUT,
            self.handle_user_input,
        )
            self.event_bus.subscribe(
                EventType.WAKE_WORD,
                self.handle_wake_word,
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

        model_response, model_error = self._generate_model_response(
            context
        )

        if model_response is not None:
            reasoning.response = model_response.text

        plan = self.planner.create_plan(
            reasoning
        )
        avatar_expression = self.avatar_behavior.for_reasoning(
            intent.type,
            reasoning,
        )

        result = BrainResult(
            reasoning=reasoning,
            plan=plan,
            context=context,
            model_response=model_response,
            model_error=model_error,
            avatar_expression=avatar_expression,
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
        self._publish_avatar_expression(result.avatar_expression)

    def handle_wake_word(self, event: Event) -> None:
        """Tell a pet UI that ORION is ready to listen after activation."""

        self._publish_avatar_expression(
            self.avatar_behavior.for_wake_word()
        )

    def _publish_avatar_expression(
        self,
        expression: Optional[AvatarExpression],
    ) -> None:
        if self.event_bus is None or expression is None:
            return

        self.event_bus.publish(
            Event(
                type=EventType.AVATAR_EXPRESSION,
                payload=expression.to_payload(),
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
            "model": BrainEngine._model_payload(result),
            "memories_used": len(result.context.memories),
            "avatar": (
                result.avatar_expression.to_payload()
                if result.avatar_expression is not None
                else None
            ),
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

    @staticmethod
    def _model_payload(result: BrainResult) -> Optional[Dict[str, Any]]:
        if result.model_response is not None:
            return result.model_response.metadata

        if result.model_error is not None:
            return {
                "status": "unavailable",
                "error": result.model_error,
            }

        return None

    def _generate_model_response(
        self,
        context: ReasoningContext,
    ) -> tuple[Optional[ModelResponse], Optional[str]]:
        """Ask an optional provider to improve the deterministic response."""

        if self.model_provider is None:
            return None, None

        try:
            return self.model_provider.generate(
                ModelRequest(
                    text=context.user_input.text,
                    intent=context.intent.type.value,
                    memories=context.memories,
                    available_tools=context.metadata.get(
                        "available_tools",
                        [],
                    ),
                )
            ), None
        except ModelProviderError as exc:
            return None, str(exc)
