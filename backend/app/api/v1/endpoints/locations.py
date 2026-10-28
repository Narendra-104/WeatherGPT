"""Location Search & Geocoding Endpoint"""

from fastapi import APIRouter, Query, status
from backend.app.schemas.common import APIResponse
from backend.app.schemas.location import LocationSearchResponse
from backend.app.services.location_service import location_service

router = APIRouter(tags=["Locations"])


@router.get(
    "/locations/search",
    response_model=APIResponse[LocationSearchResponse],
    status_code=status.HTTP_200_OK,
    summary="Search Locations & Geocode Coordinates",
)
async def search_locations(
    q: str = Query(..., min_length=2, max_length=100, description="City, district, town, or village name"),
    count: int = Query(10, ge=1, le=20, description="Maximum number of candidates to return"),
    language: str = Query("en", pattern="^(en|hi|mr)$", description="Target language ('en', 'hi', 'mr')"),
):
    """Geocode a place name into geographical coordinates with multilingual display support."""
    data = await location_service.search_locations(q, count=count, language=language)
    return APIResponse(
        success=True,
        message=f"Found {data.count} location matches",
        data=data,
    )
