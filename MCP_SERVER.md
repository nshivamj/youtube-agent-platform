# MCP Server System

## 1. Overview

This project uses the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) to expose GitHub operations as tools that ADK (Agent Development Kit) agents can call at runtime. MCP is a standardised JSON-RPC protocol that lets an AI agent discover and invoke tools hosted in a separate process. The protocol decouples tool implementation from agent logic: the MCP server owns the API credentials and HTTP calls, while the agent only sees typed tool schemas.

In this project the pattern works as follows:

1. **`mcp_servers/github/`** contains a standalone MCP server built with `FastMCP`. It wraps the GitHub REST API v3 and exposes ten tools (list repos, read files, search code, manage issues and PRs, etc.).
2. **`run_mcp_github.py`** is the entry point that starts the server in one of three transport modes (stdio, SSE, streamable HTTP).
3. **`framework/tools/mcp/github_mcp.py`** creates an ADK `McpToolset` that spawns the server as a stdio subprocess so the agent can call every tool without any additional wiring.
4. **`framework/tools/registry.py`** registers the MCP toolset under the `"github"` domain, and the agent in `agents/github_agent/agent.py` pulls it into its tool list.

### Key dependencies

| Package | Role |
|---------|------|
| `fastmcp>=0.1.0` | High-level MCP server framework (wraps `mcp` SDK) |
| `mcp>=1.0.0` | Core MCP protocol library (client + server) |
| `httpx>=0.27.0` | HTTP client used by the GitHub REST layer |
| `google-adk>=1.0.0` | Agent Development Kit — provides `McpToolset`, `LlmAgent` |
| `python-dotenv>=1.0.0` | Loads `.env` for `GITHUB_TOKEN` and other secrets |

---

## 2. Server Architecture and Components

```
mcp_servers/
  __init__.py              # Package marker
  github/
    __init__.py            # Package marker
    github_client.py       # Thin REST client (httpx) for GitHub API v3
    logger.py              # Structured JSON logging + tool_span context manager
    server.py              # FastMCP instance + @mcp.tool() definitions

run_mcp_github.py          # CLI entry point — picks transport and starts server
framework/tools/mcp/
    github_mcp.py          # ADK McpToolset that spawns the server over stdio
framework/tools/
    registry.py            # Domain-based tool registry (local vs mcp)
    resolver.py            # Flat name->callable resolver for local tools
```

### 2.1 `server.py` -- FastMCP instance and tool definitions

Creates a `FastMCP` instance named `"github"` with a natural-language instruction string. Each tool is a plain Python function decorated with `@mcp.tool()`. The function signature (with type hints) becomes the tool's JSON Schema automatically. Every tool body delegates to `github_client.py` inside a `tool_span` context manager for logging.

```python
mcp = FastMCP(
    "github",
    instructions=(
        "Provides tools to interact with GitHub: list repositories, "
        "read files, search code, create issues, list commits, "
        "and get repository summaries. "
        "All operations require a valid GITHUB_TOKEN."
    ),
)
```

### 2.2 `github_client.py` -- REST layer

A stateless module with two internal helpers (`_get`, `_post`) that wrap `httpx.Client` calls. Every public function (e.g. `list_repositories`, `read_file`) hits a GitHub API v3 endpoint, maps the response to a minimal dict/list, and returns it. The module never touches MCP concepts; it is pure HTTP.

Key internals:

- **`_headers()`** -- reads `GITHUB_TOKEN` from the environment and builds the `Authorization: Bearer` header. Raises `GitHubError` if the token is missing.
- **`_raise_for_status(resp)`** -- translates HTTP 401/403/404/4xx+ into human-readable `GitHubError` exceptions, including rate-limit detection.
- **`_get(path, params)`** and **`_post(path, payload)`** -- create a short-lived `httpx.Client(timeout=15)`, make the request, check status, and return `resp.json()`.

### 2.3 `logger.py` -- structured logging

Writes JSON-formatted log lines to `stderr` (important: MCP stdio transport uses stdout for protocol messages, so logs must go to stderr).

The `tool_span` context manager is the main interface:

```python
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
```

Every tool call produces at least two log lines: `call_start` (with inputs) and either `call_end` (with latency) or `call_error` (with error message and latency).

---

## 3. Available Tools

### 3.1 `list_repositories`

