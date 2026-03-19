"""Functional callback system — used by framework/factory.py.

SHARED_REGISTRY maps callback names (referenced in agent YAML files) to
their callables. compose() resolves a list of names and agent-specific
functions into a single chained callable for LlmAgent.
"""
from typing import Callable

from framework.callbacks.before_agent_cb import before_agent_cb
from framework.callbacks.after_agent_cb import after_agent_cb
from framework.callbacks.narration_cb import narration_cb
from framework.callbacks.logging_cb import logging_cb
from framework.callbacks.approval_cb import approval_cb
from framework.callbacks.tool_state_cb import tool_state_cb

SHARED_REGISTRY: dict[str, Callable] = {
    "before_agent_cb": before_agent_cb,
    "after_agent_cb": after_agent_cb,
    "narration_cb": narration_cb,
    "logging_cb": logging_cb,
    "approval_cb": approval_cb,
    "tool_state_cb": tool_state_cb,
}


def compose(
    names: list[str],
    agent_specific: list[Callable] | None = None,
) -> Callable | None:
    """Resolve callback names from SHARED_REGISTRY and append agent_specific callables.

    Returns None (no callbacks), a single callable, or a wrapper that calls
    each in order and returns the first non-None result.
    """
    resolved: list[Callable] = []

    for name in names:
        if name not in SHARED_REGISTRY:
            raise KeyError(
                f"Unknown shared callback '{name}'. Available: {list(SHARED_REGISTRY)}"
            )
        resolved.append(SHARED_REGISTRY[name])

    if agent_specific:
        resolved.extend(agent_specific)

    if not resolved:
        return None
    if len(resolved) == 1:
        return resolved[0]

    callbacks = list(resolved)

    def _composed(callback_context):
        for cb in callbacks:
            result = cb(callback_context)
            if result is not None:
                return result
        return None

    return _composed
