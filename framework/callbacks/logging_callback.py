import logging
from framework.callbacks.base_callback import BaseCallback

logger = logging.getLogger("platform.agent")


class LoggingCallback(BaseCallback):
    async def on_agent_start(self, agent_name, context):
        logger.info(f"[START] {agent_name}")

    async def on_tool_call(self, tool_name, input, context):
        logger.info(f"[TOOL] {tool_name} | input={input}")

    async def on_tool_result(self, tool_name, result, context):
        logger.info(f"[RESULT] {tool_name} | ok")

    async def on_agent_complete(self, agent_name, output, context):
        logger.info(f"[DONE] {agent_name}")

    async def on_error(self, agent_name, error, context):
        logger.error(f"[ERROR] {agent_name}: {error}")
