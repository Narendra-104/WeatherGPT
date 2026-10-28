"""Application Configuration Module

Loads environment variables using pydantic-settings with sensible defaults.
Zero mandatory external API keys are required to run health checks or local tests.
"""

from typing import List
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
    PRIMARY_WEATHER_PROVIDER: str = "open-meteo"
    WEATHER_API_KEY: str = ""
    WEATHER_API_BASE_URL: str = "https://api.open-meteo.com/v1"
    WEATHER_GEOCODING_URL: str = "https://geocoding-api.open-meteo.com/v1"
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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
