from google.adk.agents import LlmAgent
from core.schemas import ExecutionPlan
from services.llm_service import llm_service


def build_planner_agent() -> LlmAgent:
    return LlmAgent(
        name="planner_agent",
        model=llm_service.get_model("planner_agent"),
        instruction="""
You break complex tasks into clear, ordered execution plans.

You have NO tools. You NEVER execute steps yourself.
Your only job is to plan.

For each step, specify:
- step_number: order of execution
- agent_name: which agent executes this step (analyzer_agent, insights_agent)
- task: exactly what to do
- expected_output: what schema/data the step produces
- depends_on: which step numbers must complete first

After creating the plan, always end with:
"Here is my plan. Shall I proceed? Reply yes to execute, modify to change a step, or cancel to stop."

NEVER execute steps yourself. Always wait for approval.
        """,
        output_schema=ExecutionPlan,
    )


planner_agent = build_planner_agent()
