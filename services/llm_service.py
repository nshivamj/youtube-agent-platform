"""
LLM Service — runtime model resolution.

Decouples agent code from a hard-coded model string.  Agents call
llm_service.get_model("my_agent") instead of embedding "gemini-2.0-flash"
directly, so the operator can swap models via .env with zero code changes.

Resolution order (first match wins):
  1. Per-agent override  MODEL_<AGENT_NAME_UPPER>=...
  2. Global override     MODEL=...
  3. Built-in default    gemini-2.0-flash

Ollama support:
  Set MODEL=ollama/<model-name> and OLLAMA_BASE_URL=http://localhost:11434
  llm_service will automatically return a LiteLlm instance instead of a string.

Example .env:
  # Gemini (default)
  MODEL=gemini-2.0-flash

  # Ollama
  MODEL=ollama/llama3.2
  OLLAMA_BASE_URL=http://localhost:11434

  # Per-agent override
  MODEL_GITLAB_AGENT=ollama/mistral
"""

import os
from dotenv import load_dotenv

load_dotenv()

_DEFAULT_MODEL = "gemini-2.0-flash"


class LLMService:
    """Resolves which model an agent should use at runtime.

    Returns a string for Gemini models, or a LiteLlm instance for
    ollama/* models (and any other LiteLLM-supported prefixes).

    Per-agent env var format: MODEL_<AGENT_NAME_UPPERCASED_WITH_UNDERSCORES>
    e.g. gitlab_agent → MODEL_GITLAB_AGENT
    """

    def get_model(self, agent_name: str = None):
        """Return the model for the given agent.

        Returns a plain string for Gemini, or a LiteLlm instance for
        ollama/* (or other non-Google) models.
        """
        model_str = self._resolve_model_str(agent_name)

        if "/" in model_str and not model_str.startswith("gemini"):
            return self._make_lite_llm(model_str)

        return model_str

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_model_str(self, agent_name: str = None) -> str:
        if agent_name:
            env_key = f"MODEL_{agent_name.upper()}"
            per_agent = os.getenv(env_key)
            if per_agent:
                return per_agent
        return os.getenv("MODEL", _DEFAULT_MODEL)

    def _make_lite_llm(self, model_str: str):
        try:
            from google.adk.models.lite_llm import LiteLlm
        except ImportError:
            raise ImportError(
                "LiteLLM support requires: pip install google-adk[extensions]"
            )

        kwargs = {"model": model_str}

        # Allow overriding the base URL (required for local Ollama)
        base_url = os.getenv("OLLAMA_BASE_URL")
        if base_url and model_str.startswith("ollama/"):
            kwargs["api_base"] = base_url

        return LiteLlm(**kwargs)


llm_service = LLMService()
