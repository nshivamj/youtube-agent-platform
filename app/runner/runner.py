"""ADK Runner — the single place in the platform that touches Google ADK Runner.

All other modules interact with agents through run_agent(); none import ADK directly.
"""

import asyncio
from typing import Any

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agents import registry
from app.tools.loader import load_tools


def run_agent(
    agent_name: str,
    prompt: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run a named agent synchronously and return a normalized result dict.

    Args:
        agent_name: Must match a YAML file in agents-config/.
        prompt:     User message to send to the agent.
        context:    Optional extra key/value pairs (reserved for future use).

    Returns::

        {"status": "success", "message": "...", "data": {"text": "..."}}
        {"status": "error",   "message": "...", "data": {}}
    """
    return asyncio.run(_run_async(agent_name, prompt, context or {}))


# ---------------------------------------------------------------------------
# Internal async implementation
# ---------------------------------------------------------------------------

async def _run_async(
    agent_name: str,
    prompt: str,
    context: dict[str, Any],
) -> dict[str, Any]:
    agent_def = registry.get(agent_name)
    tools = load_tools(agent_def)

    adk_agent = Agent(
        name=agent_def.name,
        model=agent_def.model,
        description=agent_def.description,
        instruction=agent_def.instruction,
        tools=tools,
    )

    session_service = InMemorySessionService()
    runner = Runner(
        agent=adk_agent,
        app_name=agent_def.name,
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name=agent_def.name,
        user_id="default_user",
    )

    message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    response_text = ""
    async for event in runner.run_async(
        user_id="default_user",
        session_id=session.id,
        new_message=message,
    ):
        if event.usage_metadata:
            u = event.usage_metadata
            print(
                f"[usage] model={event.model_version or agent_def.model}  "
                f"prompt_tokens={u.prompt_token_count}  "
                f"output_tokens={u.candidates_token_count}  "
                f"total_tokens={u.total_token_count}"
            )
        if event.is_final_response() and event.content and event.content.parts:
            response_text = event.content.parts[0].text or ""
            break

    return {
        "status": "success",
        "message": "Agent completed successfully.",
        "data": {"text": response_text},
    }
