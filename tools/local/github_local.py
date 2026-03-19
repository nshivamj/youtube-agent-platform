"""GitHub tools — plain functions, no BaseTool wrapping.

ADK can use these directly as tool callables. Each function calls the
GitHub REST API via mcp_servers/github/github_client.py.

Self-registers into the plain function registry on import.
"""
from mcp_servers.github.github_client import (
    list_repositories,
    read_file,
    search_code,
    create_issue,
)
from framework.tools.resolver import register_plain


def github_list_repos(username: str = "nshivamj") -> list[dict]:
    """List public repositories for a GitHub user.

    Args:
        username: GitHub username. Defaults to 'nshivamj'.

    Returns:
        List of repos with name, description, language, stars, url.
    """
    return list_repositories(username)


def github_read_file(owner: str, repo: str, path: str, ref: str = "HEAD") -> str:
    """Read a file from a GitHub repository.

    Args:
        owner: Repository owner (e.g. 'nshivamj').
        repo: Repository name.
        path: File path within the repo (e.g. 'README.md').
        ref: Branch or commit SHA. Defaults to HEAD.

    Returns:
        The file contents as text.
    """
    return read_file(owner, repo, path, ref)


def github_search_code(query: str, owner: str = "", repo: str = "") -> list[dict]:
    """Search code on GitHub.

    Args:
        query: Search query string.
        owner: Optional — scope search to this user/org.
        repo: Optional — scope search to this repo (requires owner too).

    Returns:
        List of matching files with repository, path, and url.
    """
    return search_code(query, owner, repo)


def github_create_issue(owner: str, repo: str, title: str, body: str = "") -> dict:
    """Create a new issue on a GitHub repository.

    Args:
        owner: Repository owner.
        repo: Repository name.
        title: Issue title.
        body: Issue body/description.

    Returns:
        Dict with issue number, title, url, state.
    """
    return create_issue(owner, repo, title, body)


# Self-register on import
register_plain("github_list_repos", github_list_repos)
register_plain("github_read_file", github_read_file)
register_plain("github_search_code", github_search_code)
register_plain("github_create_issue", github_create_issue)
