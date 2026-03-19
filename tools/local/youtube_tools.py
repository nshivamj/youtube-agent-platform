"""YouTube watch-history tools — plain functions, registered as ADK FunctionTools on import."""
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from framework.tools.registry import tool

DATA_PATH = Path("data/watch-history.json")


@dataclass
class _Video:
    video_id: str
    title: str
    watched_at: datetime
    channel: str
    is_short: bool


# Module-level cache — loaded once per process
_data: list[_Video] = []
_loaded = False


def _load() -> None:
    global _data, _loaded
    if _loaded:
        return
    if not DATA_PATH.exists():
        _data = []
        _loaded = True
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
            items.append(_Video(
                video_id=url.split("v=")[-1] if "v=" in url else url,
                title=title,
                watched_at=watched_at,
                channel=channel,
                is_short="shorts" in url.lower(),
            ))
        except Exception:
            pass
    _data = items
    _loaded = True


def _filter_by_month(month: str) -> list[_Video]:
    _load()
    month_map = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12,
    }
    m_lower = month.lower().strip()
    if m_lower in month_map:
        m = month_map[m_lower]
        return [v for v in _data if v.watched_at.month == m]
    if "-" in month:
        parts = month.split("-")
        if len(parts) == 2:
            year, mon = int(parts[0]), int(parts[1])
            return [v for v in _data if v.watched_at.year == year and v.watched_at.month == mon]
    return _data


def _binge_sessions(videos: list[_Video], threshold_minutes: int = 120) -> list[dict]:
    if not videos:
        return []
    sorted_v = sorted(videos, key=lambda v: v.watched_at)
    sessions, start, prev, count = [], sorted_v[0].watched_at, sorted_v[0].watched_at, 1
    for v in sorted_v[1:]:
        if (v.watched_at - prev).total_seconds() / 60 < 30:
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
            start = prev = v.watched_at
            count = 1
    return sessions


@tool()
def get_watch_summary(month: str) -> dict:
    """Get watch statistics for a given month.

    Args:
        month: Month name ('january') or year-month ('2024-01').

    Returns:
        period, total_videos, shorts_count, regular_count, shorts_percentage,
        total_hours, avg_hours_per_day, top_channels, peak_hour, binge_sessions.
    """
    filtered = _filter_by_month(month)
    if not filtered:
        return {
            "period": month, "total_videos": 0, "shorts_count": 0, "regular_count": 0,
            "shorts_percentage": 0.0, "total_hours": 0.0, "avg_hours_per_day": 0.0,
            "top_channels": [], "peak_hour": 0, "binge_sessions": [],
        }
    shorts = [v for v in filtered if v.is_short]
    channels = Counter(v.channel for v in filtered if v.channel)
    hours_by_day: dict = defaultdict(float)
    for v in filtered:
        hours_by_day[v.watched_at.date()] += 1 / 60
    days = len(hours_by_day) or 1
    total_hours = sum(hours_by_day.values())
    hour_counts = Counter(v.watched_at.hour for v in filtered)
    return {
        "period": month,
        "total_videos": len(filtered),
        "shorts_count": len(shorts),
        "regular_count": len(filtered) - len(shorts),
        "shorts_percentage": round(len(shorts) / len(filtered) * 100, 1),
        "total_hours": round(total_hours, 1),
        "avg_hours_per_day": round(total_hours / days, 2),
        "top_channels": [ch for ch, _ in channels.most_common(5)],
        "peak_hour": hour_counts.most_common(1)[0][0] if hour_counts else 0,
        "binge_sessions": _binge_sessions(filtered),
    }


@tool()
def get_shorts_ratio(month: str) -> float:
    """Get the percentage of Shorts watched in a given month.

    Args:
        month: Month name ('january') or year-month ('2024-01').

    Returns:
        Percentage of videos that are YouTube Shorts (0.0–100.0).
    """
    return get_watch_summary(month)["shorts_percentage"]


@tool()
def get_top_channels(n: int = 5) -> list:
    """Get the most-watched channels across all history.

    Args:
        n: Number of top channels to return. Defaults to 5.

    Returns:
        List of channel names ordered by watch count.
    """
    _load()
    return [ch for ch, _ in Counter(v.channel for v in _data if v.channel).most_common(n)]


@tool()
def get_watch_by_hour() -> dict:
    """Get video count broken down by hour of day (0–23).

    Returns:
        Dict mapping hour string ('0'–'23') to video count.
    """
    _load()
    counts = Counter(v.watched_at.hour for v in _data)
    return {str(h): counts.get(h, 0) for h in range(24)}


@tool()
def get_binge_sessions(threshold_minutes: int = 120) -> list:
    """Find binge-watching sessions that exceed a duration threshold.

    Args:
        threshold_minutes: Minimum session duration to include. Defaults to 120.

    Returns:
        List of {start_time, end_time, video_count, total_minutes}.
    """
    _load()
    return _binge_sessions(_data, threshold_minutes)
