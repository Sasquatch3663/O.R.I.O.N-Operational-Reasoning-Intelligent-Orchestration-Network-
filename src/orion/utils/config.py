from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import yaml
from dotenv import load_dotenv  # type: ignore


class ConfigurationError(Exception):
    """Raised when ORION configuration is invalid."""


class Config:
    """
    Central configuration manager for ORION.

    Configuration precedence:

    1. Base YAML configuration
    2. Environment-specific YAML
    3. .env
    4. System environment variables
    """

    def __init__(
        self,
        project_root: Optional[Path] = None,
    ) -> None:

        if project_root is None:
            project_root = Path(__file__).resolve().parents[3]

        self.project_root = project_root.resolve()

        self.config_dir = self.project_root / "config"
        self.environment_dir = (
            self.config_dir / "environments"
        )

        self._data: Dict[str, Any] = {}

        self._load()

    # --------------------------------------------------------
    # Loading
    # --------------------------------------------------------

    def _load(self) -> None:
        """Load all configuration sources."""

        env_file = self.project_root / ".env"

        if env_file.exists():
            load_dotenv(env_file)

        base_config = self._load_yaml(
            self.config_dir / "config.yaml"
        )

        environment = os.getenv(
            "ORION_ENV",
            base_config
            .get("environment", {})
            .get("default", "development"),
        )

        environment_config_path = (
            self.environment_dir
            / f"{environment}.yaml"
        )

        environment_config: Dict[str, Any] = {}

        if environment_config_path.exists():
            environment_config = self._load_yaml(
                environment_config_path
            )

        self._data = self._deep_merge(
            base_config,
            environment_config,
        )

        self._apply_environment_variables()

        self._data["environment"] = environment

        self.validate()

    # --------------------------------------------------------
    # YAML
    # --------------------------------------------------------

    @staticmethod
    def _load_yaml(
        path: Path,
    ) -> Dict[str, Any]:
        """Load a YAML configuration file."""

        if not path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {path}"
            )

        try:
            with path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = yaml.safe_load(file) or {}

        except yaml.YAMLError as exc:
            raise ConfigurationError(
                f"Invalid YAML configuration: {path}"
            ) from exc

        if not isinstance(data, dict):
            raise ConfigurationError(
                f"Configuration root must be a mapping: {path}"
            )

        return data

    # --------------------------------------------------------
    # Merge
    # --------------------------------------------------------

    @classmethod
    def _deep_merge(
        cls,
        base: Dict[str, Any],
        override: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries."""

        result = dict(base)

        for key, value in override.items():

            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = cls._deep_merge(
                    result[key],
                    value,
                )

            else:
                result[key] = value

        return result

    # --------------------------------------------------------
    # Environment variables
    # --------------------------------------------------------

    def _apply_environment_variables(self) -> None:
        """Apply supported environment variables."""

        mappings = {
            "ORION_NAME": (
                "orion",
                "name",
            ),
            "ORION_VERSION": (
                "orion",
                "version",
            ),
            "ORION_LOG_LEVEL": (
                "logging",
                "level",
            ),
            "ORION_MODEL_PROVIDER": (
                "brain",
                "provider",
            ),
            "ORION_MODEL_NAME": (
                "brain",
                "model",
            ),
        }

        for env_name, path in mappings.items():

            value = os.getenv(env_name)

            if value is not None:
                self._set_nested(
                    path,
                    value,
                )

    def _set_nested(
        self,
        path: Tuple[str, ...],
        value: Any,
    ) -> None:
        """Set a nested configuration value."""

        current = self._data

        for key in path[:-1]:
            current = current.setdefault(
                key,
                {},
            )

        current[path[-1]] = value

    # --------------------------------------------------------
    # Access
    # --------------------------------------------------------

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get a configuration value using dot notation.

        Example:

            config.get("orion.name")
        """

        current: Any = self._data

        for part in key.split("."):

            if not isinstance(current, dict):
                return default

            if part not in current:
                return default

            current = current[part]

        return current

    def require(
        self,
        key: str,
    ) -> Any:
        """Get a required configuration value."""

        value = self.get(key)

        if value is None:
            raise ConfigurationError(
                f"Required configuration missing: {key}"
            )

        return value

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    def validate(self) -> None:
        """Validate required configuration."""

        required_keys = [
            "orion.name",
            "orion.version",
            "runtime.data_directory",
            "runtime.log_directory",
            "runtime.model_directory",
            "interface.default",
            "brain.provider",
            "memory.enabled",
            "security.enabled",
        ]

        missing = []

        for key in required_keys:

            if self.get(key) is None:
                missing.append(key)

        if missing:
            raise ConfigurationError(
                "Missing configuration values: "
                + ", ".join(missing)
            )

    # --------------------------------------------------------
    # Full configuration
    # --------------------------------------------------------

    @property
    def data(self) -> Dict[str, Any]:
        """Return a copy of the configuration."""

        return dict(self._data)