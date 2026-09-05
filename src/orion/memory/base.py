from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4


class MemoryError(Exception):
    """Raised when ORION memory encounters an error."""


@dataclass
class MemoryRecord:
    """
    Represents a single ORION memory.
    """

    content: str
    memory_id: str = field(
        default_factory=lambda: str(uuid4())
    )
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not self.content:
            raise ValueError(
                "Memory content cannot be empty."
            )

        if not self.memory_id:
            raise ValueError(
                "Memory ID cannot be empty."
            )

        if not isinstance(self.metadata, dict):
            raise TypeError(
                "Memory metadata must be a dictionary."
            )


class BaseMemory(ABC):
    """
    Abstract interface for ORION memory providers.
    """

    @abstractmethod
    def store(
        self,
        memory: MemoryRecord,
    ) -> None:
        """
        Store a memory.
        """

    @abstractmethod
    def retrieve(
        self,
        memory_id: str,
    ) -> Optional[MemoryRecord]:
        """
        Retrieve a memory by ID.
        """

    @abstractmethod
    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> List[MemoryRecord]:
        """
        Search memories.
        """

    @abstractmethod
    def delete(
        self,
        memory_id: str,
    ) -> None:
        """
        Delete a memory.
        """

    @abstractmethod
    def clear(self) -> None:
        """
        Clear all memories.
        """