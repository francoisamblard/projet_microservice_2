from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime
from shared.db_config import Base


class Warehouse(Base):
    """Warehouse entity"""

    __tablename__ = "warehouse"

    pk = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "pk": self.pk,
            "name": self.name,
            "location": self.location,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Product(Base):
    """Product mirror in Inventory service"""

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


class Inventory(Base):
    """Inventory entity (stock per product and warehouse)"""

    __tablename__ = "inventory"
    __table_args__ = (UniqueConstraint("product_pk", "warehouse_pk", name="uq_product_warehouse"),)

    pk = Column(Integer, primary_key=True, autoincrement=True)
    product_pk = Column(Integer, ForeignKey("product.pk"), nullable=False)
    warehouse_pk = Column(Integer, ForeignKey("warehouse.pk"), nullable=False)
    quantity = Column(Integer, default=0, nullable=False)
    reserved = Column(Integer, default=0, nullable=False)  # Reserved for orders
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "pk": self.pk,
            "product_pk": self.product_pk,
            "warehouse_pk": self.warehouse_pk,
            "quantity": self.quantity,
            "reserved": self.reserved,
            "available": self.quantity - self.reserved,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
