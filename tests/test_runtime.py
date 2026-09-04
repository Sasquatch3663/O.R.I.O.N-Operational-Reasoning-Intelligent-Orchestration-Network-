from pathlib import Path

from orion.core.assistant import OrionAssistant
from orion.core.engine import RuntimeEngine
from orion.core.state import RuntimeState
from orion.utils.config import Config
from orion.utils.logger import setup_logging


def test_runtime_initial_state() -> None:
    engine = RuntimeEngine()

    assert engine.state == RuntimeState.CREATED
    assert engine.is_running is False


def test_runtime_initialization() -> None:
    engine = RuntimeEngine()

    engine.initialize()

    assert engine.state == RuntimeState.INITIALIZING


def test_runtime_start() -> None:
    engine = RuntimeEngine()

    engine.initialize()
    engine.start()

    assert engine.state == RuntimeState.RUNNING
    assert engine.is_running is True

    engine.stop()

    assert engine.state == RuntimeState.STOPPED
    assert engine.is_running is False


def test_runtime_shutdown() -> None:
    engine = RuntimeEngine()

    engine.initialize()
    engine.start()
    engine.shutdown()

    assert engine.state == RuntimeState.STOPPED


def test_assistant_runtime(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]

    config = Config(root)

    setup_logging(
        config_path=(
            root
            / "config"
            / "logging.yaml"
        ),
        log_directory=tmp_path / "logs",
        level="DEBUG",
    )

    assistant = OrionAssistant(config)

    assistant.initialize()

    assert assistant.initialized is True
    assert (
        assistant.engine.state
        == RuntimeState.INITIALIZING
    )

    assistant.start()

    assert (
        assistant.engine.state
        == RuntimeState.RUNNING
    )

    status = assistant.status()

    assert status["initialized"] is True
    assert status["running"] is True
    assert status["runtime_state"] == "running"

    assistant.shutdown()

    assert (
        assistant.engine.state
        == RuntimeState.STOPPED
    )

    assert assistant.initialized is False