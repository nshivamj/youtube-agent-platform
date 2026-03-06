from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# ── Entitlement check ────────────────────────────────────────────────────────

class EntitlementCheckResult(BaseModel):
    user_id: str
    app_name: str
    has_access: bool
    access_type: Optional[str] = None   # "read" | "write" | "admin" | None
    is_valid_user: bool = True          # False → ghost / service account
    reason: Optional[str] = None


# ── Plan ─────────────────────────────────────────────────────────────────────

class ControlTestPlan(BaseModel):
    control_name: str
    control_objective: str
    app_name: str
    users_to_test: list[str]
    test_steps: list[str]
    risk_level: str          # "low" | "medium" | "high"
    notes: Optional[str] = None


# ── Review ───────────────────────────────────────────────────────────────────

class PlanReview(BaseModel):
    iteration: int
    review_focus: str        # what angle this review covered
    approved: bool
    feedback: str
    suggested_changes: list[str] = []
    confidence_score: float  # 0.0 – 1.0


# ── Execution ────────────────────────────────────────────────────────────────

class ControlStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PARTIAL = "PARTIAL"


class ControlTestResult(BaseModel):
    app_name: str
    total_users_tested: int
    users_with_access: list[str]
    users_without_access: list[str]
    invalid_users: list[str]            # ghost / stale accounts
    check_results: list[EntitlementCheckResult]


# ── Summary ──────────────────────────────────────────────────────────────────

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
    exceptions: list[str] = Field(
        default_factory=list,
        description="Users who failed the entitlement check — requires follow-up",
    )
    plan_review_iterations: int
    summary_narrative: str
    recommendations: list[str]
