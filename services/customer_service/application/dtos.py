from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime


class CustomerCreateDTO(BaseModel):
    """DTO for creating a customer"""

    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    customer_type: Literal["individual", "business"] = "individual"
    price_category: str = Field("standard", max_length=50)
    credit_limit: float = Field(0.0, ge=0)


class CustomerUpdateDTO(BaseModel):
    """DTO for updating a customer"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    price_category: Optional[str] = Field(None, max_length=50)
    credit_limit: Optional[float] = Field(None, ge=0)


class CustomerResponseDTO(BaseModel):
    """DTO for customer response"""

    pk: int
    name: str
    email: str
    phone: Optional[str]
    customer_type: str
    price_category: str
    credit_limit: float
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True
