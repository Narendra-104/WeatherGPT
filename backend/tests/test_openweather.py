"""Automated Tests for OpenWeather Provider Integration

Verifies provider factory selection, error handling, mock HTTP responses,
trilingual translations, and cache separation between providers.
Does NOT make paid or unmocked external requests.
"""

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock

from backend.app.config import settings
from backend.app.database.cache import weather_cache
from backend.app.providers.base import WeatherProvider
from backend.app.providers.factory import get_weather_provider
from backend.app.providers.openweather import OpenWeatherProvider
from backend.app.providers.open_meteo import OpenMeteoProvider
from backend.app.services.weather_service import weather_service
from backend.app.utils.exceptions import (
    WeatherProviderError,
    RateLimitExceededError,
    LocationNotFoundError,
    InvalidParameterError,
    WeatherGPTException,
)

MOCK_OW_CURRENT = {
    "coord": {"lon": 73.8567, "lat": 18.5204},
    "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
    "main": {
        "temp": 28.5,
        "feels_like": 29.2,
        "temp_min": 27.0,
        "temp_max": 30.0,
        "pressure": 1012,
        "humidity": 55,
    },
    "wind": {"speed": 3.5, "deg": 160},
    "rain": {"1h": 0.0},
    "dt": 1661870592,
    "name": "Pune",
    "cod": 200,
}

MOCK_OW_FORECAST = {
    "cod": "200",
    "message": 0,
    "cnt": 3,
    "list": [
        {
            "dt": 1661870400,
            "dt_txt": "2026-10-28 12:00:00",
            "main": {"temp": 28.0, "temp_min": 26.0, "temp_max": 29.0, "humidity": 60, "pressure": 1012},
            "weather": [{"id": 500, "main": "Rain", "description": "light rain"}],
            "wind": {"speed": 4.0},
            "pop": 0.75,
            "rain": {"3h": 1.8},
        },
        {
            "dt": 1661881200,
            "dt_txt": "2026-10-28 15:00:00",
            "main": {"temp": 26.5, "temp_min": 25.0, "temp_max": 27.0, "humidity": 70, "pressure": 1011},
            "weather": [{"id": 500, "main": "Rain", "description": "light rain"}],
            "wind": {"speed": 3.8},
            "pop": 0.60,
            "rain": {"3h": 0.5},
        },
        {
            "dt": 1661956800,
            "dt_txt": "2026-10-29 12:00:00",
            "main": {"temp": 30.0, "temp_min": 24.0, "temp_max": 31.0, "humidity": 50, "pressure": 1013},
            "weather": [{"id": 800, "main": "Clear", "description": "clear sky"}],
            "wind": {"speed": 2.5},
            "pop": 0.10,
            "rain": {},
        },
    ],
    "city": {
        "id": 1259229,
        "name": "Pune",
        "coord": {"lat": 18.5204, "lon": 73.8567},
        "country": "IN",
        "timezone": 19800,
    },
}

MOCK_OW_GEOCODING = [
    {
        "name": "Pune",
        "local_names": {"en": "Pune", "hi": "पुणे", "mr": "पुणे"},
        "lat": 18.5204,
        "lon": 73.8567,
        "country": "IN",
        "state": "Maharashtra",
    }
]


# -----------------------------------------------------------------------------
# 1. Provider Selection Tests
# -----------------------------------------------------------------------------
def test_provider_factory_selection():
    p1 = get_weather_provider("open_meteo")
    assert isinstance(p1, OpenMeteoProvider)

    p2 = get_weather_provider("openweather")
    assert isinstance(p2, OpenWeatherProvider)

    p3 = get_weather_provider("open-meteo")
    assert isinstance(p3, OpenMeteoProvider)

    with pytest.raises(WeatherGPTException) as exc:
        get_weather_provider("unsupported_provider")
    assert "Unsupported weather provider" in str(exc.value)


# -----------------------------------------------------------------------------
# 2. Missing OpenWeather API Key
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_missing_openweather_api_key(monkeypatch):
    monkeypatch.setattr(settings, "WEATHER_API_KEY", "")
    provider = OpenWeatherProvider()
    with pytest.raises(WeatherProviderError) as exc:
        await provider.get_current_weather(18.52, 73.85)
    assert exc.value.status_code == 500
    assert "OpenWeather API key is not configured" in exc.value.message


# -----------------------------------------------------------------------------
# 3. Successful Current Weather with Mocked HTTP Data
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_openweather_current_weather_mocked(monkeypatch):
    monkeypatch.setattr(settings, "WEATHER_API_KEY", "mock_dummy_key")

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_OW_CURRENT
    mock_client.get.return_value = mock_resp

    provider = OpenWeatherProvider(client=mock_client)
    result = await provider.get_current_weather(18.5204, 73.8567, language="en")

    assert result.temperature == 28.5
    assert result.apparent_temperature == 29.2
    assert result.relative_humidity == 55
    assert result.location_name == "Pune"
    assert result.weather_code == 800
    assert result.provider == "openweather"
    assert result.wind_speed == round(3.5 * 3.6, 1)  # m/s converted to km/h