List GitHub repositories for a user.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `username` | `str` | Yes | -- | GitHub username or organisation name |
| `repo_type` | `str` | No | `"public"` | Visibility filter: `public`, `private`, `all`, `forks`, `sources`, `member` |

**Returns:** `list[dict]` -- each dict contains `name`, `full_name`, `description`, `language`, `stars`, `forks`, `private`, `url`.

### 3.2 `read_file`

Read the text content of a file in a GitHub repository.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `owner` | `str` | Yes | -- | Repository owner (user or org) |
| `repo` | `str` | Yes | -- | Repository name |
| `path` | `str` | Yes | -- | File path inside the repo (e.g. `src/main.py`) |
| `ref` | `str` | No | `"HEAD"` | Branch, tag, or commit SHA |

**Returns:** `str` -- full UTF-8 text content of the file. Raises `GitHubError` if the path is a directory.

### 3.3 `search_code`

Search code across GitHub.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | `str` | Yes | -- | Search terms (GitHub code search syntax supported) |
| `owner` | `str` | No | `""` | Scope results to this user/org |
| `repo` | `str` | No | `""` | Scope results to this repository (requires `owner`) |

**Returns:** `list[dict]` -- up to 10 matching files, each with `repository`, `path`, `url`, `score`.

### 3.4 `create_issue`

Create a new GitHub issue.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `owner` | `str` | Yes | -- | Repository owner |
| `repo` | `str` | Yes | -- | Repository name |
| `title` | `str` | Yes | -- | Issue title |
| `body` | `str` | No | `""` | Issue body/description in markdown |

**Returns:** `dict` -- `number`, `title`, `url`, `state`.

### 3.5 `list_commits`

