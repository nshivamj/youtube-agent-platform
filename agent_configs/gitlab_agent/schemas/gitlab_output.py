from pydantic import BaseModel
from typing import Any


class GitLabResult(BaseModel):
    operation: str
    success: bool
    data: list[dict[str, Any]] = []
    summary: str = ""
    error: str | None = None


class CommitInfo(BaseModel):
    sha: str
    short_sha: str
    title: str
    author: str
    date: str
    url: str


class MergeRequestInfo(BaseModel):
    iid: int
    title: str
    state: str
    source_branch: str
    target_branch: str
    author: str
    url: str


class PipelineInfo(BaseModel):
    id: int
    status: str
    ref: str
    created_at: str
    url: str
