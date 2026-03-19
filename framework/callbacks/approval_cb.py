"""Shared default approval callback (controller, before_tool)."""
import os
from observability.tracker import tracker


def approval_cb(callback_context):
    """Gate write tools behind human approval unless AUTO_APPROVE=true."""
    tool = getattr(callback_context, "tool", None)
    requires_approval = getattr(tool, "requires_approval", False) if tool else False

    if not requires_approval:
        return None

    auto_approve = os.getenv("AUTO_APPROVE", "false").lower()
    if auto_approve == "true":
        agent_name = getattr(callback_context, "agent_name", "unknown")
        tool_name = getattr(tool, "name", "unknown") if tool else "unknown"
        tracker.log_agent_event(
            "auto_approved",
            agent_name,
            {"tool": tool_name, "warning": "AUTO_APPROVE bypassed confirmation"},
        )
        return None

    # Return a content block asking for confirmation
    tool_name = getattr(tool, "name", "this tool") if tool else "this tool"
    tool_args = getattr(callback_context, "tool_call_args", {}) or {}

    try:
        from google.genai import types as genai_types
        msg = (
            f"This action requires approval.\n"
            f"Tool: **{tool_name}**\n"
            f"Arguments: {tool_args}\n\n"
            f"Please confirm (yes/no)."
        )
        return genai_types.Content(
            role="model",
            parts=[genai_types.Part(text=msg)],
        )
    except ImportError:
        return None
