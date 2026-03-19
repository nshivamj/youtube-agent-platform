from pydantic import BaseModel


class CommitStats(BaseModel):
    additions: int
    deletions: int
    total: int


class CommitInfo(BaseModel):
    sha: str
    short_sha: str
    title: str
    message: str
    author_name: str
    author_email: str
    authored_date: str
    committed_date: str
    web_url: str
    stats: CommitStats | None = None


class MergeRequestInfo(BaseModel):
    iid: int
    title: str
    description: str
    state: str
    author: str
    source_branch: str
    target_branch: str
    created_at: str
    updated_at: str
    merged_at: str | None = None
    web_url: str
    labels: list[str]
    has_conflicts: bool


class PipelineInfo(BaseModel):
    id: int
    status: str
    ref: str
    sha: str
    created_at: str
    updated_at: str
    web_url: str
    source: str


class ProjectInfo(BaseModel):
    id: int
    name: str
    path_with_namespace: str
    description: str
    default_branch: str
    web_url: str
    star_count: int
    forks_count: int
    open_issues_count: int
    last_activity_at: str


class GitLabQueryResult(BaseModel):
    operation: str
    project: str
    data: list[dict] | dict
    count: int
    timestamp: str
