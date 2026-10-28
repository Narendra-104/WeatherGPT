from backend.app.schemas.alert import WeatherAlert
from backend.app.services.alert_service import alert_service


class MockAlertProvider:
    name = "mock-alert"

    async def get_current_weather(self, latitude: float, longitude: float, language: str = "en"):
        raise NotImplementedError

    async def get_forecast(self, latitude: float, longitude: float, days: int = 7, language: str = "en"):
        raise NotImplementedError

    async def search_locations(self, query: str, count: int = 10, language: str = "en"):
        raise NotImplementedError

    async def get_alerts(self, latitude: float, longitude: float, language: str = "en"):
        return [
            WeatherAlert(
                id="alert-rain-test",
                title="Severe Heavy Rainfall Warning" if language == "en" else "मुसळधार पावसाचा इशारा",
                severity="warning",
                urgency="Expected",
                description="Expected precipitation: 65mm",
                instruction="Avoid waterlogging" if language == "en" else "पाणी साचलेल्या रस्त्यांवर जाणे टाळा",
                areas=["Coastal Maharashtra"],
                effective="2026-10-28T12:00:00Z",
                source="Meteorological Advisory Engine",
            )
        ]


async def test_alerts_endpoint(client, monkeypatch):
    monkeypatch.setattr(alert_service, "provider", MockAlertProvider())

    response = await client.get("/api/v1/alerts?latitude=18.52&longitude=73.85&language=mr")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["count"] == 1
    alert = data["data"]["alerts"][0]
    assert alert["severity"] == "warning"
    assert "मुसळधार" in alert["title"]
