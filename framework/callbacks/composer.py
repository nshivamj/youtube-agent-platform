from framework.callbacks.base_callback import BaseCallback
from framework.callbacks.logging_callback import LoggingCallback
from framework.callbacks.tracing_callback import TracingCallback
from framework.callbacks.narration_callback import NarrationCallback
from observability.tracker import ObservabilityTracker


class CallbackComposer(BaseCallback):
    """Merges global + agent-specific callbacks into one pipeline.
    Runtime talks to this one object only."""

    def __init__(self, callbacks: list[BaseCallback] = None):
        self._callbacks = callbacks or [
            LoggingCallback(),
            TracingCallback(),
            NarrationCallback(),
            ObservabilityTracker(),
        ]

    async def on_agent_start(self, agent_name, context):
        for cb in self._callbacks:
            await cb.on_agent_start(agent_name, context)

    async def before_model_call(self, callback_context, llm_request):
        for cb in self._callbacks:
            await cb.before_model_call(callback_context, llm_request)

    async def on_tool_call(self, tool_name, input, context):
        for cb in self._callbacks:
            await cb.on_tool_call(tool_name, input, context)

    async def on_tool_result(self, tool_name, result, context):
        for cb in self._callbacks:
            await cb.on_tool_result(tool_name, result, context)

    async def on_agent_text(self, text, context):
        for cb in self._callbacks:
            await cb.on_agent_text(text, context)

    async def on_agent_complete(self, agent_name, output, context):
        for cb in self._callbacks:
            await cb.on_agent_complete(agent_name, output, context)

    async def on_error(self, agent_name, error, context):
        for cb in self._callbacks:
            await cb.on_error(agent_name, error, context)


composer = CallbackComposer()
