# Re-export all schemas for backwards-compatible imports.
# Import directly from sub-modules for domain clarity:
#   from core.schemas.youtube import AnalyzerOutput
#   from core.schemas.control_testing import ControlTestPlan

from core.schemas.youtube import (
    VideoItem,
    BingeSession,
    AnalyzerOutput,
    InsightsInput,
    Recommendation,
    InsightsOutput,
    ReportInput,
    ReportOutput,
)
from core.schemas.planning import Step, ExecutionPlan
from core.schemas.approval import ApprovalDecision, ApprovalRequest, ApprovalResponse
from core.schemas.control_testing import (
    EntitlementCheckResult,
    ControlTestPlan,
    PlanReview,
    ControlStatus,
    ControlTestResult,
    ControlTestSummary,
)

__all__ = [
    # youtube
    "VideoItem", "BingeSession", "AnalyzerOutput", "InsightsInput",
    "Recommendation", "InsightsOutput", "ReportInput", "ReportOutput",
    # planning
    "Step", "ExecutionPlan",
    # approval
    "ApprovalDecision", "ApprovalRequest", "ApprovalResponse",
    # control testing
    "EntitlementCheckResult", "ControlTestPlan", "PlanReview",
    "ControlStatus", "ControlTestResult", "ControlTestSummary",
]
