"""after_tool_callback — logs every tool call to the observability tracker."""
import logging
from observability.tracker import tracker

logger = logging.getLogger("platform.callbacks")


def logging_cb(tool, args, tool_context, tool_response) -> None:
    """Log tool call outcome to the append-only JSONL tracer."""
    tool_name = getattr(tool, "name", str(tool))
    agent_name = getattr(tool_context, "agent_name", None) or "unknown"
    success = "error" not in (tool_response or {})
    response_preview = str(tool_response)[:200] if tool_response else "(empty)"
    status = "📦 Got results" if success else "❌ Error"
    logger.info(f"{status} from {tool_name} (called by {agent_name})")
    logger.debug(f"   📥 args: {args}")
    logger.debug(f"   📤 response: {response_preview}")
    tracker.log_tool_call(agent_name, tool_name, success, 0.0)
    return None
