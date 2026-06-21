"""API request/response data models."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ChatRequest(BaseModel):
    """Schema for /api/chat endpoint."""

    message: str = Field(..., min_length=1, max_length=2000)
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_phone: str = Field(..., min_length=1, max_length=20)
    provider: Optional[str] = Field(default="local", pattern="^(local|groq|gemini)$")

    class Config:
        example = {
            "message": "السلام عليكم، أريد موبايل أيفون",
            "customer_name": "أحمد علي",
            "customer_phone": "+201001234567",
            "provider": "local",
        }


class ChatResponse(BaseModel):
    """Schema for /api/chat response."""

    response: str
    status: str = "success"

    class Config:
        example = {
            "response": "السلام عليكم وعليكم السلام، لدينا عدة أيفونات متاحة",
            "status": "success",
        }


class WebhookResponse(BaseModel):
    """Schema for Telegram webhook response."""

    status: str = Field(..., pattern="^(success|error|ignored)$")
    detail: Optional[str] = None

    class Config:
        example = {"status": "success", "detail": None}
