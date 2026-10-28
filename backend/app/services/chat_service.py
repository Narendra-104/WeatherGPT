"""Conversational Weather Assistant Service"""

from typing import Any, Dict, Optional
from backend.app.ai.base import AIAssistantService
from backend.app.ai.mock_assistant import SafeAIAssistant
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.weather_service import weather_service
from backend.app.utils.logger import logger


class ChatService:
    def __init__(self, ai_assistant: Optional[AIAssistantService] = None):
        self.assistant = ai_assistant or SafeAIAssistant()

    async def chat(self, request: ChatRequest) -> ChatResponse:
        weather_context: Optional[Dict[str, Any]] = None

        # Fetch live meteorological context if coordinates are available
        if request.latitude is not None and request.longitude is not None:
            try:
                current = await weather_service.get_current_weather(
                    request.latitude, request.longitude, language=request.language
                )
                weather_context = {
                    "latitude": current.latitude,
                    "longitude": current.longitude,
                    "location_name": request.location_name or current.location_name,
                    "temperature": current.temperature,
                    "apparent_temperature": current.apparent_temperature,
                    "weather_description": current.weather_description,
                    "precipitation": current.precipitation or 0.0,
                    "relative_humidity": current.relative_humidity or 50.0,
                    "wind_speed": current.wind_speed or 0.0,
                }
            except Exception as e:
                logger.warning(f"Could not fetch weather context for chat: {str(e)}")

        return await self.assistant.generate_response(request, weather_context=weather_context)


chat_service = ChatService()
