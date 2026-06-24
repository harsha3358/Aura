from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.auth import get_current_user
from app.models.core import User, Conversation, Message, Fact, Decision, Task, Deadline, Observation
from app.extraction.schemas import ExtractionResult, FactItem, DecisionItem, ConsideredOptionItem, TaskItem, DeadlineItem, ContextItem
from app.extraction.service import ExtractionService

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

class MessagePostResponse(BaseModel):
    message: MessageResponse
    extraction: ExtractionResult

    class Config:
        from_attributes = True

def parse_deadline_date(date_str: str) -> datetime:
    date_str_clean = date_str.lower().strip()
    now = datetime.utcnow()
    if "today" in date_str_clean:
        return now
    if "tomorrow" in date_str_clean:
        return now + timedelta(days=1)
    if "friday" in date_str_clean:
        days_ahead = 4 - now.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return now + timedelta(days=days_ahead)
    try:
        from dateutil import parser
        return parser.parse(date_str)
    except Exception:
        return now + timedelta(days=7)

def get_extraction_service() -> ExtractionService:
    return ExtractionService()

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

@router.post("/conversations/{id}/messages", response_model=MessagePostResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation_message(
    id: uuid.UUID,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    extractor: ExtractionService = Depends(get_extraction_service)
):
    # Verify conversation exists
    stmt = select(Conversation).where(Conversation.id == id, Conversation.user_id == current_user.id)
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # 1. Save the raw user message to the database
    message = Message(
        conversation_id=id,
        role=payload.role,
        content=payload.content
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    
    # 2. Run the extraction service (if message is from user)
    extraction_result = ExtractionResult(
        facts=[], decisions=[], considered_options=[], tasks=[], deadlines=[], contexts=[],
        metadata={"confidence": 1.0, "reasoning": "Extraction skipped for non-user roles."}
    )
    
    if payload.role == "user":
        extraction_result, observations = await extractor.extract_from_message(payload.content)
        
        # 3. Persist valid extractions
        # facts
        for fact in extraction_result.facts:
            db_fact = Fact(
                user_id=current_user.id,
                entity=fact.entity or "general",
                value=fact.value,
                context_id=conversation.context_id,
                source_message_id=message.id,
                confidence=fact.confidence
            )
            db.add(db_fact)
            
        # decisions
        for dec in extraction_result.decisions:
            db_dec = Decision(
                user_id=current_user.id,
                chosen_option=dec.value,
                rejected_options=[],
                context_id=conversation.context_id,
                source_message_id=message.id,
                confidence=dec.confidence
            )
            db.add(db_dec)
            
        # tasks
        for tsk in extraction_result.tasks:
            db_tsk = Task(
                user_id=current_user.id,
                task=tsk.value,
                status="pending",
                context_id=conversation.context_id,
                source_message_id=message.id
            )
            db.add(db_tsk)
            
        # deadlines
        for dl in extraction_result.deadlines:
            due_date = parse_deadline_date(dl.value)
            db_dl = Deadline(
                user_id=current_user.id,
                title=dl.value,
                due_at=due_date,
                context_id=conversation.context_id,
                source_message_id=message.id,
                confidence=dl.confidence
            )
            db.add(db_dl)
            
        # considered_options -> store as observations since no separate table exists
        for opt in extraction_result.considered_options:
            db_obs = Observation(
                user_id=current_user.id,
                raw_type="ConsideredOption",
                payload={"value": opt.value, "entity": opt.entity, "category": opt.category},
                confidence=opt.confidence,
                source_message_id=message.id
            )
            db.add(db_obs)
            
        # contexts -> store as observations since Context Engine is built in next phase
        for ctx in extraction_result.contexts:
            db_obs = Observation(
                user_id=current_user.id,
                raw_type="ContextShift",
                payload={"value": ctx.value, "entity": ctx.entity, "category": ctx.category},
                confidence=ctx.confidence,
                source_message_id=message.id
            )
            db.add(db_obs)
            
        # 4. Persist demoted/rejected observations (sub-threshold items)
        for obs in observations:
            db_obs = Observation(
                user_id=current_user.id,
                raw_type=obs["raw_type"],
                payload=obs["payload"],
                confidence=obs["confidence"],
                source_message_id=message.id
            )
            db.add(db_obs)
            
        await db.commit()

    return {
        "message": message,
        "extraction": extraction_result
    }

@router.post("/messages", response_model=MessagePostResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    extractor: ExtractionService = Depends(get_extraction_service)
):
    if not payload.conversation_id:
        raise HTTPException(status_code=400, detail="conversation_id is required")
        
    return await create_conversation_message(
        id=payload.conversation_id,
        payload=payload,
        db=db,
        current_user=current_user,
        extractor=extractor
    )
