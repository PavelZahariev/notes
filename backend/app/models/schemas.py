"""
Pydantic Schemas
Data models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class NoteBase(BaseModel):
    title: str
    content: str
    tags: Optional[list[str]] = []

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[list[str]] = None

class Note(NoteBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ReminderBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: datetime
    completed: bool = False

class ReminderCreate(ReminderBase):
    pass

class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None

class Reminder(ReminderBase):
    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class VoiceCommand(BaseModel):
    text: str
    audio_url: Optional[str] = None

class VoiceResponse(BaseModel):
    response: str
    intent: str
    entities: dict = {}

class TranscriptionResponse(BaseModel):
    text: str
    language: str

# Agent Intelligence Schemas
class AgentResponse(BaseModel):
    """Structured output from the AI agent for intent classification and extraction"""
    intent: Literal['NOTE', 'REMINDER', 'QUERY']
    content: str = Field(description="The cleaned-up version of the transcript")
    category: str = Field(description="Auto-categorized topic (e.g., 'Work', 'Personal', 'Health')")
    due_date: Optional[str] = Field(default=None, description="ISO format datetime string for reminders")
    is_complete: bool = Field(description="False if the instruction is missing details")
    clarification_question: Optional[str] = Field(default=None, description="Question to ask if is_complete is False")

class AgentClassifyRequest(BaseModel):
    """Request schema for agent classification endpoint"""
    text: str = Field(description="The transcribed text to classify")
    context_vars: Optional[dict] = Field(default_factory=dict, description="Global context variables")


