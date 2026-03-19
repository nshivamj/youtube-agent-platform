"""GitLab local tool implementations. Self-registers all tools on import."""
import os
from typing import Any

from framework.tools.base_tool import BaseTool, ToolResult

try:
    import gitlab as python_gitlab
    _GITLAB_AVAILABLE = True
except ImportError:
    _GITLAB_AVAILABLE = False


def _get_client():
    if not _GITLAB_AVAILABLE:
        raise RuntimeError("python-gitlab is not installed. Run: pip install python-gitlab")
    url = os.getenv("GITLAB_URL", "https://gitlab.com")
    token = os.getenv("GITLAB_TOKEN", "")
    return python_gitlab.Gitlab(url=url, private_token=token)


def _get_project(gl, project_path: str | None = None):
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


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

class ListCommitsTool(BaseTool):
    name = "gitlab_list_commits"
    description = "List recent commits on a branch. Args: ref_name (str, default 'main'), per_page (int, default 20), project (str, optional)."
    requires_approval = False

    def execute(self, ref_name: str = "main", per_page: int = 20, project: str | None = None) -> ToolResult:
        try:
            gl = _get_client()
            proj = _get_project(gl, project)
            raw = proj.commits.list(ref_name=ref_name, per_page=per_page)
            commits = [_commit(c.asdict() if hasattr(c, "asdict") else c.__dict__["_attrs"]) for c in raw]
            return ToolResult(success=True, data=commits, metadata={"count": len(commits)})
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))


class GetCommitTool(BaseTool):
    name = "gitlab_get_commit"
    description = "Get a single commit by SHA. Args: sha (str), project (str, optional)."
    requires_approval = False

    def execute(self, sha: str, project: str | None = None) -> ToolResult:
        try:
            gl = _get_client()
            proj = _get_project(gl, project)
            raw = proj.commits.get(sha)
            return ToolResult(success=True, data=_commit(raw._attrs))
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))


class ListMRsTool(BaseTool):
    name = "gitlab_list_mrs"
    description = "List merge requests. Args: state (str, default 'opened'), per_page (int, default 20), project (str, optional)."
    requires_approval = False

    def execute(self, state: str = "opened", per_page: int = 20, project: str | None = None) -> ToolResult:
        try:
            gl = _get_client()
            proj = _get_project(gl, project)
            raw = proj.mergerequests.list(state=state, per_page=per_page)
            mrs = [_mr(mr._attrs) for mr in raw]
            return ToolResult(success=True, data=mrs, metadata={"count": len(mrs)})
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))


class GetMRTool(BaseTool):
    name = "gitlab_get_mr"
    description = "Get a single MR by iid. Args: iid (int), project (str, optional)."
    requires_approval = False

    def execute(self, iid: int, project: str | None = None) -> ToolResult:
        try:
            gl = _get_client()
            proj = _get_project(gl, project)
            raw = proj.mergerequests.get(iid)
            return ToolResult(success=True, data=_mr(raw._attrs))
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))


class CreateMRTool(BaseTool):
    name = "gitlab_create_mr"
    description = "Create a merge request. Args: source_branch (str), target_branch (str), title (str), description (str, optional), project (str, optional)."
    requires_approval = True

    def execute(self, source_branch: str, target_branch: str, title: str, description: str = "", project: str | None = None) -> ToolResult:
        try:
            gl = _get_client()
            proj = _get_project(gl, project)
            mr = proj.mergerequests.create({
                "source_branch": source_branch,
                "target_branch": target_branch,
                "title": title,
                "description": description,
            })
            return ToolResult(success=True, data=_mr(mr._attrs))
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))


class ListPipelinesTool(BaseTool):
    name = "gitlab_list_pipelines"
    description = "List pipelines. Args: ref (str, optional), per_page (int, default 20), project (str, optional)."
    requires_approval = False

    def execute(self, ref: str | None = None, per_page: int = 20, project: str | None = None) -> ToolResult:
        try:
            gl = _get_client()
            proj = _get_project(gl, project)
            kwargs: dict[str, Any] = {"per_page": per_page}
            if ref:
                kwargs["ref"] = ref
            raw = proj.pipelines.list(**kwargs)
            pipelines = [_pipeline(p._attrs) for p in raw]
            return ToolResult(success=True, data=pipelines, metadata={"count": len(pipelines)})
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))


class GetPipelineTool(BaseTool):
    name = "gitlab_get_pipeline"
    description = "Get a pipeline by ID. Args: pipeline_id (int), project (str, optional)."
    requires_approval = False

    def execute(self, pipeline_id: int, project: str | None = None) -> ToolResult:
        try:
            gl = _get_client()
            proj = _get_project(gl, project)
            raw = proj.pipelines.get(pipeline_id)
            return ToolResult(success=True, data=_pipeline(raw._attrs))
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))


class TriggerPipelineTool(BaseTool):
    name = "gitlab_trigger_pipeline"
    description = "Trigger a pipeline on a branch/ref. Args: ref (str), variables (dict, optional), project (str, optional)."
    requires_approval = True

    def execute(self, ref: str, variables: dict | None = None, project: str | None = None) -> ToolResult:
        try:
            gl = _get_client()
            proj = _get_project(gl, project)
            pipeline = proj.pipelines.create({"ref": ref, "variables": variables or []})
            return ToolResult(success=True, data=_pipeline(pipeline._attrs))
        except Exception as exc:
            return ToolResult(success=False, error=str(exc))


# ---------------------------------------------------------------------------
# Self-register all tools on import
# ---------------------------------------------------------------------------

from framework.tools.local_registry import register

for _cls in [
    ListCommitsTool,
    GetCommitTool,
    ListMRsTool,
    GetMRTool,
    CreateMRTool,
    ListPipelinesTool,
    GetPipelineTool,
    TriggerPipelineTool,
]:
    register(_cls())
