from pydantic import BaseModel, Field
from typing import Optional


class PriceCreateDTO(BaseModel):
    """DTO for creating a price"""

    product_pk: int
    base_price: float = Field(..., gt=0)
    discount_percent: float = Field(default=0.0, ge=0, le=100)
    currency: str = Field(default="EUR", max_length=3)


class PriceUpdateDTO(BaseModel):
    """DTO for updating a price"""

    discount_percent: Optional[float] = Field(None, ge=0, le=100)
    base_price: Optional[float] = Field(None, gt=0)


class PriceResponseDTO(BaseModel):
    """DTO for price response"""

    pk: int
    product_pk: int
    base_price: float
    discount_percent: float
    final_price: float
    currency: str
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True
