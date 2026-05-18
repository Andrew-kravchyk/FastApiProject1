import pytest


pytestmark = pytest.mark.asyncio


async def test_root_returns_ok(client):
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "OK"}
