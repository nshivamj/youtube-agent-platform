from platform_config.domains.gitlab.schemas import (
    CommitInfo,
    CommitStats,
    MergeRequestInfo,
    PipelineInfo,
    ProjectInfo,
)


def transform_commit(raw: dict) -> CommitInfo:
    stats_raw = raw.get("stats")
    stats = None
    if stats_raw:
        stats = CommitStats(
            additions=stats_raw.get("additions", 0),
            deletions=stats_raw.get("deletions", 0),
            total=stats_raw.get("total", 0),
        )
    return CommitInfo(
        sha=raw.get("id", ""),
        short_sha=raw.get("short_id", raw.get("id", "")[:8]),
        title=raw.get("title", ""),
        message=raw.get("message", ""),
        author_name=raw.get("author_name", ""),
        author_email=raw.get("author_email", ""),
        authored_date=raw.get("authored_date", ""),
        committed_date=raw.get("committed_date", ""),
        web_url=raw.get("web_url", ""),
        stats=stats,
    )


def transform_merge_request(raw: dict) -> MergeRequestInfo:
    author = raw.get("author", {})
    author_name = author.get("username", "") if isinstance(author, dict) else str(author)
    return MergeRequestInfo(
        iid=raw.get("iid", 0),
        title=raw.get("title", ""),
        description=raw.get("description", "") or "",
        state=raw.get("state", ""),
        author=author_name,
        source_branch=raw.get("source_branch", ""),
        target_branch=raw.get("target_branch", ""),
        created_at=raw.get("created_at", ""),
        updated_at=raw.get("updated_at", ""),
        merged_at=raw.get("merged_at"),
        web_url=raw.get("web_url", ""),
        labels=raw.get("labels", []),
        has_conflicts=raw.get("has_conflicts", False),
    )


def transform_pipeline(raw: dict) -> PipelineInfo:
    return PipelineInfo(
        id=raw.get("id", 0),
        status=raw.get("status", ""),
        ref=raw.get("ref", ""),
        sha=raw.get("sha", ""),
        created_at=raw.get("created_at", ""),
        updated_at=raw.get("updated_at", ""),
        web_url=raw.get("web_url", ""),
        source=raw.get("source", ""),
    )


def transform_project(raw: dict) -> ProjectInfo:
    return ProjectInfo(
        id=raw.get("id", 0),
        name=raw.get("name", ""),
        path_with_namespace=raw.get("path_with_namespace", ""),
        description=raw.get("description", "") or "",
        default_branch=raw.get("default_branch", "main"),
        web_url=raw.get("web_url", ""),
        star_count=raw.get("star_count", 0),
        forks_count=raw.get("forks_count", 0),
        open_issues_count=raw.get("open_issues_count", 0),
        last_activity_at=raw.get("last_activity_at", ""),
    )
