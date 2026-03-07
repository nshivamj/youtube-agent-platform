from google.adk.agents import SequentialAgent
from agents.analyzer_agent import analyzer_agent
from agents.insights_agent import insights_agent
from framework.workflow_registry import workflow_registry

youtube_workflow = SequentialAgent(
    name="youtube_workflow",
    description="Analyzes YouTube history then generates insights and saves report",
    sub_agents=[analyzer_agent, insights_agent],
)

workflow_registry.register(
    name="youtube_workflow",
    workflow=youtube_workflow,
    description="Analyzes YouTube watch history, generates habits insights and saves a report",
    triggers=[
        "analyze my january",
        "how much shorts did i watch",
        "what are my watch habits",
        "top channels",
        "binge sessions",
    ],
)
