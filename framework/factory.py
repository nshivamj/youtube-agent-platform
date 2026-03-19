"""Factory: builds agents and workflows from YAML config files."""
import importlib
from pathlib import Path
from typing import Any, Callable

import yaml

# Register every @tool-decorated function before resolving names
import tools.all_tools  # noqa: F401

from framework.callbacks.composer import SHARED_REGISTRY
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


def _resolve_callbacks(names: list[str], agent_specific: list[Callable]) -> list[Callable]:
    """Look up shared callbacks by name and append agent-specific ones."""
    result = []
    for name in names:
        if name not in SHARED_REGISTRY:
            raise KeyError(
                f"Unknown shared callback '{name}'. Available: {list(SHARED_REGISTRY)}"
            )
        result.append(SHARED_REGISTRY[name])
    result.extend(agent_specific)
    return result


class Factory:
    AGENT_CONFIGS_DIR = Path("agent_configs")
    WORKFLOW_CONFIGS_DIR = Path("workflow_configs")

    def create_agent(self, agent_id: str):
        """Load YAML, resolve tools and callbacks, return LlmAgent."""
        from google.adk.agents import LlmAgent

        yaml_path = self.AGENT_CONFIGS_DIR / agent_id / f"{agent_id}.yaml"
        cfg = _load_yaml(yaml_path)

        tool_names: list[str] = cfg.get("tools") or []
        tools = get_many(tool_names) if tool_names else []

        cb_cfg = cfg.get("callbacks") or {}

        # before_agent: always starts with before_agent_cb; YAML adds extras
        before_cbs = _resolve_callbacks(
            ["before_agent_cb"] + (cb_cfg.get("shared_before") or []),
            [_load_agent_callback(agent_id, n) for n in (cb_cfg.get("agent_before") or [])],
        )

        # after_agent: always ends with after_agent_cb; YAML adds extras
        after_cbs = _resolve_callbacks(
            ["after_agent_cb"] + (cb_cfg.get("shared_after") or []),
            [_load_agent_callback(agent_id, n) for n in (cb_cfg.get("agent_after") or [])],
        )

        # after_tool: YAML-only, no default
        after_tool_cbs = _resolve_callbacks(cb_cfg.get("after_tool") or [], [])

        prompt = cfg.get("prompt", "")
        model = cfg.get("model") or llm_service.get_model(agent_id)

        kwargs: dict[str, Any] = dict(
            name=agent_id,
            model=model,
            instruction=prompt,
            tools=tools,
            before_agent_callback=before_cbs,
            after_agent_callback=after_cbs,
        )
        if after_tool_cbs:
            kwargs["after_tool_callback"] = after_tool_cbs

        return LlmAgent(**kwargs)

    def create_workflow(self, workflow_id: str):
        """Build a SequentialAgent workflow from YAML."""
        from google.adk.agents import SequentialAgent

        yaml_path = self.WORKFLOW_CONFIGS_DIR / workflow_id / f"{workflow_id}.yaml"
        cfg = _load_yaml(yaml_path)

        sub_agents = [self.create_agent(aid) for aid in (cfg.get("agents") or [])]

        cb_cfg = cfg.get("callbacks") or {}
        before_cbs = _resolve_callbacks(cb_cfg.get("shared_before") or [], [])
        after_cbs = _resolve_callbacks(cb_cfg.get("shared_after") or [], [])

        kwargs: dict[str, Any] = dict(name=workflow_id, sub_agents=sub_agents)
        if before_cbs:
            kwargs["before_agent_callback"] = before_cbs
        if after_cbs:
            kwargs["after_agent_callback"] = after_cbs

        return SequentialAgent(**kwargs)

    def bootstrap(self):
        """Create all enabled workflows, wire into coordinator, return coordinator."""
        workflows = []
        if self.WORKFLOW_CONFIGS_DIR.exists():
            for wf_dir in sorted(self.WORKFLOW_CONFIGS_DIR.iterdir()):
                yaml_path = wf_dir / f"{wf_dir.name}.yaml"
                if not yaml_path.exists():
                    continue
                if _load_yaml(yaml_path).get("enabled", True):
                    workflows.append(self.create_workflow(wf_dir.name))

        coordinator = self.create_agent("coordinator_agent")
        if workflows:
            coordinator.sub_agents = workflows
        return coordinator
