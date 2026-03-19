"""Shared default after-agent callback (controller)."""
import logging
from observability.tracker import tracker

logger = logging.getLogger("platform.callbacks")


def after_agent_cb(callback_context):
    """
    1. Semantic validation — log _validation_error if set.
    2. Checkpoint — write {agent_name}_output and checkpoint_{agent_name} to state.
    """
    agent_name = getattr(callback_context, "agent_name", "") or "unknown"
    logger.info(f"✅ {agent_name} finished — saving checkpoint")

    # 1. Validation error
    validation_error = callback_context.state.get("_validation_error")
    if validation_error:
        tracker.log_agent_event("validation_error", agent_name, {"error": validation_error})

    # 2. Checkpoint
    output = getattr(callback_context, "output", None)
    if output is not None:
        callback_context.state[f"{agent_name}_output"] = output
    callback_context.state[f"checkpoint_{agent_name}"] = True

    return None
