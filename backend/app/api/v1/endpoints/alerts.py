"""Severe Weather Alerts Endpoint"""

from typing import Optional
from fastapi import APIRouter, Query, status
from backend.app.schemas.common import APIResponse
from backend.app.schemas.alert import AlertListResponse
from backend.app.services.alert_service import alert_service

router = APIRouter(tags=["Alerts"])


@router.get(
    "/alerts",
    response_model=APIResponse[AlertListResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Active Severe Weather Alerts & Advisories",
)
async def get_alerts(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Latitude between -90 and 90"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Longitude between -180 and 180"),
    location: Optional[str] = Query(None, description="Optional human-readable location name"),
    language: str = Query("en", pattern="^(en|hi|mr)$", description="Target language ('en', 'hi', 'mr')"),
):
    """Retrieve verified severe meteorological alerts, hazard levels, and actionable safety instructions."""
    data = await alert_service.get_alerts(latitude, longitude, location=location, language=language)
    return APIResponse(
        success=True,
        message=f"Retrieved {data.count} active alerts",
        data=data,
    )
