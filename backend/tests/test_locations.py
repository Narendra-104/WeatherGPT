from backend.app.schemas.location import LocationResult
from backend.app.services.location_service import location_service


class MockLocationProvider:
    name = "mock-loc"

    async def get_current_weather(self, latitude: float, longitude: float, language: str = "en"):
        raise NotImplementedError

    async def get_forecast(self, latitude: float, longitude: float, days: int = 7, language: str = "en"):
        raise NotImplementedError

    async def search_locations(self, query: str, count: int = 10, language: str = "en"):
        if "pune" in query.lower():
            return [
                LocationResult(
                    id=1259229,
                    name="Pune",
                    latitude=18.5196,
                    longitude=73.8553,
                    elevation=560.0,
                    country="India",
                    admin1="Maharashtra",
                    country_code="IN",
                )
            ]
        return []

    async def get_alerts(self, latitude: float, longitude: float, language: str = "en"):
        raise NotImplementedError


async def test_location_search_success(client, monkeypatch):
    monkeypatch.setattr(location_service, "provider", MockLocationProvider())

    response = await client.get("/api/v1/locations/search?q=Pune&count=5")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["count"] == 1
    result = data["data"]["results"][0]
    assert result["name"] == "Pune"
    assert result["admin1"] == "Maharashtra"
    assert result["country"] == "India"


async def test_location_search_too_short(client):
    # Query length < 2 triggers 422
    response = await client.get("/api/v1/locations/search?q=a")
    assert response.status_code == 422
