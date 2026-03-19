"""Tool registry — the only place that knows about ADK's FunctionTool.

Usage
-----
In a tool module:
    from framework.tools.registry import tool

    @tool()
    def my_tool(x: str) -> dict:
        """Does something. Returns: ..."""
        ...

    @tool(requires_approval=True)
    def my_write_tool(x: str) -> dict:
        """Creates something. Returns: ..."""
        ...

In the factory / agent:
    from framework.tools.registry import get_many

    tools = get_many(["my_tool", "my_write_tool"])

Notes
-----
- FunctionTool extracts name from fn.__name__, description from docstring,
  and parameters + types from type hints. Keep those accurate.
- @tool returns the original function unchanged so modules can still call
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
