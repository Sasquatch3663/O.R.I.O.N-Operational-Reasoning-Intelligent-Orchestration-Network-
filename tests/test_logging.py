from pathlib import Path

from orion.utils.config import Config
from orion.utils.logger import (
    get_logger,
    setup_logging,
)
from orion.utils.system import OrionPaths


def test_logging_initializes(tmp_path: Path) -> None:

    root = Path(__file__).resolve().parents[1]

    config = Config(root)

    log_directory = (
        tmp_path / "logs"
    )

    setup_logging(
        config_path=(
            root
            / "config"
            / "logging.yaml"
        ),
        log_directory=log_directory,
        level="DEBUG",
    )

    logger = get_logger(
        "orion.test"
    )

    logger.info(
        "Logging test message."
    )

    assert (
        log_directory / "orion.log"
    ).exists()

    assert (
        log_directory / "errors.log"
    ).exists()


def test_logger_namespace() -> None:

    logger = get_logger(
        "orion.test.namespace"
    )

    assert logger.name.startswith(
        "orion"
    )


def test_logger_short_namespace() -> None:

    logger = get_logger(
        "test.short"
    )

    assert logger.name.startswith(
        "orion"
    )

def test_exception_logging(
    tmp_path: Path,
) -> None:

    root = Path(__file__).resolve().parents[1]

    config = Config(root)

    log_directory = (
        tmp_path / "logs"
    )

    setup_logging(
        config_path=(
            root
            / "config"
            / "logging.yaml"
        ),
        log_directory=log_directory,
        level="DEBUG",
    )

    logger = get_logger(
        "orion.test.exception"
    )

    try:
        raise ValueError(
            "Intentional test exception"
        )

    except ValueError:
        logger.exception(
            "Test exception captured."
        )

    error_log = (
        log_directory
        / "errors.log"
    )

    assert error_log.exists()

    content = error_log.read_text(
        encoding="utf-8"
    )

    assert (
        "Test exception captured."
        in content
    )

    assert (
        "ValueError"
        in content
    )