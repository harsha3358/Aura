from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.dependencies import get_db
from app.auth import get_current_user
from app.models.core import User, Fact, Decision, Task, Deadline

router = APIRouter()

# Schema definitions
class FactResponse(BaseModel):
    id: uuid.UUID
    entity: str
    value: str
    confidence: float
    context_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

class DecisionResponse(BaseModel):
    id: uuid.UUID
    chosen_option: str
    confidence: float
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
    context_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TaskUpdatePayload(BaseModel):
    status: Optional[str] = None
    priority: Optional[int] = None

class DeadlineResponse(BaseModel):
    id: uuid.UUID
    title: str
    due_at: datetime
    confidence: Optional[float] = 1.0
    context_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True

# GET Endpoints
@router.get("/facts", response_model=List[FactResponse])
async def list_facts(
    context_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Fact).where(Fact.user_id == current_user.id)
    if context_id:
        stmt = stmt.where(Fact.context_id == context_id)
    stmt = stmt.order_by(Fact.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/decisions", response_model=List[DecisionResponse])
async def list_decisions(
    context_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Decision).where(Decision.user_id == current_user.id)
    if context_id:
        stmt = stmt.where(Decision.context_id == context_id)
    stmt = stmt.order_by(Decision.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    context_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Task).where(Task.user_id == current_user.id)
    if context_id:
        stmt = stmt.where(Task.context_id == context_id)
    stmt = stmt.order_by(Task.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()

@router.patch("/tasks/{id}", response_model=TaskResponse)
async def update_task(
    id: uuid.UUID,
    payload: TaskUpdatePayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify ownership
    stmt = select(Task).where(Task.id == id, Task.user_id == current_user.id)
    res = await db.execute(stmt)
    task = res.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if payload.status is not None:
        task.status = payload.status
    if payload.priority is not None:
        task.priority = payload.priority
        
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task

@router.get("/deadlines", response_model=List[DeadlineResponse])
async def list_deadlines(
    context_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Deadline).where(Deadline.user_id == current_user.id)
    if context_id:
        stmt = stmt.where(Deadline.context_id == context_id)
    stmt = stmt.order_by(Deadline.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()
