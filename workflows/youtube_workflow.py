from google.adk.agents import SequentialAgent
from agents.analyzer_agent import analyzer_agent
from agents.insights_agent import insights_agent

youtube_workflow = SequentialAgent(
    name="youtube_workflow",
    description="Analyzes YouTube history then generates insights and saves report",
    sub_agents=[analyzer_agent, insights_agent],
)
