from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from shared.db_config import Base


class Product(Base):
    """Product mirror in Pricing service"""

    __tablename__ = "product"

    pk = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    sku = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "pk": self.pk,
            "name": self.name,
            "sku": self.sku,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Price(Base):
    """Price entity"""

    __tablename__ = "price"

    pk = Column(Integer, primary_key=True, autoincrement=True)
    product_pk = Column(Integer, nullable=False, unique=True)
    base_price = Column(Float, nullable=False)
    discount_percent = Column(Float, default=0.0, nullable=False)
    final_price = Column(Float, nullable=False)
    currency = Column(String(3), default="EUR", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "pk": self.pk,
            "product_pk": self.product_pk,
            "base_price": self.base_price,
            "discount_percent": self.discount_percent,
            "final_price": self.final_price,
            "currency": self.currency,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
