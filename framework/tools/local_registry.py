from framework.tools.base_tool import BaseTool

_local: dict[str, BaseTool] = {}


def register(tool: BaseTool) -> None:
    _local[tool.name] = tool


def get(name: str) -> BaseTool | None:
    return _local.get(name)


def list_all() -> list[str]:
    return list(_local.keys())


def get_many(names: list[str]) -> list[BaseTool]:
    return [_local[n] for n in names if n in _local]
