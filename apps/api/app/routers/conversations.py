from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.auth import get_current_user
from app.models.core import (
    User, Conversation, Message, Fact, Decision, Task, 
    Deadline, Observation, Context, ContextAssignment
)
from app.extraction.schemas import ExtractionResult
from app.extraction.service import ExtractionService
from app.extraction.context import ContextClassifier
from app.routers.contexts import get_context_classifier

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

class MessageDetailResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    created_at: datetime
    facts: List["SavedFactResponse"] = []
    decisions: List["SavedDecisionResponse"] = []
    tasks: List["SavedTaskResponse"] = []
    deadlines: List["SavedDeadlineResponse"] = []

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: Optional[str]
    context_id: Optional[uuid.UUID] = None
    created_at: datetime
    messages: List[MessageDetailResponse] = []

    class Config:
        from_attributes = True

class SavedFactResponse(BaseModel):
    id: uuid.UUID
    entity: str
    value: str
    confidence: float
    review_state: str

    class Config:
        from_attributes = True

class SavedDecisionResponse(BaseModel):
    id: uuid.UUID
    chosen_option: str
    confidence: float
    review_state: str

    class Config:
        from_attributes = True

class SavedTaskResponse(BaseModel):
    id: uuid.UUID
    task: str
    status: str
    review_state: str
    confidence: float

    class Config:
        from_attributes = True

class SavedDeadlineResponse(BaseModel):
    id: uuid.UUID
    title: str
    due_at: datetime
    confidence: float
    review_state: str

    class Config:
        from_attributes = True

class MessagePostResponse(BaseModel):
    message: MessageResponse
    facts: List[SavedFactResponse] = []
    decisions: List[SavedDecisionResponse] = []
    tasks: List[SavedTaskResponse] = []
    deadlines: List[SavedDeadlineResponse] = []

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

