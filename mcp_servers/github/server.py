"""GitHub MCP server — exposes GitHub tools via the MCP protocol.

Run standalone:
    python run_mcp_github.py

Or consume from an ADK agent via McpToolset + StdioServerParameters.
"""

from mcp.server.fastmcp import FastMCP

from mcp_servers.github import github_client as gh
from mcp_servers.github.logger import tool_span

mcp = FastMCP(
    "github",
    instructions=(
        "Provides tools to interact with GitHub: list repositories, "
        "read files, search code, and create issues. "
        "All operations require a valid GITHUB_TOKEN."
    ),
)


# ---------------------------------------------------------------------------
# Tool: list_repositories
# ---------------------------------------------------------------------------

@mcp.tool()
def list_repositories(username: str, repo_type: str = "public") -> list[dict]:
    """List GitHub repositories for a user.

    Args:
        username:  GitHub username or organisation name.
        repo_type: Visibility filter — public | private | all | forks | sources | member.
                   Defaults to 'public'.

    Returns:
        List of repository summaries (name, description, language, stars, url).
    """
    with tool_span("list_repositories", {"username": username, "repo_type": repo_type}):
        return gh.list_repositories(username, repo_type)


# ---------------------------------------------------------------------------
# Tool: read_file
# ---------------------------------------------------------------------------

@mcp.tool()
def read_file(owner: str, repo: str, path: str, ref: str = "HEAD") -> str:
    """Read the text content of a file in a GitHub repository.

    Args:
        owner: Repository owner (user or org).
        repo:  Repository name.
        path:  File path inside the repo (e.g. 'src/main.py').
        ref:   Branch, tag, or commit SHA. Defaults to 'HEAD'.

    Returns:
        Full UTF-8 text content of the file.
    """
    with tool_span("read_file", {"owner": owner, "repo": repo, "path": path, "ref": ref}):
        return gh.read_file(owner, repo, path, ref)


# ---------------------------------------------------------------------------
# Tool: search_code
# ---------------------------------------------------------------------------

@mcp.tool()
def search_code(query: str, owner: str = "", repo: str = "") -> list[dict]:
    """Search code across GitHub.

    Args:
        query: Search terms (GitHub code search syntax supported).
        owner: Optional — scope results to this user/org.
        repo:  Optional — scope results to this repository (requires owner).

    Returns:
        Up to 10 matching files with repository name, file path, and URL.
    """
    with tool_span("search_code", {"query": query, "owner": owner, "repo": repo}):
        return gh.search_code(query, owner, repo)


# ---------------------------------------------------------------------------
# Tool: create_issue
# ---------------------------------------------------------------------------

@mcp.tool()
def create_issue(owner: str, repo: str, title: str, body: str = "") -> dict:
    """Create a new GitHub issue.

    Args:
        owner: Repository owner.
        repo:  Repository name.
        title: Issue title (required).
        body:  Issue body / description in markdown. Optional.

    Returns:
        Created issue with number, title, URL, and state.
    """
    with tool_span("create_issue", {"owner": owner, "repo": repo, "title": title}):
        return gh.create_issue(owner, repo, title, body)
