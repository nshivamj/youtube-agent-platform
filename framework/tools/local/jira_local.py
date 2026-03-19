"""Jira/Copilot tracking tools — reads Excel to check if a Jira ID used Copilot."""

from pathlib import Path

import openpyxl

_DATA_FILE = Path(__file__).parent.parent.parent.parent / "data" / "copilot_tracking.xlsx"


class JiraLocalTools:
    name = "jira_tools"
    description = "Check Jira IDs against Copilot usage tracking spreadsheet"
    tool_names = [
        "check_copilot_usage",
        "list_all_copilot_entries",
    ]

    def _load_data(self) -> dict[str, str]:
        """Load Excel into a dict of {jira_id: copilot_used}."""
        if not _DATA_FILE.exists():
            raise FileNotFoundError(f"Tracking file not found: {_DATA_FILE}")
        wb = openpyxl.load_workbook(_DATA_FILE, read_only=True)
        ws = wb.active
        data = {}
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0] is not None:
                jira_id = str(row[0]).strip().upper()
                copilot_used = str(row[1]).strip().lower() if row[1] else "no"
                data[jira_id] = copilot_used
        wb.close()
        return data

    async def check_copilot_usage(self, jira_id: str) -> dict:
        """Check if a specific Jira ID has Copilot usage tagged.

        Args:
            jira_id: The Jira ticket ID to look up (e.g. 'PROJ-101').

        Returns:
            Dict with jira_id, copilot_used (bool), and status.
        """
        data = self._load_data()
        jira_id = jira_id.strip().upper()
        if jira_id in data:
            used = data[jira_id] in ("yes", "true", "1")
            return {
                "jira_id": jira_id,
                "copilot_used": used,
                "status": "found",
            }
        return {
            "jira_id": jira_id,
            "copilot_used": False,
            "status": "not_found",
        }

    async def list_all_copilot_entries(self) -> list[dict]:
        """List all Jira IDs and their Copilot usage status from the tracking spreadsheet.

        Returns:
            List of dicts with jira_id and copilot_used for every entry.
        """
        data = self._load_data()
        return [
            {"jira_id": jid, "copilot_used": val in ("yes", "true", "1")}
            for jid, val in data.items()
        ]
