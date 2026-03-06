import os
from dotenv import load_dotenv

load_dotenv()


class ToolRegistry:
    """Stores all available tool implementations keyed by domain.
    Reads TOOL_MODE from .env to decide local vs MCP."""

    def __init__(self):
        self._tools: dict[str, dict] = {}
        self.mode = os.getenv("TOOL_MODE", "local")

    def register(self, domain: str, mode: str, tool_instance):
        if domain not in self._tools:
            self._tools[domain] = {}
        self._tools[domain][mode] = tool_instance

    def get(self, domain: str):
        if domain not in self._tools:
            raise ValueError(f"No tools registered for domain: {domain}")
        available = self._tools[domain]
        if self.mode in available:
            return available[self.mode]
        # fallback to local if mcp not available
        return available.get("local")


registry = ToolRegistry()

# Register local tools
from framework.tools.local.youtube_local import YouTubeLocalTools
from framework.tools.local.file_local import FileLocalTools
from framework.tools.local.entitlement_local import EntitlementLocalTools

registry.register("youtube", "local", YouTubeLocalTools())
registry.register("file", "local", FileLocalTools())
registry.register("entitlement", "local", EntitlementLocalTools())

# Populate resolver with active tool callables (respects TOOL_MODE).
# Each tool class declares tool_names — registry reads the active mode instance
# and registers each method by name. Agents then declare exactly which names
# they need via resolver.declare(). No central DOMAIN_METHODS list needed.
from framework.tools.resolver import resolver as _resolver

for _domain in ["youtube", "file", "entitlement"]:
    _instance = registry.get(_domain)
    for _name in getattr(_instance, "tool_names", []):
        _fn = getattr(_instance, _name, None)
        if callable(_fn):
            _resolver.register_tool(_name, _fn)
