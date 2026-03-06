from abc import ABC


class BaseCallback(ABC):
    """Interface all callbacks implement. Override only what you need."""

    async def on_agent_start(self, agent_name: str, context: dict): pass
    async def on_model_call(self, agent_name: str, prompt: str, context: dict): pass
    async def before_model_call(self, callback_context, llm_request): pass
    async def on_tool_call(self, tool_name: str, input: dict, context: dict): pass
    async def on_tool_result(self, tool_name: str, result, context: dict): pass
    async def on_agent_text(self, text: str, context: dict): pass
    async def on_agent_complete(self, agent_name: str, output, context: dict): pass
    async def on_error(self, agent_name: str, error: Exception, context: dict): pass
