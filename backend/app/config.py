"""Application Configuration Module

Loads environment variables using pydantic-settings with sensible defaults.
Supports both Open-Meteo and OpenWeather providers.
Zero mandatory external API keys are required to run health checks or local tests.
"""

from typing import List, Optional
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    APP_ENV: str = "development"
    APP_NAME: str = "WeatherGPT Backend"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DEBUG: bool = True
    VERSION: str = "1.0.0"

    # CORS Settings
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173,https://weathergpt-ai-vert.vercel.app"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    # Meteorological Provider Settings
    WEATHER_PROVIDER: str = Field(
        default="open-meteo",
        validation_alias=AliasChoices("WEATHER_PROVIDER", "PRIMARY_WEATHER_PROVIDER"),
        description="Active provider: 'open_meteo' or 'openweather'"
    )

    # OpenWeather Configuration
    WEATHER_API_KEY: str = Field(default="", description="API key for providers requiring authentication")
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org"
    OPENWEATHER_GEOCODING_URL: str = "https://api.openweathermap.org/geo/1.0"

    # Open-Meteo Configuration
    WEATHER_API_BASE_URL: str = "https://api.open-meteo.com/v1"
    WEATHER_GEOCODING_URL: str = "https://geocoding-api.open-meteo.com/v1"

    # Common Weather Engine Settings
    WEATHER_CACHE_TTL_SECONDS: int = 900  # 15 minutes default
    HTTP_TIMEOUT_SECONDS: float = 10.0

    # AI Model Settings (Safe fallback if key is absent)
    AI_PROVIDER: str = "mock"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    AI_MODEL_NAME: str = "gemini-1.5-flash"

    # Localization
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: List[str] = ["en", "hi", "mr"]

    # Database
    DATABASE_URL: str = "sqlite:///./weathergpt.db"

    @property
    def normalized_weather_provider(self) -> str:
        prov = self.WEATHER_PROVIDER.lower().replace("-", "_").strip()
        if prov in ["openweather", "open_weather", "openweathermap"]:
            return "openweather"
        if prov in ["open_meteo", "openmeteo"]:
            return "open_meteo"
        return prov

    @property
    def is_weather_api_key_configured(self) -> bool:
        """Returns True if an API key is present without exposing its value."""
        return bool(self.WEATHER_API_KEY and len(self.WEATHER_API_KEY.strip()) > 5)

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
