import pytest
from starlette.testclient import TestClient

from modules.helloria.core import app


@pytest.mark.asyncio
async def test_root_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Arkalia-LUNA API active"}
