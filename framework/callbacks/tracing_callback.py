import time
from framework.callbacks.base_callback import BaseCallback


class TracingCallback(BaseCallback):
    def __init__(self):
        self._timings: dict[str, float] = {}
        self.traces: list[dict] = []

    async def on_agent_start(self, agent_name, context):
        self._timings[agent_name] = time.time()

    async def on_agent_complete(self, agent_name, output, context):
        elapsed = time.time() - self._timings.get(agent_name, time.time())
        self.traces.append({
            "agent": agent_name,
            "duration_ms": round(elapsed * 1000),
            "success": True
        })

    async def on_error(self, agent_name, error, context):
        elapsed = time.time() - self._timings.get(agent_name, time.time())
        self.traces.append({
            "agent": agent_name,
            "duration_ms": round(elapsed * 1000),
            "success": False,
            "error": str(error)
        })
