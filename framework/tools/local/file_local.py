from pathlib import Path
from framework.tools.base_tool import BaseTool
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
REPORTS_DIR = Path("reports")


class FileLocalTools(BaseTool):
    name = "file_tools"
    description = "Reads and writes report files"
    tool_names = ["save_report", "list_reports", "get_report"]

    def __init__(self):
        REPORTS_DIR.mkdir(exist_ok=True)

    async def save_report(
        self,
        period: str,
        summary: str,
        overall_risk: str,
        recommendations: list[dict],
        analysis: dict,
    ) -> dict:
        """Save insights report to a JSON file in the reports directory."""
        filename = f"{period.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        file_path = REPORTS_DIR / filename
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
            logger.info(f"Report saved: {file_path}")
            return {"file_path": str(file_path), "summary": summary, "success": True}
        except Exception as e:
            return {"file_path": "", "summary": "", "success": False, "error": str(e)}

    async def list_reports(self) -> list[str]:
        """List all saved reports."""
        return [str(p) for p in REPORTS_DIR.glob("*.json")]

    async def get_report(self, filename: str) -> str:
        """Read a saved report by filename."""
        path = REPORTS_DIR / filename
        if not path.exists():
            return f"Report not found: {filename}"
        return path.read_text()

    async def execute(self, tool_name: str, **kwargs):
        method = getattr(self, tool_name, None)
        if not method:
            raise ValueError(f"Unknown tool: {tool_name}")
        return await method(**kwargs)
