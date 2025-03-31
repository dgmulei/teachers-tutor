"""
Data models for the AI Teaching Assistant Platform.
Uses Pydantic for data validation and serialization.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, EmailStr, UUID4


class User(BaseModel):
    """User model representing a teacher or administrator."""
    id: UUID4
    email: EmailStr
    full_name: str
    school_id: Optional[UUID4] = None
    role: str = "teacher"
    created_at: datetime
    last_login: Optional[datetime] = None


class School(BaseModel):
    """School model representing an educational institution."""
    id: UUID4
    name: str
    subscription_tier: str = "basic"
    max_users: int = 10
    created_at: datetime


class Document(BaseModel):
    """Document model representing an uploaded curriculum document."""
    id: UUID4
    user_id: UUID4
    assistant_id: Optional[UUID4] = None
    filename: str
    file_type: str
    file_size: int
    openai_file_id: str
    status: str = "processing"
    created_at: datetime


class Assistant(BaseModel):
    """Assistant model representing an AI teaching assistant."""
    id: UUID4
    user_id: UUID4
    name: str
    description: Optional[str] = None
    openai_assistant_id: str
    created_at: datetime
    last_used: Optional[datetime] = None


class ChatThread(BaseModel):
    """Chat thread model representing a conversation with an assistant."""
    id: UUID4
    assistant_id: UUID4
    user_id: UUID4
    name: Optional[str] = None
    openai_thread_id: str
    created_at: datetime
    last_message_at: datetime


class ChatMessage(BaseModel):
    """Chat message model representing a message in a chat thread."""
    id: UUID4
    thread_id: UUID4
    role: str  # "user" or "assistant"
    content: str
    created_at: datetime


# Request and Response Models

class UserCreate(BaseModel):
    """Model for creating a new user."""
    email: EmailStr
    password: str
    full_name: str
    school_id: Optional[UUID4] = None


class UserLogin(BaseModel):
    """Model for user login."""
    email: EmailStr
    password: str


class AssistantCreate(BaseModel):
    """Model for creating a new assistant."""
    name: str
    description: Optional[str] = None


class ThreadCreate(BaseModel):
    """Model for creating a new chat thread."""
    assistant_id: UUID4
    name: Optional[str] = None


class MessageCreate(BaseModel):
    """Model for creating a new message."""
    content: str


class ApiResponse(BaseModel):
    """Generic API response model."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
