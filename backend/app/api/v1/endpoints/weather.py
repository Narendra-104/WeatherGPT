"""Current Weather Observation Endpoint"""

from fastapi import APIRouter, Query, status
from backend.app.schemas.common import APIResponse
from backend.app.schemas.weather import CurrentWeatherData
from backend.app.services.weather_service import weather_service

router = APIRouter(tags=["Weather"])


@router.get(
    "/weather/current",
    response_model=APIResponse[CurrentWeatherData],
    status_code=status.HTTP_200_OK,
    summary="Get Real-Time Weather Observation",
)
async def get_current_weather(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Latitude between -90 and 90"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Longitude between -180 and 180"),
    language: str = Query("en", pattern="^(en|hi|mr)$", description="Target language ('en', 'hi', 'mr')"),
):
    """Retrieve verified current meteorological observations for the specified coordinates."""
    data = await weather_service.get_current_weather(latitude, longitude, language=language)
    return APIResponse(
        success=True,
        message="Current weather retrieved successfully",
        data=data,
    )
