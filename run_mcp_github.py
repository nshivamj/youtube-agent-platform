"""Entry point — run the GitHub MCP server over stdio.

Usage:
    python run_mcp_github.py              # stdio transport (used by ADK agents)
    python run_mcp_github.py --sse        # SSE transport for browser / curl testing
    python run_mcp_github.py --http       # Streamable HTTP transport

The server reads GITHUB_TOKEN from environment (loaded via .env).
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path when run directly
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

load_dotenv()

from app.config import config  # noqa: F401  (imported to trigger .env load + validation)
from mcp_servers.github.server import mcp


def main() -> None:
    parser = argparse.ArgumentParser(description="GitHub MCP server")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--sse", action="store_true", help="Run SSE transport on :8001")
    group.add_argument("--http", action="store_true", help="Run streamable-HTTP transport on :8001")
    args = parser.parse_args()

    if args.sse:
        print("[github-mcp] Starting SSE server on http://127.0.0.1:8001/sse", file=sys.stderr)
        mcp.settings.port = 8001
        mcp.run(transport="sse")
    elif args.http:
        print("[github-mcp] Starting HTTP server on http://127.0.0.1:8001/mcp", file=sys.stderr)
        mcp.settings.port = 8001
        mcp.run(transport="streamable-http")
    else:
        # stdio — default, used by ADK McpToolset
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
