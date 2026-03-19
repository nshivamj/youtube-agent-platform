import logging

from framework.tools.base_tool import BaseTool, ToolResult
from framework.tools.mcp.mcp_client import MCPClient

logger = logging.getLogger("platform.mcp_tool")


class MCPTool(BaseTool):
    def __init__(
        self,
        name: str,
        description: str,
        schema: dict,
        mcp_client: MCPClient,
        local_fallback: BaseTool | None = None,
        requires_approval: bool = False,
    ):
        self.name = name
        self.description = description
        self._schema = schema
        self._mcp_client = mcp_client
        self._local_fallback = local_fallback
        self.requires_approval = requires_approval

    async def execute(self, **kwargs) -> ToolResult:
        result = await self._mcp_client.call_tool(self.name, **kwargs)

        if result.success:
            return result

        if self._local_fallback is not None:
            logger.info(
                "MCP failed for %s, falling back to local: %s",
                self.name, result.error,
            )
            fallback_result = await self._local_fallback.execute(**kwargs)
            fallback_result.metadata["source"] = "local_fallback"
            return fallback_result

        return result

    def get_schema(self) -> dict:
        return self._schema
