"""Order data models."""

from pydantic import BaseModel, Field
from typing import List, Optional


class OrderLine(BaseModel):
    """Single line in an order."""

    product_id: int
    quantity: int = Field(default=1, ge=1)
    unit_price: float = Field(..., ge=0)
    subtotal: float = Field(..., ge=0)

    class Config:
        example = {
            "product_id": 1,
            "quantity": 1,
            "unit_price": 5000.0,
            "subtotal": 5000.0,
        }


class OrderCreate(BaseModel):
    """Schema for creating an order."""

    customer_id: int
    lines: List[OrderLine] = Field(..., min_items=1)
    notes: Optional[str] = None

    class Config:
        example = {
            "customer_id": 123,
            "lines": [{"product_id": 1, "quantity": 1, "unit_price": 5000.0, "subtotal": 5000.0}],
            "notes": "Please deliver by tomorrow",
        }


class OrderResponse(BaseModel):
    """Schema for order response from Odoo."""

    id: int
    name: str  # SO0001, SO0002, etc.
    customer_id: int
    customer_name: str
    total_amount: float = Field(..., ge=0)
    status: str  # draft, confirmed, shipped, delivered, etc.
    created_at: Optional[str] = None
    lines: List[OrderLine] = []

    class Config:
        example = {
            "id": 1,
            "name": "SO0001",
            "customer_id": 123,
            "customer_name": "أحمد علي",
            "total_amount": 5000.0,
            "status": "confirmed",
            "created_at": "2026-06-17T10:30:00",
            "lines": [{"product_id": 1, "quantity": 1, "unit_price": 5000.0, "subtotal": 5000.0}],
        }
