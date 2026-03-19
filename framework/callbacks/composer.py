"""Shared callback registry — used by framework/factory.py.

SHARED_REGISTRY maps names (referenced in agent YAML files under callbacks:)
to the actual callable. factory.py resolves names to callables and passes
them as lists directly to LlmAgent — ADK iterates the list natively.

Callback signatures (enforced by ADK):
  before_agent_callback / after_agent_callback : (context) -> Optional[Content]
  after_tool_callback                           : (tool, args, context, response) -> Optional[dict]
"""
from typing import Callable

from framework.callbacks.before_agent_cb import before_agent_cb
from framework.callbacks.after_agent_cb import after_agent_cb
from framework.callbacks.narration_cb import narration_cb
from framework.callbacks.logging_cb import logging_cb
from framework.callbacks.approval_cb import approval_cb
from framework.callbacks.tool_state_cb import tool_state_cb

SHARED_REGISTRY: dict[str, Callable] = {
    # before/after agent — signature: (context)
    "before_agent_cb": before_agent_cb,
    "after_agent_cb":  after_agent_cb,
    "narration_cb":    narration_cb,
    "approval_cb":     approval_cb,
    # after_tool — signature: (tool, args, context, response)
    "logging_cb":      logging_cb,
    "tool_state_cb":   tool_state_cb,
}
