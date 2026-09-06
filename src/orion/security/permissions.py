from __future__ import annotations

from enum import IntEnum


class PermissionLevel(IntEnum):
    """
    Permission levels for ORION operations.
    """

    NONE = 0
    READ = 10
    WRITE = 20
    EXECUTE = 30
    ADMIN = 40


class PermissionManager:
    """
    Manages ORION permissions.
    """

    def __init__(
        self,
        default_level: PermissionLevel = PermissionLevel.READ,
    ) -> None:
        self.default_level = default_level

    def allows(
        self,
        required: PermissionLevel,
        granted: PermissionLevel | None = None,
    ) -> bool:
        """
        Determine whether a granted permission
        satisfies a required permission.
        """

        if granted is None:
            granted = self.default_level

        return granted >= required