from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.auth import get_current_user
from app.models.core import (
    User,
    Fact,
    Decision,
    Task,
    Deadline,
    KnowledgeReview,
    ExtractionFeedback,
)

router = APIRouter()


# Schema definitions
class FactResponse(BaseModel):
    id: uuid.UUID
    entity: str
    value: str
    confidence: float
    review_state: str
    context_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DecisionResponse(BaseModel):
    id: uuid.UUID
    chosen_option: str
    confidence: float
    review_state: str
    context_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    id: uuid.UUID
    task: str
    status: Optional[str] = "pending"
    priority: Optional[int] = 1
    review_state: str
    confidence: float
    context_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DeadlineResponse(BaseModel):
    id: uuid.UUID
    title: str
    due_at: datetime
    confidence: Optional[float] = 1.0
    review_state: str
    context_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RejectPayload(BaseModel):
    reason: str
    message_id: Optional[uuid.UUID] = None


class FactPatchPayload(BaseModel):
    entity: Optional[str] = None
    value: Optional[str] = None
    message_id: Optional[uuid.UUID] = None


class DecisionPatchPayload(BaseModel):
    chosen_option: Optional[str] = None
    message_id: Optional[uuid.UUID] = None


class TaskPatchPayload(BaseModel):
    task: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    message_id: Optional[uuid.UUID] = None


class DeadlinePatchPayload(BaseModel):
    title: Optional[str] = None
    due_at: Optional[datetime] = None
    message_id: Optional[uuid.UUID] = None


