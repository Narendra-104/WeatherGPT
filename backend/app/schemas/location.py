from typing import List, Optional
from pydantic import BaseModel, Field


class LocationResult(BaseModel):
    """Geocoded location entity."""
    id: Optional[int] = None
    name: str = Field(..., description="Place / City / Town name")
    latitude: float
    longitude: float
    elevation: Optional[float] = None
    country: Optional[str] = None
    admin1: Optional[str] = Field(None, description="State / Province / Region (e.g., Maharashtra)")
    country_code: Optional[str] = None


class LocationSearchResponse(BaseModel):
    """List of resolved locations."""
    query: str
    count: int
    results: List[LocationResult]
