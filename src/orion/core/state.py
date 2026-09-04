from __future__ import annotations

from enum import Enum


class RuntimeState(str, Enum):
    """Lifecycle states for the ORION runtime."""

    CREATED = "created"
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"