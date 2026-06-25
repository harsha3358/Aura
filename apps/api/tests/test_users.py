import pytest
from fastapi import Depends
from httpx import AsyncClient, ASGITransport
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.auth import get_current_user
from app.dependencies import get_db
from app.models.core import User

MOCK_USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")

async def mock_get_current_user_onboarding(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == MOCK_USER_ID))
    user = result.scalars().first()
    if user is None:
        user = User(
            id=MOCK_USER_ID,
            email="onboard@example.com",
            display_name=None,
            timezone="UTC",
            onboarding_completed=False
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        user.onboarding_completed = False
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user

@pytest.fixture
def setup_auth_onboarding():
    app.dependency_overrides[get_current_user] = mock_get_current_user_onboarding
    yield
    app.dependency_overrides.clear()

@pytest.mark.anyio
async def test_onboarding_wizard_endpoint(setup_auth_onboarding):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "display_name": "Harsha",
            "timezone": "Asia/Kolkata",
            "what_are_you_building": "AURA AI Platform",
            "top_goals": ["Ship Sprint 5", "Verify capture loops", ""],
            "biggest_challenges": ["Time constraints", "Ollama latency"]
        }
        response = await ac.post("/api/v1/users/me/onboarding", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "Harsha"
        assert data["timezone"] == "Asia/Kolkata"
        assert data["onboarding_completed"] is True
