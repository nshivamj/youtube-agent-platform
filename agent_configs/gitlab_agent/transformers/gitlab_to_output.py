from agent_configs.gitlab_agent.schemas.gitlab_output import (
    CommitInfo,
    MergeRequestInfo,
    PipelineInfo,
)


def raw_to_commit(raw: dict) -> CommitInfo:
    return CommitInfo(
        sha=raw.get("id", ""),
        short_sha=raw.get("short_id", raw.get("id", "")[:8]),
        title=raw.get("title", ""),
        author=raw.get("author_name", ""),
        date=raw.get("created_at", ""),
        url=raw.get("web_url", ""),
    )


def raw_to_mr(raw: dict) -> MergeRequestInfo:
    author = raw.get("author", {})
    author_name = author.get("name", "") if isinstance(author, dict) else str(author)
    return MergeRequestInfo(
        iid=raw.get("iid", 0),
        title=raw.get("title", ""),
        state=raw.get("state", ""),
        source_branch=raw.get("source_branch", ""),
        target_branch=raw.get("target_branch", ""),
        author=author_name,
        url=raw.get("web_url", ""),
    )


def raw_to_pipeline(raw: dict) -> PipelineInfo:
    return PipelineInfo(
        id=raw.get("id", 0),
        status=raw.get("status", ""),
        ref=raw.get("ref", ""),
        created_at=raw.get("created_at", ""),
        url=raw.get("web_url", ""),
    )
