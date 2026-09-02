from typing import Dict

from orion.utils.config import Config
from orion.utils.logger import get_logger
from orion.utils.system import OrionPaths


class OrionAssistant:
    """Top-level ORION application."""

    def __init__(
        self,
        config: Config,
    ) -> None:

        self.config = config
        self.paths = OrionPaths(config)

        self.logger = get_logger(
            "orion.core.assistant"
        )

        self.initialized = False

    def initialize(self) -> None:
        """Initialize the ORION foundation."""

        self.logger.info(
            "Starting ORION initialization."
        )

        self.paths.create_directories()

        self.initialized = True

        self.logger.info(
            "ORION initialization completed."
        )

    def status(self) -> Dict[str, bool]:
        """Return ORION foundation status."""

        status = {
            "configuration": self.config is not None,
            "paths": self.paths.data.exists(),
            "initialized": self.initialized,
        }

        self.logger.debug(
            "ORION status: %s",
            status,
        )

        return status