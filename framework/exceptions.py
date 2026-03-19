"""Framework exceptions for governance enforcement."""


class PermissionDeniedError(Exception):
    def __init__(self, agent_name: str, tool_name: str = "", reason: str = ""):
        self.agent_name = agent_name
        self.tool_name = tool_name
        self.reason = reason
        msg = f"Permission denied for agent '{agent_name}'"
        if tool_name:
            msg += f" on tool '{tool_name}'"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class ApprovalRequiredError(Exception):
    def __init__(self, agent_name: str, tool_name: str, reason: str = ""):
        self.agent_name = agent_name
        self.tool_name = tool_name
        self.reason = reason
        msg = f"Approval required for agent '{agent_name}' to use tool '{tool_name}'"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class ValidationError(Exception):
    def __init__(self, agent_name: str, errors: list[str] = None, reason: str = ""):
        self.agent_name = agent_name
        self.errors = errors or []
        self.reason = reason
        msg = f"Validation failed for agent '{agent_name}'"
        if reason:
            msg += f": {reason}"
        if self.errors:
            msg += f" [{', '.join(self.errors)}]"
        super().__init__(msg)


class MCPToolError(Exception):
    def __init__(self, tool_name: str, reason: str = "", agent_name: str = ""):
        self.tool_name = tool_name
        self.reason = reason
        self.agent_name = agent_name
        msg = f"MCP tool error for '{tool_name}'"
        if agent_name:
            msg += f" (agent: {agent_name})"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
