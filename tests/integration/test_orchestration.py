import pytest
from httpx import ASGITransport, AsyncClient

from modules.helloria.core import app  # Chemin propre modulaire

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_root_endpoint() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        assert "Arkalia-LUNA API active" in response.json()["message"]
