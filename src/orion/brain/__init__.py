from __future__ import annotations

from importlib import import_module
from typing import Any


__all__ = [
    "BrainEngine",
    "BrainResult",
    "UserInput",
    "Intent",
    "IntentAnalyzer",
    "IntentType",
    "BaseModelProvider",
    "ModelProviderError",
    "ModelRequest",
    "ModelResponse",
    "OllamaModelProvider",
    "create_model_provider",
    "Plan",
    "PlanStep",
    "Planner",
    "ReasoningContext",
    "ReasoningEngine",
    "ReasoningResult",
]


_LAZY_IMPORTS = {
    "BrainEngine": ("orion.brain.engine", "BrainEngine"),
    "BrainResult": ("orion.brain.engine", "BrainResult"),

    "UserInput": ("orion.brain.input", "UserInput"),

    "Intent": ("orion.brain.intent", "Intent"),
    "IntentAnalyzer": ("orion.brain.intent", "IntentAnalyzer"),
    "IntentType": ("orion.brain.intent", "IntentType"),

    "BaseModelProvider": ("orion.brain.model", "BaseModelProvider"),
    "ModelProviderError": ("orion.brain.model", "ModelProviderError"),
    "ModelRequest": ("orion.brain.model", "ModelRequest"),
    "ModelResponse": ("orion.brain.model", "ModelResponse"),

    "OllamaModelProvider": (
        "orion.brain.local_model",
        "OllamaModelProvider",
    ),

    "create_model_provider": (
        "orion.brain.providers",
        "create_model_provider",
    ),

    "Plan": ("orion.brain.planner", "Plan"),
    "PlanStep": ("orion.brain.planner", "PlanStep"),
    "Planner": ("orion.brain.planner", "Planner"),

    "ReasoningContext": (
        "orion.brain.reasoning",
        "ReasoningContext",
    ),
    "ReasoningEngine": (
        "orion.brain.reasoning",
        "ReasoningEngine",
    ),
    "ReasoningResult": (
        "orion.brain.reasoning",
        "ReasoningResult",
    ),
}


def __getattr__(name: str) -> Any:
    """
    Lazily resolve public Brain API objects.

    This prevents the package initializer from importing the entire
    Brain subsystem when a lower-level module such as
    ``orion.brain.intent`` is imported.
    """
    if name not in _LAZY_IMPORTS:
        raise AttributeError(
            f"module {__name__!r} has no attribute {name!r}"
        )

    module_name, attribute_name = _LAZY_IMPORTS[name]

    module = import_module(module_name)
    value = getattr(module, attribute_name)

    globals()[name] = value

    return value