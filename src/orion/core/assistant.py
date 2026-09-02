from typing import Dict

from orion.utils.config import Config
from orion.utils.system import OrionPaths


class OrionAssistant:
    """Top-level ORION application."""

    def __init__(
        self,
        config: Config,
    ) -> None:

        self.config = config
        self.paths = OrionPaths(config)

        self.initialized = False

    def initialize(self) -> None:
        """Initialize the ORION foundation."""

        self.paths.create_directories()

        self.initialized = True

    def status(self) -> Dict[str, bool]:
        """Return ORION foundation status."""

        return {
            "configuration": self.config is not None,
            "paths": self.paths.data.exists(),
            "initialized": self.initialized,
        }