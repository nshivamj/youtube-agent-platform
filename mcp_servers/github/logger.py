"""Structured JSON logger for MCP tool calls."""

import json
import logging
import sys
import time
from contextlib import contextmanager
from typing import Any, Generator

_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("%(message)s"))

logger = logging.getLogger("github_mcp")
logger.setLevel(logging.DEBUG)
logger.addHandler(_handler)
logger.propagate = False


def _emit(level: str, tool: str, **fields: Any) -> None:
    record = {"level": level, "tool": tool, **fields}
    msg = json.dumps(record, default=str)
    getattr(logger, level.lower(), logger.info)(msg)


@contextmanager
def tool_span(tool_name: str, inputs: dict) -> Generator[None, None, None]:
    """Context manager that logs start, end, latency and any errors."""
    _emit("info", tool_name, event="call_start", inputs=inputs)
    t0 = time.perf_counter()
    try:
        yield
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        _emit("info", tool_name, event="call_end", latency_ms=latency_ms)
    except Exception as exc:
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        _emit("error", tool_name, event="call_error", error=str(exc), latency_ms=latency_ms)
        raise
