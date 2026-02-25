from infrastructure.db.repository import OrderRepository, OrderLineRepository
from application.dtos import (
    OrderCreateDTO,
    OrderUpdateDTO,
    OrderResponseDTO,
    OrderLineResponseDTO,
)
from typing import Optional, List


class OrderService:
    """Business logic for orders"""

    def __init__(self, order_repo: OrderRepository, orderline_repo: OrderLineRepository):
        self.order_repo = order_repo
        self.orderline_repo = orderline_repo

    def create_order(self, dto: OrderCreateDTO) -> OrderResponseDTO:
        """Create a new order"""
        if not dto.lines or len(dto.lines) == 0:
            raise ValueError("Order must have at least one line")

        order = self.order_repo.create(dto)
        return self._order_to_response(order)

    def get_order(self, pk: int) -> Optional[OrderResponseDTO]:
        """Get order by ID"""
        order = self.order_repo.get_by_pk(pk)
        if order:
            return self._order_to_response(order)
        return None

    def get_all_orders(self, skip: int = 0, limit: int = 100) -> List[OrderResponseDTO]:
        """Get all orders"""
        orders = self.order_repo.get_all(skip, limit)
        return [self._order_to_response(o) for o in orders]

    def get_customer_orders(
        self, customer_pk: int, skip: int = 0, limit: int = 100
    ) -> List[OrderResponseDTO]:
        """Get all orders for a customer"""
        orders = self.order_repo.get_by_customer(customer_pk, skip, limit)
        return [self._order_to_response(o) for o in orders]

    def update_order(self, pk: int, dto: OrderUpdateDTO) -> Optional[OrderResponseDTO]:
        """Update an order"""
        order = self.order_repo.update(pk, dto)
        if order:
            return self._order_to_response(order)
        return None

    def _order_to_response(self, order) -> OrderResponseDTO:
        """Convert Order entity to response DTO with lines"""
        order_dict = order.to_dict()
        lines = self.orderline_repo.get_by_order(order.pk)
        order_dict["lines"] = [OrderLineResponseDTO(**line.to_dict()) for line in lines]
        return OrderResponseDTO(**order_dict)
