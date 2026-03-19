"""GitHub MCP tools — wraps the project's own MCP server via McpToolset.

When TOOL_MODE=mcp, the registry uses this instead of the local version.
The McpToolset spawns run_mcp_github.py as a subprocess (stdio transport).
"""

import sys
from pathlib import Path

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp.client.stdio import StdioServerParameters

_ROOT = Path(__file__).parent.parent.parent.parent


def get_github_mcp_toolset() -> McpToolset:
    """Return a McpToolset that connects to the project's GitHub MCP server."""
    return McpToolset(
        connection_params=StdioServerParameters(
            command=sys.executable,
            args=[str(_ROOT / "run_mcp_github.py")],
        ),
    )
