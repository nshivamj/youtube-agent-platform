"""Agent Platform — entrypoint.

Agents and workflows are defined in agent_configs/ and workflow_configs/.
Factory.bootstrap() discovers all enabled workflows and wires them into
the coordinator automatically — no imports needed when adding new configs.

Usage:
    python main.py                          # starts ADK web UI at http://localhost:8080
    python main.py --port 9090              # custom port
    adk web .                               # ADK CLI — discovers coordinator_agent/ package
"""

import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

from framework.factory import Factory

coordinator = Factory().bootstrap()

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