# -----------------------------------------------------------------------------
# 4. Successful Forecast Response with Mocked HTTP Data
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_openweather_forecast_mocked(monkeypatch):
    monkeypatch.setattr(settings, "WEATHER_API_KEY", "mock_dummy_key")

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_OW_FORECAST
    mock_client.get.return_value = mock_resp

    provider = OpenWeatherProvider(client=mock_client)
    result = await provider.get_forecast(18.5204, 73.8567, days=2, language="en")

    assert result.provider == "openweather"
    assert len(result.hourly) == 3
    assert result.hourly[0].temperature == 28.0
    assert result.hourly[0].precipitation_probability == 75.0
    assert len(result.daily) == 2
    assert result.daily[0].date == "2026-10-28"
    assert result.daily[0].temperature_max == 28.0


# -----------------------------------------------------------------------------
# 5. Invalid API Key Handling (401)
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_openweather_invalid_api_key(monkeypatch):
    monkeypatch.setattr(settings, "WEATHER_API_KEY", "invalid_key")

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 401
    mock_client.get.return_value = mock_resp

    provider = OpenWeatherProvider(client=mock_client)
    with pytest.raises(WeatherProviderError) as exc:
        await provider.get_current_weather(18.52, 73.85)
    assert exc.value.status_code == 401
    assert "Invalid OpenWeather API key" in exc.value.message


# -----------------------------------------------------------------------------
# 6. Rate Limit Handling (429)
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_openweather_rate_limit(monkeypatch):
    monkeypatch.setattr(settings, "WEATHER_API_KEY", "valid_key")

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 429
    mock_client.get.return_value = mock_resp

    provider = OpenWeatherProvider(client=mock_client)
    with pytest.raises(RateLimitExceededError):
        await provider.get_current_weather(18.52, 73.85)


# -----------------------------------------------------------------------------
# 7. Timeout Handling
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_openweather_timeout(monkeypatch):
    monkeypatch.setattr(settings, "WEATHER_API_KEY", "valid_key")

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = httpx.TimeoutException("Read timeout")

    provider = OpenWeatherProvider(client=mock_client)
    with pytest.raises(WeatherProviderError) as exc:
        await provider.get_current_weather(18.52, 73.85)
    assert "timed out" in exc.value.message.lower()


# -----------------------------------------------------------------------------
# 8. Malformed Provider Response Handling
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_openweather_malformed_response(monkeypatch):
    monkeypatch.setattr(settings, "WEATHER_API_KEY", "valid_key")

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"incomplete": "payload"}
    mock_client.get.return_value = mock_resp

    provider = OpenWeatherProvider(client=mock_client)
    with pytest.raises(WeatherProviderError) as exc:
        await provider.get_current_weather(18.52, 73.85)
    assert "Malformed response" in exc.value.message


# -----------------------------------------------------------------------------
# 9. Location Search Behavior
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_openweather_location_search(monkeypatch):
    monkeypatch.setattr(settings, "WEATHER_API_KEY", "valid_key")

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = MOCK_OW_GEOCODING
    mock_client.get.return_value = mock_resp

    provider = OpenWeatherProvider(client=mock_client)
    results = await provider.search_locations("Pune", count=5, language="mr")
    assert len(results) == 1
    assert results[0].name == "पुणे"
    assert results[0].admin1 == "Maharashtra"
    assert results[0].country == "IN"


# -----------------------------------------------------------------------------
# 10. Forecast Range Boundary Check (OpenWeather standard <= 5 days)
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_openweather_forecast_days_limit(monkeypatch):
    monkeypatch.setattr(settings, "WEATHER_API_KEY", "valid_key")
    provider = OpenWeatherProvider()
    with pytest.raises(InvalidParameterError) as exc:
        await provider.get_forecast(18.52, 73.85, days=7)
    assert "supports up to 5 days" in exc.value.message


# -----------------------------------------------------------------------------
# 11. Multilingual Translations: Hindi & Marathi
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_openweather_multilingual_translations(monkeypatch):
    monkeypatch.setattr(settings, "WEATHER_API_KEY", "valid_key")

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "coord": {"lon": 73.85, "lat": 18.52},
        "weather": [{"id": 500, "main": "Rain", "description": "light rain"}],
        "main": {"temp": 24.0, "humidity": 80, "pressure": 1010},
        "name": "Pune",
        "dt": 1661870592,
    }
    mock_client.get.return_value = mock_resp

    provider = OpenWeatherProvider(client=mock_client)

    # Hindi
    res_hi = await provider.get_current_weather(18.52, 73.85, language="hi")
    assert res_hi.weather_description == "बारिश"

    # Marathi
    res_mr = await provider.get_current_weather(18.52, 73.85, language="mr")
    assert res_mr.weather_description == "पाऊस"


# -----------------------------------------------------------------------------
# 12. Cache Separation Between Providers
# -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_cache_separation_between_providers():
    weather_cache.clear()

    # Manually populate cache for both providers for identical coordinates
    key_om = "open-meteo:current:18.520:73.850:en"
    key_ow = "openweather:current:18.520:73.850:en"

    weather_cache.set(key_om, "OM_DATA", ttl_seconds=600)
    weather_cache.set(key_ow, "OW_DATA", ttl_seconds=600)

    # Verify they don't overwrite each other
    assert weather_cache.get(key_om) == "OM_DATA"
    assert weather_cache.get(key_ow) == "OW_DATA"

    weather_cache.clear()
