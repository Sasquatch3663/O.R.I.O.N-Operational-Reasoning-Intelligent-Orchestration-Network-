from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from orion.brain.reasoning import ReasoningResult


@dataclass
class PlanStep:
    """A single step in an ORION plan."""

    step_id: int
    action: str
    parameters: Dict[str, Any] = field(
        default_factory=dict
    )


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

    def create_plan(
        self,
        result: ReasoningResult,
    ) -> Plan:

        steps = []

        for index, action in enumerate(
            result.actions,
            start=1,
        ):
            steps.append(
                PlanStep(
                    step_id=index,
                    action=action.get(
                        "type",
                        "unknown",
                    ),
                    parameters=action.get(
                        "parameters",
                        {},
                    ),
                )
            )

        return Plan(steps=steps)