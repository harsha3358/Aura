import pytest
from httpx import AsyncClient, ASGITransport
import uuid
from app.main import app
from app.auth import get_current_user
from app.routers.conversations import get_extraction_service
from app.models.core import User
from app.extraction.schemas import ExtractionResult

MOCK_USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
mock_user = User(id=MOCK_USER_ID, email="test@example.com", display_name="Test User")

async def mock_get_current_user_dep():
    return mock_user

class MockExtractionService:
    async def extract_from_message(self, message: str):
        return ExtractionResult(
            facts=[],
            decisions=[],
            considered_options=[],
            tasks=[],
            deadlines=[],
            contexts=[],
            metadata={"confidence": 1.0, "reasoning": "Mocked extraction"}
        ), []

async def mock_get_extraction_service():
    return MockExtractionService()

@pytest.fixture(autouse=True)
def setup_auth_override():
    app.dependency_overrides[get_current_user] = mock_get_current_user_dep
    app.dependency_overrides[get_extraction_service] = mock_get_extraction_service
    yield
    app.dependency_overrides.clear()

@pytest.mark.anyio
async def test_create_and_get_conversation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/conversations", json={"title": "Test Chat"})
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Chat"
        assert "id" in data
        conv_id = data["id"]

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
        response = await ac.post("/api/v1/conversations", json={"title": "Message Chat"})
        conv_id = response.json()["id"]

        response = await ac.post(f"/api/v1/conversations/{conv_id}/messages", json={
            "content": "Hello AURA",
            "role": "user"
        })
        assert response.status_code == 201
        res_data = response.json()
        assert "message" in res_data
        assert "extraction" in res_data
        msg_data = res_data["message"]
        assert msg_data["content"] == "Hello AURA"
        assert msg_data["role"] == "user"
        assert msg_data["conversation_id"] == conv_id

        response = await ac.get(f"/api/v1/conversations/{conv_id}")
        conv_data = response.json()
        assert len(conv_data["messages"]) == 1
        assert conv_data["messages"][0]["content"] == "Hello AURA"

@pytest.mark.anyio
async def test_submit_feedback():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create conversation
        response = await ac.post("/api/v1/conversations", json={"title": "Feedback Chat"})
        conv_id = response.json()["id"]

        # Add message to get a valid extraction run message id
        msg_resp = await ac.post(f"/api/v1/conversations/{conv_id}/messages", json={
            "content": "AURA feedback test message",
            "role": "user"
        })
        msg_id = msg_resp.json()["message"]["id"]

        # Submit feedback
        fb_resp = await ac.post("/api/v1/extraction/feedback", json={
            "extraction_run_id": msg_id,
            "feedback_type": "correct",
            "comment": "Perfect extraction"
        })
        assert fb_resp.status_code == 201
        fb_data = fb_resp.json()
        assert fb_data["extraction_run_id"] == msg_id
        assert fb_data["feedback_type"] == "correct"
        assert fb_data["comment"] == "Perfect extraction"
