from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.dependencies import get_db
from app.models.core import User, Context, Project, Task, Observation

router = APIRouter()

class OnboardingPayload(BaseModel):
    display_name: str
    timezone: str
    what_are_you_building: str
    top_goals: List[str]
    biggest_challenges: List[str]

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "display_name": current_user.display_name,
        "timezone": current_user.timezone,
        "onboarding_completed": current_user.onboarding_completed
    }

@router.post("/me/onboarding")
async def submit_onboarding(
    payload: OnboardingPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.onboarding_completed:
        raise HTTPException(status_code=400, detail="Onboarding has already been completed.")

    # 1. Update user info
    current_user.display_name = payload.display_name
    current_user.timezone = payload.timezone
    current_user.onboarding_completed = True
    db.add(current_user)

    # 2. Create default Context
    context = Context(
        user_id=current_user.id,
        name="General focus",
        description=f"Initial context created during onboarding for building {payload.what_are_you_building}",
        confidence=1.0,
        is_active=True
    )
    db.add(context)
    await db.flush() # Get context.id

    # 3. Create Project
    project = Project(
        user_id=current_user.id,
        project_name=payload.what_are_you_building,
        description=f"Primary project created during onboarding: {payload.what_are_you_building}",
        status="active",
        context_id=context.id
    )
    db.add(project)
    await db.flush() # Get project.id

    # 4. Map goals -> Tasks
    for goal in payload.top_goals:
        if goal.strip():
            task = Task(
                user_id=current_user.id,
                task=goal.strip(),
                status="pending",
                priority=1,
                context_id=context.id,
                project_id=project.id,
                confidence=1.0,
                extractor_version="onboarding"
            )
            db.add(task)

    # 5. Map challenges -> Observations
    for challenge in payload.biggest_challenges:
        if challenge.strip():
            obs = Observation(
                user_id=current_user.id,
                raw_type="Challenge",
                payload={"value": challenge.strip()},
                confidence=1.0,
                review_status="pending"
            )
            db.add(obs)

    await db.commit()
    await db.refresh(current_user)

    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "display_name": current_user.display_name,
        "timezone": current_user.timezone,
        "onboarding_completed": current_user.onboarding_completed
    }

