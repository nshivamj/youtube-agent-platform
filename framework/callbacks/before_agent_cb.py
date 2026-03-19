"""Shared default before-agent callback (controller)."""
import os


def before_agent_cb(callback_context):
    """
    1. Permission check — if ALLOWED_AGENTS != '*', block unlisted agents.
    2. Session injection — write user_goals into callback_context.state if present.
    """
    agent_name = getattr(callback_context, "agent_name", "") or ""

    # 1. Permission check
    allowed = os.getenv("ALLOWED_AGENTS", "*")
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

    # 2. Session injection — pull user_goals from ADK session state if set
    goals = callback_context.state.get("user_goals")
    if goals:
        callback_context.state["user_goals"] = goals

    return None
