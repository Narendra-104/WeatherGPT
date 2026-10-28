from backend.app.config import settings
from backend.app.providers.base import WeatherProvider
from backend.app.providers.open_meteo import OpenMeteoProvider


def get_weather_provider() -> WeatherProvider:
    """Factory function returning the configured meteorological provider."""
    provider_name = settings.PRIMARY_WEATHER_PROVIDER.lower().strip()
    if provider_name == "open-meteo":
        return OpenMeteoProvider()
    
    # Default fallback to Open-Meteo
    return OpenMeteoProvider()
