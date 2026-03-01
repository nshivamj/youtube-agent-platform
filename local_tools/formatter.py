"""Formatting helpers exposed as local ADK tools.

ADK reads the function signature and docstring to auto-generate
the Gemini function declaration — no manual schema needed.
"""


def format_report(text: str) -> str:
    """Format raw agent output into a clean, structured report.

    Strips leading/trailing whitespace and applies title-casing to headings.

    Args:
        text: Raw text string to format.

    Returns:
        The formatted report string.
    """
    lines = text.strip().splitlines()
    formatted = []
    for line in lines:
        stripped = line.strip()
        # Title-case lines that look like headings (short, no period at end)
        if stripped and len(stripped) < 60 and not stripped.endswith("."):
            formatted.append(stripped.title())
        else:
            formatted.append(stripped)
    return "\n".join(formatted)
