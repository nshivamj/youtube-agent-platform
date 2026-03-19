from framework.callbacks.base_callback import BaseCallback, CallbackEvent
from framework.exceptions import ValidationError as FrameworkValidationError
from framework.validation.registry import validator_registry


class ValidationCallback(BaseCallback):
    """On after_agent, runs all registered validators. Raises ValidationError if score < 0.5."""

    async def after_agent(self, event: CallbackEvent) -> None:
        output = event.payload.get("output", {})
        context = {
            "agent_name": event.agent_name,
            "run_id": event.run_id,
            "session": event.session,
        }

        results = await validator_registry.run_all(output, context)

        errors: list[str] = []
        for result in results:
            if result.score < 0.5:
                errors.extend(result.errors)

        if errors:
            raise FrameworkValidationError(
                agent_name=event.agent_name,
                errors=errors,
                reason="One or more validators returned score below threshold",
            )
