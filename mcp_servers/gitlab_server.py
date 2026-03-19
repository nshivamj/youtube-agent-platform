"""GitLab MCP server — exposes GitLab tools via the MCP protocol.

Run standalone:
    python mcp_servers/gitlab_server.py
    python mcp_servers/gitlab_server.py --sse
    python mcp_servers/gitlab_server.py --http
"""

import argparse
import json
import logging
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from mcp.server.fastmcp import FastMCP

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from platform_config.domains.gitlab.tools.gitlab_local import GitLabTool

_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("%(message)s"))

logger = logging.getLogger("gitlab_mcp")
logger.setLevel(logging.DEBUG)
logger.addHandler(_handler)
logger.propagate = False

_tool = GitLabTool()


def _emit(level: str, tool: str, **fields: Any) -> None:
    record = {"level": level, "tool": tool, **fields}
    msg = json.dumps(record, default=str)
    getattr(logger, level.lower(), logger.info)(msg)


@contextmanager
def tool_span(tool_name: str, inputs: dict) -> Generator[None, None, None]:
    _emit("info", tool_name, event="call_start", inputs=inputs)
    t0 = time.perf_counter()
    try:
        yield
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        _emit("info", tool_name, event="call_end", latency_ms=latency_ms)
    except Exception as exc:
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        _emit("error", tool_name, event="call_error", error=str(exc), latency_ms=latency_ms)
        raise


mcp = FastMCP(
    "gitlab",
    instructions=(
        "Provides tools to interact with GitLab: list commits, "
        "manage merge requests, view pipelines, and trigger builds. "
        "All operations require a valid GITLAB_TOKEN."
    ),
)


import asyncio


def _run_sync(coro):
    """Run an async coroutine synchronously."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as pool:
        return pool.submit(asyncio.run, coro).result()


@mcp.tool()
def get_commit(project: str = "", sha: str = "HEAD") -> dict:
    """Get details of a specific commit.

    Args:
        project: GitLab project path (e.g. 'group/project'). Uses default if empty.
        sha:     Commit SHA or ref. Defaults to 'HEAD'.
    """
    with tool_span("get_commit", {"project": project, "sha": sha}):
        result = _run_sync(_tool.execute(operation="get_commit", project=project or None, sha=sha))
        if not result.success:
            raise RuntimeError(result.error)
        return result.data


@mcp.tool()
def list_commits(project: str = "", ref_name: str = "main", per_page: int = 20) -> list[dict]:
    """List recent commits for a project.

    Args:
        project:  GitLab project path. Uses default if empty.
        ref_name: Branch or tag name. Defaults to 'main'.
        per_page: Number of commits to return (max 100). Defaults to 20.
    """
    with tool_span("list_commits", {"project": project, "ref_name": ref_name}):
        result = _run_sync(_tool.execute(
            operation="list_commits", project=project or None,
            ref_name=ref_name, per_page=per_page,
        ))
        if not result.success:
            raise RuntimeError(result.error)
        return result.data


@mcp.tool()
def get_mr(project: str = "", mr_iid: int = 0) -> dict:
    """Get details of a specific merge request.

    Args:
        project: GitLab project path. Uses default if empty.
        mr_iid:  Merge request IID.
    """
    with tool_span("get_mr", {"project": project, "mr_iid": mr_iid}):
        result = _run_sync(_tool.execute(operation="get_mr", project=project or None, mr_iid=mr_iid))
        if not result.success:
            raise RuntimeError(result.error)
        return result.data


@mcp.tool()
def list_mrs(project: str = "", state: str = "opened", per_page: int = 20) -> list[dict]:
    """List merge requests for a project.

    Args:
        project:  GitLab project path. Uses default if empty.
        state:    MR state filter — opened | closed | merged | all. Defaults to 'opened'.
        per_page: Number of MRs to return (max 100). Defaults to 20.
    """
    with tool_span("list_mrs", {"project": project, "state": state}):
        result = _run_sync(_tool.execute(
            operation="list_mrs", project=project or None,
            state=state, per_page=per_page,
        ))
        if not result.success:
            raise RuntimeError(result.error)
        return result.data


@mcp.tool()
def create_mr(
    project: str = "",
    source_branch: str = "",
    target_branch: str = "",
    title: str = "",
    description: str = "",
) -> dict:
    """Create a new merge request.

    Args:
        project:       GitLab project path. Uses default if empty.
        source_branch: Branch containing changes.
        target_branch: Branch to merge into.
        title:         MR title (required).
        description:   MR description. Optional.
    """
    with tool_span("create_mr", {"project": project, "title": title}):
        result = _run_sync(_tool.execute(
            operation="create_mr", project=project or None,
            source_branch=source_branch, target_branch=target_branch,
            title=title, description=description,
        ))
        if not result.success:
            raise RuntimeError(result.error)
        return result.data


@mcp.tool()
def get_pipeline(project: str = "", pipeline_id: int = 0) -> dict:
    """Get details of a specific pipeline.

    Args:
        project:     GitLab project path. Uses default if empty.
        pipeline_id: Pipeline ID.
    """
    with tool_span("get_pipeline", {"project": project, "pipeline_id": pipeline_id}):
        result = _run_sync(_tool.execute(
            operation="get_pipeline", project=project or None,
            pipeline_id=pipeline_id,
        ))
        if not result.success:
            raise RuntimeError(result.error)
        return result.data


@mcp.tool()
def list_pipelines(project: str = "", ref: str = "main", per_page: int = 20) -> list[dict]:
    """List pipelines for a project.

    Args:
        project:  GitLab project path. Uses default if empty.
        ref:      Branch ref to filter pipelines. Defaults to 'main'.
        per_page: Number of pipelines to return (max 100). Defaults to 20.
    """
    with tool_span("list_pipelines", {"project": project, "ref": ref}):
        result = _run_sync(_tool.execute(
            operation="list_pipelines", project=project or None,
            ref=ref, per_page=per_page,
        ))
        if not result.success:
            raise RuntimeError(result.error)
        return result.data


@mcp.tool()
def trigger_pipeline(project: str = "", ref: str = "main") -> dict:
    """Trigger a new pipeline run.

    Args:
        project: GitLab project path. Uses default if empty.
        ref:     Branch ref to run the pipeline on. Defaults to 'main'.
    """
    with tool_span("trigger_pipeline", {"project": project, "ref": ref}):
        result = _run_sync(_tool.execute(
            operation="trigger_pipeline", project=project or None, ref=ref,
        ))
        if not result.success:
            raise RuntimeError(result.error)
        return result.data


def main() -> None:
    parser = argparse.ArgumentParser(description="GitLab MCP server")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--sse", action="store_true", help="Run SSE transport on :8010")
    group.add_argument("--http", action="store_true", help="Run streamable-HTTP transport on :8010")
    args = parser.parse_args()

    if args.sse:
        print("[gitlab-mcp] Starting SSE server on http://127.0.0.1:8010/sse", file=sys.stderr)
        mcp.settings.port = 8010
        mcp.run(transport="sse")
    elif args.http:
        print("[gitlab-mcp] Starting HTTP server on http://127.0.0.1:8010/mcp", file=sys.stderr)
        mcp.settings.port = 8010
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
