from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user', 'assistant', or 'system'")
    content: str


class ChatRequest(BaseModel):
    """User conversational inquiry."""
    message: str = Field(..., min_length=1, max_length=1000, description="User's query")
    language: str = Field(default="en", description="Target response language ('en', 'hi', 'mr')")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    location_name: Optional[str] = None
    history: Optional[List[ChatMessage]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """Grounded assistant response."""
    reply: str
    language: str
    model: str = "WeatherGPT-SafeService"
    grounded_facts: Optional[Dict[str, Any]] = Field(None, description="Meteorological facts used to ground answer")
    suggestions: List[str] = Field(default_factory=list, description="Follow-up prompt suggestions")
