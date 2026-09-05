from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4


class EventType(str, Enum):
    """Built-in ORION event types."""

    STARTUP = "startup"
    SHUTDOWN = "shutdown"

    USER_INPUT = "user_input"

    SYSTEM_EVENT = "system_event"

    ERROR = "error"

    TOOL_REQUEST = "tool_request"

    MEMORY_REQUEST = "memory_request"

    VOICE_INPUT = "voice_input"

    WAKE_WORD = "wake_word"


@dataclass
class Event:
    """
    Represents an event inside ORION.
    """

    type: EventType
    payload: Dict[str, Any] = field(default_factory=dict)

    event_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    source: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.type, EventType):
            raise TypeError(
                "Event type must be an EventType."
            )

        if not isinstance(self.payload, dict):
            raise TypeError(
                "Event payload must be a dictionary."
            )

        if not self.event_id:
            raise ValueError(
                "Event ID cannot be empty."
            )


EventHandler = Callable[[Event], None]


class EventBus:
    """
    Synchronous publish/subscribe event bus.

    Components can subscribe to event types and receive
    matching events when they are published.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[
            EventType,
            List[EventHandler],
        ] = {}

    def subscribe(
        self,
        event_type: EventType,
        handler: EventHandler,
    ) -> None:
        """Subscribe a handler to an event type."""

        if not callable(handler):
            raise TypeError(
                "Event handler must be callable."
            )

        handlers = self._subscribers.setdefault(
            event_type,
            [],
        )

        if handler not in handlers:
            handlers.append(handler)

    def unsubscribe(
        self,
        event_type: EventType,
        handler: EventHandler,
    ) -> None:
        """Remove a handler from an event type."""

        handlers = self._subscribers.get(
            event_type,
            [],
        )

        if handler in handlers:
            handlers.remove(handler)

        if not handlers:
            self._subscribers.pop(
                event_type,
                None,
            )

    def publish(self, event: Event) -> None:
        """Publish an event to all matching subscribers."""

        if not isinstance(event, Event):
            raise TypeError(
                "EventBus.publish() requires an Event."
            )

        handlers = list(
            self._subscribers.get(
                event.type,
                [],
            )
        )

        for handler in handlers:
            handler(event)

    def clear(self) -> None:
        """Remove all subscriptions."""

        self._subscribers.clear()

    def subscriber_count(
        self,
        event_type: Optional[EventType] = None,
    ) -> int:
        """Return the number of subscribers."""

        if event_type is not None:
            return len(
                self._subscribers.get(
                    event_type,
                    [],
                )
            )

        return sum(
            len(handlers)
            for handlers in self._subscribers.values()
        )