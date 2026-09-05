from datetime import timezone

import pytest # type: ignore

from orion.core.events import (
    Event,
    EventBus,
    EventType,
)


def test_event_creation() -> None:
    event = Event(
        type=EventType.USER_INPUT,
        payload={
            "text": "hello"
        },
        source="cli",
    )

    assert event.type == EventType.USER_INPUT
    assert event.payload["text"] == "hello"
    assert event.source == "cli"
    assert event.event_id
    assert event.timestamp.tzinfo == timezone.utc


def test_event_bus_subscription() -> None:
    bus = EventBus()

    received = []

    def handler(event: Event) -> None:
        received.append(event)

    bus.subscribe(
        EventType.USER_INPUT,
        handler,
    )

    event = Event(
        type=EventType.USER_INPUT,
        payload={
            "text": "hello"
        },
    )

    bus.publish(event)

    assert len(received) == 1
    assert received[0] is event


def test_event_bus_multiple_handlers() -> None:
    bus = EventBus()

    received = []

    def handler_one(event: Event) -> None:
        received.append("one")

    def handler_two(event: Event) -> None:
        received.append("two")

    bus.subscribe(
        EventType.USER_INPUT,
        handler_one,
    )

    bus.subscribe(
        EventType.USER_INPUT,
        handler_two,
    )

    bus.publish(
        Event(
            type=EventType.USER_INPUT
        )
    )

    assert received == [
        "one",
        "two",
    ]


def test_event_bus_unsubscribe() -> None:
    bus = EventBus()

    received = []

    def handler(event: Event) -> None:
        received.append(event)

    bus.subscribe(
        EventType.USER_INPUT,
        handler,
    )

    bus.unsubscribe(
        EventType.USER_INPUT,
        handler,
    )

    bus.publish(
        Event(
            type=EventType.USER_INPUT
        )
    )

    assert received == []


def test_event_bus_duplicate_subscription() -> None:
    bus = EventBus()

    def handler(event: Event) -> None:
        pass

    bus.subscribe(
        EventType.USER_INPUT,
        handler,
    )

    bus.subscribe(
        EventType.USER_INPUT,
        handler,
    )

    assert (
        bus.subscriber_count(
            EventType.USER_INPUT
        )
        == 1
    )


def test_event_type_validation() -> None:
    with pytest.raises(TypeError):
        Event(
            type="user_input"  # type: ignore[arg-type]
        )


def test_payload_validation() -> None:
    with pytest.raises(TypeError):
        Event(
            type=EventType.USER_INPUT,
            payload="invalid",  # type: ignore[arg-type]
        )


def test_publish_validation() -> None:
    bus = EventBus()

    with pytest.raises(TypeError):
        bus.publish("invalid")  # type: ignore[arg-type]


def test_clear_event_bus() -> None:
    bus = EventBus()

    def handler(event: Event) -> None:
        pass

    bus.subscribe(
        EventType.USER_INPUT,
        handler,
    )

    assert bus.subscriber_count() == 1

    bus.clear()

    assert bus.subscriber_count() == 0