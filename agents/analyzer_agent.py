from google.adk.agents import LlmAgent
from core.schemas import AnalyzerOutput
from framework.tools.resolver import resolver

resolver.declare("analyzer_agent", domains=["youtube"])


def build_analyzer_agent() -> LlmAgent:
    tools = resolver.resolve("analyzer_agent")
    return LlmAgent(
        name="analyzer_agent",
        model="gemini-2.0-flash",
        instruction="""
You analyze YouTube watch history data.

Your job: use the available tools to gather statistics about the user's watch history,
then return a structured AnalyzerOutput.

Tools available:
- get_watch_summary(month): full stats for a period
- get_shorts_ratio(month): percentage of Shorts watched
- get_top_channels(n): most-watched channels
- get_watch_by_hour(): hour-by-hour breakdown
- get_binge_sessions(threshold_minutes): find binge sessions

Always use get_watch_summary first. Then enrich with other tools if needed.
Return structured data only. Do not guess or estimate — use tool results.
        """,
        tools=tools,
        output_schema=AnalyzerOutput,
    )


analyzer_agent = build_analyzer_agent()
