import json
import logging
from pathlib import Path
from datetime import datetime
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
