"""MCP Execution Client — stub for calling tools on remote MCP servers over HTTP.

Current state: Tool execution is handled transparently by ADK's McpToolset;
Gemini triggers the call and ADK sends it over the stdio pipe.

Future: When bypassing ADK (e.g. for batch jobs or server-to-server calls),
this client will call a remote MCP server's tools/call endpoint directly.
"""


def call_tool(server_url: str, tool_name: str, arguments: dict) -> dict:
    """Execute *tool_name* on a remote MCP server and return the result.

    Args:
        server_url: Base URL of the remote MCP server.
        tool_name:  Name of the tool to invoke.
        arguments:  Tool input arguments as a dict.

    Returns:
        The tool result dict as returned by the MCP server.
    """
    raise NotImplementedError(
        "Direct MCP tool execution not yet implemented. "
        "Tool calls are currently handled by ADK's McpToolset."
    )
