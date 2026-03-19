"""Input validation using Pydantic schemas."""

import logging
from pydantic import BaseModel, ValidationError

logger = logging.getLogger("platform.validation")


class ValidationResult:
    def __init__(self, valid: bool, errors: list[str] | None = None, data: dict | None = None):
        self.valid = valid
        self.errors = errors or []
        self.data = data or {}


def validate_input(data: dict, schema: type[BaseModel]) -> ValidationResult:
    """Validate input data against a Pydantic schema."""
    try:
        validated = schema(**data)
        return ValidationResult(valid=True, data=validated.model_dump())
    except ValidationError as e:
        errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
        logger.warning("Input validation failed: %s", errors)
        return ValidationResult(valid=False, errors=errors)
