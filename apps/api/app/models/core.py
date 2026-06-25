from datetime import datetime
import uuid
from sqlalchemy import Column, String, Boolean, Float, Integer, ForeignKey, DateTime, Text, Date, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False)
    display_name = Column(String)
    timezone = Column(String, default="UTC")
    onboarding_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Context(Base):
    __tablename__ = "contexts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    confidence = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    user = relationship("User")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    project_name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String)
    context_id = Column(UUID(as_uuid=True), ForeignKey("contexts.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User")
    context = relationship("Context")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String)
    context_id = Column(UUID(as_uuid=True), ForeignKey("contexts.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Fact(Base):
    __tablename__ = "facts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    entity = Column(String, nullable=False)
    value = Column(String, nullable=False)
    context_id = Column(UUID(as_uuid=True), ForeignKey("contexts.id"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    source_message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    source_conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    extractor_version = Column(String, default="v0.1")
    review_state = Column(String, default="pending")
    confidence = Column(Float, nullable=False)
    embedding = Column(Vector(768))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    superseded_by = Column(UUID(as_uuid=True), ForeignKey("facts.id"))

class Decision(Base):
    __tablename__ = "decisions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    chosen_option = Column(String, nullable=False)
    rejected_options = Column(JSONB, default=list)
    reason = Column(Text)
    context_id = Column(UUID(as_uuid=True), ForeignKey("contexts.id"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    source_message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    source_conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    extractor_version = Column(String, default="v0.1")
    review_state = Column(String, default="pending")
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    task = Column(String, nullable=False)
    status = Column(String)
    priority = Column(Integer)
    deadline = Column(DateTime(timezone=True))
    context_id = Column(UUID(as_uuid=True), ForeignKey("contexts.id"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    source_message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    source_conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    extractor_version = Column(String, default="v0.1")
    review_state = Column(String, default="pending")
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Deadline(Base):
    __tablename__ = "deadlines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String, nullable=False)
    due_at = Column(DateTime(timezone=True), nullable=False)
    context_id = Column(UUID(as_uuid=True), ForeignKey("contexts.id"))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"))
    source_message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    source_conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    extractor_version = Column(String, default="v0.1")
    review_state = Column(String, default="pending")
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Observation(Base):
    __tablename__ = "observations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    raw_type = Column(String)
    payload = Column(JSONB)
    confidence = Column(Float)
    source_message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"))
    review_status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class ExtractionFeedback(Base):
    __tablename__ = "extraction_feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    extraction_run_id = Column(UUID(as_uuid=True), ForeignKey("messages.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    feedback_type = Column(String, nullable=False) # correct, incorrect, partial
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    user = relationship("User")
    message = relationship("Message", foreign_keys=[extraction_run_id])

class ContextAssignment(Base):
    __tablename__ = "context_assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String, nullable=False) # e.g. "message", "fact", "task"
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    context_id = Column(UUID(as_uuid=True), ForeignKey("contexts.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    context = relationship("Context")

class ExecutiveBrief(Base):
    __tablename__ = "executive_briefs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    brief_date = Column(Date, nullable=False)
    structured_brief = Column(JSONB, nullable=False)
    rendered_brief = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    user = relationship("User")
    feedbacks = relationship("BriefFeedback", back_populates="brief", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("user_id", "brief_date", name="uq_user_brief_date"),
    )

class BriefFeedback(Base):
    __tablename__ = "brief_feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brief_id = Column(UUID(as_uuid=True), ForeignKey("executive_briefs.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    rating = Column(String, nullable=False) # e.g. "useful", "neutral", "not_useful"
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    user = relationship("User")
    brief = relationship("ExecutiveBrief", back_populates="feedbacks")

class KnowledgeReview(Base):
    __tablename__ = "knowledge_reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String, nullable=False) # 'fact', 'decision', 'task', 'deadline'
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    review_type = Column(String, nullable=False) # 'incorrect', 'partial'
    rejection_reason = Column(String) # 'Wrong Type', 'Wrong Value', 'Incomplete', 'Hallucinated', 'Duplicate'
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    reviewer = relationship("User")
