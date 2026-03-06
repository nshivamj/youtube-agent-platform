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
