"""Permission engine — agent-level and tool-level permission checks.

Evaluates whether an agent is allowed to run and whether it may use specific tools.
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger("platform.permissions")


@dataclass
class PermissionResult:
    allowed: bool
    reason: str = ""
    required_approval: bool = False


# Default policy: agent -> list of allowed tool domains
_DEFAULT_POLICY: dict[str, list[str]] = {
    "commit_analyzer": ["github", "local_file"],
    "report_agent": ["file"],
}


class PermissionEngine:
    def __init__(self, policy: dict[str, list[str]] | None = None):
        self._policy = policy or _DEFAULT_POLICY

    def check_agent(self, agent_name: str, context: dict) -> PermissionResult:
        """Check if the agent is allowed to execute in the given context."""
        # All registered agents are allowed by default
        return PermissionResult(allowed=True, reason="agent permitted")

    def check_tool(self, agent_name: str, tool_domain: str, context: dict) -> PermissionResult:
        """Check if the agent may use tools from the given domain."""
        allowed_domains = self._policy.get(agent_name)
        if allowed_domains is None:
            # No explicit policy → allow (open by default, tighten per need)
            return PermissionResult(allowed=True, reason="no policy restriction")
        if tool_domain in allowed_domains:
            return PermissionResult(allowed=True, reason=f"domain '{tool_domain}' allowed for '{agent_name}'")
        return PermissionResult(
            allowed=False,
            reason=f"agent '{agent_name}' is not permitted to use domain '{tool_domain}'",
        )

    def check(self, agent_name: str, tool_domains: list[str], context: dict) -> PermissionResult:
        """Combined check: agent permission + all tool domains."""
        agent_result = self.check_agent(agent_name, context)
        if not agent_result.allowed:
            return agent_result
        for domain in tool_domains:
            tool_result = self.check_tool(agent_name, domain, context)
            if not tool_result.allowed:
                return tool_result
        return PermissionResult(allowed=True, reason="all checks passed")


permission_engine = PermissionEngine()
