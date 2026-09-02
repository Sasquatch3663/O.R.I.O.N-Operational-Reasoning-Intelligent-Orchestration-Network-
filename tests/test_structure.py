from pathlib import Path


def test_repository_structure() -> None:

    root = Path(__file__).resolve().parents[1]

    required_directories = [
        "config",
        "config/environments",
        "src",
        "src/orion",
        "src/orion/core",
        "src/orion/brain",
        "src/orion/interface",
        "src/orion/tools",
        "src/orion/memory",
        "src/orion/security",
        "src/orion/online",
        "src/orion/utils",
        "tests",
        "data",
        "data/cache",
        "data/knowledge",
        "data/memory",
        "logs",
        "models",
        "scripts",
        "docs",
    ]

    for directory in required_directories:

        path = root / directory

        assert path.is_dir(), (
            f"Missing directory: {directory}"
        )


def test_required_files() -> None:

    root = Path(__file__).resolve().parents[1]

    required_files = [
        "main.py",
        "pyproject.toml",
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "README.md",
        "config/config.yaml",
        "config/logging.yaml",
    ]

    for filename in required_files:

        path = root / filename

        assert path.is_file(), (
            f"Missing file: {filename}"
        )