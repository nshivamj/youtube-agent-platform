"""MCP Discovery Client — stub for querying remote MCP servers over HTTP.

Current state: Tool discovery happens automatically via ADK's McpToolset
over the stdio subprocess pipe (no HTTP needed).

Future: When MCP servers are deployed as shared remote services (SSE or
streamable-HTTP transport), this client will fetch their tool schemas
without spawning a subprocess.
"""


def discover_tools(server_url: str) -> list[dict]:
    """Return the tool schemas advertised by a remote MCP server.

    Args:
        server_url: Base URL of the remote MCP server (e.g. http://localhost:8001).

    Returns:
        List of tool schema dicts as returned by the MCP tools/list endpoint.
    """
    raise NotImplementedError(
        "Remote MCP tool discovery not yet implemented. "
        "Use McpToolset with StdioServerParameters or SseConnectionParams."
    )
