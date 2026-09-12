from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from orion.brain.reasoning import ReasoningResult
from orion.security import (
    ConfirmationManager,
    PermissionLevel,
)


@dataclass
class PlanStep:
    """A single step in an ORION plan."""

    step_id: int
    action: str
    parameters: Dict[str, Any] = field(
        default_factory=dict
    )
    permission: PermissionLevel = PermissionLevel.READ
    requires_confirmation: bool = False


@dataclass
class Plan:
    """Represents an ORION execution plan."""

    steps: List[PlanStep] = field(
        default_factory=list
    )


class Planner:
    """
    Converts reasoning results into executable plans.
    """

    def __init__(
        self,
        confirmation_manager: ConfirmationManager | None = None,
    ) -> None:
        self.confirmation_manager = (
            confirmation_manager
            or ConfirmationManager()
        )

    def create_plan(
        self,
        result: ReasoningResult,
    ) -> Plan:

        steps = []

        for index, action in enumerate(
            result.actions,
            start=1,
        ):
            action_type = action.get(
                "type",
                "unknown",
            )
            permission = self._permission_for(action_type)

            steps.append(
                PlanStep(
                    step_id=index,
                    action=action_type,
                    parameters=action.get(
                        "parameters",
                        {},
                    ),
                    permission=permission,
                    requires_confirmation=(
                        self.confirmation_manager
                        .requires_confirmation(permission)
                    ),
                )
            )

        return Plan(steps=steps)

    @staticmethod
    def _permission_for(
        action: str,
    ) -> PermissionLevel:
        """Return the minimum permission required for an action."""

        if action == "memory_store":
            return PermissionLevel.WRITE

        if action == "tool_request":
            return PermissionLevel.EXECUTE

        return PermissionLevel.READ
