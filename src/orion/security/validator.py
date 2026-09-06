from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from orion.security.permissions import (
    PermissionLevel,
    PermissionManager,
)


class SecurityError(Exception):
    """Raised when a security check fails."""


class ConfirmationRequired(SecurityError):
    """Raised when user confirmation is required."""


@dataclass
class SecurityRequest:
    """
    Represents a request that requires authorization.
    """

    action: str
    permission: PermissionLevel
    parameters: Dict[str, Any]

    def __post_init__(self) -> None:
        if not self.action:
            raise ValueError(
                "Security action cannot be empty."
            )

        if not isinstance(
            self.permission,
            PermissionLevel,
        ):
            raise TypeError(
                "Permission must be a PermissionLevel."
            )

        if not isinstance(
            self.parameters,
            dict,
        ):
            raise TypeError(
                "Security parameters must be a dictionary."
            )


class SecurityValidator:
    """
    Validates ORION security requests.
    """

    def __init__(
        self,
        permission_manager: PermissionManager,
    ) -> None:
        self.permission_manager = permission_manager

    def validate(
        self,
        request: SecurityRequest,
        granted: PermissionLevel | None = None,
    ) -> bool:
        """
        Validate a security request.
        """

        allowed = self.permission_manager.allows(
            request.permission,
            granted,
        )

        if not allowed:
            raise SecurityError(
                f"Permission denied for action: "
                f"{request.action}"
            )

        return True


class ConfirmationManager:
    """
    Determines whether an operation requires
    explicit user confirmation.
    """

    def __init__(
        self,
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled

    def requires_confirmation(
        self,
        permission: PermissionLevel,
    ) -> bool:
        """
        Return whether the requested permission
        requires user confirmation.
        """

        if not self.enabled:
            return False

        return permission >= PermissionLevel.WRITE