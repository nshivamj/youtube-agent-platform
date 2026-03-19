import logging
import os

logger = logging.getLogger("platform.callbacks")


def gitlab_before_cb(callback_context) -> None:
    """Agent-specific before-agent callback. Injects GITLAB_DEFAULT_PROJECT."""
    default_project = os.getenv("GITLAB_DEFAULT_PROJECT", "")
    logger.info(f"🔧 Configuring GitLab agent — default project: {default_project or '(none)'}")
    callback_context.state["gitlab_default_project"] = default_project
    return None
