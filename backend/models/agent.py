"""Agent request/response data models."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class AgentRequest(BaseModel):
    """Schema for agent request."""

    user_message: str = Field(..., min_length=1, max_length=2000)
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_phone: str = Field(..., min_length=1, max_length=20)
    provider: Optional[str] = Field(default="local", pattern="^(local|groq|gemini)$")
    user_id: Optional[str] = None

    class Config:
        example = {
            "user_message": "السلام عليكم، أريد موبايل أيفون",
            "customer_name": "أحمد علي",
            "customer_phone": "+201001234567",
            "provider": "local",
        }


class AgentResponse(BaseModel):
    """Schema for agent response."""

    response: str
    action: Optional[str] = None  # create_order, get_stock, etc.
    data: Optional[Dict[str, Any]] = None

    class Config:
        example = {
            "response": "السلام عليكم وعليكم السلام، لدينا عدة أيفونات متاحة",
            "action": None,
            "data": None,
        }
