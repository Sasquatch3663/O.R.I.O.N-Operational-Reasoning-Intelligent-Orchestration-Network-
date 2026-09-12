import pytest

from orion.brain import (
    BaseModelProvider,
    BrainEngine,
    ModelProviderError,
    ModelRequest,
    ModelResponse,
    UserInput,
)
from orion.core.engine import RuntimeEngine
from orion.core.events import Event, EventBus, EventType
from orion.voice import WakeWordDetector, WakeWordProfile


class OfflineProvider(BaseModelProvider):
    def generate(self, request: ModelRequest) -> ModelResponse:
        raise ModelProviderError("Local service is offline.")


class ReplyProvider(BaseModelProvider):
    def generate(self, request: ModelRequest) -> ModelResponse:
        return ModelResponse(
            text="I can help with that.",
            metadata={"provider": "validation"},
        )


def test_phase1_voice_to_brain_to_pet_pipeline():
    runtime = RuntimeEngine(
        wake_word_detector=WakeWordDetector(
            WakeWordProfile("ayush", "hello nova")
        )
    )
    wake_events = []
    responses = []
    expressions = []

    runtime.event_bus.subscribe(EventType.WAKE_WORD, wake_events.append)
    runtime.event_bus.subscribe(
        EventType.BRAIN_RESPONSE,
        responses.append,
    )
    runtime.event_bus.subscribe(
        EventType.AVATAR_EXPRESSION,
        expressions.append,
    )

    runtime.event_bus.publish(
        Event(
            type=EventType.VOICE_INPUT,
            payload={"text": "hello nova open calculator"},
            source="windows",
        )
    )

    assert wake_events[0].payload["user_id"] == "ayush"
    assert wake_events[0].payload["command"] == "open calculator"
    assert responses[0].payload["plan"][0]["action"] == "tool_request"
    assert expressions[0].payload["state"] == "listening"
    assert expressions[-1].payload["state"] == "thinking"


def test_phase1_disabled_wake_profile_does_not_activate():
    detector = WakeWordDetector(
        WakeWordProfile(
            user_id="ayush",
            phrase="hello nova",
            enabled=False,
        )
    )

    assert detector.detect("hello nova open calculator") is None


def test_phase1_model_failure_keeps_event_pipeline_operational():
    bus = EventBus()
    BrainEngine(bus, model_provider=OfflineProvider())
    responses = []

    bus.subscribe(EventType.BRAIN_RESPONSE, responses.append)
    bus.publish(
        Event(
            type=EventType.USER_INPUT,
            payload={"text": "What is ORION?"},
        )
    )

    assert responses[0].payload["response"] == (
        "I understand that you are asking a question."
    )
    assert responses[0].payload["model"]["status"] == "unavailable"


def test_phase1_model_enhances_response_without_changing_plan():
    brain = BrainEngine(model_provider=ReplyProvider())

    result = brain.process(UserInput(text="open calculator"))

    assert result.reasoning.response == "I can help with that."
    assert result.plan.steps[0].action == "tool_request"
    assert result.plan.steps[0].requires_confirmation is True


def test_phase1_rejects_malformed_user_input_event():
    bus = EventBus()
    BrainEngine(bus)

    with pytest.raises(TypeError, match="text as a string"):
        bus.publish(
            Event(
                type=EventType.USER_INPUT,
                payload={"text": 42},
            )
        )
