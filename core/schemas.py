from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


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


class Step(BaseModel):
    step_number: int
    agent_name: str
    task: str
    expected_output: str
    depends_on: list[int] = []


class ExecutionPlan(BaseModel):
    goal: str
    steps: list[Step]
    estimated_duration: str


class ApprovalDecision(str, Enum):
    APPROVED = "approved"
    MODIFIED = "modified"
    REJECTED = "rejected"


class ApprovalRequest(BaseModel):
    request_id: str = ""
    agent_name: str
    triggered_by: str   # "agent" | "tool" | "runtime"
    action: str
    message: str
    options: list[str]
    risk_level: str     # "low" | "medium" | "high"
    context: dict = {}
    default: str
    session_id: str


class ApprovalResponse(BaseModel):
    request_id: str
    decision: ApprovalDecision
    modified: Optional[str] = None
    reason: Optional[str] = None
