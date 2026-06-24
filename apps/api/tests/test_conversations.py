import pytest
from httpx import AsyncClient, ASGITransport
import uuid
from app.main import app
from app.auth import get_current_user
from app.models.core import User
from app.dependencies import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Define a mock current user
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
async def test_create_and_get_conversation():
    # Setup async client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create a conversation
        response = await ac.post("/api/v1/conversations", json={"title": "Test Chat"})
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Chat"
        assert "id" in data
        conv_id = data["id"]

        # Get conversation
        response = await ac.get(f"/api/v1/conversations/{conv_id}")
        assert response.status_code == 200
        get_data = response.json()
        assert get_data["id"] == conv_id
        assert get_data["title"] == "Test Chat"
        assert get_data["messages"] == []

@pytest.mark.anyio
async def test_add_message():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create conversation
        response = await ac.post("/api/v1/conversations", json={"title": "Message Chat"})
        conv_id = response.json()["id"]

        # Add message
        response = await ac.post(f"/api/v1/conversations/{conv_id}/messages", json={
            "content": "Hello AURA",
            "role": "user"
        })
        assert response.status_code == 201
        msg_data = response.json()
        assert msg_data["content"] == "Hello AURA"
        assert msg_data["role"] == "user"
        assert msg_data["conversation_id"] == conv_id

        # Get conversation and verify messages list
        response = await ac.get(f"/api/v1/conversations/{conv_id}")
        conv_data = response.json()
        assert len(conv_data["messages"]) == 1
        assert conv_data["messages"][0]["content"] == "Hello AURA"
