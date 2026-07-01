import pytest
from httpx import AsyncClient, ASGITransport
import uuid
from datetime import datetime, timedelta
from app.main import app
from app.auth import get_current_user
from app.dependencies import get_db
from app.models.core import User, Context, Project, Task, Deadline, Decision, Fact, Conversation, Message, ExtractionFeedback, ExecutiveBrief, BriefFeedback, KnowledgeReview, Observation, ContextAssignment

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
async def test_briefing_generation_and_retrieval(anyio_backend):
    # Retrieve DB session using helper
    db_gen = get_db()
    db = await anext(db_gen)

    # 1. Setup mock database records
    # Clean up old records for mock user if any
    from sqlalchemy import delete, select
    
    await db.execute(delete(BriefFeedback).where(BriefFeedback.user_id == MOCK_USER_ID))
    await db.execute(delete(ExecutiveBrief).where(ExecutiveBrief.user_id == MOCK_USER_ID))
    await db.execute(delete(ExtractionFeedback).where(ExtractionFeedback.user_id == MOCK_USER_ID))
    await db.execute(delete(KnowledgeReview).where(KnowledgeReview.reviewer_id == MOCK_USER_ID))
    await db.execute(delete(Observation).where(Observation.user_id == MOCK_USER_ID))
    await db.execute(delete(Fact).where(Fact.user_id == MOCK_USER_ID))
    await db.execute(delete(Decision).where(Decision.user_id == MOCK_USER_ID))
    await db.execute(delete(Deadline).where(Deadline.user_id == MOCK_USER_ID))
    await db.execute(delete(Task).where(Task.user_id == MOCK_USER_ID))
    
    # Delete messages referencing mock conversations
    subq = select(Conversation.id).where(Conversation.user_id == MOCK_USER_ID)
    convo_ids = (await db.execute(subq)).scalars().all()
    if convo_ids:
        msg_subq = select(Message.id).where(Message.conversation_id.in_(convo_ids))
        msg_ids = (await db.execute(msg_subq)).scalars().all()
        if msg_ids:
            await db.execute(delete(ContextAssignment).where(
                (ContextAssignment.entity_type == "message") & ContextAssignment.entity_id.in_(msg_ids)
            ))
        await db.execute(delete(Message).where(Message.conversation_id.in_(convo_ids)))
        
    await db.execute(delete(Conversation).where(Conversation.user_id == MOCK_USER_ID))
    await db.execute(delete(Project).where(Project.user_id == MOCK_USER_ID))
    
    # Delete context assignments referencing contexts of this user
    ctx_subq = select(Context.id).where(Context.user_id == MOCK_USER_ID)
    ctx_ids = (await db.execute(ctx_subq)).scalars().all()
    if ctx_ids:
        await db.execute(delete(ContextAssignment).where(ContextAssignment.context_id.in_(ctx_ids)))
        
    await db.execute(delete(Context).where(Context.user_id == MOCK_USER_ID))
    await db.commit()

    # Create Context
    context = Context(
        user_id=MOCK_USER_ID,
        name="Startup Building",
        description="Developing AURA",
        is_active=True
    )
    db.add(context)
    await db.flush()

    # Create Project
    project = Project(
        user_id=MOCK_USER_ID,
        project_name="AURA",
        description="Cognitive Operating System",
        context_id=context.id
    )
    db.add(project)

    # Create Task
    task = Task(
        user_id=MOCK_USER_ID,
        task="Build Executive Brief UI",
        status="pending",
        context_id=context.id
    )
    db.add(task)

    # Create Deadline
    deadline = Deadline(
        user_id=MOCK_USER_ID,
        title="Benchmark Review",
        due_at=datetime.utcnow() + timedelta(days=2),
        context_id=context.id
    )
    db.add(deadline)

    # Create Decision
    decision = Decision(
        user_id=MOCK_USER_ID,
        chosen_option="PostgreSQL selected",
        confidence=1.0,
        context_id=context.id
    )
    db.add(decision)
    await db.commit()

    # 2. Call Brief API using AsyncClient
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Generate Brief
        response = await ac.post("/api/v1/brief/generate")
        assert response.status_code == 201
        data = response.json()
        
        assert "structured_brief" in data
        assert "rendered_brief" in data
        
        structured = data["structured_brief"]
        assert "AURA" in structured["active_projects"]
        assert "Startup Building" in structured["current_contexts"]
        assert "Build Executive Brief UI" in structured["open_tasks"]
        assert "PostgreSQL selected" in structured["recent_decisions"]
        
        rendered = data["rendered_brief"]
        assert "GOOD MORNING TEST USER" in rendered
        assert "Active Project:\n- AURA" in rendered
        assert "Current Context:\n- Startup Building" in rendered
        assert "Open Tasks:\n- Build Executive Brief UI" in rendered

        # Retrieve Today's Brief
        get_response = await ac.get("/api/v1/brief/today")
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["id"] == data["id"]
        assert get_data["rendered_brief"] == data["rendered_brief"]

        # Submit Brief Feedback
        feedback_response = await ac.post(
            f"/api/v1/brief/{data['id']}/feedback",
            json={"rating": "useful", "feedback": "Great brief!"}
        )
        assert feedback_response.status_code == 201
        fb_data = feedback_response.json()
        assert fb_data["status"] == "success"
        assert "feedback_id" in fb_data
