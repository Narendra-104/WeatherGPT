from backend.app.schemas.weather import CurrentWeatherData
from backend.app.services.weather_service import weather_service


class MockWeatherProviderForChat:
    name = "mock-chat-provider"

    async def get_current_weather(self, latitude: float, longitude: float, language: str = "en"):
        desc = "हल्की बारिश" if language == "hi" else "हलका पाऊस" if language == "mr" else "Light rain"
        return CurrentWeatherData(
            latitude=latitude,
            longitude=longitude,
            location_name="Pune",
            observation_time="2026-10-28T12:00:00Z",
            temperature=26.0,
            apparent_temperature=27.0,
            relative_humidity=85.0,
            precipitation=3.2,
            weather_code=61,
            weather_description=desc,
            wind_speed=18.0,
            wind_direction=240.0,
            surface_pressure=1009.0,
            uv_index=3.0,
            provider="mock-chat-provider",
        )

    async def get_forecast(self, latitude: float, longitude: float, days: int = 7, language: str = "en"):
        raise NotImplementedError

    async def search_locations(self, query: str, count: int = 10, language: str = "en"):
        raise NotImplementedError

    async def get_alerts(self, latitude: float, longitude: float, language: str = "en"):
        raise NotImplementedError


async def test_chat_without_location(client):
    # Without coordinates or location
    payload = {"message": "Is it going to rain?", "language": "en"}
    response = await client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "location coordinates" in data["data"]["reply"].lower() or "city" in data["data"]["reply"].lower()
    assert len(data["data"]["suggestions"]) > 0


async def test_chat_with_grounded_weather_hindi(client, monkeypatch):
    monkeypatch.setattr(weather_service, "provider", MockWeatherProviderForChat())

    # Hindi question regarding rain
    payload = {
        "message": "क्या अभी बारिश हो रही है?",
        "language": "hi",
        "latitude": 18.52,
        "longitude": 73.85,
        "location_name": "Pune",
    }
    response = await client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["language"] == "hi"
    assert "Pune" in data["data"]["reply"] or "बारिश" in data["data"]["reply"]
    assert data["data"]["grounded_facts"] is not None
    assert data["data"]["grounded_facts"]["temperature"] == 26.0


async def test_chat_agri_advisory_marathi(client, monkeypatch):
    monkeypatch.setattr(weather_service, "provider", MockWeatherProviderForChat())

    # Marathi question for agricultural spraying
    payload = {
        "message": "शेतीमध्ये आज औषध फवारणी करावी का?",
        "language": "mr",
        "latitude": 18.52,
        "longitude": 73.85,
        "location_name": "Pune",
    }
    response = await client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["language"] == "mr"
    # Because precipitation is 3.2mm, should advise postponement
    assert "फवारणी" in data["data"]["reply"]
