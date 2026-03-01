"""Workflow runner — executes a WorkflowDefinition step by step.

Each step's output becomes {previous_output} for the next step.
If any step fails the workflow stops immediately and returns the error.
"""

from typing import Any

from app.runner import runner as _agent_runner
from app.workflow.definitions import WorkflowDefinition


def run_workflow(workflow_def: WorkflowDefinition, prompt: str) -> dict[str, Any]:
    """Execute all steps in *workflow_def* sequentially.

    Args:
        workflow_def: The loaded workflow definition.
        prompt:       The original user input — available as {input} in templates.

    Returns::

        {"status": "success", "message": "...", "data": {"text": "...", "steps": [...]}}
        {"status": "error",   "message": "...", "data": {}}
    """
    previous_output = ""
    step_outputs: list[dict[str, Any]] = []
    total = len(workflow_def.steps)

    for i, step in enumerate(workflow_def.steps, start=1):
        step_prompt = step.prompt_template.format(
            input=prompt,
            previous_output=previous_output,
        )

        print(f"[workflow:{workflow_def.name}] step {i}/{total} → {step.agent}")

        result = _agent_runner.run_agent(step.agent, step_prompt)

        if result["status"] == "error":
            return {
                "status": "error",
                "message": (
                    f"Workflow '{workflow_def.name}' failed at step {i} "
                    f"({step.agent}): {result['message']}"
                ),
                "data": {},
            }

        previous_output = result["data"]["text"]
        step_outputs.append({"step": i, "agent": step.agent, "output": previous_output})

    return {
        "status": "success",
        "message": f"Workflow '{workflow_def.name}' completed {total} step(s).",
        "data": {
            "text": previous_output,
            "steps": step_outputs,
        },
    }
