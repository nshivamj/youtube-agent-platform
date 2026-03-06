"""
Control Testing Agent — Standalone Entrypoint
=============================================

Usage:
    python -m control_testing.main

Or to start the ADK web UI:
    adk web control_testing.main:root_agent

The agent accepts natural-language requests such as:
  "Check if alice, bob, carol, and dave have access to Salesforce."
  "Run entitlement control test for Jira with users: alice, eve, ghost_user."
"""
import os
from google.adk.agents import LlmAgent
from control_testing.workflow import control_testing_workflow


def build_root_agent() -> LlmAgent:
    """
    Thin entry-point agent that parses the user's request and hands off
    to the control_testing_workflow.
    """
    return LlmAgent(
        name="control_testing_root",
        model="gemini-2.0-flash",
        instruction="""
You are the entry point for the Entitlement Control Testing platform.

When the user provides an entitlement test request, extract:
  - app_name : the application to test
  - users    : the list of user IDs to verify

Then delegate IMMEDIATELY to the control_testing_workflow sub-agent.
Do NOT attempt to do any analysis yourself.

If the user's request is unclear, ask ONE clarifying question:
  "Please provide the application name and the list of user IDs to test."

Example valid requests:
  "Check if alice, bob, carol have access to Salesforce."
  "Run entitlement test for Jira: users alice, dave, eve, ghost_user."
        """,
        sub_agents=[control_testing_workflow],
    )


# ADK discovers this as the root agent when running `adk web control_testing.main`
root_agent = build_root_agent()


if __name__ == "__main__":
    import asyncio
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Set GOOGLE_API_KEY in your environment or .env file before running."
        )

    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="control_testing",
        session_service=session_service,
    )

    async def _run():
        print("\nControl Testing Agent ready.")
        print("Example: 'Check if alice, bob, carol, svc_batch have access to Salesforce.'\n")

        from google.adk.sessions import Session
        from google.genai.types import Content, Part

        session: Session = await session_service.create_session(
            app_name="control_testing",
            user_id="auditor",
        )

        user_input = input("Enter your control test request: ").strip()
        if not user_input:
            user_input = (
                "Check if alice, bob, carol, svc_batch, and ghost_user "
                "have access to Salesforce."
            )

        print(f"\nRunning: {user_input}\n")
        print("=" * 60)

        async for event in runner.run_async(
            user_id="auditor",
            session_id=session.id,
            new_message=Content(parts=[Part(text=user_input)], role="user"),
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text)

    asyncio.run(_run())
