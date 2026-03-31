from fastapi import APIRouter, Header
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

from app.core.assistant_orchestrator import handle_assistant_request

router = APIRouter()

# =========================
# REQUEST SCHEMAS (LOCKED)
# =========================

class AssistantInput(BaseModel):
    message: Optional[str] = None
    summarized_payload: Optional[dict] = None


class AssistantContext(BaseModel):
    platform: str = "web"
    device: str = "desktop"
    session_id: Optional[str] = None
    voice_input: bool = False

    class Config:
        extra = "allow"



class AssistantRequest(BaseModel):
    version: Literal["3.0.0"]
    input: AssistantInput
    context: AssistantContext


# =========================
# RESPONSE SCHEMAS (LOCKED)
# =========================

class AssistantResult(BaseModel):
    type: Literal["passive", "intelligence", "workflow"]
    response: str
    task: Optional[dict] = None


class AssistantSuccessResponse(BaseModel):
    version: Literal["3.0.0"]
    status: Literal["success"]
    result: AssistantResult
    processed_at: str


class AssistantErrorResponse(BaseModel):
    version: Literal["3.0.0"]
    status: Literal["error"]
    error: dict
    processed_at: str


# =========================
# SINGLE PUBLIC ENDPOINT
# =========================

@router.post(
    "/api/assistant",
    response_model=AssistantSuccessResponse | AssistantErrorResponse
)
async def assistant_endpoint(
    request: AssistantRequest,
    x_api_key: str = Header(...)
):
    """
    SINGLE production entrypoint for AI Assistant.
    Backend is LOCKED and frontend-safe.
    """
    return await handle_assistant_request(request)
