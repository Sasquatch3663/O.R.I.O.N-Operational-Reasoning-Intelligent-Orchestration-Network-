from pathlib import Path

from orion.utils.config import Config
from orion.utils.system import OrionPaths


def test_config_loads() -> None:
    root = Path(__file__).resolve().parents[1]

    config = Config(root)

    assert config.get("orion.name") == "ORION"
    assert config.get("orion.version") == "0.1.0"


def test_environment_loads() -> None:
    root = Path(__file__).resolve().parents[1]

    config = Config(root)

    assert config.get("environment") in {
        "development",
        "production",
    }


def test_nested_configuration() -> None:
    root = Path(__file__).resolve().parents[1]

    config = Config(root)

    assert (
        config.get("runtime.data_directory")
        == "data"
    )


def test_paths() -> None:
    root = Path(__file__).resolve().parents[1]

    config = Config(root)
    paths = OrionPaths(config)

    assert paths.root == root
    assert paths.data.name == "data"
    assert paths.logs.name == "logs"
    assert paths.models.name == "models"