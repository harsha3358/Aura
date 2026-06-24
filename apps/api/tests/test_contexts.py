import pytest
from httpx import AsyncClient, ASGITransport
import uuid
from app.main import app
from app.auth import get_current_user
from app.models.core import User

MOCK_USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
mock_user = User(id=MOCK_USER_ID, email="test@example.com", display_name="Test User")

async def mock_get_current_user_dep():
    return mock_user

@pytest.fixture(autouse=True)
def setup_auth_override():
    app.dependency_overrides[get_current_user] = mock_get_current_user_dep
    yield
    app.dependency_overrides.clear()

@pytest.mark.anyio
async def test_create_and_list_contexts():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/contexts", json={
            "name": "Startup Building",
            "description": "Building my next startup AURA"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Startup Building"
        assert data["description"] == "Building my next startup AURA"
        assert "id" in data
        ctx_id = data["id"]

        list_resp = await ac.get("/api/v1/contexts")
        assert list_resp.status_code == 200
        contexts = list_resp.json()
        assert len(contexts) >= 1
        assert any(c["id"] == ctx_id for c in contexts)
