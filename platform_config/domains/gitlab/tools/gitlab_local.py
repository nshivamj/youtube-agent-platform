"""GitLab operations tool — uses python-gitlab SDK to interact with GitLab."""

import os
from datetime import datetime, timezone

import gitlab

from framework.tools.base_tool import BaseTool, ToolResult
from platform_config.domains.gitlab.transformers import (
    transform_commit,
    transform_merge_request,
    transform_pipeline,
    transform_project,
)


class GitLabTool(BaseTool):
    name = "gitlab"
    description = "GitLab operations tool"

    _APPROVAL_OPERATIONS = {"create_mr", "trigger_pipeline"}

    def __init__(self):
        self._url = os.getenv("GITLAB_URL", "https://gitlab.com")
        self._token = os.getenv("GITLAB_TOKEN", "")
        self._default_project = os.getenv("GITLAB_DEFAULT_PROJECT", "")

    def _client(self) -> gitlab.Gitlab:
        if not self._token:
            raise ValueError("GITLAB_TOKEN is not set. Add it to your .env file.")
        return gitlab.Gitlab(self._url, private_token=self._token)

    def _resolve_project(self, project: str | None) -> str:
        resolved = project or self._default_project
        if not resolved:
            raise ValueError(
                "No project specified and GITLAB_DEFAULT_PROJECT is not set."
            )
        return resolved

    async def execute(self, operation: str = "", **kwargs) -> ToolResult:
        if not operation:
            return ToolResult(
                success=False,
                data=None,
                error="No operation specified.",
            )

        if operation in self._APPROVAL_OPERATIONS:
            self.requires_approval = True
        else:
            self.requires_approval = False

        dispatch = {
            "get_commit": self._get_commit,
            "list_commits": self._list_commits,
            "get_mr": self._get_mr,
            "list_mrs": self._list_mrs,
            "create_mr": self._create_mr,
            "get_pipeline": self._get_pipeline,
            "list_pipelines": self._list_pipelines,
            "trigger_pipeline": self._trigger_pipeline,
        }

        handler = dispatch.get(operation)
        if handler is None:
            return ToolResult(
                success=False,
                data=None,
                error=f"Unknown operation: {operation}",
            )

        try:
            data = handler(**kwargs)
            return ToolResult(
                success=True,
                data=data if isinstance(data, list) else data.model_dump(),
                metadata={
                    "operation": operation,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                data=None,
                error=str(exc),
                metadata={"operation": operation},
            )

    def _get_commit(self, project: str | None = None, sha: str = "HEAD"):
        gl = self._client()
        proj = gl.projects.get(self._resolve_project(project))
        commit = proj.commits.get(sha)
        return transform_commit(commit.attributes)

    def _list_commits(
        self,
        project: str | None = None,
        ref_name: str = "main",
        per_page: int = 20,
    ):
        gl = self._client()
        proj = gl.projects.get(self._resolve_project(project))
        commits = proj.commits.list(ref_name=ref_name, per_page=min(per_page, 100))
        return [transform_commit(c.attributes) for c in commits]

    def _get_mr(self, project: str | None = None, mr_iid: int = 0):
        gl = self._client()
        proj = gl.projects.get(self._resolve_project(project))
        mr = proj.mergerequests.get(mr_iid)
        return transform_merge_request(mr.attributes)

    def _list_mrs(
        self,
        project: str | None = None,
        state: str = "opened",
        per_page: int = 20,
    ):
        gl = self._client()
        proj = gl.projects.get(self._resolve_project(project))
        mrs = proj.mergerequests.list(state=state, per_page=min(per_page, 100))
        return [transform_merge_request(m.attributes) for m in mrs]

    def _create_mr(
        self,
        project: str | None = None,
        source_branch: str = "",
        target_branch: str = "",
        title: str = "",
        description: str = "",
    ):
        gl = self._client()
        proj = gl.projects.get(self._resolve_project(project))
        mr = proj.mergerequests.create({
            "source_branch": source_branch,
            "target_branch": target_branch,
            "title": title,
            "description": description,
        })
        return transform_merge_request(mr.attributes)

    def _get_pipeline(self, project: str | None = None, pipeline_id: int = 0):
        gl = self._client()
        proj = gl.projects.get(self._resolve_project(project))
        pipeline = proj.pipelines.get(pipeline_id)
        return transform_pipeline(pipeline.attributes)

    def _list_pipelines(
        self,
        project: str | None = None,
        ref: str = "main",
        per_page: int = 20,
    ):
        gl = self._client()
        proj = gl.projects.get(self._resolve_project(project))
        pipelines = proj.pipelines.list(ref=ref, per_page=min(per_page, 100))
        return [transform_pipeline(p.attributes) for p in pipelines]

    def _trigger_pipeline(self, project: str | None = None, ref: str = "main"):
        gl = self._client()
        proj = gl.projects.get(self._resolve_project(project))
        pipeline = proj.pipelines.create({"ref": ref})
        return transform_pipeline(pipeline.attributes)

    def get_schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": [
                            "get_commit",
                            "list_commits",
                            "get_mr",
                            "list_mrs",
                            "create_mr",
                            "get_pipeline",
                            "list_pipelines",
                            "trigger_pipeline",
                        ],
                        "description": "The GitLab operation to perform.",
                    },
                    "project": {
                        "type": "string",
                        "description": "GitLab project path (e.g. 'group/project'). Falls back to GITLAB_DEFAULT_PROJECT.",
                    },
                    "sha": {
                        "type": "string",
                        "description": "Commit SHA (for get_commit).",
                    },
                    "ref_name": {
                        "type": "string",
                        "description": "Branch or tag name (for list_commits). Default: 'main'.",
                    },
                    "ref": {
                        "type": "string",
                        "description": "Branch ref (for list_pipelines, trigger_pipeline). Default: 'main'.",
                    },
                    "per_page": {
                        "type": "integer",
                        "description": "Number of results per page (max 100).",
                    },
                    "mr_iid": {
                        "type": "integer",
                        "description": "Merge request IID (for get_mr).",
                    },
                    "state": {
                        "type": "string",
                        "description": "MR state filter (for list_mrs). Default: 'opened'.",
                    },
                    "source_branch": {
                        "type": "string",
                        "description": "Source branch (for create_mr).",
                    },
                    "target_branch": {
                        "type": "string",
                        "description": "Target branch (for create_mr).",
                    },
                    "title": {
                        "type": "string",
                        "description": "MR title (for create_mr).",
                    },
                    "description": {
                        "type": "string",
                        "description": "MR description (for create_mr).",
                    },
                    "pipeline_id": {
                        "type": "integer",
                        "description": "Pipeline ID (for get_pipeline).",
                    },
                },
                "required": ["operation"],
            },
        }
