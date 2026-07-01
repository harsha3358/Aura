from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.auth import get_current_user
from app.models.core import User, Message, ExtractionFeedback

router = APIRouter()


class FeedbackCreate(BaseModel):
    extraction_run_id: uuid.UUID
    feedback_type: str
    comment: Optional[str] = None


@router.post("/extraction/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    payload: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.feedback_type not in ["correct", "incorrect", "partial"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid feedback type. Must be 'correct', 'incorrect', or 'partial'",
        )

    msg_stmt = select(Message).where(Message.id == payload.extraction_run_id)
    msg_res = await db.execute(msg_stmt)
    msg = msg_res.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="Extraction run message not found")

    feedback = ExtractionFeedback(
        extraction_run_id=payload.extraction_run_id,
        user_id=current_user.id,
        feedback_type=payload.feedback_type,
        comment=payload.comment,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    return {
        "id": feedback.id,
        "extraction_run_id": feedback.extraction_run_id,
        "feedback_type": feedback.feedback_type,
        "comment": feedback.comment,
        "created_at": feedback.created_at,
    }
