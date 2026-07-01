from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.auth import get_current_user
from app.models.core import User, ExecutiveBrief, BriefFeedback
from app.services.brief import BriefingService

router = APIRouter()


class BriefResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    brief_date: date
    structured_brief: Dict[str, Any]
    rendered_brief: str
    created_at: datetime

    class Config:
        from_attributes = True


class BriefGenerateRequest(BaseModel):
    target_date: Optional[date] = None


class BriefFeedbackCreate(BaseModel):
    rating: str
    feedback: Optional[str] = None


@router.get("/brief/today", response_model=BriefResponse)
async def get_today_brief(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    today = datetime.utcnow().date()

    stmt = select(ExecutiveBrief).where(
        ExecutiveBrief.user_id == current_user.id, ExecutiveBrief.brief_date == today
    )
    res = await db.execute(stmt)
    brief = res.scalar_one_or_none()

    if not brief:
        service = BriefingService(db)
        brief = await service.generate_brief(current_user, today)
        db.add(brief)
        await db.commit()
        await db.refresh(brief)

    return brief


@router.post(
    "/brief/generate", response_model=BriefResponse, status_code=status.HTTP_201_CREATED
)
async def generate_brief(
    payload: Optional[BriefGenerateRequest] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target_date = payload.target_date if payload else None
    if not target_date:
        target_date = datetime.utcnow().date()

    stmt = select(ExecutiveBrief).where(
        ExecutiveBrief.user_id == current_user.id,
        ExecutiveBrief.brief_date == target_date,
    )
    res = await db.execute(stmt)
    existing_brief = res.scalar_one_or_none()
    if existing_brief:
        await db.delete(existing_brief)
        await db.flush()

    service = BriefingService(db)
    brief = await service.generate_brief(current_user, target_date)
    db.add(brief)
    await db.commit()
    await db.refresh(brief)
    return brief


@router.post("/brief/{brief_id}/feedback", status_code=status.HTTP_201_CREATED)
async def submit_brief_feedback(
    brief_id: uuid.UUID,
    payload: BriefFeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify ownership/existence of the brief
    stmt = select(ExecutiveBrief).where(
        ExecutiveBrief.id == brief_id, ExecutiveBrief.user_id == current_user.id
    )
    res = await db.execute(stmt)
    brief = res.scalar_one_or_none()
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")

    # Create or update feedback record
    fb_stmt = select(BriefFeedback).where(
        BriefFeedback.brief_id == brief_id, BriefFeedback.user_id == current_user.id
    )
    fb_res = await db.execute(fb_stmt)
    existing_fb = fb_res.scalar_one_or_none()

    if existing_fb:
        existing_fb.rating = payload.rating
        existing_fb.feedback = payload.feedback
        existing_fb.created_at = datetime.utcnow()
        db.add(existing_fb)
        db_fb = existing_fb
    else:
        db_fb = BriefFeedback(
            brief_id=brief_id,
            user_id=current_user.id,
            rating=payload.rating,
            feedback=payload.feedback,
        )
        db.add(db_fb)

    await db.commit()
    return {"status": "success", "feedback_id": str(db_fb.id)}
