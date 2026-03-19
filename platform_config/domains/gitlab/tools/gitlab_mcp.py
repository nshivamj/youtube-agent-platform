"""GitLab MCP tool — wraps GitLabTool with MCP transport and local fallback."""

from framework.tools.mcp.mcp_client import MCPClient
from framework.tools.mcp.mcp_tool import MCPTool
from platform_config.domains.gitlab.tools.gitlab_local import GitLabTool


def register_gitlab_mcp_tools(mcp_base_url: str) -> MCPTool:
    local_tool = GitLabTool()
    client = MCPClient(mcp_base_url)
    return MCPTool(
        name="gitlab",
        description="GitLab operations tool (MCP-backed with local fallback)",
        schema=local_tool.get_schema(),
        mcp_client=client,
        local_fallback=local_tool,
    )
