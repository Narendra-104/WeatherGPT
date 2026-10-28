import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.database.cache import weather_cache


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear in-memory cache before and after every test run to ensure isolation."""
    weather_cache.clear()
    yield
    weather_cache.clear()


@pytest.fixture
async def client():
    """Asynchronous HTTPX test client using ASGITransport."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
