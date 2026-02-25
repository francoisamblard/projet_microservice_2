from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from datetime import datetime
from enum import Enum as PyEnum
from shared.db_config import Base


class CustomerType(str, PyEnum):
    """Customer type enumeration"""

    INDIVIDUAL = "individual"
    BUSINESS = "business"


class Customer(Base):
    """Customer entity"""

    __tablename__ = "customer"

    pk = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    customer_type = Column(
        Enum(CustomerType), default=CustomerType.INDIVIDUAL, nullable=False
    )
    price_category = Column(String(50), default="standard", nullable=False)
    credit_limit = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "pk": self.pk,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "customer_type": self.customer_type.value if self.customer_type else None,
            "price_category": self.price_category,
            "credit_limit": self.credit_limit,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
