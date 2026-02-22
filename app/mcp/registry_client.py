"""MCP Registry Client — stub for future service-based MCP discovery.

Current state: MCP servers are hard-coded in app/tools/mcp_loader.py.

Future: This client will query a registry service (e.g. a config API or
service mesh) to discover available MCP servers dynamically at runtime,
without requiring code changes.
"""


def list_servers() -> list[str]:
    """Return the logical names of all registered MCP servers."""
    raise NotImplementedError(
        "Dynamic MCP registry not yet implemented. "
        "Add servers directly to app/tools/mcp_loader._MCP_REGISTRY."
    )
