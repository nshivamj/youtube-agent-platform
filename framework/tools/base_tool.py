from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable
from pydantic import BaseModel


@dataclass
class ToolResult:
    success: bool
    data: Any = None
    error: str | None = None
    metadata: dict = field(default_factory=dict)


class BaseTool(ABC):
    """Interface every tool must implement. Local and MCP tools are interchangeable."""

    name: str = ""
    description: str = ""
    requires_approval: bool = False

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult: ...

    def to_adk_function(self) -> Callable:
        """Wrap execute() as a plain callable ADK can register as a tool."""
        tool = self

        def _fn(**kwargs):
            result = tool.execute(**kwargs)
            if result.success:
                return result.data
            raise RuntimeError(result.error or "Tool execution failed")

        _fn.__name__ = self.name
        _fn.__doc__ = self.description
        return _fn

    def to_adk_tool(self):
        """Legacy alias — kept for backward compatibility."""
        return self.to_adk_function()
