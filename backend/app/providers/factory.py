"""Weather Provider Factory Module

Centralized provider resolution supporting Open-Meteo and OpenWeather.
Validates provider choice and raises clear configuration errors for invalid options.
"""

from typing import Optional
from backend.app.config import settings
from backend.app.providers.base import WeatherProvider
from backend.app.providers.open_meteo import OpenMeteoProvider
from backend.app.providers.openweather import OpenWeatherProvider
from backend.app.utils.exceptions import WeatherGPTException
from backend.app.utils.logger import logger


def get_weather_provider(provider_override: Optional[str] = None) -> WeatherProvider:
    """Factory function returning the configured meteorological provider."""
    raw_name = provider_override or settings.WEATHER_PROVIDER
    normalized = raw_name.lower().replace("-", "_").strip()

    if normalized in ["open_meteo", "openmeteo"]:
        return OpenMeteoProvider()
    elif normalized in ["openweather", "open_weather", "openweathermap"]:
        return OpenWeatherProvider()
    else:
        logger.error(f"Invalid weather provider configured: '{raw_name}'")
        raise WeatherGPTException(
            f"Unsupported weather provider '{raw_name}'. "
            f"Supported providers are 'open_meteo' and 'openweather'.",
            status_code=500,
        )
