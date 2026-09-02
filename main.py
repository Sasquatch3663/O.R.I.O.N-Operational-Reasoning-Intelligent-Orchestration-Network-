from pathlib import Path

from orion.core.assistant import OrionAssistant
from orion.utils.config import Config
from orion.utils.logger import get_logger, setup_logging
from orion.utils.system import OrionPaths


def main() -> None:
    """Start ORION."""

    project_root = Path(__file__).resolve().parent

    # --------------------------------------------------------
    # Configuration
    # --------------------------------------------------------

    config = Config(project_root)

    # --------------------------------------------------------
    # Filesystem
    # --------------------------------------------------------

    paths = OrionPaths(config)

    paths.create_directories()

    # --------------------------------------------------------
    # Logging
    # --------------------------------------------------------

    setup_logging(
        config_path=(
            project_root
            / "config"
            / "logging.yaml"
        ),
        log_directory=paths.logs,
        level=config.get(
            "logging.level",
            "INFO",
        ),
    )

    logger = get_logger(
        "orion.core.startup"
    )

    logger.info(
        "ORION startup sequence initiated."
    )

    # --------------------------------------------------------
    # Assistant
    # --------------------------------------------------------

    assistant = OrionAssistant(config)

    assistant.initialize()

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("                         ORION")
    print("             Personal AI System Assistant")
    print("=" * 60)
    print()

    print("System")
    print("-------")
    print(
        f"Name:        {config.get('orion.name')}"
    )
    print(
        f"Version:     {config.get('orion.version')}"
    )
    print(
        f"Environment: {config.get('environment')}"
    )

    print()

    print("Foundation")
    print("----------")
    print("Configuration : READY")
    print("Filesystem    : READY")
    print("Logging       : READY")
    print("Runtime       : READY")

    print()

    print(
        "ORION foundation initialized successfully."
    )

    print("=" * 60)
    print()

    logger.info(
        "ORION startup sequence completed."
    )


if __name__ == "__main__":
    main()