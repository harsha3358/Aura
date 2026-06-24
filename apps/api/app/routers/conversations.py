from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.auth import get_current_user
from app.models.core import User, Conversation, Message

router = APIRouter()

class ConversationCreate(BaseModel):
    title: Optional[str] = None
    context_id: Optional[uuid.UUID] = None

class MessageCreate(BaseModel):
    content: str
    role: str = "user"
    conversation_id: Optional[uuid.UUID] = None

class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: Optional[str]
    context_id: Optional[uuid.UUID] = None
    created_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True

@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = Conversation(
        user_id=current_user.id,
        title=payload.title or "New Conversation",
        context_id=payload.context_id
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "context_id": conversation.context_id,
        "created_at": conversation.created_at,
        "messages": []
    }

@router.get("/conversations/{id}", response_model=ConversationResponse)
async def get_conversation(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Conversation).where(Conversation.id == id, Conversation.user_id == current_user.id)
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    msg_stmt = select(Message).where(Message.conversation_id == id).order_by(Message.created_at.asc())
    msg_result = await db.execute(msg_stmt)
    messages = msg_result.scalars().all()
    
    return {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "context_id": conversation.context_id,
        "created_at": conversation.created_at,
        "messages": messages
    }

@router.post("/conversations/{id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation_message(
    id: uuid.UUID,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Conversation).where(Conversation.id == id, Conversation.user_id == current_user.id)
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    message = Message(
        conversation_id=id,
        role=payload.role,
        content=payload.content
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message

@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not payload.conversation_id:
        raise HTTPException(status_code=400, detail="conversation_id is required")
        
    return await create_conversation_message(
        id=payload.conversation_id,
        payload=payload,
        db=db,
        current_user=current_user
    )
