from framework.callbacks.base_callback import BaseCallback
from framework.approval.approval_handler import approval_handler
from core.schemas import ApprovalRequest

APPROVAL_SIGNALS = [
    "shall i proceed", "do you want me to", "should i",
    "confirm", "overwrite", "would you like", "may i"
]


class ApprovalCallback(BaseCallback):
    """Detects when agent asks a question and routes it through the approval handler."""

    async def on_agent_text(self, text: str, context: dict):
        if self._is_approval_ask(text):
            request = ApprovalRequest(
                agent_name=context.get("agent_name", "unknown"),
                triggered_by="agent",
                action="continue_execution",
                message=text,
                options=["yes", "modify", "cancel"],
                risk_level="medium",
                context=context,
                default="cancel",
                session_id=context.get("session_id", "")
            )
            response = await approval_handler.request_approval(request)
            context["last_approval"] = response.decision.value

    def _is_approval_ask(self, text: str) -> bool:
        lower = text.lower()
        return any(signal in lower for signal in APPROVAL_SIGNALS)
