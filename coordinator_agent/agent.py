"""
ADK web entry point — discovered by `adk web .`

All agents and workflows are defined in agent_configs/ and workflow_configs/.
Factory.bootstrap() discovers them automatically and wires sub-agents into
the coordinator.
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path when loaded by `adk web`
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
load_dotenv()

from framework.factory import Factory

root_agent = Factory().bootstrap()
