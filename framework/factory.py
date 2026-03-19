"""Factory: builds agents and workflows from YAML config files."""
import importlib
import os
from pathlib import Path
from typing import Any

import yaml

# Trigger self-registration of all local tools
import tools.local.gitlab_local  # noqa: F401

from framework.callbacks.composer import compose
from framework.tools.resolver import resolve
from services.llm_service import llm_service


def _load_yaml(path: Path) -> dict:
    with open(path, "r") as fh:
        return yaml.safe_load(fh) or {}


def _load_agent_callback(agent_id: str, cb_name: str):
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
        """Load YAML, resolve tools and callbacks, return LlmAgent."""
        from google.adk.agents import LlmAgent

        yaml_path = self.AGENT_CONFIGS_DIR / agent_id / f"{agent_id}.yaml"
        cfg = _load_yaml(yaml_path)

        tool_names: list[str] = cfg.get("tools") or []
        tool_mode = os.getenv("TOOL_MODE", "local")
        tools = resolve(tool_names, tool_mode) if tool_names else []

        cb_cfg = cfg.get("callbacks") or {}

        # --- before-agent: always start with before_agent_cb; YAML adds extras ---
        before_names: list[str] = ["before_agent_cb"] + (cb_cfg.get("shared_before") or [])
        agent_before_names: list[str] = cb_cfg.get("agent_before") or []
        agent_before_fns = [_load_agent_callback(agent_id, n) for n in agent_before_names]
        before_cb = compose(before_names, agent_before_fns)

        # --- after-agent: always end with after_agent_cb; YAML adds extras ---
        after_names: list[str] = ["after_agent_cb"] + (cb_cfg.get("shared_after") or [])
        agent_after_names: list[str] = cb_cfg.get("agent_after") or []
        agent_after_fns = [_load_agent_callback(agent_id, n) for n in agent_after_names]
        after_cb = compose(after_names, agent_after_fns)

        # --- after-tool ---
        after_tool_names: list[str] = cb_cfg.get("after_tool") or []
        after_tool_cb = compose(after_tool_names) if after_tool_names else None

        prompt = cfg.get("prompt", "")
        model = cfg.get("model") or llm_service.get_model(agent_id)

        kwargs: dict[str, Any] = dict(
            name=agent_id,
            model=model,
            instruction=prompt,
            tools=tools,
        )
        if before_cb:
            kwargs["before_agent_callback"] = before_cb
        if after_cb:
            kwargs["after_agent_callback"] = after_cb
        if after_tool_cb:
            kwargs["after_tool_callback"] = after_tool_cb

        return LlmAgent(**kwargs)

    def create_workflow(self, workflow_id: str):
        """Build a SequentialAgent workflow from YAML."""
        from google.adk.agents import SequentialAgent

        yaml_path = self.WORKFLOW_CONFIGS_DIR / workflow_id / f"{workflow_id}.yaml"
        cfg = _load_yaml(yaml_path)

        agent_ids: list[str] = cfg.get("agents") or []
        sub_agents = [self.create_agent(aid) for aid in agent_ids]

        cb_cfg = cfg.get("callbacks") or {}
        before_names: list[str] = cb_cfg.get("shared_before") or []
        after_names: list[str] = cb_cfg.get("shared_after") or []
        before_cb = compose(before_names) if before_names else None
        after_cb = compose(after_names) if after_names else None

        kwargs: dict[str, Any] = dict(
            name=workflow_id,
            sub_agents=sub_agents,
        )
        if before_cb:
            kwargs["before_agent_callback"] = before_cb
        if after_cb:
            kwargs["after_agent_callback"] = after_cb

        return SequentialAgent(**kwargs)

    def bootstrap(self):
        """Create all enabled workflows, wire into coordinator, return coordinator."""
        from google.adk.agents import LlmAgent

        # Discover enabled workflows
        workflows = []
        if self.WORKFLOW_CONFIGS_DIR.exists():
            for wf_dir in sorted(self.WORKFLOW_CONFIGS_DIR.iterdir()):
                yaml_path = wf_dir / f"{wf_dir.name}.yaml"
                if not yaml_path.exists():
                    continue
                cfg = _load_yaml(yaml_path)
                if cfg.get("enabled", True):
                    workflows.append(self.create_workflow(wf_dir.name))

        # Build coordinator
        coordinator = self.create_agent("coordinator_agent")

        # Attach workflows as sub-agents
        if workflows:
            coordinator.sub_agents = workflows

        return coordinator
