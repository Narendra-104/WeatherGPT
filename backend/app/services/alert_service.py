"""Severe Weather Alert Service"""

from typing import Optional
from backend.app.config import settings
from backend.app.database.cache import weather_cache
from backend.app.providers.base import WeatherProvider
from backend.app.providers.factory import get_weather_provider
from backend.app.schemas.alert import AlertListResponse
from backend.app.utils.logger import logger


class AlertService:
    def __init__(self, provider: Optional[WeatherProvider] = None):
        self._provider = provider
        self.ttl = 600  # 10 minutes cache for alerts

    @property
    def provider(self) -> WeatherProvider:
        if self._provider is not None:
            return self._provider
        return get_weather_provider()

    @provider.setter
    def provider(self, val: Optional[WeatherProvider]):
        self._provider = val

    async def get_alerts(
        self, latitude: float, longitude: float, location: Optional[str] = None, language: str = "en"
    ) -> AlertListResponse:
        active_provider = self.provider
        cache_key = f"{active_provider.name}:alerts:{latitude:.2f}:{longitude:.2f}:{language}"
        cached = weather_cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for [{active_provider.name}] weather alerts at {latitude},{longitude}")
            return cached

        logger.info(f"Checking alerts for {latitude},{longitude} via [{active_provider.name}]")
        alerts = await active_provider.get_alerts(latitude, longitude, language=language)
        response = AlertListResponse(
            location=location or f"Coords ({latitude:.2f}, {longitude:.2f})",
            latitude=latitude,
            longitude=longitude,
            count=len(alerts),
            alerts=alerts,
        )
        weather_cache.set(cache_key, response, ttl_seconds=self.ttl)
        return response


alert_service = AlertService()
