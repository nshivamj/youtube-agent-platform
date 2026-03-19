import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from collections import Counter, defaultdict
from framework.tools.base_tool import BaseTool
import logging

logger = logging.getLogger(__name__)

DATA_PATH = Path("data/watch-history.json")


@dataclass
class _VideoItem:
    video_id: str
    title: str
    watched_at: datetime
    channel: str
    is_short: bool


class YouTubeLocalTools(BaseTool):
    """Day 1: reads watch-history.json from Google Takeout directly.
    Day 2: replaced by YouTubeMCPTools — zero agent code changes."""

    name = "youtube_tools"
    description = "Analyzes YouTube watch history data"
    tool_names = [
        "get_watch_summary",
        "get_shorts_ratio",
        "get_top_channels",
        "get_watch_by_hour",
        "get_binge_sessions",
    ]

    def __init__(self):
        self._data: list[_VideoItem] = []
        self._loaded = False

    def _load(self):
        if self._loaded:
            return
        if not DATA_PATH.exists():
            logger.warning(f"watch-history.json not found at {DATA_PATH}")
            self._data = []
            self._loaded = True
            return
        raw = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        items = []
        for entry in raw:
            try:
                title = entry.get("title", "").replace("Watched ", "")
                url = entry.get("titleUrl", "")
                time_str = entry.get("time", "")
                channel = ""
                if "subtitles" in entry and entry["subtitles"]:
                    channel = entry["subtitles"][0].get("name", "")
                if not time_str:
                    continue
                watched_at = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                is_short = "shorts" in url.lower()
                items.append(_VideoItem(
                    video_id=url.split("v=")[-1] if "v=" in url else url,
                    title=title,
                    watched_at=watched_at,
                    channel=channel,
                    is_short=is_short,
                ))
            except Exception as e:
                logger.debug(f"Skipping entry: {e}")
        self._data = items
        self._loaded = True
        logger.info(f"Loaded {len(self._data)} videos from watch history")

    async def get_watch_summary(self, month: str) -> dict:
        """Get summary stats for a given month (e.g. 'january', '2024-01')."""
        self._load()
        filtered = self._filter_by_month(month)
        if not filtered:
            return {
                "period": month, "total_videos": 0, "shorts_count": 0,
                "regular_count": 0, "shorts_percentage": 0.0, "total_hours": 0.0,
                "avg_hours_per_day": 0.0, "top_channels": [], "peak_hour": 0,
                "binge_sessions": [],
            }
        shorts = [v for v in filtered if v.is_short]
        channels = Counter(v.channel for v in filtered if v.channel)
        hours_by_day = defaultdict(float)
        for v in filtered:
            hours_by_day[v.watched_at.date()] += 1 / 60
        days = len(hours_by_day) or 1
        hour_counts = Counter(v.watched_at.hour for v in filtered)
        peak_hour = hour_counts.most_common(1)[0][0] if hour_counts else 0
        total_hours = sum(hours_by_day.values())

        return {
            "period": month,
            "total_videos": len(filtered),
            "shorts_count": len(shorts),
            "regular_count": len(filtered) - len(shorts),
            "shorts_percentage": round(len(shorts) / len(filtered) * 100, 1),
            "total_hours": round(total_hours, 1),
            "avg_hours_per_day": round(total_hours / days, 2),
            "top_channels": [ch for ch, _ in channels.most_common(5)],
            "peak_hour": peak_hour,
            "binge_sessions": self._find_binge_sessions(filtered),
        }

    async def get_shorts_ratio(self, month: str) -> float:
        """Get percentage of Shorts watched in a given month."""
        summary = await self.get_watch_summary(month)
        return summary["shorts_percentage"]

    async def get_top_channels(self, n: int = 5) -> list[str]:
        """Get top N most-watched channels overall."""
        self._load()
        channels = Counter(v.channel for v in self._data if v.channel)
        return [ch for ch, _ in channels.most_common(n)]

    async def get_watch_by_hour(self) -> dict:
        """Get video count by hour of day (0-23)."""
        self._load()
        counts = Counter(v.watched_at.hour for v in self._data)
        return {str(h): counts.get(h, 0) for h in range(24)}

    async def get_binge_sessions(self, threshold_minutes: int = 120) -> list[dict]:
        """Find binge watching sessions over threshold_minutes."""
        self._load()
        return self._find_binge_sessions(self._data, threshold_minutes)

    def _filter_by_month(self, month: str) -> list[_VideoItem]:
        month_lower = month.lower().strip()
        month_names = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12,
        }
        if month_lower in month_names:
            m = month_names[month_lower]
            return [v for v in self._data if v.watched_at.month == m]
        if "-" in month:
            parts = month.split("-")
            if len(parts) == 2:
                year, mon = int(parts[0]), int(parts[1])
                return [v for v in self._data
                        if v.watched_at.year == year and v.watched_at.month == mon]
        return self._data

    def _find_binge_sessions(
        self, videos: list[_VideoItem], threshold_minutes: int = 120
    ) -> list[dict]:
        if not videos:
            return []
        sorted_v = sorted(videos, key=lambda v: v.watched_at)
        sessions = []
        start = sorted_v[0].watched_at
        prev = start
        count = 1
        for v in sorted_v[1:]:
            gap = (v.watched_at - prev).total_seconds() / 60
            if gap < 30:
                count += 1
                prev = v.watched_at
            else:
                duration = (prev - start).total_seconds() / 60
                if duration >= threshold_minutes:
                    sessions.append({
                        "start_time": start.isoformat(),
                        "end_time": prev.isoformat(),
                        "video_count": count,
                        "total_minutes": round(duration, 1),
                    })
                start = v.watched_at
                prev = start
                count = 1
        return sessions

    async def execute(self, tool_name: str, **kwargs):
        method = getattr(self, tool_name, None)
        if not method:
            raise ValueError(f"Unknown tool: {tool_name}")
        return await method(**kwargs)
