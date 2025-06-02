# api/schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

now = datetime.now()
date_time = now.strftime("%Y-%m-%dT%H:%M:%S")
class UserRole(str, Enum):
    """
    Enumeration for user roles.
    """
    SYSTEM_ADMIN = "admin"
    BLOOD_BANK_ADMIN = "blood_bank_admin"
    BLOOD_BANK_USER = "blood_bank"
    HOSPITAL_USER = "hospital"
    HOSPITAL_ADMIN = "hospital_admin"

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
    role: UserRole = Field(default=UserRole.SYSTEM_ADMIN)
    company_id: str = Field(default="CMP-RRPZYICLEG")
    user_id: str = Field(default="USR-IHI6SJSYB0")
    session_id:str = Field(default="CSI-H6T63DZ26K")
    timestamp: str = Field(default=date_time) #2023-10-01T12:00:00Z
    
    # history: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    
    @field_validator("message")
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

class FaqRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    role: UserRole = Field(default=UserRole.SYSTEM_ADMIN)
    company_id: str = Field(default="CMP-RRPZYICLEG")
    user_id: str = Field(default="USR-IHI6SJSYB0")

# Response schema
class FaqResponse(BaseModel):
    response: str
    suggested_actions: Optional[List[str]] = Field(default_factory=list)
