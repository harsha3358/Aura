from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.auth import get_current_user
from app.models.core import User, Context, Message, ContextAssignment
from app.extraction.context import ContextClassifier

router = APIRouter()


class ContextCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ContextResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: Optional[str] = None
    confidence: Optional[float] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


def get_context_classifier() -> ContextClassifier:
    return ContextClassifier()


@router.get("/contexts", response_model=List[ContextResponse])
async def list_contexts(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    stmt = (
        select(Context)
        .where(Context.user_id == current_user.id)
        .order_by(Context.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/contexts", response_model=ContextResponse, status_code=status.HTTP_201_CREATED
)
async def create_context(
    payload: ContextCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not payload.name.strip():
        raise HTTPException(status_code=400, detail="Context name cannot be empty")

    context = Context(
        user_id=current_user.id,
        name=payload.name.strip(),
        description=payload.description,
        confidence=1.0,
        is_active=True,
    )
    db.add(context)
    await db.commit()
    await db.refresh(context)
    return context


@router.post("/messages/{id}/classify-context", status_code=status.HTTP_200_OK)
async def classify_message_context(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    classifier: ContextClassifier = Depends(get_context_classifier),
):
    msg_stmt = select(Message).where(Message.id == id)
    msg_res = await db.execute(msg_stmt)
    message = msg_res.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    ctx_stmt = select(Context).where(Context.user_id == current_user.id)
    ctx_res = await db.execute(ctx_stmt)
    existing_contexts = ctx_res.scalars().all()

    res = await classifier.classify(message.content, existing_contexts)

    active_context_id = None
    shift_detected = res.get("shift_detected", False)

    if shift_detected and res.get("new_context"):
        new_ctx_data = res["new_context"]
        new_ctx = Context(
            user_id=current_user.id,
            name=new_ctx_data["name"],
            description=new_ctx_data.get("description"),
            confidence=res.get("confidence", 1.0),
            is_active=True,
        )
        db.add(new_ctx)
        await db.flush()
        active_context_id = new_ctx.id
    elif res.get("matched_context_name"):
        matched_name = res["matched_context_name"].lower().strip()
        matched_ctx = next(
            (c for c in existing_contexts if c.name.lower().strip() == matched_name),
            None,
        )
        if matched_ctx:
            active_context_id = matched_ctx.id

    if active_context_id:
        assignment = ContextAssignment(
            entity_type="message", entity_id=message.id, context_id=active_context_id
        )
        db.add(assignment)
        await db.commit()

    return {
        "message_id": id,
        "context_id": active_context_id,
        "shift_detected": shift_detected,
        "matched_context_name": res.get("matched_context_name"),
        "reasoning": res.get("reasoning"),
    }
