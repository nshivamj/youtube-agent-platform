"""Tool loader — resolves an agent's tool list into ADK-compatible tool objects.

Routing rules (by suffix convention):
    *_mcp    → McpToolset via mcp_loader
    *_local  → local Python callable (future)
    *_agent  → another agent wrapped as a tool (future)
"""

from typing import Any

from app.agents.definitions import AgentDefinition
from app.tools import local_loader, mcp_loader


def load_tools(agent_def: AgentDefinition) -> list[Any]:
    """Return a list of ADK tool objects for the given AgentDefinition."""
    tools: list[Any] = []

    for name in agent_def.tools:
        if name.endswith("_mcp"):
            tools.append(mcp_loader.load(name))

        elif name.endswith("_local"):
            tools.append(local_loader.load(name))

        elif name.endswith("_agent"):
            # Future: from app.tools import builder
            # tools.append(builder.build_agent_tool(name))
            raise NotImplementedError(f"Agent-as-tool not yet supported: '{name}'")

        else:
            raise ValueError(
                f"Cannot resolve tool '{name}'. "
                "Tool names must end with _mcp, _local, or _agent."
            )

    return tools
