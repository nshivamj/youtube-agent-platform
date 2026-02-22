"""Thin GitHub REST API v3 client — used exclusively by the MCP server tools."""

import base64
import os
from typing import Any

import httpx

_BASE = "https://api.github.com"
_ACCEPT = "application/vnd.github+json"


class GitHubError(Exception):
    """Raised for all GitHub API errors with a human-readable message."""


def _headers() -> dict[str, str]:
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        raise GitHubError("GITHUB_TOKEN is not set. Add it to your .env file.")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": _ACCEPT,
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _get(path: str, params: dict | None = None) -> Any:
    url = f"{_BASE}{path}"
    with httpx.Client(timeout=15) as client:
        resp = client.get(url, headers=_headers(), params=params or {})
    _raise_for_status(resp)
    return resp.json()


def _post(path: str, payload: dict) -> Any:
    url = f"{_BASE}{path}"
    with httpx.Client(timeout=15) as client:
        resp = client.post(url, headers=_headers(), json=payload)
    _raise_for_status(resp)
    return resp.json()


def _raise_for_status(resp: httpx.Response) -> None:
    if resp.status_code == 401:
        raise GitHubError("Authentication failed — check your GITHUB_TOKEN.")
    if resp.status_code == 403:
        remaining = resp.headers.get("x-ratelimit-remaining", "?")
        if remaining == "0":
            reset = resp.headers.get("x-ratelimit-reset", "?")
            raise GitHubError(f"GitHub rate limit exceeded. Resets at epoch {reset}.")
        raise GitHubError(f"Forbidden (403): {resp.text[:200]}")
    if resp.status_code == 404:
        raise GitHubError(f"Resource not found (404): {resp.url}")
    if resp.status_code >= 400:
        raise GitHubError(f"GitHub API error {resp.status_code}: {resp.text[:200]}")


# ---------------------------------------------------------------------------
# Domain functions
# ---------------------------------------------------------------------------

def list_repositories(username: str, repo_type: str = "public") -> list[dict]:
    """Return repos for *username*. repo_type: public | private | all | forks | sources | member."""
    data = _get(f"/users/{username}/repos", params={"type": repo_type, "per_page": 30})
    return [
        {
            "name": r["name"],
            "full_name": r["full_name"],
            "description": r.get("description") or "",
            "language": r.get("language") or "",
            "stars": r["stargazers_count"],
            "forks": r["forks_count"],
            "private": r["private"],
            "url": r["html_url"],
        }
        for r in data
    ]


def read_file(owner: str, repo: str, path: str, ref: str = "HEAD") -> str:
    """Return decoded text content of a file in *owner/repo* at *path*."""
    data = _get(f"/repos/{owner}/{repo}/contents/{path.lstrip('/')}", params={"ref": ref})
    if isinstance(data, list):
        raise GitHubError(f"'{path}' is a directory, not a file.")
    if data.get("encoding") != "base64":
        raise GitHubError(f"Unexpected encoding: {data.get('encoding')}")
    return base64.b64decode(data["content"]).decode("utf-8", errors="replace")


def search_code(query: str, owner: str = "", repo: str = "") -> list[dict]:
    """Search code across GitHub. Optionally scope to owner or owner/repo."""
    scoped = query
    if owner and repo:
        scoped = f"{query} repo:{owner}/{repo}"
    elif owner:
        scoped = f"{query} user:{owner}"
    data = _get("/search/code", params={"q": scoped, "per_page": 10})
    return [
        {
            "repository": item["repository"]["full_name"],
            "path": item["path"],
            "url": item["html_url"],
            "score": item.get("score", 0),
        }
        for item in data.get("items", [])
    ]


def create_issue(owner: str, repo: str, title: str, body: str = "") -> dict:
    """Open a new issue in *owner/repo* and return key fields."""
    data = _post(f"/repos/{owner}/{repo}/issues", {"title": title, "body": body})
    return {
        "number": data["number"],
        "title": data["title"],
        "url": data["html_url"],
        "state": data["state"],
    }
