from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.extraction import contract


class ExtractionMetadata(BaseModel):
    confidence: float
    reasoning: str

    @field_validator("confidence")
    @classmethod
    def confidence_valid(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class FactItem(BaseModel):
    value: str
    entity: Optional[str] = None
    confidence: float
    category: contract.Fact

    @field_validator("value")
    @classmethod
    def value_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Value cannot be empty")
        return v.strip()

    @field_validator("confidence")
    @classmethod
    def confidence_valid(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class DecisionItem(BaseModel):
    value: str
    entity: Optional[str] = None
    confidence: float
    category: contract.Decision

    @field_validator("value")
    @classmethod
    def value_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Value cannot be empty")
        return v.strip()

    @field_validator("confidence")
    @classmethod
    def confidence_valid(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class ConsideredOptionItem(BaseModel):
    value: str
    entity: Optional[str] = None
    confidence: float
    category: contract.ConsideredOption

    @field_validator("value")
    @classmethod
    def value_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Value cannot be empty")
        return v.strip()

    @field_validator("confidence")
    @classmethod
    def confidence_valid(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class TaskItem(BaseModel):
    value: str
    entity: Optional[str] = None
    confidence: float
    category: contract.Task

    @field_validator("value")
    @classmethod
    def value_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Value cannot be empty")
        return v.strip()

    @field_validator("confidence")
    @classmethod
    def confidence_valid(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class DeadlineItem(BaseModel):
    value: str
    entity: Optional[str] = None
    confidence: float
    category: contract.Deadline

    @field_validator("value")
    @classmethod
    def value_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Value cannot be empty")
        return v.strip()

    @field_validator("confidence")
    @classmethod
    def confidence_valid(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class ContextItem(BaseModel):
    value: str
    entity: Optional[str] = None
    confidence: float
    category: contract.Context

    @field_validator("value")
    @classmethod
    def value_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Value cannot be empty")
        return v.strip()

    @field_validator("confidence")
    @classmethod
    def confidence_valid(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class ExtractionResult(BaseModel):
    facts: List[FactItem] = Field(default_factory=list)
    decisions: List[DecisionItem] = Field(default_factory=list)
    considered_options: List[ConsideredOptionItem] = Field(default_factory=list)
    tasks: List[TaskItem] = Field(default_factory=list)
    deadlines: List[DeadlineItem] = Field(default_factory=list)
    contexts: List[ContextItem] = Field(default_factory=list)
    metadata: ExtractionMetadata
