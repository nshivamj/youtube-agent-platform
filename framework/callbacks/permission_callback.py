from framework.callbacks.base_callback import BaseCallback, CallbackEvent
from framework.exceptions import PermissionDeniedError
from framework.permissions.evaluator import evaluate_permission, PermissionContext
from framework.permissions.registry import policy_registry


class PermissionCallback(BaseCallback):
    """On before_agent, evaluates permission policy. Raises PermissionDeniedError if denied."""

    async def before_agent(self, event: CallbackEvent) -> None:
        policy = policy_registry.get_policy(event.agent_name)
        tool_name = event.payload.get("tool_name", "")
        context = PermissionContext(
            agent_name=event.agent_name,
            tool_name=tool_name,
            user_id=event.payload.get("user_id", ""),
            session=event.session,
        )
        result = evaluate_permission(context, policy)
        if not result.allowed:
            raise PermissionDeniedError(
                agent_name=event.agent_name,
                tool_name=tool_name,
                reason=result.reason,
            )
