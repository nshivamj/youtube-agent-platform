"""Shared default narration callback (observer, before_model)."""
import logging

logger = logging.getLogger("platform.callbacks")


NARRATION_MAP = {
    "gitlab_agent": "Only call a tool when the user explicitly asks for GitLab data. For greetings or general questions, just reply with text.",
}


def narration_cb(callback_context):
    """Append narration style to system instruction based on agent name."""
    agent_name = getattr(callback_context, "agent_name", "") or ""
    narration = NARRATION_MAP.get(agent_name)
    if narration:
        logger.info(f"📝 Setting behavior for {agent_name}")
    if not narration:
        return None

    # Append to system instruction if the llm_request is accessible
    llm_request = getattr(callback_context, "llm_request", None)
    if llm_request and hasattr(llm_request, "config") and llm_request.config:
        existing = getattr(llm_request.config, "system_instruction", "") or ""
        llm_request.config.system_instruction = (
            f"{existing}\n\n{narration}".strip() if existing else narration
        )

    return None
