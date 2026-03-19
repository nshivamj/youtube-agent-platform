"""Shared default logging callback (observer, after_tool)."""
import time
from observability.tracker import tracker


def logging_cb(callback_context):
    """Log tool call outcome to tracker."""
    agent_name = getattr(callback_context, "agent_name", "") or "unknown"
    tool_name = getattr(callback_context, "tool_name", "") or "unknown"
    success = not bool(getattr(callback_context, "tool_exception", None))

    # duration_ms — best-effort from context or default
    duration_ms = getattr(callback_context, "duration_ms", 0.0)

    tracker.log_tool_call(agent_name, tool_name, success, duration_ms)
    return None
