"""Product data models."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class Product(BaseModel):
    """Product from Odoo inventory."""

    id: int
    name: str
    list_price: float = Field(..., ge=0)
    qty_available: int = Field(default=0, ge=0)
    description_sale: Optional[str] = None
    display_specs: Optional[str] = None
    brand_id: Optional[int] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    processor: Optional[str] = None
    camera: Optional[str] = None
    battery: Optional[str] = None
    color: Optional[str] = None
    sku: Optional[str] = None
    image_url: Optional[str] = None

    @field_validator('description_sale', 'display_specs', 'ram', 'storage', 
                     'processor', 'camera', 'battery', 'color', 'sku', 'image_url', 
                     mode='before')
    def handle_odoo_false_values(cls, value):
        if value is False or value is None:
            return ""
        return str(value)

    @field_validator('brand_id', mode='before')
    def handle_odoo_false_int(cls, value):
        if value is False or value is None:
            return None
        return int(value)

    class Config:
        example = {
            "id": 1,
            "name": "iPhone 14 Pro",
            "list_price": 5000.0,
            "qty_available": 10,
            "description_sale": "Latest iPhone with A16 chip",
            "sku": "IPHONE-14-PRO",
            "image_url": "https://example.com/iphone14.jpg",
        }


class ProductSearch(BaseModel):
    """Schema for product search request."""

    query: str = Field(..., min_length=1, max_length=255)
    limit: int = Field(default=10, ge=1, le=100)
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)

    class Config:
        example = {
            "query": "iPhone",
            "limit": 10,
            "min_price": 1000.0,
            "max_price": 10000.0,
        }