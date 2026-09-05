from __future__ import annotations

from typing import List, Optional

from orion.memory.base import (
    BaseMemory,
    MemoryRecord,
    MemoryError,
)


class MemoryManager:
    """
    Coordinates the active ORION memory provider.
    """

    def __init__(
        self,
        provider: BaseMemory,
    ) -> None:
        if not isinstance(provider, BaseMemory):
            raise TypeError(
                "Memory provider must implement BaseMemory."
            )

        self.provider = provider

    def store(
        self,
        content: str,
        metadata: Optional[dict] = None,
    ) -> MemoryRecord:

        memory = MemoryRecord(
            content=content,
            metadata=metadata or {},
        )

        self.provider.store(memory)

        return memory

    def retrieve(
        self,
        memory_id: str,
    ) -> Optional[MemoryRecord]:

        return self.provider.retrieve(
            memory_id
        )

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> List[MemoryRecord]:

        if limit <= 0:
            raise ValueError(
                "Memory search limit must be greater than zero."
            )

        return self.provider.search(
            query,
            limit,
        )

    def delete(
        self,
        memory_id: str,
    ) -> None:

        self.provider.delete(
            memory_id
        )

    def clear(self) -> None:

        self.provider.clear()