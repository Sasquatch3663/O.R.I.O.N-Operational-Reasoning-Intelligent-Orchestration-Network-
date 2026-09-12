import pytest # type: ignore

from orion.brain import (
    BaseModelProvider,
    BrainEngine,
    IntentAnalyzer,
    IntentType,
    ModelRequest,
    ModelResponse,
    UserInput,
)
from orion.core.events import Event, EventBus, EventType
from orion.security import (
    PermissionLevel,
    PermissionManager,
    SecurityError,
    SecurityValidator,
)


class StubModelProvider(BaseModelProvider):
    """Small provider implementation used to test the abstraction."""

    def generate(self, request: ModelRequest) -> ModelResponse:
        return ModelResponse(
            text=f"Model reply for: {request.text}",
            confidence=0.9,
            metadata={"provider": "stub"},
        )


def test_user_input_normalization():
    user_input = UserInput(
        text="  Hello ORION  ",
        source="cli",
    )

    assert user_input.text == "Hello ORION"
    assert user_input.source == "cli"


def test_question_intent():
    analyzer = IntentAnalyzer()

    intent = analyzer.analyze(
        "What is Python?"
    )

    assert intent.type == IntentType.QUESTION
    assert intent.confidence > 0


def test_memory_intent():
    analyzer = IntentAnalyzer()

    intent = analyzer.analyze(
        "remember that my project is ORION"
    )

    assert (
        intent.type
        == IntentType.MEMORY_REQUEST
    )


def test_memory_request_creates_write_plan():
    brain = BrainEngine()

    result = brain.process(
        UserInput(
            text="remember that ORION is local",
            source="test",
        )
    )

    step = result.plan.steps[0]

    assert step.action == "memory_store"
    assert step.permission == PermissionLevel.WRITE
    assert step.requires_confirmation is True


def test_tool_intent():
    analyzer = IntentAnalyzer()

    intent = analyzer.analyze(
        "open calculator"
    )

    assert (
        intent.type
        == IntentType.TOOL_REQUEST
    )


def test_brain_question():
    brain = BrainEngine()

    result = brain.process(
        UserInput(
            text="What is Python?",
            source="test",
        )
    )

    assert result.reasoning.response
    assert result.plan.steps == []


def test_brain_uses_optional_model_provider():
    brain = BrainEngine(model_provider=StubModelProvider())

    result = brain.process(
        UserInput(text="What is ORION?", source="test")
    )

    assert result.reasoning.response == (
        "Model reply for: What is ORION?"
    )
    assert result.model_response is not None
    assert result.model_response.metadata["provider"] == "stub"


def test_model_request_builds_portable_prompt():
    request = ModelRequest(
        text="Hello ORION",
        intent="conversation",
        available_tools=["calendar"],
    )

    assert "Hello ORION" in request.prompt()
    assert "calendar" in request.prompt()


def test_brain_tool_request():
    brain = BrainEngine()

    result = brain.process(
        UserInput(
            text="open calculator",
            source="test",
        )
    )

    assert result.reasoning.actions
    assert len(result.plan.steps) == 1
    assert (
        result.plan.steps[0].action
        == "tool_request"
    )


def test_brain_processes_user_input_events():
    bus = EventBus()
    brain = BrainEngine(bus)
    responses = []

    bus.subscribe(
        EventType.BRAIN_RESPONSE,
        responses.append,
    )

    bus.publish(
        Event(
            type=EventType.USER_INPUT,
            payload={"text": "open calculator"},
            source="cli",
        )
    )

    assert brain.last_result is not None
    assert len(responses) == 1
    assert responses[0].source == "brain"
    assert (
        responses[0].payload["plan"][0]["action"]
        == "tool_request"
    )


def test_tool_plan_requires_execute_permission():
    brain = BrainEngine()

    result = brain.process(
        UserInput(text="open calculator")
    )

    step = result.plan.steps[0]

    assert step.permission == PermissionLevel.EXECUTE
    assert step.requires_confirmation is True


def test_brain_validates_plan_against_security_policy():
    brain = BrainEngine(
        security_validator=SecurityValidator(
            PermissionManager(PermissionLevel.READ)
        )
    )

    result = brain.process(
        UserInput(text="open calculator")
    )

    with pytest.raises(SecurityError):
        brain.validate_plan(result.plan)
