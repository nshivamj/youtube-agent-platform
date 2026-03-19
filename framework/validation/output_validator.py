"""Output validation with retry support."""

import logging
from pydantic import BaseModel, ValidationError

logger = logging.getLogger("platform.validation")


class PartialResult:
    def __init__(self, success: bool, data=None, errors: list[str] | None = None):
        self.success = success
        self.data = data
        self.errors = errors or []


def validate_output(data: dict, schema: type[BaseModel]) -> PartialResult:
    """Validate output data against a Pydantic schema."""
    try:
        validated = schema(**data)
        return PartialResult(success=True, data=validated.model_dump())
    except ValidationError as e:
        errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
        logger.warning("Output validation failed: %s", errors)
        return PartialResult(success=False, errors=errors)
