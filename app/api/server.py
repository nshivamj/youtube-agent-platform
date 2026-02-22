"""API server — future FastAPI HTTP entrypoint.

To activate:
    pip install fastapi uvicorn
    uvicorn app.api.server:app --reload

All routes delegate to the orchestrator, keeping HTTP concerns isolated here.
"""

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from app.orchestrator.orchestrator import handle_request
#
# app = FastAPI(title="ADK Agent Platform")
#
#
# class RunRequest(BaseModel):
#     agent: str
#     prompt: str
#
#
# @app.post("/run")
# async def run(req: RunRequest) -> dict:
#     result = handle_request(req.agent, req.prompt)
#     if result["status"] == "error":
#         raise HTTPException(status_code=400, detail=result["message"])
#     return result
