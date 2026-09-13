import pytest # type: ignore

from orion.brain import (
    BaseModelProvider,
    BrainEngine,
    IntentAnalyzer,
    IntentType,
    ModelRequest,
    ModelResponse,
    ModelProviderError,
    OllamaModelProvider,
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


class UnavailableModelProvider(BaseModelProvider):
    def generate(self, request: ModelRequest) -> ModelResponse:
        raise ModelProviderError("Local service is offline.")


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


def test_spoken_question_intent_without_question_mark():
    analyzer = IntentAnalyzer()

    intent = analyzer.analyze("what time is it")

    assert intent.type == IntentType.QUESTION


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


def test_ollama_provider_uses_local_generate_contract():
    captured = {}

    def transport(payload):
        captured.update(payload)
        return {
            "model": "qwen2.5:3b",
            "response": "Hello from local ORION.",
            "total_duration": 42,
            "eval_count": 9,
        }

    provider = OllamaModelProvider(
        model="qwen2.5:3b",
        transport=transport,
    )

    response = provider.generate(
        ModelRequest(text="Hello", intent="conversation")
    )

    assert captured["model"] == "qwen2.5:3b"
    assert captured["stream"] is False
    assert response.text == "Hello from local ORION."
    assert response.metadata["provider"] == "ollama"


def test_unavailable_model_preserves_deterministic_response():
    brain = BrainEngine(
        model_provider=UnavailableModelProvider()
    )

    result = brain.process(UserInput(text="What is ORION?"))

    assert result.model_response is None
    assert result.model_error == "Local service is offline."
    assert result.reasoning.response == (
        "I understand that you are asking a question."
    )


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


def test_brain_publishes_avatar_expression():
    bus = EventBus()
    BrainEngine(bus)
    expressions = []

    bus.subscribe(EventType.AVATAR_EXPRESSION, expressions.append)

    bus.publish(
        Event(
            type=EventType.USER_INPUT,
            payload={"text": "What is ORION?"},
        )
    )

    assert expressions[0].payload["state"] == "thinking"
    assert expressions[0].payload["gesture"] == "head_tilt"


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
