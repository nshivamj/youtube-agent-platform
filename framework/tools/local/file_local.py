from pathlib import Path
from core.schemas import ReportInput, ReportOutput
from framework.tools.base_tool import BaseTool
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
REPORTS_DIR = Path("reports")


class FileLocalTools(BaseTool):
    name = "file_tools"
    description = "Reads and writes report files"

    def __init__(self):
        REPORTS_DIR.mkdir(exist_ok=True)

    async def save_report(self, data: ReportInput) -> ReportOutput:
        """Save insights report to a JSON file in the reports directory."""
        filename = f"{data.period.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        file_path = REPORTS_DIR / filename
        try:
            content = {
                "period": data.period,
                "generated_at": datetime.now().isoformat(),
                "summary": data.insights.summary,
                "overall_risk": data.insights.overall_risk,
                "recommendations": [r.model_dump() for r in data.insights.recommendations],
                "analysis": data.analysis.model_dump()
            }
            file_path.write_text(json.dumps(content, indent=2, default=str))
            logger.info(f"Report saved: {file_path}")
            return ReportOutput(
                file_path=str(file_path),
                summary=data.insights.summary,
                success=True
            )
        except Exception as e:
            return ReportOutput(
                file_path="", summary="", success=False, error=str(e)
            )

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
