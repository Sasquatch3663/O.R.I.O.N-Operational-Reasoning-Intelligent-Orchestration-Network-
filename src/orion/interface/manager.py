from __future__ import annotations

from typing import Dict, Optional

from orion.interface.base import BaseInterface
from orion.utils.logger import get_logger


class InterfaceManager:
    """
    Manages ORION interfaces.

    Interfaces are registered by name and can be started
    or stopped independently.
    """

    def __init__(self) -> None:
        self.logger = get_logger(
            "orion.interface.manager"
        )

        self._interfaces: Dict[
            str,
            BaseInterface,
        ] = {}

    def register(
        self,
        interface: BaseInterface,
    ) -> None:
        """Register an interface."""

        if interface.name in self._interfaces:
            raise ValueError(
                f"Interface already registered: "
                f"{interface.name}"
            )

        self._interfaces[
            interface.name
        ] = interface

        self.logger.info(
            "Registered interface: %s",
            interface.name,
        )

    def unregister(self, name: str) -> None:
        """Remove an interface."""

        interface = self._interfaces.pop(
            name,
            None,
        )

        if interface is None:
            return

        if interface.is_running:
            interface.stop()

        self.logger.info(
            "Unregistered interface: %s",
            name,
        )

    def get(
        self,
        name: str,
    ) -> Optional[BaseInterface]:
        """Return an interface by name."""

        return self._interfaces.get(name)

    def start(self, name: str) -> None:
        """Start one interface."""

        interface = self.get(name)

        if interface is None:
            raise KeyError(
                f"Interface not found: {name}"
            )

        interface.start()

    def stop(self, name: str) -> None:
        """Stop one interface."""

        interface = self.get(name)

        if interface is None:
            return

        interface.stop()

    def start_all(self) -> None:
        """Start every registered interface."""

        for interface in self._interfaces.values():
            interface.start()

    def stop_all(self) -> None:
        """Stop every registered interface."""

        for interface in self._interfaces.values():
            interface.stop()

    def names(self) -> list[str]:
        """Return registered interface names."""

        return list(self._interfaces.keys())

    def count(self) -> int:
        """Return number of registered interfaces."""

        return len(self._interfaces)