from typing import List, Optional
from pydantic import BaseModel, Field


class WeatherAlert(BaseModel):
    """Standardized severe weather alert notification."""
    id: str
    title: str
    severity: str = Field(..., description="Severity level: info, watch, warning, emergency")
    urgency: Optional[str] = Field(None, description="Immediate, Expected, Future, Past")
    description: str
    instruction: Optional[str] = Field(None, description="Recommended safety actions")
    areas: List[str] = Field(default_factory=list)
    effective: str
    expires: Optional[str] = None
    source: str = Field(default="Official Meteorological Agency")


class AlertListResponse(BaseModel):
    """List of active severe weather alerts."""
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    count: int
    alerts: List[WeatherAlert]
