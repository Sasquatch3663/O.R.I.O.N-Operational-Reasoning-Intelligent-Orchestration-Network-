from typing import List, Optional

from orion.memory import (
    BaseMemory,
    MemoryManager,
    MemoryRecord,
)


class MockMemory(BaseMemory):

    def __init__(self):
        self.memories = {}

    def store(
        self,
        memory: MemoryRecord,
    ) -> None:
        self.memories[memory.memory_id] = memory

    def retrieve(
        self,
        memory_id: str,
    ) -> Optional[MemoryRecord]:
        return self.memories.get(memory_id)

    def search(
        self,
        query: str,
        limit: int = 10,
    ) -> List[MemoryRecord]:

        results = [
            memory
            for memory in self.memories.values()
            if query.lower() in memory.content.lower()
        ]

        return results[:limit]

    def delete(
        self,
        memory_id: str,
    ) -> None:
        self.memories.pop(memory_id, None)

    def clear(self) -> None:
        self.memories.clear()


def test_memory_record():
    memory = MemoryRecord(
        content="ORION test memory"
    )

    assert memory.content == (
        "ORION test memory"
    )

    assert memory.memory_id
    assert memory.timestamp


def test_memory_manager_store():
    provider = MockMemory()
    manager = MemoryManager(provider)

    memory = manager.store(
        "ORION remembers this."
    )

    assert memory.content == (
        "ORION remembers this."
    )

    assert (
        provider.retrieve(memory.memory_id)
        == memory
    )


def test_memory_manager_retrieve():
    provider = MockMemory()
    manager = MemoryManager(provider)

    memory = manager.store(
        "Test memory"
    )

    result = manager.retrieve(
        memory.memory_id
    )

    assert result == memory


def test_memory_manager_search():
    provider = MockMemory()
    manager = MemoryManager(provider)

    manager.store("Python project")
    manager.store("ORION project")
    manager.store("Gaming")

    results = manager.search(
        "project"
    )

    assert len(results) == 2


def test_memory_manager_delete():
    provider = MockMemory()
    manager = MemoryManager(provider)

    memory = manager.store(
        "Temporary memory"
    )

    manager.delete(
        memory.memory_id
    )

    assert (
        manager.retrieve(memory.memory_id)
        is None
    )


def test_memory_manager_clear():
    provider = MockMemory()
    manager = MemoryManager(provider)

    manager.store("Memory 1")
    manager.store("Memory 2")

    manager.clear()

    assert manager.search("Memory") == []