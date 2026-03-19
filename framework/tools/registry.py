"""Tool registry -- the only place that knows about ADK's FunctionTool.

Decorating a function with @tool() wraps it as an ADK FunctionTool and
registers it by name. Use get_many(names) to retrieve them for an agent.

FunctionTool extracts name from fn.__name__, description from docstring,
and parameters + types from type hints. Keep those accurate.
@tool returns the original function unchanged so modules can still call
their own functions directly in tests without going through ADK.
"""

from google.adk.tools import FunctionTool
from typing import Callable

_registry: dict[str, FunctionTool] = {}


def tool(*, requires_approval: bool = False):
    """Decorator that wraps a function as an ADK FunctionTool and registers it."""
    def decorator(fn: Callable) -> Callable:
        _registry[fn.__name__] = FunctionTool(fn, require_confirmation=requires_approval)
        return fn  # return the original fn so callers can still invoke it directly
    return decorator


def get_many(names: list[str]) -> list[FunctionTool]:
    """Return the registered FunctionTools for the given names, in order."""
    missing = [n for n in names if n not in _registry]
    if missing:
        raise KeyError(f"Tools not registered: {missing}. Did you import tools.all_tools?")
    return [_registry[n] for n in names]
