"""GitLab tools — plain functions, registered as ADK FunctionTools on import."""
import os
from typing import Any

from framework.tools.registry import tool

try:
    import gitlab as python_gitlab
    _GITLAB_AVAILABLE = True
except ImportError:
    _GITLAB_AVAILABLE = False


def _client():
    if not _GITLAB_AVAILABLE:
        raise RuntimeError("python-gitlab not installed. Run: pip install python-gitlab")
    return python_gitlab.Gitlab(
        url=os.getenv("GITLAB_URL", "https://gitlab.com"),
        private_token=os.getenv("GITLAB_TOKEN", ""),
    )


def _project(gl, project_path: str | None = None):
    path = project_path or os.getenv("GITLAB_DEFAULT_PROJECT", "")
    if not path:
        raise ValueError("No GitLab project specified. Set GITLAB_DEFAULT_PROJECT in .env.")
    return gl.projects.get(path)


def _commit(raw: dict) -> dict:
    return {
        "sha": raw.get("id", ""),
        "short_sha": raw.get("short_id", raw.get("id", "")[:8]),
        "title": raw.get("title", ""),
        "author": raw.get("author_name", ""),
        "date": raw.get("created_at", ""),
        "url": raw.get("web_url", ""),
    }


def _mr(raw: dict) -> dict:
    author = raw.get("author", {})
    return {
        "iid": raw.get("iid", 0),
        "title": raw.get("title", ""),
        "state": raw.get("state", ""),
        "source_branch": raw.get("source_branch", ""),
        "target_branch": raw.get("target_branch", ""),
        "author": author.get("name", "") if isinstance(author, dict) else str(author),
        "url": raw.get("web_url", ""),
    }


def _pipeline(raw: dict) -> dict:
    return {
        "id": raw.get("id", 0),
        "status": raw.get("status", ""),
        "ref": raw.get("ref", ""),
        "created_at": raw.get("created_at", ""),
        "url": raw.get("web_url", ""),
    }


@tool()
def gitlab_list_commits(
    ref_name: str = "main",
    per_page: int = 20,
    project: str | None = None,
) -> dict:
    """List recent commits on a branch.

    Args:
        ref_name: Branch or tag name. Defaults to 'main'.
        per_page: Max results to return. Defaults to 20.
        project: GitLab project path (e.g. 'group/repo'). Uses GITLAB_DEFAULT_PROJECT if omitted.

    Returns:
        commits: list of {sha, short_sha, title, author, date, url}
    """
    try:
        gl = _client()
        proj = _project(gl, project)
        raw = proj.commits.list(ref_name=ref_name, per_page=per_page, get_all=False)
        commits = [_commit(c.asdict() if hasattr(c, "asdict") else c.__dict__["_attrs"]) for c in raw]
        return {"commits": commits, "count": len(commits)}
    except Exception as exc:
        return {"error": str(exc), "commits": []}


@tool()
def gitlab_get_commit(sha: str, project: str | None = None) -> dict:
    """Get a single commit by SHA.

    Args:
        sha: Full or short commit SHA.
        project: GitLab project path. Uses GITLAB_DEFAULT_PROJECT if omitted.

    Returns:
        Commit fields: sha, short_sha, title, author, date, url.
    """
    try:
        gl = _client()
        proj = _project(gl, project)
        return _commit(proj.commits.get(sha)._attrs)
    except Exception as exc:
        return {"error": str(exc)}


@tool()
def gitlab_list_mrs(
    state: str = "opened",
    per_page: int = 20,
    project: str | None = None,
) -> dict:
    """List merge requests.

    Args:
        state: Filter by state — 'opened', 'closed', 'merged', or 'all'. Defaults to 'opened'.
        per_page: Max results to return. Defaults to 20.
        project: GitLab project path. Uses GITLAB_DEFAULT_PROJECT if omitted.

    Returns:
        mrs: list of {iid, title, state, source_branch, target_branch, author, url}
    """
    try:
        gl = _client()
        proj = _project(gl, project)
        raw = proj.mergerequests.list(state=state, per_page=per_page, get_all=False)
        mrs = [_mr(mr._attrs) for mr in raw]
        return {"mrs": mrs, "count": len(mrs)}
    except Exception as exc:
        return {"error": str(exc), "mrs": []}


