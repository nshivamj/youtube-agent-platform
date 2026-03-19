import logging

logger = logging.getLogger("platform.callbacks")


def gitlab_after_cb(callback_context) -> None:
    """Agent-specific after-agent callback. Handles errors and persists last op."""
    logger.info("🔍 Reviewing GitLab agent results...")

    output = callback_context.state.get("gitlab_agent_output")
    if output and hasattr(output, "success") and not output.success:
        error = getattr(output, "error", "Unknown error")
        logger.warning(f"⚠️  GitLab error detected: {error}")
        callback_context.state["gitlab_last_error"] = error

    if output and hasattr(output, "operation") and output.operation:
        logger.info(f"📋 Last operation: {output.operation}")
        callback_context.state["last_gitlab_operation"] = output.operation

    return None
