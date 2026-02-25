from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from datetime import datetime
from enum import Enum as PyEnum
from shared.db_config import Base


class OrderStatus(str, PyEnum):
    """Order status enumeration"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    """Order entity"""

    __tablename__ = "order"

    pk = Column(Integer, primary_key=True, autoincrement=True)
    customer_pk = Column(Integer, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_amount = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "pk": self.pk,
            "customer_pk": self.customer_pk,
            "status": self.status.value if self.status else None,
            "total_amount": self.total_amount,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class OrderLine(Base):
    """OrderLine entity (items in an order)"""

    __tablename__ = "orderline"

    pk = Column(Integer, primary_key=True, autoincrement=True)
    order_pk = Column(Integer, ForeignKey("order.pk"), nullable=False)
    product_pk = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    line_total = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "pk": self.pk,
            "order_pk": self.order_pk,
            "product_pk": self.product_pk,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "line_total": self.line_total,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
