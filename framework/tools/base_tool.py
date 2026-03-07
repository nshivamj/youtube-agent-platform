from abc import ABC, abstractmethod
from pydantic import BaseModel


class BaseTool(ABC):
    """Interface every tool must implement. Local and MCP tools are interchangeable."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    async def execute(self, **kwargs) -> BaseModel: ...

    def to_adk_tool(self):
        """Convert to ADK-compatible tool format."""
        return self  # ADK accepts callables with __call__
