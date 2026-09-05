from __future__ import annotations

from typing import Dict

from orion.core.engine import RuntimeEngine
from orion.interface.cli import CLIInterface
from orion.interface.manager import InterfaceManager
from orion.utils.config import Config
from orion.utils.logger import get_logger
from orion.utils.system import OrionPaths


class OrionAssistant:
    """Top-level ORION application."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.paths = OrionPaths(config)
        self.logger = get_logger("orion.core.assistant")

        # Create the runtime engine before interfaces,
        # because interfaces use the engine's EventBus.
        self.engine = RuntimeEngine()

        self.interfaces = InterfaceManager()

        self.cli = CLIInterface(
            self.engine.event_bus
        )

        self.interfaces.register(self.cli)

        self.initialized = False

    def initialize(self) -> None:
        """Initialize ORION foundation and runtime."""

        if self.initialized:
            self.logger.warning(
                "ORION initialization requested more than once."
            )
            return

        self.logger.info("Starting ORION initialization.")

        self.paths.create_directories()
        self.engine.initialize()

        self.initialized = True

        self.logger.info(
            "ORION initialization completed."
        )

    def start(self) -> None:
        """Start ORION."""

        if not self.initialized:
            self.initialize()

        self.logger.info("Starting ORION.")

        self.engine.start()
        self.interfaces.start_all()

        self.logger.info("ORION is now running.")

    def run(self) -> None:
        """Run ORION."""

        if not self.initialized:
            self.initialize()

        if not self.engine.is_running:
            self.start()

        self.engine.run(self.cli)

    def stop(self) -> None:
        """Stop ORION."""

        self.logger.info("Stopping ORION.")

        self.engine.stop()

    def shutdown(self) -> None:
        """Shutdown ORION."""

        self.logger.info("Shutting down ORION.")

        self.interfaces.stop_all()
        self.engine.shutdown()

        self.initialized = False

        self.logger.info("ORION shutdown completed.")

    def status(self) -> Dict[str, object]:
        """Return current ORION status."""

        status = {
            "configuration": self.config is not None,
            "paths": self.paths.data.exists(),
            "initialized": self.initialized,
            "runtime_state": self.engine.state.value,
            "running": self.engine.is_running,
        }

        self.logger.debug(
            "ORION status: %s",
            status,
        )

        return status