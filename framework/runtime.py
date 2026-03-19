"""Runtime: wraps ADK Runner, manages session lifecycle."""
import asyncio
from uuid import uuid4

from google.adk.runners import Runner
from google.genai import types as genai_types

from framework.execution_context import ExecutionContext
from session_manager import session_mgr


class Runtime:
    def __init__(self, coordinator, session_service):
        self.runner = Runner(
            agent=coordinator,
            app_name="agentic-platform",
            session_service=session_service,
        )

    async def run(self, user_message: str, user_id: str, session_id: str) -> str:
        ctx = ExecutionContext(
            run_id=str(uuid4()),
            session_id=session_id,
            user_id=user_id,
            agent_id="coordinator_agent",
            tool_mode=session_mgr.get("app:tool_mode", "local"),
        )

        session_mgr.get_or_create(user_id, session_id)

        content = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=user_message)],
        )

        response_text = ""
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                response_text = "".join(
                    p.text for p in event.content.parts if hasattr(p, "text")
                )

        # Cleanup
        session_mgr.clear_session_scope()

        return response_text
