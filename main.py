from pathlib import Path

from orion.core.assistant import OrionAssistant
from orion.utils.config import Config


def main() -> None:
    """Start ORION."""

    project_root = Path(__file__).resolve().parent

    config = Config(project_root)

    assistant = OrionAssistant(config)

    assistant.initialize()

    print()
    print("=" * 60)
    print("                         ORION")
    print("             Personal AI System Assistant")
    print("=" * 60)
    print()
    print("System")
    print("-------")
    print(f"Name:        {config.get('orion.name')}")
    print(f"Version:     {config.get('orion.version')}")
    print(f"Environment: {config.get('environment')}")
    print()
    print("Foundation")
    print("----------")
    print("Configuration : READY")
    print("Filesystem    : READY")
    print("Runtime       : READY")
    print()
    print("ORION foundation initialized successfully.")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()