"""Shared default before-agent callback (controller)."""
from session_manager import session_mgr


def before_agent_cb(callback_context):
    """
    1. Permission check — if allowed_agents != '*', block unlisted agents.
    2. Session injection — write user:goals into callback_context.state.
    """
    agent_name = getattr(callback_context, "agent_name", "") or ""

    # 1. Permission check
    allowed = session_mgr.get("app:allowed_agents", "*")
    if allowed != "*":
        permitted = [a.strip() for a in allowed.split(",")]
        if agent_name not in permitted:
            try:
                from google.genai import types as genai_types
                return genai_types.Content(
                    role="model",
                    parts=[genai_types.Part(text=f"Agent '{agent_name}' is not permitted.")],
                )
            except ImportError:
                pass  # ADK not installed yet — skip blocking during tests

    # 2. Session injection
    goals = session_mgr.get("user:goals")
    if goals:
        callback_context.state["user_goals"] = goals

    return None
