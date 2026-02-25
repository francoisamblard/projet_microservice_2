from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal


# Product DTOs
class ProductCreateRequest(BaseModel):
    """Request to create a product"""

    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    sku: str
    base_price: float = Field(..., gt=0)


class ProductUpdateRequest(BaseModel):
    """Request to update a product"""

    name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None


# Customer DTOs
class CustomerCreateRequest(BaseModel):
    """Request to create a customer"""

    name: str
    email: EmailStr
    phone: Optional[str] = None
    customer_type: Literal["individual", "business"] = "individual"
    price_category: str = "standard"
    credit_limit: float = 0.0


class CustomerUpdateRequest(BaseModel):
    """Request to update a customer"""

    name: Optional[str] = None
    phone: Optional[str] = None
    price_category: Optional[str] = None
    credit_limit: Optional[float] = None


# Warehouse DTOs
class WarehouseCreateRequest(BaseModel):
    """Request to create a warehouse"""

    name: str
    location: Optional[str] = None


# Inventory DTOs
class InventoryCreateRequest(BaseModel):
    """Request to create inventory"""

    product_pk: int
    warehouse_pk: int
    quantity: int = 0
    reserved: int = 0


class InventoryUpdateRequest(BaseModel):
    """Request to update inventory"""

    quantity: Optional[int] = None
    reserved: Optional[int] = None


# Pricing DTOs
class PricingCreateRequest(BaseModel):
    """Request to create pricing"""

    product_pk: int
    base_price: float = Field(..., gt=0)
    discount_percent: float = 0.0
    currency: str = "EUR"


class PricingUpdateRequest(BaseModel):
    """Request to update pricing"""

    discount_percent: Optional[float] = None
    base_price: Optional[float] = None


# Order DTOs
class OrderLineCreateRequest(BaseModel):
    """Request to create an order line"""

    product_pk: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)


class OrderCreateRequest(BaseModel):
    """Request to create an order"""

    customer_pk: int
    lines: List[OrderLineCreateRequest]


class OrderUpdateRequest(BaseModel):
    """Request to update an order"""

    status: Optional[Literal["pending", "confirmed", "shipped", "delivered", "cancelled"]] = None
