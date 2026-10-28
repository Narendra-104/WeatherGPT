import pytest
import httpx
from backend.app.main import app


@pytest.mark.asyncio
async def test_live_open_meteo_current_weather(client):
    """Integration test verifying live meteorological data from Open-Meteo for Pune, India."""
    # Coordinates for Pune: 18.5204° N, 73.8567° E
    response = await client.get("/api/v1/weather/current?latitude=18.5204&longitude=73.8567&language=hi")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["provider"] == "open-meteo"
    assert isinstance(data["data"]["temperature"], (int, float))
    assert -50 <= data["data"]["temperature"] <= 60  # Physically realistic temperature
    assert len(data["data"]["weather_description"]) > 0


@pytest.mark.asyncio
async def test_live_open_meteo_forecast(client):
    """Integration test verifying live multi-day and hourly forecast from Open-Meteo."""
    response = await client.get("/api/v1/weather/forecast?latitude=28.6139&longitude=77.2090&days=3&language=en")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["hourly"]) > 0
    assert len(data["data"]["daily"]) == 3


@pytest.mark.asyncio
async def test_live_open_meteo_geocoding(client):
    """Integration test verifying live geocoding search for 'Mumbai'."""
    response = await client.get("/api/v1/locations/search?q=Mumbai&count=3&language=en")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["count"] > 0
    first_result = data["data"]["results"][0]
    assert "mumbai" in first_result["name"].lower()
    assert first_result["country"] == "India"
