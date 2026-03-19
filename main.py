"""Agent Platform — entrypoint.

Add new workflows by creating a workflows/<name>.py that calls workflow_registry.register().
No changes needed here — just add a new import below.

Usage:
    python main.py                          # starts ADK web UI at http://localhost:8080
    python main.py --port 9090              # custom port
"""

import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

# Import workflows to trigger self-registration into workflow_registry.
# Add new workflow imports here as you create them.
import workflows.youtube_workflow           # noqa: E402, F401
import workflows.control_testing_workflow   # noqa: E402, F401

from agents.coordinator_agent import build_coordinator_agent    # noqa: E402

coordinator = build_coordinator_agent()

# Exposed as root_agent so `adk web` CLI can discover it automatically.
root_agent = coordinator

if __name__ == "__main__":
    import argparse
    from google.adk.web import start_web

    parser = argparse.ArgumentParser(description="Agent Platform")
    parser.add_argument("--port", type=int, default=8080, help="Port for ADK web UI")
    args = parser.parse_args()

    print("Starting Agent Platform...")
    print(f"Open http://localhost:{args.port} in your browser")
    start_web(coordinator, port=args.port)
