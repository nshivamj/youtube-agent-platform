from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class ExecutionContext:
    run_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    user_id: str = ""
    agent_id: str = ""
    tool_mode: str = "local"
    step_index: int = 0
    environment: str = "development"
