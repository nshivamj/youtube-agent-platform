from framework.callbacks.base_callback import BaseCallback

NARRATION_STYLES = {
    "analyzer_agent": """
Before each tool call, write one sentence explaining what you are about to check and why.
After each tool result, write one sentence summarizing what you found before moving on.
""",
    "insights_agent": """
Explain each recommendation as you generate it.
State the risk level before finalizing.
""",
    "planner_agent": """
Think out loud as you build the plan. Show your reasoning before finalizing steps.
""",
    "coordinator_agent": "",  # coordinator stays silent
}


class NarrationCallback(BaseCallback):
    """Injects per-agent narration style into every LLM call.
    Agents never hardcode narration. This callback handles it for all agents."""

    async def before_model_call(self, callback_context, llm_request):
        agent_name = getattr(callback_context, "agent_name", "")
        style = NARRATION_STYLES.get(agent_name, "")
        if not style:
            return
        if hasattr(llm_request, "config") and hasattr(llm_request.config, "system_instruction"):
            if llm_request.config.system_instruction:
                llm_request.config.system_instruction += f"\n\n{style}"
