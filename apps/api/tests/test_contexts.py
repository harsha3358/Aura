import pytest
from httpx import AsyncClient, ASGITransport
import uuid
from app.main import app
from app.auth import get_current_user
from app.models.core import User, Context
from app.extraction.context import ContextClassifier
from app.services.llm import LLMProvider

MOCK_USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
mock_user = User(id=MOCK_USER_ID, email="test@example.com", display_name="Test User")


async def mock_get_current_user_dep():
    return mock_user


class MockContextLLM(LLMProvider):
    def __init__(self, response_text: str):
        self.response_text = response_text

    async def generate_chat(self, messages, format=None):
        return self.response_text


@pytest.fixture(autouse=True)
def setup_auth_override():
    app.dependency_overrides[get_current_user] = mock_get_current_user_dep
    yield
    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_create_and_list_contexts():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/contexts",
            json={
                "name": "Startup Building",
                "description": "Building my next startup AURA",
            },
        )
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


@pytest.mark.anyio
async def test_context_classifier_match():
    raw_json = """{
      "matched_context_name": "Startup Building",
      "shift_detected": false,
      "new_context": null,
      "confidence": 0.95,
      "reasoning": "Matches existing Startup Building context."
    }"""
    mock_llm = MockContextLLM(raw_json)
    classifier = ContextClassifier(llm_provider=mock_llm)

    existing = [
        Context(name="Startup Building", description="AURA app development"),
        Context(name="Learning", description="FastAPI and pytest"),
    ]
    res = await classifier.classify(
        "I am writing the context router code now.", existing
    )
    assert res["matched_context_name"] == "Startup Building"
    assert res["shift_detected"] is False
    assert res["new_context"] is None


@pytest.mark.anyio
async def test_context_classifier_shift():
    raw_json = """{
      "matched_context_name": null,
      "shift_detected": true,
      "new_context": {
        "name": "Research",
        "description": "Studying neural networks and vector spaces"
      },
      "confidence": 0.9,
      "reasoning": "Differs from existing contexts, shifts to Research."
    }"""
    mock_llm = MockContextLLM(raw_json)
    classifier = ContextClassifier(llm_provider=mock_llm)

    existing = [Context(name="Startup Building", description="AURA app development")]
    res = await classifier.classify(
        "I want to read papers on neural net quantization.", existing
    )
    assert res["matched_context_name"] is None
    assert res["shift_detected"] is True
    assert res["new_context"]["name"] == "Research"
