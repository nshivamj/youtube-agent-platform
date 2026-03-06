import asyncio
import uuid
import logging
from core.schemas import ApprovalRequest, ApprovalResponse, ApprovalDecision

logger = logging.getLogger("platform.approval")


class ApprovalHandler:
    """Central approval engine. Three trigger points feed into this one handler.
    Every request + decision is saved to session for full audit trail.
    Uses asyncio.Future to pause execution while waiting for human."""

    def __init__(self, session_manager=None, stream_fn=None):
        self.session = session_manager
        self.stream = stream_fn
        self._pending: dict[str, asyncio.Future] = {}

    async def request_approval(self, request: ApprovalRequest) -> ApprovalResponse:
        request.request_id = str(uuid.uuid4())
        logger.info(f"Approval requested: {request.action} (risk={request.risk_level})")

        # Save to session
        if self.session:
            self.session.save(f"approval:{request.request_id}", request.model_dump())
            self.session.save("awaiting_approval", True)

        # Stream widget to UI
        if self.stream:
            await self.stream({
                "type": "approval_required",
                "request_id": request.request_id,
                "message": request.message,
                "options": request.options,
                "risk_level": request.risk_level,
                "context": request.context,
            })

        # Create future and wait for human response
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[request.request_id] = future

        try:
            response = await asyncio.wait_for(future, timeout=300.0)
            if self.session:
                self.session.save(
                    f"approval_decision:{request.request_id}",
                    response.model_dump()
                )
            return response
        except asyncio.TimeoutError:
            logger.warning(f"Approval timed out: {request.request_id}")
            return ApprovalResponse(
                request_id=request.request_id,
                decision=ApprovalDecision.REJECTED,
                reason=f"Timed out — defaulted to: {request.default}"
            )
        finally:
            self._pending.pop(request.request_id, None)
            if self.session:
                self.session.save("awaiting_approval", False)

    async def submit_response(self, response: ApprovalResponse):
        """Called by UI/API when user clicks approve/reject/modify."""
        future = self._pending.get(response.request_id)
        if future and not future.done():
            future.set_result(response)
        else:
            logger.warning(f"No pending future for: {response.request_id}")


approval_handler = ApprovalHandler()
