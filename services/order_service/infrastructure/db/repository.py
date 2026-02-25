from sqlalchemy.orm import Session
from domain.entities import Order, OrderLine
from application.dtos import OrderCreateDTO, OrderUpdateDTO
from typing import Optional, List


class OrderRepository:
    """Order repository"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, dto: OrderCreateDTO) -> Order:
        """Create a new order"""
        # Calculate total amount
        total_amount = sum(line.quantity * line.unit_price for line in dto.lines)

        order = Order(customer_pk=dto.customer_pk, total_amount=total_amount)
        self.session.add(order)
        self.session.flush()  # Get the order ID without committing

        # Create order lines
        for line_dto in dto.lines:
            line = OrderLine(
                order_pk=order.pk,
                product_pk=line_dto.product_pk,
                quantity=line_dto.quantity,
                unit_price=line_dto.unit_price,
                line_total=line_dto.quantity * line_dto.unit_price,
            )
            self.session.add(line)

        self.session.commit()
        self.session.refresh(order)
        return order

    def get_by_pk(self, pk: int) -> Optional[Order]:
        """Get order by primary key"""
        return self.session.query(Order).filter(Order.pk == pk).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all orders"""
        return self.session.query(Order).offset(skip).limit(limit).all()

    def get_by_customer(self, customer_pk: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get all orders for a customer"""
        return (
            self.session.query(Order)
            .filter(Order.customer_pk == customer_pk)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update(self, pk: int, dto: OrderUpdateDTO) -> Optional[Order]:
        """Update an order"""
        order = self.get_by_pk(pk)
        if order and dto.status:
            order.status = dto.status
            self.session.commit()
            self.session.refresh(order)
        return order


class OrderLineRepository:
    """OrderLine repository"""

    def __init__(self, session: Session):
        self.session = session

    def get_by_order(self, order_pk: int) -> List[OrderLine]:
        """Get all lines for an order"""
        return self.session.query(OrderLine).filter(OrderLine.order_pk == order_pk).all()

    def get_by_pk(self, pk: int) -> Optional[OrderLine]:
        """Get order line by primary key"""
        return self.session.query(OrderLine).filter(OrderLine.pk == pk).first()
