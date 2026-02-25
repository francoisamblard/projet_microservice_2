from typing import Dict, Any


class ProductEventPublisher:
    """Publish product events to RabbitMQ"""

    def __init__(self, rabbitmq_client):
        self.rabbitmq_client = rabbitmq_client

    def publish_product_created(self, product_id: int, product_data: Dict[str, Any]):
        """Publish product.created event"""
        message = {
            "event": "product.created",
            "product_id": product_id,
            "product_data": product_data,
        }
        self.rabbitmq_client.publish(
            exchange="products", routing_key="product.created", message=message
        )
