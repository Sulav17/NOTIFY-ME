import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_send_notification():
    payload = {
        "recipient": "user@example.com",
        "message": "Test notification"
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/notify/", json=payload)

    assert response.status_code == 200
    assert response.json()["recipient"] == payload["recipient"]
    assert "id" in response.json()
