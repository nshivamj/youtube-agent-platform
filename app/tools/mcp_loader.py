"""MCP tool loader — maps tool names to McpToolset instances.

Agents declare tools by name in their YAML config (e.g. "github_mcp").
This module is the ONLY place that knows which name → which MCP server script.

To add a new MCP server:
    1. Add its entry script path to _MCP_REGISTRY below.
    2. No changes needed in agent code or orchestrator.
"""

import sys
from pathlib import Path

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp.client.stdio import StdioServerParameters

_ROOT = Path(__file__).parent.parent.parent

# Registry: logical tool name → path to MCP server entry script
_MCP_REGISTRY: dict[str, Path] = {
    "github_mcp": _ROOT / "run_mcp_github.py",
    # "jira_mcp":   _ROOT / "run_mcp_jira.py",   ← add future servers here
}


def load(tool_name: str) -> McpToolset:
    """Return a McpToolset that spawns the matching MCP server subprocess.

    Args:
        tool_name: Logical name from agent YAML (e.g. "github_mcp").

    Raises:
        ValueError: If tool_name is not registered.
        FileNotFoundError: If the server script does not exist on disk.
    """
    script = _MCP_REGISTRY.get(tool_name)
    if script is None:
        known = list(_MCP_REGISTRY)
        raise ValueError(f"Unknown MCP tool: '{tool_name}'. Registered: {known}")
    if not script.exists():
        raise FileNotFoundError(f"MCP server script missing: {script}")

    # Strip the _mcp suffix for the tool name prefix
    # e.g. "github_mcp" → tools are prefixed "github_"
    prefix = tool_name.removesuffix("_mcp")

    return McpToolset(
        connection_params=StdioServerParameters(
            command=sys.executable,
            args=[str(script)],
        ),
        tool_name_prefix=prefix,
    )
