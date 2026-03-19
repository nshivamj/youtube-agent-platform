"""Step-by-step logging callbacks for debugging agent execution.

Logs before/after every agent, model call, and tool call so you can see
exactly what's happening at each step in the terminal.

ADK calls callbacks with keyword args, so all functions use **kwargs style.
"""
import logging

logger = logging.getLogger("platform.steps")
logger.setLevel(logging.DEBUG)

# Ensure output goes to console even if root logger isn't configured
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
    ))
    logger.addHandler(_handler)
    logger.propagate = False


# ── Before Agent ──────────────────────────────────────────────────────────
def step_before_agent_cb(callback_context=None, **kwargs):
    agent_name = getattr(callback_context, "agent_name", "unknown") if callback_context else "unknown"
    logger.info(f">>> AGENT START: {agent_name}")
    return None


# ── After Agent ───────────────────────────────────────────────────────────
def step_after_agent_cb(callback_context=None, **kwargs):
    agent_name = getattr(callback_context, "agent_name", "unknown") if callback_context else "unknown"
    logger.info(f"<<< AGENT DONE: {agent_name}")
    return None


# ── Before Model Call ─────────────────────────────────────────────────────
def step_before_model_cb(callback_context=None, llm_request=None, **kwargs):
    agent_name = getattr(callback_context, "agent_name", "unknown") if callback_context else "unknown"
    logger.info(f"  >> MODEL CALL: {agent_name}")

    if llm_request:
        # Log system instruction
        config = getattr(llm_request, "config", None)
        if config:
            sys_instr = getattr(config, "system_instruction", None)
            if sys_instr:
                preview = str(sys_instr)[:200]
                logger.debug(f"     system_instruction: {preview}...")

        # Log the contents/messages being sent
        contents = getattr(llm_request, "contents", None)
        if contents:
            logger.debug(f"     message count: {len(contents)}")
            if len(contents) > 0:
                last = contents[-1]
                parts = getattr(last, "parts", []) or []
                for part in parts[:2]:
                    text = getattr(part, "text", None)
                    if text:
                        logger.debug(f"     last msg: {text[:200]}")
                    fc = getattr(part, "function_call", None)
                    if fc:
                        args = dict(fc.args) if getattr(fc, "args", None) else {}
                        logger.debug(f"     function_call: {fc.name}({args})")
                    fr = getattr(part, "function_response", None)
                    if fr:
                        resp_preview = str(fr.response)[:200] if getattr(fr, "response", None) else ""
                        logger.debug(f"     function_response: {fr.name} -> {resp_preview}")

        # Log available tools
        tools = getattr(llm_request, "tools", None)
        if tools:
            tool_names = []
            for t in tools:
                decls = getattr(t, "function_declarations", None) or []
                tool_names.extend(d.name for d in decls)
            if tool_names:
                logger.debug(f"     available tools: {tool_names}")

    return None


# ── After Model Call ──────────────────────────────────────────────────────
def step_after_model_cb(callback_context=None, llm_response=None, **kwargs):
    agent_name = getattr(callback_context, "agent_name", "unknown") if callback_context else "unknown"
    logger.info(f"  << MODEL RESPONSE: {agent_name}")

    if llm_response:
        content = getattr(llm_response, "content", None)
        if content:
            parts = getattr(content, "parts", []) or []
            for part in parts[:3]:
                text = getattr(part, "text", None)
                if text:
                    logger.info(f"     text: {text[:300]}")
                fc = getattr(part, "function_call", None)
                if fc:
                    args = dict(fc.args) if getattr(fc, "args", None) else {}
                    logger.info(f"     -> CALLING TOOL: {fc.name}({args})")
    return None


# ── After Tool ────────────────────────────────────────────────────────────
def step_after_tool_cb(tool=None, args=None, tool_context=None, tool_response=None, **kwargs):
    tool_name = getattr(tool, "name", str(tool)) if tool else "unknown"
    logger.info(f"  <- TOOL RESULT: {tool_name}")
    logger.debug(f"     args: {args}")
    response_preview = str(tool_response)[:300] if tool_response else "(empty)"
    logger.debug(f"     response: {response_preview}")
    return None
