from google.adk.agents import LlmAgent
from agents.planner_agent import planner_agent
from framework.workflow_registry import workflow_registry
from services.llm_service import llm_service


def build_coordinator_agent() -> LlmAgent:
    """Build coordinator from all registered workflows + planner_agent.
    Workflows self-register via workflow_registry — no manual edits here needed."""
    workflows = workflow_registry.all_workflows()
    routing_guide = workflow_registry.routing_summary()

    return LlmAgent(
        name="coordinator_agent",
        model=llm_service.get_model("coordinator_agent"),
        instruction=f"""
You are the entry point for all user requests. Route to the right specialist.

Sub-agents available:
{routing_guide}
- planner_agent: for complex multi-step, comparative, or ambiguous requests
  (e.g. "compare my last 3 months and tell me what to change")

Rules:
- One routing decision per request. Do not do the work yourself.
- Use planner_agent for requests that span multiple workflows or need decomposition.
- Respond in plain English. Never expose internal schemas to the user.
        """,
        sub_agents=[*workflows, planner_agent],
    )
