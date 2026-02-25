from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class OrderLineCreateDTO(BaseModel):
    """DTO for creating an order line"""

    product_pk: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)


class OrderCreateDTO(BaseModel):
    """DTO for creating an order"""

    customer_pk: int
    lines: List[OrderLineCreateDTO]


class OrderUpdateDTO(BaseModel):
    """DTO for updating an order"""

    status: Optional[Literal["pending", "confirmed", "shipped", "delivered", "cancelled"]] = None


class OrderLineResponseDTO(BaseModel):
    """DTO for order line response"""

    pk: int
    order_pk: int
    product_pk: int
    quantity: int
    unit_price: float
    line_total: float
    created_at: Optional[str]

    class Config:
        from_attributes = True


class OrderResponseDTO(BaseModel):
    """DTO for order response"""

    pk: int
    customer_pk: int
    status: str
    total_amount: float
    lines: List[OrderLineResponseDTO] = []
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True
