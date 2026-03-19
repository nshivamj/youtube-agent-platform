from framework.tools.base_tool import BaseTool

_mcp: dict[str, BaseTool] = {}


def register(tool: BaseTool) -> None:
    _mcp[tool.name] = tool


def get(name: str) -> BaseTool | None:
    return _mcp.get(name)


def list_all() -> list[str]:
    return list(_mcp.keys())


def get_many(names: list[str]) -> list[BaseTool]:
    return [_mcp[n] for n in names if n in _mcp]