@tool()
def gitlab_get_mr(iid: int, project: str | None = None) -> dict:
    """Get a single merge request by internal ID.

    Args:
        iid: Merge request internal ID (the number shown in the GitLab UI).
        project: GitLab project path. Uses GITLAB_DEFAULT_PROJECT if omitted.

    Returns:
        MR fields: iid, title, state, source_branch, target_branch, author, url.
    """
    try:
        gl = _client()
        proj = _project(gl, project)
        return _mr(proj.mergerequests.get(iid)._attrs)
    except Exception as exc:
        return {"error": str(exc)}


@tool(requires_approval=True)
def gitlab_create_mr(
    source_branch: str,
    target_branch: str,
    title: str,
    description: str = "",
    project: str | None = None,
) -> dict:
    """Create a merge request.

    Args:
        source_branch: Branch to merge from.
        target_branch: Branch to merge into.
        title: MR title.
        description: Optional MR description.
        project: GitLab project path. Uses GITLAB_DEFAULT_PROJECT if omitted.

    Returns:
        Created MR fields: iid, title, state, source_branch, target_branch, author, url.
    """
    try:
        gl = _client()
        proj = _project(gl, project)
        mr = proj.mergerequests.create({
            "source_branch": source_branch,
            "target_branch": target_branch,
            "title": title,
            "description": description,
        })
        return _mr(mr._attrs)
    except Exception as exc:
        return {"error": str(exc)}


@tool()
def gitlab_list_pipelines(
    ref: str | None = None,
    per_page: int = 20,
    project: str | None = None,
) -> dict:
    """List pipelines.

    Args:
        ref: Filter by branch/tag name. Omit for all pipelines.
        per_page: Max results to return. Defaults to 20.
        project: GitLab project path. Uses GITLAB_DEFAULT_PROJECT if omitted.

    Returns:
        pipelines: list of {id, status, ref, created_at, url}
    """
    try:
        gl = _client()
        proj = _project(gl, project)
        kwargs: dict[str, Any] = {"per_page": per_page}
        if ref:
            kwargs["ref"] = ref
        raw = proj.pipelines.list(**kwargs, get_all=False)
        pipelines = [_pipeline(p._attrs) for p in raw]
        return {"pipelines": pipelines, "count": len(pipelines)}
    except Exception as exc:
        return {"error": str(exc), "pipelines": []}


@tool()
def gitlab_get_pipeline(pipeline_id: int, project: str | None = None) -> dict:
    """Get a pipeline by ID.

    Args:
        pipeline_id: Pipeline numeric ID.
        project: GitLab project path. Uses GITLAB_DEFAULT_PROJECT if omitted.

    Returns:
        Pipeline fields: id, status, ref, created_at, url.
    """
    try:
        gl = _client()
        proj = _project(gl, project)
        return _pipeline(proj.pipelines.get(pipeline_id)._attrs)
    except Exception as exc:
        return {"error": str(exc)}


@tool(requires_approval=True)
def gitlab_trigger_pipeline(
    ref: str,
    variables: dict | None = None,
    project: str | None = None,
) -> dict:
    """Trigger a pipeline on a branch or tag.

    Args:
        ref: Branch or tag to run the pipeline on.
        variables: Optional dict of CI/CD variable key-value pairs.
        project: GitLab project path. Uses GITLAB_DEFAULT_PROJECT if omitted.

    Returns:
        Triggered pipeline fields: id, status, ref, created_at, url.
    """
    try:
        gl = _client()
        proj = _project(gl, project)
        pipeline = proj.pipelines.create({"ref": ref, "variables": variables or []})
        return _pipeline(pipeline._attrs)
    except Exception as exc:
        return {"error": str(exc)}
