from pathlib import Path

from orion.core.assistant import OrionAssistant
from orion.utils.config import Config


def create_test_config() -> Config:
    """Create a Config using the existing ORION project configuration API."""

    project_root = Path(__file__).resolve().parents[1]

    return Config(project_root)


def test_assistant_initialization():
    assistant = OrionAssistant(
        create_test_config()
    )

    assert assistant.initialized is False
    assert assistant.status()["running"] is False


def test_assistant_start_initializes_and_runs():
    assistant = OrionAssistant(
        create_test_config()
    )

    assistant.start()

    assert assistant.initialized is True
    assert assistant.status()["running"] is True
    assert assistant.engine.is_running is True

    assistant.stop()


def test_assistant_start_is_idempotent():
    assistant = OrionAssistant(
        create_test_config()
    )

    assistant.start()
    assistant.start()

    assert assistant.status()["running"] is True

    assistant.stop()


def test_assistant_stop_is_idempotent():
    assistant = OrionAssistant(
        create_test_config()
    )

    assistant.start()

    assistant.stop()
    assistant.stop()

    assert assistant.status()["running"] is False
    assert assistant.engine.is_running is False


def test_assistant_shutdown_stops_everything():
    assistant = OrionAssistant(
        create_test_config()
    )

    assistant.start()
    assistant.shutdown()

    assert assistant.initialized is False
    assert assistant.status()["running"] is False
    assert assistant.engine.is_running is False


def test_assistant_shutdown_without_start():
    assistant = OrionAssistant(
        create_test_config()
    )

    assistant.shutdown()

    assert assistant.initialized is False
    assert assistant.status()["running"] is False