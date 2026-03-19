"""Entry point for the new modular agentic platform.

Run with:
    adk web              # launches the ADK web UI
    python main_platform.py   # runs a quick smoke-test prompt
"""
import asyncio
import os
import sys

from dotenv import load_dotenv

load_dotenv()

from session_manager import session_mgr
from framework.factory import Factory
from framework.runtime import Runtime
from google.adk.sessions import InMemorySessionService

# Initialise scoped app config from env
session_mgr.init_app_scope()

# Build the agent graph
coordinator = Factory().bootstrap()

# Build runtime (runner is accessible at runtime.runner for adk web)
runtime = Runtime(coordinator, InMemorySessionService())


async def _smoke_test(prompt: str) -> None:
    import uuid
    user_id = "smoke-test-user"
    session_id = str(uuid.uuid4())
    response = await runtime.run(prompt, user_id, session_id)
    print("Response:", response)


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "List the last 5 commits on main"
    asyncio.run(_smoke_test(prompt))
