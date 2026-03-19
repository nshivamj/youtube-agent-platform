"""after_tool_callback — persists selected tool outputs to session state.

Tools stay pure (no ToolContext imports). This callback is the single place
that decides what gets written to state and under which key.

Add entries to _PERSIST to include new tools. Format: tool_name -> state_key.
"""
import logging

logger = logging.getLogger("platform.callbacks")

# tool_name -> session state key
_PERSIST: dict[str, str] = {
    # GitLab
    "gitlab_list_commits":   "gitlab_commits",
    "gitlab_list_mrs":       "gitlab_mrs",
    "gitlab_list_pipelines": "gitlab_pipelines",
    # YouTube
    "get_watch_summary":     "watch_summary",
    "get_binge_sessions":    "binge_sessions",
    "get_top_channels":      "top_channels",
    # Entitlement
    "check_user_entitlements": "entitlement_result",
}


def tool_state_cb(tool, args, tool_context, tool_response) -> None:
    """Write tool output to session state if the tool is in _PERSIST."""
    tool_name = getattr(tool, "name", str(tool))
    key = _PERSIST.get(tool_name)
    if key:
        logger.info(f"💾 Saving {tool_name} results to session state['{key}']")
        tool_context.state[key] = tool_response
    else:
        logger.debug(f"   ⏭️  {tool_name} — no state persistence needed")
    return None
