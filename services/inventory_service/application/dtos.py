from pydantic import BaseModel, Field
from typing import Optional


class WarehouseCreateDTO(BaseModel):
    """DTO for creating a warehouse"""

    name: str = Field(..., min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=255)


class WarehouseResponseDTO(BaseModel):
    """DTO for warehouse response"""

    pk: int
    name: str
    location: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True


class InventoryCreateDTO(BaseModel):
    """DTO for creating inventory entry"""

    product_pk: int
    warehouse_pk: int
    quantity: int = Field(default=0, ge=0)
    reserved: int = Field(default=0, ge=0)


class InventoryUpdateDTO(BaseModel):
    """DTO for updating inventory"""

    quantity: Optional[int] = Field(None, ge=0)
    reserved: Optional[int] = Field(None, ge=0)


class InventoryResponseDTO(BaseModel):
    """DTO for inventory response"""

    pk: int
    product_pk: int
    warehouse_pk: int
    quantity: int
    reserved: int
    available: int
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True
