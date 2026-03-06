"""WorkflowRegistry — register workflows once, discover everywhere.

Usage in a workflow file:
    from framework.workflow_registry import workflow_registry
    workflow_registry.register(
        name="youtube_workflow",
        workflow=youtube_workflow,
        description="Analyzes YouTube history and generates insights",
        triggers=["analyze my youtube", "watch habits", "shorts ratio"],
    )

The coordinator and main.py read from this registry — no manual edits needed
when adding new workflows.
"""


class WorkflowRegistry:
    def __init__(self):
        self._workflows: dict[str, dict] = {}

    def register(self, name: str, workflow, description: str, triggers: list[str]):
        """Register a workflow with routing metadata.

        Args:
            name:        Unique workflow identifier (matches workflow.name).
            workflow:    The ADK agent/workflow object.
            description: One-line description shown to the coordinator.
            triggers:    Example phrases that should route to this workflow.
        """
        self._workflows[name] = {
            "workflow": workflow,
            "description": description,
            "triggers": triggers,
        }

    def get(self, name: str):
        entry = self._workflows.get(name)
        return entry["workflow"] if entry else None

    def all_workflows(self) -> list:
        """Return all registered workflow objects."""
        return [v["workflow"] for v in self._workflows.values()]

    def routing_summary(self) -> str:
        """Generate a coordinator-ready routing description from registered workflows."""
        lines = []
        for name, meta in self._workflows.items():
            trigger_examples = ", ".join(f'"{t}"' for t in meta["triggers"][:3])
            lines.append(f"- {name}: {meta['description']} (e.g. {trigger_examples})")
        return "\n".join(lines)


workflow_registry = WorkflowRegistry()
