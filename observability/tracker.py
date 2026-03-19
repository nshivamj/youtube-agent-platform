import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger("platform.observability")


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


# Module-level singleton used by functional callbacks
tracker = _Tracker()
