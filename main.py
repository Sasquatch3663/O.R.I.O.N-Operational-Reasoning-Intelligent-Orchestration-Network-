from pathlib import Path

from orion.core.assistant import OrionAssistant
from orion.utils.config import Config
from orion.utils.logger import get_logger, setup_logging
from orion.utils.system import OrionPaths


def main() -> None:
    project_root = Path(__file__).resolve().parent

    # ---------------------------------------------------------
    # Configuration
    # ---------------------------------------------------------

    config = Config(project_root)

    # ---------------------------------------------------------
    # Runtime paths
    # ---------------------------------------------------------

    paths = OrionPaths(config)
    paths.create_directories()

    # ---------------------------------------------------------
    # Logging
    # ---------------------------------------------------------

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

    logger = get_logger("orion.core.startup")

    logger.info(
        "ORION startup sequence initiated."
    )

    assistant = OrionAssistant(config)

    try:
        # -----------------------------------------------------
        # Initialize
        # -----------------------------------------------------

        assistant.initialize()

        # -----------------------------------------------------
        # Display status
        # -----------------------------------------------------

        print()
        print("=" * 60)
        print("                         ORION")
        print("             Personal AI System Assistant")
        print("=" * 60)
        print()

        print("System")
        print("-------")
        print(
            f"Name:        "
            f"{config.get('orion.name')}"
        )
        print(
            f"Version:     "
            f"{config.get('orion.version')}"
        )
        print(
            f"Environment: "
            f"{config.get('environment')}"
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
            "Runtime State : "
            f"{assistant.engine.state.value.upper()}"
        )

        print()

        print(
            "ORION foundation initialized successfully."
        )

        print("=" * 60)
        print()

        # -----------------------------------------------------
        # Start runtime
        # -----------------------------------------------------

        assistant.start()

        print(
            "ORION is running."
        )
        print(
            "Type 'exit', 'shutdown', 'quit' to shut down."
        )
        print()

        assistant.run()

    except KeyboardInterrupt:
        logger.info(
            "Keyboard interrupt received."
        )

    except Exception:
        logger.exception(
            "Fatal error during ORION runtime."
        )

    finally:
        assistant.shutdown()

        logger.info(
            "ORION shutdown sequence completed."
        )


if __name__ == "__main__":
    main()