from typing import Dict, Any


class OrderEventPublisher:
    """Publish order events to RabbitMQ"""

    def __init__(self, rabbitmq_client):
        self.rabbitmq_client = rabbitmq_client

    def publish_order_created(self, order_id: int, order_data: Dict[str, Any]):
        """Publish order.created event"""
        message = {
            "event": "order.created",
            "order_id": order_id,
            "order_data": order_data,
        }
        self.rabbitmq_client.publish(
            exchange="orders", routing_key="order.created", message=message
        )

    def publish_orderline_created(
        self, order_id: int, product_pk: int, quantity: int, unit_price: float
    ):
        """Publish orderline.created event"""
        message = {
            "event": "orderline.created",
            "order_id": order_id,
            "product_pk": product_pk,
            "quantity": quantity,
            "unit_price": unit_price,
        }
        self.rabbitmq_client.publish(
            exchange="orders", routing_key="orderline.created", message=message
        )
