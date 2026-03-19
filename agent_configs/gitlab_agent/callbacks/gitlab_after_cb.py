from session_manager import session_mgr


def gitlab_after_cb(callback_context) -> None:
    """Agent-specific after-agent callback. Handles errors and persists last op."""
    # Try to extract output from state or response
    output = callback_context.state.get("gitlab_agent_output")
    if output and hasattr(output, "success") and not output.success:
        callback_context.state["gitlab_last_error"] = getattr(output, "error", "Unknown error")

    operation = None
    if output and hasattr(output, "operation"):
        operation = output.operation

    if operation:
        session_mgr.set("user:last_gitlab_operation", operation)

    return None
