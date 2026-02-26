"""Workflow registry — loads WorkflowDefinitions from workflows-config/*.yaml.

Follows the same pattern as the agent registry:
    registry.get("fetch_and_summarize")  →  WorkflowDefinition
"""

from pathlib import Path

import yaml

from app.workflow.definitions import WorkflowDefinition, WorkflowStep

_CONFIG_DIR = Path(__file__).parent.parent.parent / "workflows-config"


def get(workflow_name: str) -> WorkflowDefinition:
    """Load and return a WorkflowDefinition by name.

    Args:
        workflow_name: Must match a YAML file in workflows-config/.

    Raises:
        FileNotFoundError: If no matching YAML exists.
        ValueError: If the YAML is missing required fields.
    """
    path = _CONFIG_DIR / f"{workflow_name}.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"Workflow config not found: '{path}'. "
            f"Create workflows-config/{workflow_name}.yaml to define it."
        )

    with path.open() as fh:
        data = yaml.safe_load(fh)

    if not data.get("name"):
        raise ValueError(f"Workflow YAML missing 'name' field: {path}")
    if not data.get("steps"):
        raise ValueError(f"Workflow YAML missing 'steps' field: {path}")

    steps = [
        WorkflowStep(
            agent=s["agent"],
            prompt_template=s["prompt_template"],
        )
        for s in data["steps"]
    ]

    return WorkflowDefinition(
        name=data["name"],
        description=data.get("description", ""),
        steps=steps,
    )
