"""API v1 Master Router"""

from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    health,
    weather,
    forecast,
    locations,
    chat,
    alerts,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(weather.router)
api_router.include_router(forecast.router)
api_router.include_router(locations.router)
api_router.include_router(chat.router)
api_router.include_router(alerts.router)
