"""ADK Agent Platform — entrypoint.

Usage:
    python main.py "List repos for google"
    python main.py --agent basic_agent "Hello!"
    python main.py --agent github_agent "Who owns the most starred Python repo?"
"""

import argparse
import sys

from dotenv import load_dotenv

load_dotenv()

from app.config import config  # noqa: E402

try:
    config.validate()
except EnvironmentError as exc:
    print(f"[startup] Configuration error:\n  {exc}", file=sys.stderr)
    sys.exit(1)

from app.orchestrator.orchestrator import handle_request  # noqa: E402
from app.services.prompt_service import format_response   # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="ADK Agent Platform CLI")
    parser.add_argument("prompt", help="Prompt to send to the agent")
    parser.add_argument(
        "--agent",
        default="github_agent",
        help="Agent name (must match agents-config/<name>.yaml). Default: github_agent",
    )
    args = parser.parse_args()

    print(f"\nAgent  : {args.agent}")
    print(f"Prompt : {args.prompt}")
    print("-" * 60)

    result = handle_request(args.agent, args.prompt)
    output = format_response(result)

    if result["status"] == "success":
        print(f"\nResponse:\n{output}\n")
    else:
        print(output, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
