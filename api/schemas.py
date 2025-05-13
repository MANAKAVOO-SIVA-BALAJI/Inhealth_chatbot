# api/schemas.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from enum import Enum

class UserRole(str, Enum):
    """
    Enumeration for user roles.
    """
    ADMIN = "admin"
    HOSPITAL = "hospital"
    BLOOD_BANK = "blood_bank"

class ChatMessage(BaseModel):
    """
    Model representing a chat message.
    """
    role: str
    content: str

class ChatHistory(BaseModel):
    """
    Model representing chat history.
    """
    messages: List[ChatMessage] = Field(default_factory=list)

class ChatRequest(BaseModel):
    """
    Model for validating chat requests.
    """
    message: str = Field(..., min_length=1, max_length=1000)
    role: UserRole = Field(default=UserRole.ADMIN)
    history: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    
    @validator("message")
    def validate_message_content(cls, v):
        """
        Validator to ensure message content is not empty.
        """
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v

class ChatResponse(BaseModel):
    """
    Model for chat response structure.
    """
    response: str
    suggested_actions: Optional[List[str]] = Field(default_factory=list)
    error: Optional[str] = None
    error_type: Optional[str] = None