"""File tools — plain functions, registered as ADK FunctionTools on import."""
import json
from datetime import datetime
from pathlib import Path

from framework.tools.registry import tool

_REPORTS_DIR = Path("reports")
_REPORTS_DIR.mkdir(exist_ok=True)


@tool()
def save_report(
    period: str,
    summary: str,
    overall_risk: str,
    recommendations: list,
    analysis: dict,
) -> dict:
    """Save an insights report to a JSON file in the reports directory.

    Args:
        period: Time period label (e.g. 'january 2024').
        summary: Human-readable summary text.
        overall_risk: Risk level string (e.g. 'low', 'medium', 'high').
        recommendations: List of recommendation dicts.
        analysis: Raw analysis data dict.

    Returns:
        {file_path, summary, success} or {file_path, summary, success, error} on failure.
    """
    filename = f"{period.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    file_path = _REPORTS_DIR / filename
    try:
        content = {
            "period": period,
            "generated_at": datetime.now().isoformat(),
            "summary": summary,
            "overall_risk": overall_risk,
            "recommendations": recommendations,
            "analysis": analysis,
        }
        file_path.write_text(json.dumps(content, indent=2, default=str))
        return {"file_path": str(file_path), "summary": summary, "success": True}
    except Exception as e:
        return {"file_path": "", "summary": "", "success": False, "error": str(e)}


@tool()
def list_reports() -> list:
    """List all saved report filenames in the reports directory.

    Returns:
        List of file path strings.
    """
    return [str(p) for p in _REPORTS_DIR.glob("*.json")]


@tool()
def get_report(filename: str) -> str:
    """Read a saved report by filename.

    Args:
        filename: Report filename (e.g. 'january_2024_20240101_120000.json').

    Returns:
        Report JSON as a string, or an error message if not found.
    """
    path = _REPORTS_DIR / filename
    if not path.exists():
        return f"Report not found: {filename}"
    return path.read_text()
