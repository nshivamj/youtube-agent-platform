import asyncio
import logging

import httpx

from framework.tools.base_tool import ToolResult

logger = logging.getLogger("platform.mcp_client")


class MCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def call_tool(self, tool_name: str, **kwargs) -> ToolResult:
        max_retries = 3
        last_error: str | None = None

        async with httpx.AsyncClient() as client:
            for attempt in range(max_retries):
                try:
                    response = await client.post(
                        f"{self.base_url}/call/{tool_name}",
                        json=kwargs,
                        timeout=30.0,
                    )
                    response.raise_for_status()
                    data = response.json()
                    return ToolResult(
                        success=True,
                        data=data,
                        metadata={"source": "mcp"},
                    )
                except (httpx.HTTPError, httpx.StreamError) as exc:
                    last_error = str(exc)
                    logger.warning(
                        "MCP call_tool %s attempt %d failed: %s",
                        tool_name, attempt + 1, last_error,
                    )
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)

        return ToolResult(
            success=False,
            data=None,
            error=f"MCP call failed after {max_retries} retries: {last_error}",
            metadata={"source": "mcp"},
        )

    async def health_check(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    timeout=10.0,
                )
                return response.status_code == 200
        except (httpx.HTTPError, httpx.StreamError):
            return False
