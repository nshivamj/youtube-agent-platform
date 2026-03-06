from pydantic import BaseModel
from typing import Optional
from enum import Enum


class EntitlementCheckResult(BaseModel):
    user_id: str
    app_name: str
    has_access: bool
    access_type: Optional[str] = None   # "read" | "write" | "admin" | None
    is_valid_user: bool = True          # False → ghost / stale account
    reason: Optional[str] = None


class ControlTestPlan(BaseModel):
    control_name: str
    control_objective: str
    app_name: str
    users_to_test: list[str]
    test_steps: list[str]
    risk_level: str                     # "low" | "medium" | "high"
    notes: Optional[str] = None


class PlanReview(BaseModel):
    iteration: int
    review_focus: str
    approved: bool
    feedback: str
    suggested_changes: list[str] = []
    confidence_score: float             # 0.0 – 1.0


class ControlStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"


class ControlTestResult(BaseModel):
    app_name: str
    total_users_tested: int
    users_with_access: list[str]
    users_without_access: list[str]
    invalid_users: list[str]
    check_results: list[EntitlementCheckResult]


class ControlTestSummary(BaseModel):
    control_name: str
    control_objective: str
    test_date: str
    overall_status: ControlStatus
    app_name: str
    total_users_tested: int
    compliant_users: int
    non_compliant_users: int
    invalid_users: int
    exceptions: list[str] = []
    plan_review_iterations: int
    summary_narrative: str
    recommendations: list[str]
