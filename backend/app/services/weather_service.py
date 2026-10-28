"""Weather Service Layer

Orchestrates provider calls, enforces caching with TTL, and formats responses.
"""

from typing import Optional
from backend.app.config import settings
from backend.app.database.cache import weather_cache
from backend.app.providers.base import WeatherProvider
from backend.app.providers.factory import get_weather_provider
from backend.app.schemas.weather import CurrentWeatherData
from backend.app.schemas.forecast import ForecastData
from backend.app.utils.logger import logger


class WeatherService:
    def __init__(self, provider: Optional[WeatherProvider] = None):
        self.provider = provider or get_weather_provider()
        self.ttl = settings.WEATHER_CACHE_TTL_SECONDS

    async def get_current_weather(
        self, latitude: float, longitude: float, language: str = "en"
    ) -> CurrentWeatherData:
        cache_key = f"current:{latitude:.3f}:{longitude:.3f}:{language}"
        cached = weather_cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for current weather at {latitude},{longitude}")
            return cached

        logger.info(f"Fetching live current weather from {self.provider.name} for {latitude},{longitude}")
        data = await self.provider.get_current_weather(latitude, longitude, language=language)
        weather_cache.set(cache_key, data, ttl_seconds=self.ttl)
        return data

    async def get_forecast(
        self, latitude: float, longitude: float, days: int = 7, language: str = "en"
    ) -> ForecastData:
        cache_key = f"forecast:{latitude:.3f}:{longitude:.3f}:{days}:{language}"
        cached = weather_cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for forecast at {latitude},{longitude}")
            return cached

        logger.info(f"Fetching live forecast from {self.provider.name} for {latitude},{longitude}")
        data = await self.provider.get_forecast(latitude, longitude, days=days, language=language)
        weather_cache.set(cache_key, data, ttl_seconds=self.ttl)
        return data


weather_service = WeatherService()
