"""after_tool_callback — logs every tool call to the observability tracker."""
import time
from google.adk.tools import BaseTool
from google.adk.agents.context import Context
from observability.tracker import tracker


def logging_cb(tool: BaseTool, args: dict, context: Context, response: dict) -> None:
    """Log tool call outcome to the append-only JSONL tracer."""
    agent_name = getattr(context, "agent_name", None) or "unknown"
    tracker.log_tool_call(
        agent=agent_name,
        tool=tool.name,
        success="error" not in (response or {}),
        duration_ms=0.0,  # ADK doesn't expose duration here; instrument externally if needed
    )
    return None  # pass response through unchanged
