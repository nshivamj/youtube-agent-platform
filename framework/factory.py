"""Factory: builds agents and workflows from YAML config files."""
import importlib
from pathlib import Path
from typing import Any, Callable

import yaml

# Register every @tool-decorated function before resolving names
import tools.all_tools  # noqa: F401

from framework.callbacks.master import (
    build_before_agent,
    build_after_agent,
    build_before_model,
    build_after_model,
    build_before_tool,
    build_after_tool,
)
from framework.tools.registry import get_many
from services.llm_service import llm_service


def _load_yaml(path: Path) -> dict:
    with open(path, "r") as fh:
        return yaml.safe_load(fh) or {}


def _load_agent_callback(agent_id: str, cb_name: str) -> Callable:
    """Dynamically import an agent-specific callback function."""
    module_path = f"agent_configs.{agent_id}.callbacks.{cb_name}"
    try:
        mod = importlib.import_module(module_path)
        return getattr(mod, cb_name)
    except (ImportError, AttributeError) as exc:
        raise ImportError(
            f"Cannot load agent callback '{cb_name}' from '{module_path}': {exc}"
        )


class Factory:
    AGENT_CONFIGS_DIR = Path("agent_configs")
    WORKFLOW_CONFIGS_DIR = Path("workflow_configs")

    def create_agent(self, agent_id: str):
        """Load YAML, resolve tools and callbacks, return LlmAgent.

        All 6 callback types are always wired. Logging/tracing/state
        persistence is built-in. YAML only declares agent-specific hooks.
        """
        from google.adk.agents import LlmAgent

        yaml_path = self.AGENT_CONFIGS_DIR / agent_id / f"{agent_id}.yaml"
        cfg = _load_yaml(yaml_path)

        tool_names: list[str] = cfg.get("tools") or []
        tools = get_many(tool_names) if tool_names else []

        cb_cfg = cfg.get("callbacks") or {}

        # Load agent-specific hooks from YAML
        agent_before = [_load_agent_callback(agent_id, n) for n in (cb_cfg.get("agent_before") or [])]
        agent_after = [_load_agent_callback(agent_id, n) for n in (cb_cfg.get("agent_after") or [])]
        agent_before_model = [_load_agent_callback(agent_id, n) for n in (cb_cfg.get("agent_before_model") or [])]
        agent_after_model = [_load_agent_callback(agent_id, n) for n in (cb_cfg.get("agent_after_model") or [])]
        agent_before_tool = [_load_agent_callback(agent_id, n) for n in (cb_cfg.get("agent_before_tool") or [])]
        agent_after_tool = [_load_agent_callback(agent_id, n) for n in (cb_cfg.get("agent_after_tool") or [])]

        prompt = cfg.get("prompt", "")
        model = cfg.get("model") or llm_service.get_model(agent_id)

        return LlmAgent(
            name=agent_id,
            model=model,
            instruction=prompt,
            tools=tools,
            before_agent_callback=build_before_agent(agent_before),
            after_agent_callback=build_after_agent(agent_after),
            before_model_callback=build_before_model(agent_before_model),
            after_model_callback=build_after_model(agent_after_model),
            before_tool_callback=build_before_tool(agent_before_tool),
            after_tool_callback=build_after_tool(agent_after_tool),
        )

    def create_workflow(self, workflow_id: str):
        """Build a SequentialAgent workflow from YAML."""
        from google.adk.agents import SequentialAgent

        yaml_path = self.WORKFLOW_CONFIGS_DIR / workflow_id / f"{workflow_id}.yaml"
        cfg = _load_yaml(yaml_path)
        sub_agents = [self.create_agent(aid) for aid in (cfg.get("agents") or [])]
        return SequentialAgent(name=workflow_id, sub_agents=sub_agents)

    def bootstrap(self):
        """Create the root workflow — gitlab_agent → summary_agent sequential."""
        return self.create_workflow("gitlab_workflow")
