"""
Entitlement Callback — agent-tool policy gate.

Enforces which tools each agent is authorised to call at runtime.
Fires inside the callback pipeline on every tool invocation, before the tool
executes, so no unauthorised call ever reaches the tool implementation.

Policy is defined as AGENT_TOOL_POLICY below — a plain dict that maps each
agent name to the exact set of tool names it may call.  Adding a new agent or
expanding its surface is a one-line edit here; agent files stay unchanged.

To extend:
  - Add a new agent key with the tools it needs.
  - An empty list [] means the agent has NO tool access (e.g. planner agents).
  - Omitting an agent entirely will also block all tool calls for that agent
    (safe-by-default behaviour).
"""

import logging
from framework.callbacks.base_callback import BaseCallback

logger = logging.getLogger("platform.entitlement")

# ---------------------------------------------------------------------------
# Policy table — agent_name → allowed tool names
# ---------------------------------------------------------------------------
AGENT_TOOL_POLICY: dict[str, list[str]] = {
    # YouTube analysis pipeline
    "analyzer_agent": [
        "get_watch_summary",
        "get_shorts_ratio",
        "get_top_channels",
        "get_watch_by_hour",
        "get_binge_sessions",
    ],
    "insights_agent": [
        "save_report",
    ],

    # Control testing pipeline
    "control_test_executor": [
        "check_user_entitlements",
    ],
    "control_test_reporter": [],   # no tools — reads history only
    "control_test_planner":  [],   # no tools — planner only
    "control_test_reviewer": [],   # no tools — reviewer only

    # Routing / orchestration — no direct tool access
    "coordinator_agent": [],
    "planner_agent":     [],
}


class EntitlementCallback(BaseCallback):
    """Blocks any tool call that is not in the agent's declared policy.

    Raises PermissionError if the agent is not authorised — the AgentRuntime
    will surface this as an error event and stop that execution branch.
    """

    async def on_tool_call(self, tool_name: str, input: dict, context: dict):
        agent_name = context.get("agent_name", "unknown")

        if agent_name not in AGENT_TOOL_POLICY:
            logger.warning(
                f"[EntitlementCallback] Unknown agent '{agent_name}' attempted "
                f"to call '{tool_name}' — blocked (not in policy)."
            )
            raise PermissionError(
                f"Agent '{agent_name}' has no tool policy defined. "
                f"Call to '{tool_name}' denied."
            )

        allowed = AGENT_TOOL_POLICY[agent_name]
        if tool_name not in allowed:
            logger.warning(
                f"[EntitlementCallback] Agent '{agent_name}' is NOT authorised "
                f"to call '{tool_name}'. Allowed: {allowed}"
            )
            raise PermissionError(
                f"Agent '{agent_name}' is not authorised to call '{tool_name}'."
            )

        logger.debug(
            f"[EntitlementCallback] '{agent_name}' → '{tool_name}' allowed."
        )
