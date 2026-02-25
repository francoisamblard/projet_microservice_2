from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductCreateDTO(BaseModel):
    """DTO for creating a product"""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    sku: str = Field(..., min_length=1, max_length=100)
    base_price: float = Field(..., gt=0)


class ProductUpdateDTO(BaseModel):
    """DTO for updating a product"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    base_price: Optional[float] = Field(None, gt=0)


class ProductResponseDTO(BaseModel):
    """DTO for product response"""

    pk: int
    name: str
    description: Optional[str]
    sku: str
    base_price: float
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True
