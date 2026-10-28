"""Location Search & Geocoding Service"""

from typing import List, Optional
from backend.app.config import settings
from backend.app.database.cache import weather_cache
from backend.app.providers.base import WeatherProvider
from backend.app.providers.factory import get_weather_provider
from backend.app.schemas.location import LocationResult, LocationSearchResponse
from backend.app.utils.logger import logger


class LocationService:
    def __init__(self, provider: Optional[WeatherProvider] = None):
        self._provider = provider
        self.ttl = 86400  # 24-hour cache for geographical geocodes

    @property
    def provider(self) -> WeatherProvider:
        if self._provider is not None:
            return self._provider
        return get_weather_provider()

    @provider.setter
    def provider(self, val: Optional[WeatherProvider]):
        self._provider = val

    async def search_locations(
        self, query: str, count: int = 10, language: str = "en"
    ) -> LocationSearchResponse:
        clean_query = query.strip()
        if len(clean_query) < 2:
            return LocationSearchResponse(query=clean_query, count=0, results=[])

        active_provider = self.provider
        cache_key = f"{active_provider.name}:location:{clean_query.lower()}:{count}:{language}"
        cached = weather_cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for [{active_provider.name}] location search: '{clean_query}'")
            return cached

        logger.info(f"Geocoding query '{clean_query}' via [{active_provider.name}]")
        results = await active_provider.search_locations(clean_query, count=count, language=language)
        response = LocationSearchResponse(query=clean_query, count=len(results), results=results)
        weather_cache.set(cache_key, response, ttl_seconds=self.ttl)
        return response


location_service = LocationService()
