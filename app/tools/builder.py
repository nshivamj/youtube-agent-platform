"""Tool builder — future home for composite and derived tool construction.

Planned use cases:
    - Wrap an ADK agent as a callable tool (agent-as-tool pattern)
    - Combine multiple MCP toolsets into a unified toolset
    - Inject shared runtime context into tool calls
"""


def build_agent_tool(agent_name: str):
    """Wrap a registered agent as a callable tool.

    Not yet implemented — placeholder for the agent-as-tool pattern.
    """
    raise NotImplementedError(
        f"agent-as-tool is not yet implemented (requested: '{agent_name}')"
    )
