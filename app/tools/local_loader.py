"""Local tool loader — maps tool names to importable Python callables.

Agents declare local tools by name in their YAML config (e.g. "format_report_local").
This module is the ONLY place that knows which name → which Python function.

To add a new local tool:
    1. Define the function in a module under local_tools/.
    2. Add its dotted path to _LOCAL_REGISTRY below.
    3. No changes needed in agent code or runner.
"""

import importlib
from typing import Callable

# Registry: logical tool name → fully-qualified "module.function" path
_LOCAL_REGISTRY: dict[str, str] = {
    "format_report_local": "local_tools.formatter.format_report",
    # "send_notification_local": "local_tools.notifier.send_notification",
}


def load(tool_name: str) -> Callable:
    """Return the Python callable for a registered local tool.

    Args:
        tool_name: Logical name from agent YAML (e.g. "format_report_local").

    Raises:
        ValueError: If tool_name is not in the registry.
        ImportError: If the module cannot be imported.
        AttributeError: If the function does not exist in the module.
    """
    dotted = _LOCAL_REGISTRY.get(tool_name)
    if dotted is None:
        known = list(_LOCAL_REGISTRY)
        raise ValueError(f"Unknown local tool: '{tool_name}'. Registered: {known}")

    module_path, func_name = dotted.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, func_name)
