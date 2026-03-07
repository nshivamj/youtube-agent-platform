from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VideoItem(BaseModel):
    video_id: str
    title: str
    watched_at: datetime
    channel: str
    is_short: bool = False


class BingeSession(BaseModel):
    start_time: datetime
    end_time: datetime
    video_count: int
    total_minutes: float


class AnalyzerOutput(BaseModel):
    period: str
    total_videos: int
    shorts_count: int
    regular_count: int
    shorts_percentage: float
    total_hours: float
    avg_hours_per_day: float
    top_channels: list[str]
    peak_hour: int
    binge_sessions: list[BingeSession]


class InsightsInput(BaseModel):
    analysis: AnalyzerOutput
    period: str
    user_goal: Optional[str] = None


class Recommendation(BaseModel):
    title: str
    detail: str
    risk_level: str  # "low" | "medium" | "high"


class InsightsOutput(BaseModel):
    recommendations: list[Recommendation]
    overall_risk: str
    summary: str
    period: str


class ReportInput(BaseModel):
    insights: InsightsOutput
    analysis: AnalyzerOutput
    period: str


class ReportOutput(BaseModel):
    file_path: str
    summary: str
    success: bool
    error: Optional[str] = None
