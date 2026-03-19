"""
ADK web entry point — discovered by `adk web .`

Imports workflows to trigger self-registration, then builds the coordinator
and exposes it as root_agent (required name for adk web discovery).
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path when loaded by `adk web`
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
load_dotenv()

import workflows.youtube_workflow           # noqa: F401 — triggers registry registration
import workflows.control_testing_workflow   # noqa: F401 — triggers registry registration

from agents.coordinator_agent import build_coordinator_agent

root_agent = build_coordinator_agent()
