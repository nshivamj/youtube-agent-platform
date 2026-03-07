"""
LLM Service — runtime model resolution.

Decouples agent code from a hard-coded model string.  Agents call
llm_service.get_model("my_agent") instead of embedding "gemini-2.0-flash"
directly, so the operator can swap models via .env with zero code changes.

Resolution order (first match wins):
  1. Per-agent override  MODEL_<AGENT_NAME_UPPER>=gemini-2.5-pro
  2. Global override     MODEL=gemini-2.0-flash
  3. Built-in default    gemini-2.0-flash

Example .env overrides:
  MODEL=gemini-2.0-flash                       # all agents use this
  MODEL_ANALYZER_AGENT=gemini-2.5-pro          # override one agent to a bigger model
  MODEL_COORDINATOR_AGENT=gemini-2.0-flash     # keep coordinator cheap
"""

import os
from dotenv import load_dotenv

load_dotenv()

_DEFAULT_MODEL = "gemini-2.0-flash"


class LLMService:
    """Resolves which model an agent should use at runtime.

    Per-agent env var format: MODEL_<AGENT_NAME_UPPERCASED_WITH_UNDERSCORES>
    e.g. analyzer_agent  → MODEL_ANALYZER_AGENT
         control_test_planner → MODEL_CONTROL_TEST_PLANNER
    """

    def get_model(self, agent_name: str = None) -> str:
        """Return the model string for the given agent.

        Args:
            agent_name: The agent's name (e.g. "analyzer_agent").
                        If None, returns the global MODEL or default.
        """
        if agent_name:
            env_key = f"MODEL_{agent_name.upper()}"
            per_agent = os.getenv(env_key)
            if per_agent:
                return per_agent

        return os.getenv("MODEL", _DEFAULT_MODEL)


llm_service = LLMService()
