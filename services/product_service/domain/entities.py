from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from shared.db_config import Base


class Product(Base):
    """Product entity"""

    __tablename__ = "product"

    pk = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    sku = Column(String(100), unique=True, nullable=False)
    base_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "pk": self.pk,
            "name": self.name,
            "description": self.description,
            "sku": self.sku,
            "base_price": self.base_price,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
