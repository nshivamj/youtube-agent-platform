def gitlab_after_cb(callback_context) -> None:
    """Agent-specific after-agent callback. Handles errors and persists last op."""
    output = callback_context.state.get("gitlab_agent_output")
    if output and hasattr(output, "success") and not output.success:
        callback_context.state["gitlab_last_error"] = getattr(output, "error", "Unknown error")

    if output and hasattr(output, "operation") and output.operation:
        callback_context.state["last_gitlab_operation"] = output.operation

    return None
