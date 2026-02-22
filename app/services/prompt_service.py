"""Prompt Service — pre/post processing for agent prompts.

Current state: thin pass-through. Extend here as needs arise.

Future additions (add without changing orchestrator or runner):
    - Prompt templating / variable injection
    - Context augmentation (user preferences, prior summaries)
    - PII / secret scrubbing before the prompt leaves the platform
    - Response formatting (markdown → plain text, truncation, etc.)
"""

from typing import Any


def prepare(raw_prompt: str, context: dict[str, Any] | None = None) -> str:
    """Pre-process a raw user prompt before it is sent to the agent.

    Args:
        raw_prompt: The user's original input string.
        context:    Optional key/value pairs for template substitution (future).

    Returns:
        A processed prompt string ready for the agent.
    """
    return raw_prompt.strip()


def format_response(result: dict[str, Any]) -> str:
    """Format a normalised result dict into a human-readable string.

    Args:
        result: Dict with keys ``status``, ``message``, ``data``.

    Returns:
        Plain-text string suitable for printing to a terminal.
    """
    if result.get("status") == "error":
        return f"[error] {result.get('message', 'Unknown error')}"
    return result.get("data", {}).get("text", "")
