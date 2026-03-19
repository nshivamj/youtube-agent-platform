import json
import logging
import time
from pathlib import Path
from datetime import datetime
from typing import Any
from framework.callbacks.base_callback import BaseCallback

logger = logging.getLogger("platform.observability")
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


class ObservabilityTracker(BaseCallback):
    """Consumes callback events and produces structured logs.
    Every agent action becomes a queryable audit record."""

    def __init__(self):
        self._log_file = LOG_DIR / f"platform_{datetime.now().strftime('%Y%m%d')}.jsonl"

    def _write(self, event_type: str, data: dict):
        record = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            **data
        }
        with open(self._log_file, "a") as f:
            f.write(json.dumps(record) + "\n")

    async def on_agent_start(self, agent_name, context):
        self._write("agent_start", {"agent": agent_name})

    async def on_tool_call(self, tool_name, input, context):
        self._write("tool_call", {"tool": tool_name, "agent": context.get("agent_name")})

    async def on_tool_result(self, tool_name, result, context):
        self._write("tool_result", {"tool": tool_name, "success": True})

    async def on_agent_complete(self, agent_name, output, context):
        self._write("agent_complete", {"agent": agent_name})

    async def on_error(self, agent_name, error, context):
        self._write("error", {"agent": agent_name, "error": str(error)})


# ---------------------------------------------------------------------------
# Lightweight functional tracker — used by framework callbacks and factory
# ---------------------------------------------------------------------------

class _Tracker:
    """Append-only JSON-lines tracer for tool calls and agent events."""

    TRACES_DIR = Path("reports/traces")

    def __init__(self):
        self.TRACES_DIR.mkdir(parents=True, exist_ok=True)
        self._tool_calls_path = self.TRACES_DIR / "tool_calls.jsonl"
        self._agent_events_path = self.TRACES_DIR / "agent_events.jsonl"

    def log_tool_call(self, agent: str, tool: str, success: bool, duration_ms: float) -> None:
        self._append(self._tool_calls_path, {
            "ts": time.time(), "agent": agent, "tool": tool,
            "success": success, "duration_ms": duration_ms,
        })

    def log_agent_event(self, event_type: str, agent: str, payload: dict[str, Any] | None = None) -> None:
        self._append(self._agent_events_path, {
            "ts": time.time(), "event_type": event_type,
            "agent": agent, "payload": payload or {},
        })

    @staticmethod
    def _append(path: Path, record: dict) -> None:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")


# Module-level singleton
tracker = _Tracker()
