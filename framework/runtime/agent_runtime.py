from google.adk.runners import Runner
from google.genai import types
from framework.callbacks.composer import CallbackComposer, composer
from framework.tools.resolver import resolver
from core.session_manager import session_manager
import logging
from typing import Callable

logger = logging.getLogger("platform.runtime")


class AgentRuntime:
    """Safety boundary for all agent execution.
    Flow: validate_input → compose_callbacks → inject_tools → execute → validate_output.
    Nothing runs ungoverned. Every action observable via callbacks.

    Pass a custom composer to add domain-specific callbacks (e.g. governance_composer
    for audit workflows that need approval gating + risk blocking).
    """

    def __init__(self, app_name: str = "youtube_platform", callbacks: CallbackComposer = None):
        self.app_name = app_name
        self._runners: dict = {}
        self.callbacks = callbacks or composer

    def _get_runner(self, agent) -> Runner:
        name = agent.name
        if name not in self._runners:
            self._runners[name] = Runner(
                agent=agent,
                app_name=self.app_name,
                session_service=session_manager.service,
            )
        return self._runners[name]

    async def execute_streaming(
        self,
        agent,
        user_id: str,
        session_id: str,
        message: str,
        stream_fn: Callable = None
    ):
        """Stream agent execution. Pushes text, tool calls, and results to stream_fn."""
        runner = self._get_runner(agent)
        content = types.Content(role="user", parts=[types.Part(text=message)])

        await self.callbacks.on_agent_start(agent.name, {"session_id": session_id})

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if not event.content or not event.content.parts:
                continue

            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    await self.callbacks.on_agent_text(part.text, {
                        "agent_name": agent.name,
                        "session_id": session_id
                    })
                    if stream_fn:
                        await stream_fn({"type": "text", "content": part.text, "agent": agent.name})

                if hasattr(part, "function_call"):
                    await self.callbacks.on_tool_call(
                        part.function_call.name,
                        dict(part.function_call.args),
                        {"agent_name": agent.name}
                    )
                    if stream_fn:
                        await stream_fn({
                            "type": "tool_start",
                            "tool": part.function_call.name,
                            "input": dict(part.function_call.args)
                        })

                if hasattr(part, "function_response"):
                    await self.callbacks.on_tool_result(
                        part.function_response.name,
                        part.function_response.response,
                        {"agent_name": agent.name}
                    )
                    if stream_fn:
                        await stream_fn({
                            "type": "tool_result",
                            "tool": part.function_response.name,
                        })

            if event.is_final_response():
                final_text = ""
                if event.content and event.content.parts:
                    final_text = event.content.parts[0].text if event.content.parts[0].text else ""
                await self.callbacks.on_agent_complete(agent.name, final_text, {})
                if stream_fn:
                    await stream_fn({"type": "done", "content": final_text})
                return final_text

    async def execute_with_approval(
        self,
        agent,
        user_id: str,
        session_id: str,
        message: str,
        stream_fn: Callable = None
    ) -> dict:
        """Run 1: execute until agent pauses for approval. Save state. Return."""
        result = await self.execute_streaming(agent, user_id, session_id, message, stream_fn)
        pending = session_manager.get("awaiting_approval", False)
        if pending:
            return {"status": "waiting_for_approval"}
        return {"status": "complete", "result": result}

    async def resume_after_approval(
        self,
        agent,
        user_id: str,
        session_id: str,
        decision: str,
        stream_fn: Callable = None
    ) -> dict:
        """Run 2: continue execution after human approves/rejects/modifies."""
        if decision == "cancel":
            session_manager.save("awaiting_approval", False)
            return {"status": "cancelled"}

        message = f"The user has approved. Decision: {decision}. Please continue."
        result = await self.execute_streaming(agent, user_id, session_id, message, stream_fn)
        return {"status": "complete", "result": result}


runtime = AgentRuntime()

# Governance runtime for audit/compliance workflows.
# Adds ApprovalCallback (agent pause-for-approval) + RiskCallback (block high-risk tools).
from framework.callbacks.composer import governance_composer  # noqa: E402

control_testing_runtime = AgentRuntime(callbacks=governance_composer)
