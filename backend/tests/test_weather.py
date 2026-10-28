from backend.app.schemas.weather import CurrentWeatherData
from backend.app.services.weather_service import weather_service


class MockWeatherProvider:
    name = "mock-provider"

    async def get_current_weather(self, latitude: float, longitude: float, language: str = "en"):
        desc = "साफ़ आसमान" if language == "hi" else "निरभ्र आकाश" if language == "mr" else "Clear sky"
        return CurrentWeatherData(
            latitude=latitude,
            longitude=longitude,
            observation_time="2026-10-28T12:00:00Z",
            temperature=28.5,
            apparent_temperature=29.0,
            relative_humidity=60.0,
            precipitation=0.0,
            weather_code=0,
            weather_description=desc,
            wind_speed=12.0,
            wind_direction=180.0,
            surface_pressure=1013.2,
            uv_index=5.0,
            provider="mock-provider",
        )

    async def get_forecast(self, latitude: float, longitude: float, days: int = 7, language: str = "en"):
        raise NotImplementedError

    async def search_locations(self, query: str, count: int = 10, language: str = "en"):
        raise NotImplementedError

    async def get_alerts(self, latitude: float, longitude: float, language: str = "en"):
        raise NotImplementedError


async def test_current_weather_validation_errors(client):
    # Latitude out of bounds (> 90)
    response = await client.get("/api/v1/weather/current?latitude=95.0&longitude=73.85")
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False

    # Longitude out of bounds (< -180)
    response = await client.get("/api/v1/weather/current?latitude=18.52&longitude=-190.0")
    assert response.status_code == 422

    # Unsupported language
    response = await client.get("/api/v1/weather/current?latitude=18.52&longitude=73.85&language=es")
    assert response.status_code == 422


async def test_current_weather_success(client, monkeypatch):
    monkeypatch.setattr(weather_service, "provider", MockWeatherProvider())

    # English test
    response = await client.get("/api/v1/weather/current?latitude=18.5204&longitude=73.8567&language=en")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["temperature"] == 28.5
    assert data["data"]["weather_description"] == "Clear sky"

    # Hindi test
    response_hi = await client.get("/api/v1/weather/current?latitude=18.5204&longitude=73.8567&language=hi")
    assert response_hi.status_code == 200
    assert response_hi.json()["data"]["weather_description"] == "साफ़ आसमान"

    # Marathi test
    response_mr = await client.get("/api/v1/weather/current?latitude=18.5204&longitude=73.8567&language=mr")
    assert response_mr.status_code == 200
    assert response_mr.json()["data"]["weather_description"] == "निरभ्र आकाश"
