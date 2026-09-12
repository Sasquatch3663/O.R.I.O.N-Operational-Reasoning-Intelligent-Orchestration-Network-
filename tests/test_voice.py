from orion.core.engine import RuntimeEngine
from orion.core.events import Event, EventType
from orion.voice import WakeWordDetector, WakeWordProfile


def test_wake_word_profile_normalizes_phrase():
    profile = WakeWordProfile(
        user_id="ayush",
        phrase="  Hello, Nova!  ",
    )

    assert profile.phrase == "hello nova"


def test_wake_word_detector_extracts_command():
    detector = WakeWordDetector(
        WakeWordProfile("ayush", "hello nova")
    )

    match = detector.detect("Hello Nova, open calendar")

    assert match is not None
    assert match.command == "open calendar"


def test_runtime_emits_wake_and_listening_expression():
    runtime = RuntimeEngine(
        WakeWordDetector(
            WakeWordProfile("ayush", "hello nova")
        )
    )
    wake_events = []
    expressions = []

    runtime.event_bus.subscribe(EventType.WAKE_WORD, wake_events.append)
    runtime.event_bus.subscribe(
        EventType.AVATAR_EXPRESSION,
        expressions.append,
    )

    runtime.event_bus.publish(
        Event(
            type=EventType.VOICE_INPUT,
            payload={"text": "hello nova what time is it"},
            source="android",
        )
    )

    assert wake_events[0].payload["user_id"] == "ayush"
    assert wake_events[0].payload["command"] == "what time is it"
    assert expressions[0].payload["state"] == "listening"
