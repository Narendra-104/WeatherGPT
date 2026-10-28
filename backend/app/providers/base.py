from abc import ABC, abstractmethod
from typing import List, Optional
from backend.app.schemas.weather import CurrentWeatherData
from backend.app.schemas.forecast import ForecastData
from backend.app.schemas.location import LocationResult
from backend.app.schemas.alert import WeatherAlert


class WeatherProvider(ABC):
    """Abstract interface for meteorological data ingestion."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier."""
        pass

    @abstractmethod
    async def get_current_weather(
        self, latitude: float, longitude: float, language: str = "en"
    ) -> CurrentWeatherData:
        """Fetch current weather observation for given coordinates."""
        pass

    @abstractmethod
    async def get_forecast(
        self, latitude: float, longitude: float, days: int = 7, language: str = "en"
    ) -> ForecastData:
        """Fetch multi-day and hourly forecast."""
        pass

    @abstractmethod
    async def search_locations(
        self, query: str, count: int = 10, language: str = "en"
    ) -> List[LocationResult]:
        """Geocode query text into list of matching geographical locations."""
        pass

    @abstractmethod
    async def get_alerts(
        self, latitude: float, longitude: float, language: str = "en"
    ) -> List[WeatherAlert]:
        """Retrieve active severe weather alerts."""
        pass
