"""Health Check Endpoint"""

import time
from fastapi import APIRouter, status
from backend.app.config import settings
from backend.app.database.cache import weather_cache
from backend.app.schemas.common import APIResponse

router = APIRouter(tags=["Health"])

START_TIME = time.time()


@router.get(
    "/health",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="System Health & Diagnostic Status",
)
async def get_health():
    """Verify backend availability, provider configuration, and active cache size."""
    uptime_seconds = int(time.time() - START_TIME)
    return APIResponse(
        success=True,
        message="WeatherGPT backend service is operating normally",
        data={
            "status": "healthy",
            "version": settings.VERSION,
            "environment": settings.APP_ENV,
            "provider": settings.PRIMARY_WEATHER_PROVIDER,
            "ai_provider": settings.AI_PROVIDER,
            "supported_languages": settings.SUPPORTED_LANGUAGES,
            "cached_entries": weather_cache.size(),
            "uptime_seconds": uptime_seconds,
        },
    )
