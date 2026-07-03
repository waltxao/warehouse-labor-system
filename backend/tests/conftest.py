import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import async_session


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def db_session():
    """Provide an async database session for unit tests."""
    async with async_session() as session:
        yield session


@pytest.fixture
async def admin_token(client):
    """Log in as admin and return the access token."""
    resp = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    data = resp.json()
    return data["data"]["access_token"]