@router.get("/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Conversation).where(Conversation.user_id == current_user.id).order_by(Conversation.created_at.desc())
    res = await db.execute(stmt)
    conversations = res.scalars().all()
    
    results = []
    for conv in conversations:
        msg_stmt = select(Message).where(Message.conversation_id == conv.id).order_by(Message.created_at.asc())
        msg_result = await db.execute(msg_stmt)
        messages = msg_result.scalars().all()
        
        msg_details = []
        for msg in messages:
            facts_stmt = select(Fact).where(Fact.source_message_id == msg.id)
            facts_res = await db.execute(facts_stmt)
            facts = facts_res.scalars().all()
            
            dec_stmt = select(Decision).where(Decision.source_message_id == msg.id)
            dec_res = await db.execute(dec_stmt)
            decisions = dec_res.scalars().all()
            
            tasks_stmt = select(Task).where(Task.source_message_id == msg.id)
            tasks_res = await db.execute(tasks_stmt)
            tasks = tasks_res.scalars().all()
            
            deadlines_stmt = select(Deadline).where(Deadline.source_message_id == msg.id)
            deadlines_res = await db.execute(deadlines_stmt)
            deadlines = deadlines_res.scalars().all()
            
            msg_details.append({
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at,
                "facts": facts,
                "decisions": decisions,
                "tasks": tasks,
                "deadlines": deadlines
            })
            
        results.append({
            "id": conv.id,
            "user_id": conv.user_id,
            "title": conv.title,
            "context_id": conv.context_id,
            "created_at": conv.created_at,
            "messages": msg_details
        })
        
    return results

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
    
    msg_details = []
    for msg in messages:
        facts_stmt = select(Fact).where(Fact.source_message_id == msg.id)
        facts_res = await db.execute(facts_stmt)
        facts = facts_res.scalars().all()
        
        dec_stmt = select(Decision).where(Decision.source_message_id == msg.id)
        dec_res = await db.execute(dec_stmt)
        decisions = dec_res.scalars().all()
        
        tasks_stmt = select(Task).where(Task.source_message_id == msg.id)
        tasks_res = await db.execute(tasks_stmt)
        tasks = tasks_res.scalars().all()
        
        deadlines_stmt = select(Deadline).where(Deadline.source_message_id == msg.id)
        deadlines_res = await db.execute(deadlines_stmt)
        deadlines = deadlines_res.scalars().all()
        
        msg_details.append({
            "id": msg.id,
            "conversation_id": msg.conversation_id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at,
            "facts": facts,
            "decisions": decisions,
            "tasks": tasks,
            "deadlines": deadlines
        })
    
    return {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "context_id": conversation.context_id,
        "created_at": conversation.created_at,
        "messages": msg_details
    }

@router.post("/conversations/{id}/messages", response_model=MessagePostResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation_message(
    id: uuid.UUID,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    extractor: ExtractionService = Depends(get_extraction_service),
    classifier: ContextClassifier = Depends(get_context_classifier)
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
    
    extraction_result = ExtractionResult(
        facts=[], decisions=[], considered_options=[], tasks=[], deadlines=[], contexts=[],
        metadata={"confidence": 1.0, "reasoning": "Extraction skipped for non-user roles."}
    )
    
    if payload.role == "user":
        # 1. Classify Context / Detect Shift
        ctx_stmt = select(Context).where(Context.user_id == current_user.id)
        ctx_res = await db.execute(ctx_stmt)
        existing_contexts = ctx_res.scalars().all()
        
        classification = await classifier.classify(payload.content, existing_contexts)
        
        active_context_id = conversation.context_id
        shift_detected = classification.get("shift_detected", False)
        
        if shift_detected and classification.get("new_context"):
            new_ctx_data = classification["new_context"]
            new_ctx = Context(
                user_id=current_user.id,
                name=new_ctx_data["name"],
                description=new_ctx_data.get("description"),
                confidence=classification.get("confidence", 1.0),
                is_active=True
            )
            db.add(new_ctx)
            await db.flush()
            active_context_id = new_ctx.id
            conversation.context_id = active_context_id
            db.add(conversation)
        elif classification.get("matched_context_name"):
            matched_name = classification["matched_context_name"].lower().strip()
            matched_ctx = next((c for c in existing_contexts if c.name.lower().strip() == matched_name), None)
            if matched_ctx:
                active_context_id = matched_ctx.id
                if conversation.context_id != active_context_id:
                    conversation.context_id = active_context_id
                    db.add(conversation)

        if active_context_id:
            assignment = ContextAssignment(
                entity_type="message",
                entity_id=message.id,
                context_id=active_context_id
            )
            db.add(assignment)
            
        # 2. Run Extraction Engine
        extraction_result, observations = await extractor.extract_from_message(payload.content)
        
        # 3. Persist valid extractions and link to active context
        saved_facts = []
        for fact in extraction_result.facts:
            db_fact = Fact(
                user_id=current_user.id,
                entity=fact.entity or "general",
                value=fact.value,
                context_id=active_context_id,
                source_message_id=message.id,
                source_conversation_id=id,
                extractor_version="v0.1",
                review_state="pending",
                confidence=fact.confidence
            )
            db.add(db_fact)
            saved_facts.append(db_fact)
            
        saved_decisions = []
        for dec in extraction_result.decisions:
            db_dec = Decision(
                user_id=current_user.id,
                chosen_option=dec.value,
                rejected_options=[],
                context_id=active_context_id,
                source_message_id=message.id,
                source_conversation_id=id,
                extractor_version="v0.1",
                review_state="pending",
                confidence=dec.confidence
            )
            db.add(db_dec)
            saved_decisions.append(db_dec)
            
        saved_tasks = []
        for tsk in extraction_result.tasks:
            db_tsk = Task(
                user_id=current_user.id,
                task=tsk.value,
                status="pending",
                context_id=active_context_id,
                source_message_id=message.id,
                source_conversation_id=id,
                extractor_version="v0.1",
                review_state="pending",
                confidence=tsk.confidence
            )
            db.add(db_tsk)
            saved_tasks.append(db_tsk)
            
        saved_deadlines = []
        for dl in extraction_result.deadlines:
            due_date = parse_deadline_date(dl.value)
            db_dl = Deadline(
                user_id=current_user.id,
                title=dl.value,
                due_at=due_date,
                context_id=active_context_id,
                source_message_id=message.id,
                source_conversation_id=id,
                extractor_version="v0.1",
                review_state="pending",
                confidence=dl.confidence
            )
            db.add(db_dl)
            saved_deadlines.append(db_dl)
            
        for opt in extraction_result.considered_options:
            db_obs = Observation(
                user_id=current_user.id,
                raw_type="ConsideredOption",
                payload={"value": opt.value, "entity": opt.entity, "category": opt.category},
                confidence=opt.confidence,
                source_message_id=message.id
            )
            db.add(db_obs)
            
        for ctx in extraction_result.contexts:
            db_obs = Observation(
                user_id=current_user.id,
                raw_type="ContextShift",
                payload={"value": ctx.value, "entity": ctx.entity, "category": ctx.category},
                confidence=ctx.confidence,
                source_message_id=message.id
            )
            db.add(db_obs)
            
        for obs in observations:
            db_obs = Observation(
                user_id=current_user.id,
                raw_type=obs["raw_type"],
                payload=obs["payload"],
                confidence=obs["confidence"],
                source_message_id=message.id
            )
            db.add(db_obs)
            
        await db.flush()
        
        # Build responses with populated database IDs
        facts_res = [
            {
                "id": f.id,
                "entity": f.entity,
                "value": f.value,
                "confidence": f.confidence,
                "review_state": f.review_state
            }
            for f in saved_facts
        ]
        decisions_res = [
            {
                "id": d.id,
                "chosen_option": d.chosen_option,
                "confidence": d.confidence,
                "review_state": d.review_state
            }
            for d in saved_decisions
        ]
        tasks_res = [
            {
                "id": t.id,
                "task": t.task,
                "status": t.status,
                "review_state": t.review_state,
                "confidence": t.confidence
            }
            for t in saved_tasks
        ]
        deadlines_res = [
            {
                "id": dl.id,
                "title": dl.title,
                "due_at": dl.due_at,
                "confidence": dl.confidence,
                "review_state": dl.review_state
            }
            for dl in saved_deadlines
        ]
        
        await db.commit()

    else:
        facts_res = []
        decisions_res = []
        tasks_res = []
        deadlines_res = []
        await db.commit()

    return {
        "message": message,
        "facts": facts_res,
        "decisions": decisions_res,
        "tasks": tasks_res,
        "deadlines": deadlines_res
    }

@router.post("/messages", response_model=MessagePostResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    extractor: ExtractionService = Depends(get_extraction_service),
    classifier: ContextClassifier = Depends(get_context_classifier)
):
    if not payload.conversation_id:
        raise HTTPException(status_code=400, detail="conversation_id is required")
        
    return await create_conversation_message(
        id=payload.conversation_id,
        payload=payload,
        db=db,
        current_user=current_user,
        extractor=extractor,
        classifier=classifier
    )
