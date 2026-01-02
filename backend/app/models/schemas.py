"""
Pydantic Schemas
Data models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional
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

