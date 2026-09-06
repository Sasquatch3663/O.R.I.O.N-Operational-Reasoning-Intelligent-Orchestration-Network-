import pytest

from orion.security import (
    ConfirmationManager,
    PermissionLevel,
    PermissionManager,
    SecurityError,
    SecurityRequest,
    SecurityValidator,
)


def test_permission_levels():
    assert PermissionLevel.NONE < PermissionLevel.READ
    assert PermissionLevel.READ < PermissionLevel.WRITE
    assert PermissionLevel.WRITE < PermissionLevel.EXECUTE
    assert PermissionLevel.EXECUTE < PermissionLevel.ADMIN


def test_permission_manager():
    manager = PermissionManager(
        PermissionLevel.READ
    )

    assert manager.allows(
        PermissionLevel.READ
    )

    assert not manager.allows(
        PermissionLevel.WRITE
    )


def test_explicit_granted_permission():
    manager = PermissionManager(
        PermissionLevel.NONE
    )

    assert manager.allows(
        PermissionLevel.WRITE,
        PermissionLevel.ADMIN,
    )


def test_security_request():
    request = SecurityRequest(
        action="read_file",
        permission=PermissionLevel.READ,
        parameters={
            "path": "test.txt",
        },
    )

    assert request.action == "read_file"
    assert request.permission == PermissionLevel.READ


def test_security_validator_allows():
    manager = PermissionManager(
        PermissionLevel.READ
    )

    validator = SecurityValidator(
        manager
    )

    request = SecurityRequest(
        action="read_file",
        permission=PermissionLevel.READ,
        parameters={},
    )

    assert validator.validate(request) is True


def test_security_validator_denies():
    manager = PermissionManager(
        PermissionLevel.READ
    )

    validator = SecurityValidator(
        manager
    )

    request = SecurityRequest(
        action="write_file",
        permission=PermissionLevel.WRITE,
        parameters={},
    )

    with pytest.raises(SecurityError):
        validator.validate(request)


def test_confirmation_manager():
    manager = ConfirmationManager(
        enabled=True
    )

    assert not manager.requires_confirmation(
        PermissionLevel.READ
    )

    assert manager.requires_confirmation(
        PermissionLevel.WRITE
    )

    assert manager.requires_confirmation(
        PermissionLevel.EXECUTE
    )

    assert manager.requires_confirmation(
        PermissionLevel.ADMIN
    )


def test_confirmation_disabled():
    manager = ConfirmationManager(
        enabled=False
    )

    assert not manager.requires_confirmation(
        PermissionLevel.ADMIN
    )