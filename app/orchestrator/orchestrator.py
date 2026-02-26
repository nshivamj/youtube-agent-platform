"""Orchestrator — coordinates agent resolution and runner delegation.

Responsibilities:
    - Accept a (agent_name, prompt) request from the entrypoint
    - Accept a (workflow_name, prompt) request from the entrypoint
    - Delegate execution to the runner or workflow runner
    - Normalise exceptions into structured error responses
    - Return a consistent result dict to the caller

The orchestrator does NOT know about ADK, MCP, or YAML — those are
runner/registry concerns.
"""

from typing import Any

from app.runner import runner as _runner
from app.workflow import registry as _workflow_registry
from app.workflow import runner as _workflow_runner


def handle_request(agent_name: str, prompt: str) -> dict[str, Any]:
    """Run the named agent with *prompt* and return a normalised result.

    Return shape::

        {"status": "success", "message": "...", "data": {"text": "..."}}
        {"status": "error",   "message": "...", "data": {}}
    """
    try:
        return _runner.run_agent(agent_name, prompt)

    except FileNotFoundError as exc:
        return _error(str(exc))

    except ValueError as exc:
        return _error(str(exc))

    except NotImplementedError as exc:
        return _error(f"Feature not yet available: {exc}")

    except Exception as exc:                             # noqa: BLE001
        return _error(f"Unexpected error running '{agent_name}': {exc}")


def handle_workflow(workflow_name: str, prompt: str) -> dict[str, Any]:
    """Run the named workflow with *prompt* and return a normalised result.

    Loads the workflow definition, executes each step sequentially, and
    threads outputs between steps.

    Return shape::

        {"status": "success", "message": "...", "data": {"text": "...", "steps": [...]}}
        {"status": "error",   "message": "...", "data": {}}
    """
    try:
        workflow_def = _workflow_registry.get(workflow_name)
        return _workflow_runner.run_workflow(workflow_def, prompt)

    except FileNotFoundError as exc:
        return _error(str(exc))

    except ValueError as exc:
        return _error(str(exc))

    except Exception as exc:                             # noqa: BLE001
        return _error(f"Unexpected error running workflow '{workflow_name}': {exc}")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _error(message: str) -> dict[str, Any]:
    return {"status": "error", "message": message, "data": {}}
