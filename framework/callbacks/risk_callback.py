from framework.callbacks.base_callback import BaseCallback
from framework.approval.approval_handler import approval_handler
from core.schemas import ApprovalRequest

HIGH_RISK_TOOLS = ["delete", "overwrite", "send", "publish", "reset"]


class RiskCallback(BaseCallback):
    """Runtime-triggered approval. Blocks high-risk tool calls before execution."""

    async def on_tool_call(self, tool_name: str, input: dict, context: dict):
        if self._is_high_risk(tool_name):
            request = ApprovalRequest(
                agent_name=context.get("agent_name", "unknown"),
                triggered_by="runtime",
                action=f"execute_{tool_name}",
                message=f"High-risk operation detected: {tool_name}. Proceed?",
                options=["allow", "deny"],
                risk_level="high",
                context={"tool": tool_name, "input": input},
                default="deny",
                session_id=context.get("session_id", "")
            )
            response = await approval_handler.request_approval(request)
            if response.decision.value != "approved":
                raise PermissionError(f"{tool_name} blocked by user")

    def _is_high_risk(self, tool_name: str) -> bool:
        return any(r in tool_name.lower() for r in HIGH_RISK_TOOLS)
