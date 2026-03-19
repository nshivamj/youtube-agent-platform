"""Master callbacks — one per ADK hook type.

The factory wires these 6 callbacks into every agent. Each one:
  1. Logs the event (narrated style)
  2. Calls any agent-specific hooks from YAML

Agent YAML only needs to declare agent-specific callbacks under:
  callbacks:
    agent_before: [my_before_cb]
    agent_after:  [my_after_cb]

Logging/tracing/state persistence is automatic — no YAML config needed.
"""
import logging
import os

from observability.tracker import tracker

logger = logging.getLogger("platform.agent")

# tool_name -> session state key (auto-persist after tool calls)
_PERSIST: dict[str, str] = {
    "gitlab_list_commits":     "gitlab_commits",
    "gitlab_list_mrs":         "gitlab_mrs",
    "gitlab_list_pipelines":   "gitlab_pipelines",
    "gitlab_list_projects":    "gitlab_projects",
    "get_watch_summary":       "watch_summary",
    "get_binge_sessions":      "binge_sessions",
    "get_top_channels":        "top_channels",
    "check_user_entitlements": "entitlement_result",
}


# ── Helpers ───────────────────────────────────────────────────────────────

def _run_agent_hooks(hooks, callback_context):
    """Run agent-specific hooks (before_agent / after_agent signature)."""
    for hook in hooks:
        result = hook(callback_context)
        if result is not None:
            return result
    return None


def _run_tool_hooks(hooks, tool, args, tool_context, tool_response=None):
    """Run agent-specific hooks (before_tool / after_tool signature)."""
    for hook in hooks:
        if tool_response is not None:
            result = hook(tool, args, tool_context, tool_response)
        else:
            result = hook(tool, args, tool_context)
        if result is not None:
            return result
    return None


# ── Builder functions ─────────────────────────────────────────────────────
# Each returns a callback with the correct ADK signature.
# Agent-specific hooks are baked in via closure.


def build_before_agent(agent_hooks: list = None):
    """before_agent_callback: (callback_context) -> Optional[Content]"""
    hooks = agent_hooks or []

    def before_agent(callback_context):
        agent_name = getattr(callback_context, "agent_name", "unknown")
        logger.info(f"🤔 Waking up {agent_name}...")

        # Permission check
        allowed = os.getenv("ALLOWED_AGENTS", "*")
        if allowed != "*":
            permitted = [a.strip() for a in allowed.split(",")]
            if agent_name not in permitted:
                logger.warning(f"🚫 Blocked {agent_name} — not in ALLOWED_AGENTS")
                try:
                    from google.genai import types as genai_types
                    return genai_types.Content(
                        role="model",
                        parts=[genai_types.Part(text=f"Agent '{agent_name}' is not permitted.")],
                    )
                except ImportError:
                    pass

        # Run agent-specific hooks
        result = _run_agent_hooks(hooks, callback_context)
        if result is not None:
            return result

        logger.info(f"✅ {agent_name} ready")
        return None

    return before_agent


def build_after_agent(agent_hooks: list = None):
    """after_agent_callback: (callback_context) -> Optional[Content]"""
    hooks = agent_hooks or []

    def after_agent(callback_context):
        agent_name = getattr(callback_context, "agent_name", "unknown")
        logger.info(f"🏁 {agent_name} finished")

        # Checkpoint
        callback_context.state[f"checkpoint_{agent_name}"] = True

        # Validation error check
        validation_error = callback_context.state.get("_validation_error")
        if validation_error:
            logger.warning(f"⚠️  Validation error in {agent_name}: {validation_error}")
            tracker.log_agent_event("validation_error", agent_name, {"error": validation_error})

        # Run agent-specific hooks
        result = _run_agent_hooks(hooks, callback_context)
        if result is not None:
            return result

        # Debug: log all state keys
        try:
            all_keys = list(callback_context.state._state.keys()) if hasattr(callback_context.state, '_state') else []
            logger.info(f"📊 {agent_name} state keys: {all_keys}")
        except Exception as e:
            logger.debug(f"   Could not read state keys: {e}")
        logger.info(f"✅ {agent_name} checkpoint saved")
        return None

    return after_agent


