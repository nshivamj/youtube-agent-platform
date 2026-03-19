import json
import logging

logger = logging.getLogger("platform.callbacks")


def summary_before_cb(callback_context) -> None:
    """Inject gitlab_commits from state into the session for the summary agent."""
    commits = callback_context.state.get("gitlab_commits")
    if commits:
        # Serialize commits so the model can read them in context
        try:
            commit_text = json.dumps(commits, indent=2, default=str)
        except (TypeError, ValueError):
            commit_text = str(commits)
        callback_context.state["commit_data_for_summary"] = commit_text
        logger.info(f"📊 Injected {len(commits) if isinstance(commits, list) else '?'} commits for summary agent")
    else:
        callback_context.state["commit_data_for_summary"] = "No commit data available."
        logger.warning("⚠️  No gitlab_commits in state for summary agent")
    return None
