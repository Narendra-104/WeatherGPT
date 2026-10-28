async def test_health_endpoint(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"
    assert "version" in data["data"]
    assert "provider" in data["data"]
    assert "uptime_seconds" in data["data"]
    assert "en" in data["data"]["supported_languages"]
    assert "hi" in data["data"]["supported_languages"]
    assert "mr" in data["data"]["supported_languages"]


async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["documentation"] == "/docs"
