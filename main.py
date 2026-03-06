"""YouTube Agent Platform — entrypoint.

Usage:
    python main.py                          # starts ADK web UI at http://localhost:8080
    python main.py --port 9090              # custom port
"""

import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

from workflows.youtube_workflow import youtube_workflow          # noqa: E402
from agents.coordinator_agent import build_coordinator_agent    # noqa: E402

coordinator = build_coordinator_agent(youtube_workflow)

if __name__ == "__main__":
    import argparse
    from google.adk.web import start_web

    parser = argparse.ArgumentParser(description="YouTube Agent Platform")
    parser.add_argument("--port", type=int, default=8080, help="Port for ADK web UI")
    args = parser.parse_args()

    print(f"Starting YouTube Agent Platform...")
    print(f"Open http://localhost:{args.port} in your browser")
    start_web(coordinator, port=args.port)
