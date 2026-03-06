from pydantic import BaseModel
from typing import Optional
from enum import Enum


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
