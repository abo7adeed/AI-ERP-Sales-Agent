"""Customer data models."""

from pydantic import BaseModel, Field
from typing import Optional


class CustomerCreate(BaseModel):
    """Schema for creating a customer."""

    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=1, max_length=20)
    email: Optional[str] = Field(None, max_length=255)

    class Config:
        example = {"name": "أحمد علي", "phone": "+201001234567", "email": "ahmed@example.com"}


class CustomerResponse(BaseModel):
    """Schema for customer response from Odoo."""

    id: int
    name: str
    phone: str
    email: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        example = {
            "id": 123,
            "name": "أحمد علي",
            "phone": "+201001234567",
            "email": "ahmed@example.com",
            "created_at": "2026-06-17T10:30:00",
        }
