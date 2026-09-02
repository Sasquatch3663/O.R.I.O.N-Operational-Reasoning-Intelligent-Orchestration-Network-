from pathlib import Path

from orion.utils.config import Config


class OrionPaths:
    """Centralized filesystem paths for ORION."""

    def __init__(
        self,
        config: Config,
    ) -> None:

        self.root = config.project_root

        self.data = (
            self.root
            / config.require(
                "runtime.data_directory"
            )
        )

        self.memory = self.data / "memory"
        self.knowledge = self.data / "knowledge"
        self.cache = self.data / "cache"

        self.logs = (
            self.root
            / config.require(
                "runtime.log_directory"
            )
        )

        self.models = (
            self.root
            / config.require(
                "runtime.model_directory"
            )
        )

    def create_directories(self) -> None:
        """Create required runtime directories."""

        directories = [
            self.data,
            self.memory,
            self.knowledge,
            self.cache,
            self.logs,
            self.models,
        ]

        for directory in directories:
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )