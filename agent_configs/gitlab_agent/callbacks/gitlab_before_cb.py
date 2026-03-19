import os


def gitlab_before_cb(callback_context) -> None:
    """Agent-specific before-agent callback. Injects GITLAB_DEFAULT_PROJECT."""
    default_project = os.getenv("GITLAB_DEFAULT_PROJECT", "")
    callback_context.state["gitlab_default_project"] = default_project
    return None
