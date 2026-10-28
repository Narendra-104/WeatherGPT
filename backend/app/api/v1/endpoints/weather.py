"""Current Weather Observation Endpoint

Supports both coordinate-based and city-name-based queries.
Precedence: If both coordinates and city are supplied, coordinates take precedence.
"""

from typing import Optional
from fastapi import APIRouter, Query, status
from backend.app.schemas.common import APIResponse
from backend.app.schemas.weather import CurrentWeatherData
from backend.app.services.weather_service import weather_service
from backend.app.services.location_service import location_service
from backend.app.utils.exceptions import InvalidParameterError, LocationNotFoundError

router = APIRouter(tags=["Weather"])


@router.get(
    "/weather/current",
    response_model=APIResponse[CurrentWeatherData],
    status_code=status.HTTP_200_OK,
    summary="Get Real-Time Weather Observation",
)
async def get_current_weather(
    city: Optional[str] = Query(None, description="City name (e.g., Pune, Mumbai, Delhi)"),
    latitude: Optional[float] = Query(None, description="Latitude between -90 and 90"),
    longitude: Optional[float] = Query(None, description="Longitude between -180 and 180"),
    language: str = Query("en", pattern="^(en|hi|mr)$", description="Target language ('en', 'hi', 'mr')"),
):
    """Retrieve verified current meteorological observations.
    
    Query modes:
    1. Coordinate query: `?latitude=18.5204&longitude=73.8567`
    2. City query: `?city=Pune`
    
    Precedence Rule:
    When both coordinates and city are supplied, numerical coordinates take precedence.
    """
    resolved_lat: Optional[float] = None
    resolved_lon: Optional[float] = None
    location_label: Optional[str] = None

    # Check for partial coordinates
    has_lat = latitude is not None
    has_lon = longitude is not None

    if has_lat != has_lon:
        raise InvalidParameterError(
            "Both latitude and longitude must be supplied together for coordinate-based weather requests."
        )

    if has_lat and has_lon:
        # Validate ranges
        if not (-90.0 <= latitude <= 90.0):
            raise InvalidParameterError(f"Latitude must be between -90 and 90 (received: {latitude}).")
        if not (-180.0 <= longitude <= 180.0):
            raise InvalidParameterError(f"Longitude must be between -180 and 180 (received: {longitude}).")

        resolved_lat = latitude
        resolved_lon = longitude
        location_label = city.strip() if city and city.strip() else None

    elif city and city.strip():
        clean_city = city.strip()
        if len(clean_city) < 2:
            raise InvalidParameterError("City name must be at least 2 characters long.")

        geocode_res = await location_service.search_locations(clean_city, count=1, language=language)
        if not geocode_res.results:
            raise LocationNotFoundError(f"Location '{clean_city}' could not be resolved.")

        top_match = geocode_res.results[0]
        resolved_lat = top_match.latitude
        resolved_lon = top_match.longitude
        location_label = top_match.name

    else:
        raise InvalidParameterError(
            "Missing location parameter. Either provide 'city' or both 'latitude' and 'longitude'."
        )

    data = await weather_service.get_current_weather(resolved_lat, resolved_lon, language=language)
    if location_label and (not data.location_name or data.location_name == "Unknown"):
        data.location_name = location_label

    return APIResponse(
        success=True,
        message="Current weather retrieved successfully",
        data=data,
    )
