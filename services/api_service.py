import httpx
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class APIService:
    """Shared HTTP client with auth, retry, and error handling.
    All MCP tool wrappers use this — never create their own httpx clients."""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=30.0
            )
        return self._client

    async def get(self, path: str, params: dict = {}) -> Any:
        client = await self._get_client()
        for attempt in range(3):
            try:
                resp = await client.get(path, params=params)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                if attempt == 2:
                    raise
                logger.warning(f"GET {path} attempt {attempt+1} failed: {e}")

    async def post(self, path: str, data: dict) -> Any:
        client = await self._get_client()
        for attempt in range(3):
            try:
                resp = await client.post(path, json=data)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                if attempt == 2:
                    raise
                logger.warning(f"POST {path} attempt {attempt+1} failed: {e}")

    async def close(self):
        if self._client:
            await self._client.aclose()
