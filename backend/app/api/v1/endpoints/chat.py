"""Conversational Weather Assistant Endpoint"""

from fastapi import APIRouter, status
from backend.app.schemas.common import APIResponse
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.chat_service import chat_service

router = APIRouter(tags=["AI Assistant"])


@router.post(
    "/chat",
    response_model=APIResponse[ChatResponse],
    status_code=status.HTTP_200_OK,
    summary="Ask WeatherGPT Conversational Assistant",
)
async def chat(request: ChatRequest):
    """Conversational endpoint grounded strictly in real weather observations.
    Supports English, Hindi, and Marathi questions and answers.
    """
    response = await chat_service.chat(request)
    return APIResponse(
        success=True,
        message="Assistant response generated",
        data=response,
    )
