from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from backend.app.schemas.chat import ChatRequest, ChatResponse


class AIAssistantService(ABC):
    """Abstract interface for grounded multilingual conversational assistant."""

    @abstractmethod
    async def generate_response(
        self, request: ChatRequest, weather_context: Optional[Dict[str, Any]] = None
    ) -> ChatResponse:
        """Synthesize assistant response grounded strictly in retrieved weather facts."""
        pass
