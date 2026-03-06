from google.adk.agents import LlmAgent
from agents.planner_agent import planner_agent


def build_coordinator_agent(workflow) -> LlmAgent:
    """Build coordinator with youtube_workflow and planner_agent.
    insights_agent is already inside youtube_workflow — ADK agents can only have one parent."""
    return LlmAgent(
        name="coordinator_agent",
        model="gemini-2.0-flash",
        instruction="""
You are the entry point for all user requests. Route to the right specialist.

Sub-agents available:
- youtube_workflow: for analysis requests and insight generation
  ("analyze my January", "how much Shorts did I watch?", "what are my habits?")
- planner_agent: for complex multi-step or ambiguous requests
  ("compare my last 3 months and tell me what to change")

Rules:
- One routing decision per request. Do not do the analysis yourself.
- Use youtube_workflow for all single-period analysis + recommendations.
- Use planner_agent for multi-step, comparative, or ambiguous requests.
- Respond in plain English. Never expose internal schemas to the user.
        """,
        sub_agents=[workflow, planner_agent],
    )
