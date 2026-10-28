from backend.app.schemas.weather import CurrentWeatherData
from backend.app.schemas.forecast import ForecastData, DailyForecastItem, HourlyForecastItem
from backend.app.schemas.location import LocationResult
from backend.app.services.weather_service import weather_service
from backend.app.services.location_service import location_service


class MockWeatherProviderForChat:
    name = "mock-chat-provider"

    async def get_current_weather(self, latitude: float, longitude: float, language: str = "en"):
        desc = "हल्की बारिश" if language == "hi" else "हलका पाऊस" if language == "mr" else "Light rain"
        loc = "Mumbai" if abs(latitude - 19.07) < 0.5 else "Pune"
        temp = 31.0 if loc == "Mumbai" else 26.0
        return CurrentWeatherData(
            latitude=latitude,
            longitude=longitude,
            location_name=loc,
            observation_time="2026-10-28T12:00:00Z",
            temperature=temp,
            apparent_temperature=temp + 1.0,
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
        return ForecastData(
            latitude=latitude,
            longitude=longitude,
            timezone="Asia/Kolkata",
            hourly=[],
            daily=[
                DailyForecastItem(
                    date="2026-10-28",
                    temperature_max=28.0,
                    temperature_min=22.0,
                    precipitation_sum=2.0,
                    precipitation_probability_max=70.0,
                    weather_code=61,
                    weather_description="Rain",
                ),
                DailyForecastItem(
                    date="2026-10-29",
                    temperature_max=29.0,
                    temperature_min=23.0,
                    precipitation_sum=5.0,
                    precipitation_probability_max=80.0,
                    weather_code=61,
                    weather_description="Rain showers",
                ),
            ],
            provider="mock-chat-provider",
        )

    async def search_locations(self, query: str, count: int = 10, language: str = "en"):
        q = query.lower()
        if "pune" in q:
            return [LocationResult(name="Pune", latitude=18.52, longitude=73.85, country="India")]
        if "mumbai" in q:
            return [LocationResult(name="Mumbai", latitude=19.07, longitude=72.87, country="India")]
        return []

    async def get_alerts(self, latitude: float, longitude: float, language: str = "en"):
        return []


async def test_chat_without_location(client):
    # Without coordinates or location
    payload = {"message": "Is it going to rain?", "language": "en"}
    response = await client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "city" in data["data"]["reply"].lower() or "coordinates" in data["data"]["reply"].lower()
    assert len(data["data"]["suggestions"]) > 0


async def test_chat_with_grounded_weather_hindi(client, monkeypatch):
    mock = MockWeatherProviderForChat()
    monkeypatch.setattr(weather_service, "provider", mock)
    monkeypatch.setattr(location_service, "provider", mock)

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


async def test_chat_agri_advisory_marathi(client, monkeypatch):
    mock = MockWeatherProviderForChat()
    monkeypatch.setattr(weather_service, "provider", mock)
    monkeypatch.setattr(location_service, "provider", mock)

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
    assert "फवारणी" in data["data"]["reply"]


async def test_chat_clothing_advisory(client, monkeypatch):
    mock = MockWeatherProviderForChat()
    monkeypatch.setattr(weather_service, "provider", mock)
    monkeypatch.setattr(location_service, "provider", mock)

    payload = {
        "message": "What should I wear today in Pune?",
        "language": "en",
    }
    response = await client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "clothing advice" in data["data"]["reply"].lower() or "umbrella" in data["data"]["reply"].lower() or "wear" in data["data"]["reply"].lower()


async def test_chat_city_comparison(client, monkeypatch):
    mock = MockWeatherProviderForChat()
    monkeypatch.setattr(weather_service, "provider", mock)
    monkeypatch.setattr(location_service, "provider", mock)

    payload = {
        "message": "Compare Pune and Mumbai",
        "language": "en",
    }
    response = await client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "pune" in data["data"]["reply"].lower()
    assert "mumbai" in data["data"]["reply"].lower()


async def test_chat_outdoor_advice(client, monkeypatch):
    mock = MockWeatherProviderForChat()
    monkeypatch.setattr(weather_service, "provider", mock)
    monkeypatch.setattr(location_service, "provider", mock)

    payload = {
        "message": "Is it a good time to go outside in Pune?",
        "language": "en",
    }
    response = await client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "outdoor" in data["data"]["reply"].lower() or "pune" in data["data"]["reply"].lower()