# GET Endpoints (filtering out rejected items)
@router.get("/facts", response_model=List[FactResponse])
async def list_facts(
    context_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Fact).where(
        Fact.user_id == current_user.id, Fact.review_state != "rejected"
    )
    if context_id:
        stmt = stmt.where(Fact.context_id == context_id)
    stmt = stmt.order_by(Fact.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/decisions", response_model=List[DecisionResponse])
async def list_decisions(
    context_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Decision).where(
        Decision.user_id == current_user.id, Decision.review_state != "rejected"
    )
    if context_id:
        stmt = stmt.where(Decision.context_id == context_id)
    stmt = stmt.order_by(Decision.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    context_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Task).where(
        Task.user_id == current_user.id, Task.review_state != "rejected"
    )
    if context_id:
        stmt = stmt.where(Task.context_id == context_id)
    stmt = stmt.order_by(Task.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/deadlines", response_model=List[DeadlineResponse])
async def list_deadlines(
    context_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Deadline).where(
        Deadline.user_id == current_user.id, Deadline.review_state != "rejected"
    )
    if context_id:
        stmt = stmt.where(Deadline.context_id == context_id)
    stmt = stmt.order_by(Deadline.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()


# APPROVE Endpoints
@router.post("/facts/{id}/approve")
async def approve_fact(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Fact).where(Fact.id == id, Fact.user_id == current_user.id)
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Fact not found")
    item.review_state = "approved"
    db.add(item)
    await db.commit()
    return {"status": "success", "id": str(id), "review_state": "approved"}


@router.post("/decisions/{id}/approve")
async def approve_decision(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Decision).where(
        Decision.id == id, Decision.user_id == current_user.id
    )
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Decision not found")
    item.review_state = "approved"
    db.add(item)
    await db.commit()
    return {"status": "success", "id": str(id), "review_state": "approved"}


@router.post("/tasks/{id}/approve")
async def approve_task(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Task).where(Task.id == id, Task.user_id == current_user.id)
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Task not found")
    item.review_state = "approved"
    db.add(item)
    await db.commit()
    return {"status": "success", "id": str(id), "review_state": "approved"}


@router.post("/deadlines/{id}/approve")
async def approve_deadline(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Deadline).where(
        Deadline.id == id, Deadline.user_id == current_user.id
    )
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Deadline not found")
    item.review_state = "approved"
    db.add(item)
    await db.commit()
    return {"status": "success", "id": str(id), "review_state": "approved"}


# REJECT Endpoints (Central review table & incorrect feedback logging)
@router.post("/facts/{id}/reject")
async def reject_fact(
    id: uuid.UUID,
    payload: RejectPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Fact).where(Fact.id == id, Fact.user_id == current_user.id)
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Fact not found")

    item.review_state = "rejected"
    db.add(item)

    review = KnowledgeReview(
        entity_type="fact",
        entity_id=id,
        review_type="incorrect",
        rejection_reason=payload.reason,
        reviewer_id=current_user.id,
    )
    db.add(review)

    if payload.message_id:
        fb = ExtractionFeedback(
            extraction_run_id=payload.message_id,
            user_id=current_user.id,
            feedback_type="incorrect",
            comment=f"Rejected Fact: {payload.reason}",
        )
        db.add(fb)

    await db.commit()
    return {"status": "success", "id": str(id), "review_state": "rejected"}


@router.post("/decisions/{id}/reject")
async def reject_decision(
    id: uuid.UUID,
    payload: RejectPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Decision).where(
        Decision.id == id, Decision.user_id == current_user.id
    )
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Decision not found")

    item.review_state = "rejected"
    db.add(item)

    review = KnowledgeReview(
        entity_type="decision",
        entity_id=id,
        review_type="incorrect",
        rejection_reason=payload.reason,
        reviewer_id=current_user.id,
    )
    db.add(review)

    if payload.message_id:
        fb = ExtractionFeedback(
            extraction_run_id=payload.message_id,
            user_id=current_user.id,
            feedback_type="incorrect",
            comment=f"Rejected Decision: {payload.reason}",
        )
        db.add(fb)

    await db.commit()
    return {"status": "success", "id": str(id), "review_state": "rejected"}


@router.post("/tasks/{id}/reject")
async def reject_task(
    id: uuid.UUID,
    payload: RejectPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Task).where(Task.id == id, Task.user_id == current_user.id)
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Task not found")

    item.review_state = "rejected"
    item.status = "rejected"
    db.add(item)

    review = KnowledgeReview(
        entity_type="task",
        entity_id=id,
        review_type="incorrect",
        rejection_reason=payload.reason,
        reviewer_id=current_user.id,
    )
    db.add(review)

    if payload.message_id:
        fb = ExtractionFeedback(
            extraction_run_id=payload.message_id,
            user_id=current_user.id,
            feedback_type="incorrect",
            comment=f"Rejected Task: {payload.reason}",
        )
        db.add(fb)

    await db.commit()
    return {"status": "success", "id": str(id), "review_state": "rejected"}


@router.post("/deadlines/{id}/reject")
async def reject_deadline(
    id: uuid.UUID,
    payload: RejectPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Deadline).where(
        Deadline.id == id, Deadline.user_id == current_user.id
    )
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Deadline not found")

    item.review_state = "rejected"
    db.add(item)

    review = KnowledgeReview(
        entity_type="deadline",
        entity_id=id,
        review_type="incorrect",
        rejection_reason=payload.reason,
        reviewer_id=current_user.id,
    )
    db.add(review)

    if payload.message_id:
        fb = ExtractionFeedback(
            extraction_run_id=payload.message_id,
            user_id=current_user.id,
            feedback_type="incorrect",
            comment=f"Rejected Deadline: {payload.reason}",
        )
        db.add(fb)

    await db.commit()
    return {"status": "success", "id": str(id), "review_state": "rejected"}


# EDIT/PATCH Endpoints
@router.patch("/facts/{id}", response_model=FactResponse)
async def update_fact(
    id: uuid.UUID,
    payload: FactPatchPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Fact).where(Fact.id == id, Fact.user_id == current_user.id)
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Fact not found")

    edited = False
    if payload.entity is not None and payload.entity != item.entity:
        item.entity = payload.entity
        edited = True
    if payload.value is not None and payload.value != item.value:
        item.value = payload.value
        edited = True

    if edited:
        item.review_state = "edited"
        db.add(item)

        review = KnowledgeReview(
            entity_type="fact",
            entity_id=id,
            review_type="partial",
            reviewer_id=current_user.id,
        )
        db.add(review)

        if payload.message_id:
            fb = ExtractionFeedback(
                extraction_run_id=payload.message_id,
                user_id=current_user.id,
                feedback_type="partial",
                comment=f"Edited Fact: {item.value}",
            )
            db.add(fb)

    await db.commit()
    await db.refresh(item)
    return item


@router.patch("/decisions/{id}", response_model=DecisionResponse)
async def update_decision(
    id: uuid.UUID,
    payload: DecisionPatchPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Decision).where(
        Decision.id == id, Decision.user_id == current_user.id
    )
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Decision not found")

    edited = False
    if (
        payload.chosen_option is not None
        and payload.chosen_option != item.chosen_option
    ):
        item.chosen_option = payload.chosen_option
        edited = True

    if edited:
        item.review_state = "edited"
        db.add(item)

        review = KnowledgeReview(
            entity_type="decision",
            entity_id=id,
            review_type="partial",
            reviewer_id=current_user.id,
        )
        db.add(review)

        if payload.message_id:
            fb = ExtractionFeedback(
                extraction_run_id=payload.message_id,
                user_id=current_user.id,
                feedback_type="partial",
                comment=f"Edited Decision: {item.chosen_option}",
            )
            db.add(fb)

    await db.commit()
    await db.refresh(item)
    return item


@router.patch("/tasks/{id}", response_model=TaskResponse)
async def update_task(
    id: uuid.UUID,
    payload: TaskPatchPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Task).where(Task.id == id, Task.user_id == current_user.id)
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Task not found")

    edited = False
    if payload.task is not None and payload.task != item.task:
        item.task = payload.task
        edited = True
    if payload.status is not None and payload.status != item.status:
        item.status = payload.status
        # Note: changing status to 'completed' or 'pending' doesn't mean edit feedback.
    if payload.priority is not None and payload.priority != item.priority:
        item.priority = payload.priority

    if edited:
        item.review_state = "edited"
        db.add(item)

        review = KnowledgeReview(
            entity_type="task",
            entity_id=id,
            review_type="partial",
            reviewer_id=current_user.id,
        )
        db.add(review)

        if payload.message_id:
            fb = ExtractionFeedback(
                extraction_run_id=payload.message_id,
                user_id=current_user.id,
                feedback_type="partial",
                comment=f"Edited Task: {item.task}",
            )
            db.add(fb)
    else:
        # If not edited in text but priority/status changed, just save the object
        db.add(item)

    await db.commit()
    await db.refresh(item)
    return item


@router.patch("/deadlines/{id}", response_model=DeadlineResponse)
async def update_deadline(
    id: uuid.UUID,
    payload: DeadlinePatchPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Deadline).where(
        Deadline.id == id, Deadline.user_id == current_user.id
    )
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Deadline not found")

    edited = False
    if payload.title is not None and payload.title != item.title:
        item.title = payload.title
        edited = True
    if payload.due_at is not None and payload.due_at != item.due_at:
        item.due_at = payload.due_at
        edited = True

    if edited:
        item.review_state = "edited"
        db.add(item)

        review = KnowledgeReview(
            entity_type="deadline",
            entity_id=id,
            review_type="partial",
            reviewer_id=current_user.id,
        )
        db.add(review)

        if payload.message_id:
            fb = ExtractionFeedback(
                extraction_run_id=payload.message_id,
                user_id=current_user.id,
                feedback_type="partial",
                comment=f"Edited Deadline: {item.title}",
            )
            db.add(fb)

    await db.commit()
    await db.refresh(item)
    return item