List recent commits for a repository.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `owner` | `str` | Yes | -- | Repository owner |
| `repo` | `str` | Yes | -- | Repository name |
| `branch` | `str` | No | `""` | Branch name (defaults to repo's default branch) |
| `per_page` | `int` | No | `20` | Number of commits to return (max 100) |

**Returns:** `list[dict]` -- each with `sha` (7-char), `message` (first line), `author`, `date`, `url`.

### 3.6 `list_pull_requests`

List pull requests for a repository.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `owner` | `str` | Yes | -- | Repository owner |
| `repo` | `str` | Yes | -- | Repository name |
| `state` | `str` | No | `"open"` | Filter: `open`, `closed`, `all` |
| `per_page` | `int` | No | `10` | Number of PRs to return (max 100) |

**Returns:** `list[dict]` -- each with `number`, `title`, `state`, `author`, `created_at`, `updated_at`, `url`, `draft`, `labels`.

### 3.7 `get_pull_request`

Get detailed information about a specific pull request.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `owner` | `str` | Yes | -- | Repository owner |
| `repo` | `str` | Yes | -- | Repository name |
| `pr_number` | `int` | Yes | -- | Pull request number |

**Returns:** `dict` -- `number`, `title`, `body` (truncated to 2000 chars), `state`, `author`, `created_at`, `merged`, `merged_at`, `head_branch`, `base_branch`, `additions`, `deletions`, `changed_files`, `url`.

### 3.8 `create_pull_request`

Create a new pull request.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `owner` | `str` | Yes | -- | Repository owner |
| `repo` | `str` | Yes | -- | Repository name |
| `title` | `str` | Yes | -- | PR title |
| `head` | `str` | Yes | -- | Source branch (branch with changes) |
| `base` | `str` | Yes | -- | Target branch (e.g. `main`) |
| `body` | `str` | No | `""` | PR description in markdown |

**Returns:** `dict` -- `number`, `title`, `url`, `state`.

### 3.9 `list_branches`

List branches for a repository.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `owner` | `str` | Yes | -- | Repository owner |
| `repo` | `str` | Yes | -- | Repository name |
| `per_page` | `int` | No | `30` | Number of branches to return (max 100) |

**Returns:** `list[dict]` -- each with `name`, `sha` (7-char), `protected`.

### 3.10 `get_repo_summary`

Get a comprehensive summary of a repository including languages, activity, and top contributors.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `owner` | `str` | Yes | -- | Repository owner |
| `repo` | `str` | Yes | -- | Repository name |

**Returns:** `dict` -- `name`, `description`, `language`, `languages` (dict of language->bytes), `stars`, `forks`, `open_issues`, `default_branch`, `created_at`, `updated_at`, `pushed_at`, `private`, `url`, `top_contributors` (list of `{login, contributions}`).

---

## 4. How to Register a New Tool

Follow these four steps to add a new tool to the GitHub MCP server.

### Step 1: Add the domain function in `github_client.py`

Write a function that calls the GitHub API and returns a clean dict or list. Use the existing `_get` / `_post` helpers.

```python
# mcp_servers/github/github_client.py

def list_issues(owner: str, repo: str, state: str = "open", per_page: int = 10) -> list[dict]:
    """Return issues for *owner/repo*."""
    data = _get(
        f"/repos/{owner}/{repo}/issues",
        params={"state": state, "per_page": min(per_page, 100)},
    )
    return [
        {
            "number": i["number"],
            "title": i["title"],
            "state": i["state"],
            "author": i["user"]["login"],
            "labels": [l["name"] for l in i.get("labels", [])],
            "url": i["html_url"],
        }
        for i in data
        if "pull_request" not in i  # GitHub mixes PRs into /issues
    ]
```

### Step 2: Wrap it in `server.py` with `@mcp.tool()`

Import `github_client` as `gh` and `tool_span` from `logger`. Write a thin wrapper whose type-annotated signature becomes the tool's JSON Schema.

```python
# mcp_servers/github/server.py

@mcp.tool()
def list_issues(owner: str, repo: str, state: str = "open", per_page: int = 10) -> list[dict]:
    """List issues for a repository.

    Args:
        owner:    Repository owner (user or org).
        repo:     Repository name.
        state:    Filter by state — open | closed | all. Defaults to 'open'.
        per_page: Number of issues to return (max 100). Defaults to 10.

    Returns:
        List of issues with number, title, state, author, labels, and URL.
    """
    with tool_span("list_issues", {"owner": owner, "repo": repo, "state": state}):
        return gh.list_issues(owner, repo, state, per_page)
```

The docstring is important -- FastMCP uses it as the tool's `description` in the MCP schema, which the LLM reads to decide when and how to call the tool.

### Step 3: The tool is automatically available

Because the `McpToolset` in `framework/tools/mcp/github_mcp.py` spawns the entire MCP server process, every `@mcp.tool()` function is discovered automatically at connection time. No changes to `github_mcp.py`, `registry.py`, or `resolver.py` are needed.

### Step 4: Update the agent instruction (optional but recommended)

Add the new tool to the agent's `instruction` string in `agents/github_agent/agent.py` so the LLM knows when to use it:

```python
"- list_issues: list issues for a repo (state, labels, author)\n"
```

---

## 5. Authentication and Transport Layer

### 5.1 Authentication

All GitHub API calls require a personal access token. The token is read from the `GITHUB_TOKEN` environment variable (typically set in a `.env` file at the project root).

The `_headers()` function in `github_client.py` constructs the auth header:

```python
def _headers() -> dict[str, str]:
    token = os.getenv("GITHUB_TOKEN", "")
    if not token:
        raise GitHubError("GITHUB_TOKEN is not set. Add it to your .env file.")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
```

The token never leaves the MCP server process. The ADK agent communicates with the server over the MCP protocol and never sees the raw token.

### 5.2 HTTP client

All requests use `httpx.Client` with a 15-second timeout. A new client is created per request (no connection pooling), which keeps the code simple and avoids stale-connection issues for a tool-call workload.

### 5.3 Error handling

`_raise_for_status(resp)` provides structured error handling:

| HTTP status | Behaviour |
|-------------|-----------|
| 401 | `GitHubError("Authentication failed — check your GITHUB_TOKEN.")` |
| 403 with `x-ratelimit-remaining: 0` | `GitHubError` with rate-limit reset time |
| 403 (other) | `GitHubError` with first 200 chars of response body |
| 404 | `GitHubError` with the request URL |
| 400+ (other) | `GitHubError` with status code and first 200 chars of body |

### 5.4 Transport modes

`run_mcp_github.py` supports three transports:

| Flag | Transport | Address | Use case |
|------|-----------|---------|----------|
| _(none)_ | `stdio` | stdin/stdout | Default. Used by ADK `McpToolset` via `StdioServerParameters` |
| `--sse` | `sse` | `http://127.0.0.1:8001/sse` | Browser or curl testing; long-lived server-sent events |
| `--http` | `streamable-http` | `http://127.0.0.1:8001/mcp` | Stateless HTTP transport for production deployments |

**stdio** is the primary mode. When an ADK agent starts, `McpToolset` spawns `run_mcp_github.py` as a child process and communicates over its stdin/stdout pipes. Logs are emitted to stderr so they do not interfere with the protocol stream.

---

## 6. Example: Adding a Hypothetical `list_releases` Tool

This section walks through a complete end-to-end example.

### 6.1 `github_client.py` -- add the API call

```python
# mcp_servers/github/github_client.py

def list_releases(owner: str, repo: str, per_page: int = 10) -> list[dict]:
    """Return published releases for *owner/repo*."""
    data = _get(
        f"/repos/{owner}/{repo}/releases",
        params={"per_page": min(per_page, 100)},
    )
    return [
        {
            "tag": r["tag_name"],
            "name": r.get("name") or r["tag_name"],
            "draft": r["draft"],
            "prerelease": r["prerelease"],
            "published_at": r.get("published_at"),
            "url": r["html_url"],
        }
        for r in data
    ]
```

### 6.2 `server.py` -- expose as an MCP tool

```python
# mcp_servers/github/server.py

@mcp.tool()
def list_releases(owner: str, repo: str, per_page: int = 10) -> list[dict]:
    """List releases for a repository.

    Args:
        owner:    Repository owner (user or org).
        repo:     Repository name.
        per_page: Number of releases to return (max 100). Defaults to 10.

    Returns:
        List of releases with tag, name, draft/prerelease flags, date, and URL.
    """
    with tool_span("list_releases", {"owner": owner, "repo": repo}):
        return gh.list_releases(owner, repo, per_page)
```

### 6.3 Agent instruction -- tell the LLM about the tool

In `agents/github_agent/agent.py`, add to the instruction string:

```python
"- list_releases: list published releases for a repo\n"
```

### 6.4 That is it

No changes to `github_mcp.py`, `registry.py`, or `resolver.py`. The `McpToolset` discovers the new tool via the MCP protocol the next time the agent starts.

---

## 7. Testing the MCP Server Locally

### 7.1 Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GITHUB_TOKEN (and GOOGLE_API_KEY for the ADK agent)
```

### 7.2 Run in stdio mode (default)

```bash
python run_mcp_github.py
```

The server reads JSON-RPC messages from stdin and writes responses to stdout. This is hard to use manually but is exactly how the ADK agent connects. You can pipe a valid MCP `initialize` request to verify the server starts:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"capabilities":{}}}' | python run_mcp_github.py
```

### 7.3 Run in SSE mode

```bash
python run_mcp_github.py --sse
```

Starts a long-lived HTTP server on `http://127.0.0.1:8001/sse`. Useful for testing with browser-based MCP clients or curl:

```bash
# In another terminal — list available tools
curl -s http://127.0.0.1:8001/sse
```

### 7.4 Run in streamable HTTP mode

```bash
python run_mcp_github.py --http
```

Starts a server on `http://127.0.0.1:8001/mcp`. Each tool call is a single HTTP POST/response cycle with no persistent connection.

### 7.5 Test with the ADK Web UI

The fastest way to test end-to-end is through the ADK development server, which provides a chat-based web UI:

```bash
adk web agents/
```

This starts the ADK web UI. Select `github_agent` from the agent list. The agent will automatically spawn the MCP server as a subprocess (stdio transport) and you can test tools conversationally:

- "List repositories for octocat"
- "Show me the last 5 commits on octocat/Hello-World"
- "Get a summary of facebook/react"

### 7.6 Checking logs

When running in stdio mode (including via ADK), tool call logs are written to **stderr** in JSON format. Example output:

```json
{"level": "info", "tool": "list_repositories", "event": "call_start", "inputs": {"username": "octocat", "repo_type": "public"}}
{"level": "info", "tool": "list_repositories", "event": "call_end", "latency_ms": 342.17}
```

If a tool call fails:

```json
{"level": "error", "tool": "read_file", "event": "call_error", "error": "Resource not found (404): https://api.github.com/repos/owner/repo/contents/missing.txt", "latency_ms": 198.03}
```
