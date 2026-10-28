"""Weather Forecast Endpoint"""

from fastapi import APIRouter, Query, status
from backend.app.schemas.common import APIResponse
from backend.app.schemas.forecast import ForecastData
from backend.app.services.weather_service import weather_service

router = APIRouter(tags=["Weather"])


@router.get(
    "/weather/forecast",
    response_model=APIResponse[ForecastData],
    status_code=status.HTTP_200_OK,
    summary="Get Hourly & Multi-Day Weather Forecast",
)
async def get_forecast(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Latitude between -90 and 90"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Longitude between -180 and 180"),
    days: int = Query(7, ge=1, le=14, description="Forecast range in days (1 to 14)"),
    language: str = Query("en", pattern="^(en|hi|mr)$", description="Target language ('en', 'hi', 'mr')"),
):
    """Retrieve verified hourly breakdown (24-48h) and multi-day extended forecast."""
    data = await weather_service.get_forecast(latitude, longitude, days=days, language=language)
    return APIResponse(
        success=True,
        message=f"{days}-day forecast retrieved successfully",
        data=data,
    )
