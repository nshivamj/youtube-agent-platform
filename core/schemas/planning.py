from pydantic import BaseModel


class Step(BaseModel):
    step_number: int
    agent_name: str
    task: str
    expected_output: str
    depends_on: list[int] = []


class ExecutionPlan(BaseModel):
    goal: str
    steps: list[Step]
    estimated_duration: str
