# api/schemas.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    HOSPITAL = "hospital"
    BLOOD_BANK = "blood_bank"

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatHistory(BaseModel):
    messages: List[ChatMessage] = Field(default_factory=list)

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    role: UserRole = Field(default=UserRole.ADMIN)
    history: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    
    @validator("message")
    def validate_message_content(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v

class ChatResponse(BaseModel):
    response: str
    suggested_actions: Optional[List[str]] = Field(default_factory=list)
    error: Optional[str] = None
    error_type: Optional[str] = None