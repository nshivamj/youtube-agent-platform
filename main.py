"""ADK Agent Platform — entrypoint.

Usage:
    python main.py "List repos for google"
    python main.py --agent basic_agent "Hello!"
    python main.py --agent github_agent "Who owns the most starred Python repo?"
    python main.py --workflow fetch_and_summarize "machine learning"
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

from app.orchestrator.orchestrator import handle_request, handle_workflow  # noqa: E402
from app.services.prompt_service import format_response                    # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="ADK Agent Platform CLI")
    parser.add_argument("prompt", help="Prompt to send to the agent or workflow")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--agent",
        default=None,
        help="Agent name (must match agents-config/<name>.yaml). Default: github_agent",
    )
    mode.add_argument(
        "--workflow",
        default=None,
        help="Workflow name (must match workflows-config/<name>.yaml)",
    )

    args = parser.parse_args()

    if args.workflow:
        print(f"\nWorkflow : {args.workflow}")
        print(f"Prompt   : {args.prompt}")
        print("-" * 60)

        result = handle_workflow(args.workflow, args.prompt)

    else:
        agent_name = args.agent or "github_agent"
        print(f"\nAgent  : {agent_name}")
        print(f"Prompt : {args.prompt}")
        print("-" * 60)

        result = handle_request(agent_name, args.prompt)

    output = format_response(result)

    if result["status"] == "success":
        print(f"\nResponse:\n{output}\n")
    else:
        print(output, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