def build_before_model(agent_hooks: list = None):
    """before_model_callback: (callback_context, llm_request) -> Optional[LlmResponse]"""
    hooks = agent_hooks or []

    def before_model(callback_context, llm_request):
        agent_name = getattr(callback_context, "agent_name", "unknown")
        logger.info(f"🧠 {agent_name} thinking...")

        # Log what's being sent
        if llm_request:
            contents = getattr(llm_request, "contents", None)
            if contents:
                logger.debug(f"   📨 Sending {len(contents)} messages to model")
                # Log last user message
                last = contents[-1] if contents else None
                if last:
                    parts = getattr(last, "parts", []) or []
                    for part in parts[:2]:
                        text = getattr(part, "text", None)
                        if text:
                            logger.debug(f"   💬 Last message: {text[:150]}")

            # Log available tools
            tools = getattr(llm_request, "tools", None)
            if tools:
                tool_names = []
                for t in tools:
                    decls = getattr(t, "function_declarations", None) or []
                    tool_names.extend(d.name for d in decls)
                if tool_names:
                    logger.debug(f"   🔧 Tools available: {tool_names}")

        # Run agent-specific hooks (e.g. narration injection)
        for hook in hooks:
            result = hook(callback_context, llm_request)
            if result is not None:
                return result

        return None

    return before_model


def build_after_model(agent_hooks: list = None):
    """after_model_callback: (callback_context, llm_response) -> Optional[LlmResponse]"""
    hooks = agent_hooks or []

    def after_model(callback_context, llm_response):
        agent_name = getattr(callback_context, "agent_name", "unknown")

        if llm_response:
            content = getattr(llm_response, "content", None)
            if content:
                parts = getattr(content, "parts", []) or []
                for part in parts[:3]:
                    text = getattr(part, "text", None)
                    if text:
                        logger.info(f"💭 {agent_name} says: {text[:200]}")
                    fc = getattr(part, "function_call", None)
                    if fc:
                        args = dict(fc.args) if getattr(fc, "args", None) else {}
                        logger.info(f"🔍 {agent_name} calling tool: {fc.name}({args})")

        # Run agent-specific hooks
        for hook in hooks:
            result = hook(callback_context, llm_response)
            if result is not None:
                return result

        return None

    return after_model


def build_before_tool(agent_hooks: list = None):
    """before_tool_callback: (tool, args, tool_context) -> Optional[dict]"""
    hooks = agent_hooks or []

    def before_tool(tool, args, tool_context):
        tool_name = getattr(tool, "name", str(tool))
        logger.info(f"⚡ Calling {tool_name}...")
        logger.debug(f"   📥 args: {args}")

        # Run agent-specific hooks
        return _run_tool_hooks(hooks, tool, args, tool_context)

    return before_tool


def build_after_tool(agent_hooks: list = None):
    """after_tool_callback: (tool, args, tool_context, tool_response) -> Optional[dict]"""
    hooks = agent_hooks or []

    def after_tool(tool, args, tool_context, tool_response):
        tool_name = getattr(tool, "name", str(tool))
        agent_name = getattr(tool_context, "agent_name", "unknown")
        success = "error" not in (tool_response or {})

        # Logging
        if success:
            logger.info(f"📦 Got results from {tool_name}")
        else:
            error = (tool_response or {}).get("error", "unknown error")
            logger.warning(f"❌ {tool_name} failed: {error}")
        logger.debug(f"   📤 response: {str(tool_response)[:200]}")

        # Tracker
        tracker.log_tool_call(agent_name, tool_name, success, 0.0)

        # State persistence
        state_key = _PERSIST.get(tool_name)
        if state_key:
            logger.info(f"💾 Saving to state['{state_key}']")
            tool_context.state[state_key] = tool_response
            logger.info(f"📋 Saved {len(str(tool_response))} chars to state['{state_key}']")

        # Run agent-specific hooks
        return _run_tool_hooks(hooks, tool, args, tool_context, tool_response)

    return after_tool
