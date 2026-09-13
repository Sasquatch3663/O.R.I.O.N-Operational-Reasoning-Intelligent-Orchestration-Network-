from pathlib import Path

from orion.core.assistant import OrionAssistant
from orion.core.state import RuntimeState
from orion.utils.config import Config


def test_orion_initialization(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]

    config = Config(root)

    assistant = OrionAssistant(config)

    assistant.initialize()

    assert assistant.initialized is True
    assert (
        assistant.engine.state
        == RuntimeState.INITIALIZING
    )

    assistant.shutdown()


def test_orion_startup_and_shutdown(tmp_path: Path):
    root = Path(__file__).resolve().parents[1]

    config = Config(root)

    assistant = OrionAssistant(config)

    assistant.start()

    assert assistant.initialized is True
    assert assistant.engine.is_running is True

    assistant.shutdown()

    assert assistant.initialized is False
    assert (
        assistant.engine.state
        == RuntimeState.STOPPED
    )


def test_voice_runtime_is_optional_when_voice_disabled():
    root = Path(__file__).resolve().parents[1]

    config = Config(root)

    assistant = OrionAssistant(config)

    assistant.start()

    assert assistant.voice_service is None
    assert assistant.voice_runtime is None

    assistant.shutdown()