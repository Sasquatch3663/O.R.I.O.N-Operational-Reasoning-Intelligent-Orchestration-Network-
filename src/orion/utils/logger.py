from __future__ import annotations

import logging
import logging.config
from pathlib import Path
from typing import Optional

import yaml


class LoggingError(Exception):
    """Raised when ORION logging cannot be initialized."""


def setup_logging(
    config_path: Path,
    log_directory: Path,
    level: Optional[str] = None,
) -> None:
    """
    Initialize the ORION logging system.

    Parameters
    ----------
    config_path:
        Path to logging.yaml.

    log_directory:
        Directory where ORION log files are stored.

    level:
        Optional runtime logging level override.
    """

    if not config_path.exists():
        raise LoggingError(
            "Logging configuration not found: "
            f"{config_path}"
        )

    log_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        with config_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            config = yaml.safe_load(file)

    except yaml.YAMLError as exc:
        raise LoggingError(
            f"Invalid logging configuration: {config_path}"
        ) from exc

    if not isinstance(config, dict):
        raise LoggingError(
            "Logging configuration must be a mapping."
        )

    # Convert log paths to absolute paths.
    handlers = config.get("handlers", {})

    if "file" in handlers:
        handlers["file"]["filename"] = str(
            log_directory / "orion.log"
        )

    if "error_file" in handlers:
        handlers["error_file"]["filename"] = str(
            log_directory / "errors.log"
        )

    # Apply runtime log level.
    if level:
        normalized_level = level.upper()

        valid_levels = {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }

        if normalized_level not in valid_levels:
            raise LoggingError(
                f"Invalid logging level: {level}"
            )

        if "orion" in config.get("loggers", {}):
            config["loggers"]["orion"]["level"] = (
                normalized_level
            )

        if "console" in handlers:
            handlers["console"]["level"] = (
                normalized_level
            )

    try:
        logging.config.dictConfig(config)

    except (ValueError, TypeError, OSError) as exc:
        raise LoggingError(
            "Failed to initialize ORION logging."
        ) from exc


def get_logger(
    name: str,
) -> logging.Logger:
    """
    Return a component-specific ORION logger.

    Example
    -------
    get_logger("orion.core")
    """

    if not name.startswith("orion"):
        name = f"orion.{name}"

    return logging.getLogger(name)


def log_exception(
    logger: logging.Logger,
    message: str,
) -> None:
    """
    Log an exception with traceback information.

    This function should be called from an exception handler.
    """

    logger.exception(message)