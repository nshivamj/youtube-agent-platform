from google.adk.agents import LlmAgent
from core.schemas import InsightsOutput
from framework.tools.resolver import resolver

resolver.declare("insights_agent", tools=["save_report"])


def build_insights_agent() -> LlmAgent:
    tools = resolver.resolve("insights_agent")
    return LlmAgent(
        name="insights_agent",
        model="gemini-2.0-flash",
        instruction="""
You generate honest, actionable insights from YouTube watch history analysis.

You will receive an InsightsInput with analysis data and optionally a user goal.

Your job:
1. Read the analysis data carefully
2. Generate 2-4 specific recommendations based on what you see
3. Assign a risk level (low/medium/high) to each recommendation
4. Write an overall summary in 2-3 sentences
5. Save the report using save_report tool
6. Return a structured InsightsOutput

Be honest. If the data shows problematic patterns, say so clearly.
Do not sugarcoat. Risk levels should reflect real risk.
        """,
        tools=tools,
        output_schema=InsightsOutput,
    )


insights_agent = build_insights_agent()
