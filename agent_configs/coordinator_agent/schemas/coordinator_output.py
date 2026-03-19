from pydantic import BaseModel


class CoordinatorDecision(BaseModel):
    route_to: str
    reason: str
