from pathlib import Path


def create_runtime_directories() -> None:
    """Create ORION runtime directories."""

    root = Path(__file__).resolve().parents[1]

    directories = [
        root / "data" / "memory",
        root / "data" / "knowledge",
        root / "data" / "cache",
        root / "logs",
        root / "models",
    ]

    for directory in directories:
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    print(
        "ORION runtime directories created successfully."
    )


if __name__ == "__main__":
    create_runtime_directories()