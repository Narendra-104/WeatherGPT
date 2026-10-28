from backend.app.schemas.forecast import ForecastData, HourlyForecastItem, DailyForecastItem
from backend.app.services.weather_service import weather_service


class MockForecastProvider:
    name = "mock-forecast"

    async def get_current_weather(self, latitude: float, longitude: float, language: str = "en"):
        raise NotImplementedError

    async def get_forecast(self, latitude: float, longitude: float, days: int = 7, language: str = "en"):
        desc = "बारिश" if language == "hi" else "पाऊस" if language == "mr" else "Rain"
        hourly = [
            HourlyForecastItem(
                time="2026-10-28T13:00",
                temperature=25.0,
                precipitation_probability=80.0,
                precipitation=2.5,
                weather_code=61,
                weather_description=desc,
                wind_speed=15.0,
            )
        ]
        daily = [
            DailyForecastItem(
                date="2026-10-28",
                temperature_max=29.0,
                temperature_min=22.0,
                precipitation_sum=10.0,
                precipitation_probability_max=85.0,
                weather_code=61,
                weather_description=desc,
            )
        ]
        return ForecastData(
            latitude=latitude,
            longitude=longitude,
            timezone="Asia/Kolkata",
            hourly=hourly,
            daily=daily,
            provider="mock-forecast",
        )

    async def search_locations(self, query: str, count: int = 10, language: str = "en"):
        raise NotImplementedError

    async def get_alerts(self, latitude: float, longitude: float, language: str = "en"):
        raise NotImplementedError


async def test_forecast_endpoint(client, monkeypatch):
    monkeypatch.setattr(weather_service, "provider", MockForecastProvider())

    response = await client.get("/api/v1/weather/forecast?latitude=18.52&longitude=73.85&days=3&language=hi")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["hourly"]) == 1
    assert data["data"]["hourly"][0]["weather_description"] == "बारिश"
    assert len(data["data"]["daily"]) == 1
    assert data["data"]["daily"][0]["temperature_max"] == 29.0


async def test_forecast_invalid_days(client):
    # Days exceeds 14
    response = await client.get("/api/v1/weather/forecast?latitude=18.52&longitude=73.85&days=20")
    assert response.status_code == 422
