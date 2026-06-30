import pytest
from httpx import AsyncClient, ASGITransport
import uuid
from app.main import app
from app.auth import get_current_user
from app.routers.conversations import get_extraction_service
from app.routers.contexts import get_context_classifier
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

class MockContextClassifier:
    async def classify(self, message: str, existing_contexts: list):
        return {
            "matched_context_name": None,
            "shift_detected": False,
            "new_context": None,
            "confidence": 1.0,
            "reasoning": "Mocked context classifier response"
        }

async def mock_get_context_classifier():
    return MockContextClassifier()

@pytest.fixture(autouse=True)
def setup_auth_override():
    app.dependency_overrides[get_current_user] = mock_get_current_user_dep
    app.dependency_overrides[get_extraction_service] = mock_get_extraction_service
    app.dependency_overrides[get_context_classifier] = mock_get_context_classifier
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
        assert "facts" in res_data
        assert "decisions" in res_data
        assert "tasks" in res_data
        assert "deadlines" in res_data
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
        response = await ac.post("/api/v1/conversations", json={"title": "Feedback Chat"})
        conv_id = response.json()["id"]

        msg_resp = await ac.post(f"/api/v1/conversations/{conv_id}/messages", json={
            "content": "AURA feedback test message",
            "role": "user"
        })
        msg_id = msg_resp.json()["message"]["id"]

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

@pytest.mark.anyio
async def test_list_conversations():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/api/v1/conversations", json={"title": "List Chat"})
        
        response = await ac.get("/api/v1/conversations")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(c["title"] == "List Chat" for c in data)

from app.extraction.schemas import FactItem, DecisionItem, TaskItem, DeadlineItem
from app.extraction.contract import Fact as FactEnum, Decision as DecisionEnum, Task as TaskEnum, Deadline as DeadlineEnum

class PopulatedMockExtractionService:
    async def extract_from_message(self, message: str):
        return ExtractionResult(
            facts=[FactItem(value="AURA Platform", entity="project", confidence=0.95, category=FactEnum.PROJECT_DETAIL)],
            decisions=[DecisionItem(value="PostgreSQL", entity="database", confidence=0.90, category=DecisionEnum.TECHNOLOGY)],
            considered_options=[],
            tasks=[TaskItem(value="Test Sprint 5", entity="tests", confidence=0.85, category=TaskEnum.TESTING)],
            deadlines=[DeadlineItem(value="Friday", entity="milestone", confidence=0.80, category=DeadlineEnum.MILESTONE)],
            contexts=[],
            metadata={"confidence": 1.0, "reasoning": "Mocked populated extraction"}
        ), []

@pytest.mark.anyio
async def test_knowledge_review_workflow():
    app.dependency_overrides[get_extraction_service] = lambda: PopulatedMockExtractionService()
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        conv_resp = await ac.post("/api/v1/conversations", json={"title": "Review Chat"})
        conv_id = conv_resp.json()["id"]
        
        msg_resp = await ac.post(f"/api/v1/conversations/{conv_id}/messages", json={
            "content": "I am building AURA using PostgreSQL by Friday",
            "role": "user"
        })
        assert msg_resp.status_code == 201
        res_data = msg_resp.json()
        assert len(res_data["facts"]) == 1
        assert len(res_data["decisions"]) == 1
        
        fact_id = res_data["facts"][0]["id"]
        dec_id = res_data["decisions"][0]["id"]
        task_id = res_data["tasks"][0]["id"]
        
        # 1. Approve a Fact
        app_resp = await ac.post(f"/api/v1/facts/{fact_id}/approve")
        assert app_resp.status_code == 200
        assert app_resp.json()["review_state"] == "approved"
        
        # 2. Reject a Decision
        rej_resp = await ac.post(f"/api/v1/decisions/{dec_id}/reject", json={
            "reason": "Wrong Type",
            "message_id": res_data["message"]["id"]
        })
        assert rej_resp.status_code == 200
        assert rej_resp.json()["review_state"] == "rejected"
        
        # 3. Edit a Task
        edit_resp = await ac.patch(f"/api/v1/tasks/{task_id}", json={
            "task": "Test Sprint 5 Completed",
            "message_id": res_data["message"]["id"]
        })
        assert edit_resp.status_code == 200
        assert edit_resp.json()["task"] == "Test Sprint 5 Completed"
        assert edit_resp.json()["review_state"] == "edited"

    app.dependency_overrides[get_extraction_service] = mock_get_extraction_service


@pytest.mark.anyio
async def test_feedback_detailed_workflows():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create a conversation and message
        conv_resp = await ac.post("/api/v1/conversations", json={"title": "Feedback Detailed"})
        conv_id = conv_resp.json()["id"]
        msg_resp = await ac.post(f"/api/v1/conversations/{conv_id}/messages", json={
            "content": "A message to gather feedback",
            "role": "user"
        })
        msg_id = msg_resp.json()["message"]["id"]

        # 1. Test correct feedback
        fb_resp = await ac.post("/api/v1/extraction/feedback", json={
            "extraction_run_id": msg_id,
            "feedback_type": "correct",
            "comment": "Nice extraction"
        })
        assert fb_resp.status_code == 201
        assert fb_resp.json()["feedback_type"] == "correct"

        # 2. Test incorrect feedback
        fb_resp = await ac.post("/api/v1/extraction/feedback", json={
            "extraction_run_id": msg_id,
            "feedback_type": "incorrect",
            "comment": "Wrong extraction"
        })
        assert fb_resp.status_code == 201
        assert fb_resp.json()["feedback_type"] == "incorrect"

        # 3. Test partial feedback
        fb_resp = await ac.post("/api/v1/extraction/feedback", json={
            "extraction_run_id": msg_id,
            "feedback_type": "partial",
            "comment": "Partial extraction"
        })
        assert fb_resp.status_code == 201
        assert fb_resp.json()["feedback_type"] == "partial"

        # 4. Test invalid feedback type
        fb_resp = await ac.post("/api/v1/extraction/feedback", json={
            "extraction_run_id": msg_id,
            "feedback_type": "invalid_type",
            "comment": "Should fail"
        })
        assert fb_resp.status_code == 400
        assert "Invalid feedback type" in fb_resp.json()["detail"]

        # 5. Test missing extraction_run_id / message id
        fb_resp = await ac.post("/api/v1/extraction/feedback", json={
            "feedback_type": "correct"
        })
        assert fb_resp.status_code == 422  # validation error

        # 6. Test invalid uuid format
        fb_resp = await ac.post("/api/v1/extraction/feedback", json={
            "extraction_run_id": "not-a-uuid",
            "feedback_type": "correct"
        })
        assert fb_resp.status_code == 422  # validation error

        # 7. Test non-existent message ID
        fb_resp = await ac.post("/api/v1/extraction/feedback", json={
            "extraction_run_id": str(uuid.uuid4()),
            "feedback_type": "correct"
        })
        assert fb_resp.status_code == 404
        assert "not found" in fb_resp.json()["detail"]


@pytest.mark.anyio
async def test_feedback_unauthorized():
    # Temporarily remove auth override to test 401/403
    original_override = app.dependency_overrides.get(get_current_user)
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/api/v1/extraction/feedback", json={
                "extraction_run_id": str(uuid.uuid4()),
                "feedback_type": "correct"
            })
            assert response.status_code in [401, 403]
    finally:
        if original_override:
            app.dependency_overrides[get_current_user] = original_override

