import json
import logging
from typing import Callable

logger = logging.getLogger(__name__)


class InventoryEventConsumer:
    """Consume events from RabbitMQ for Inventory service"""

    def __init__(self, rabbitmq_client, product_repo):
        self.rabbitmq_client = rabbitmq_client
        self.product_repo = product_repo

    def setup_subscriptions(self):
        """Setup event subscriptions"""
        # Subscribe to product.created
        self.rabbitmq_client.declare_exchange(exchange="products", exchange_type="topic")
        self.rabbitmq_client.declare_queue(queue="inventory.product_created")
        self.rabbitmq_client.bind_queue(
            queue="inventory.product_created",
            exchange="products",
            routing_key="product.created",
        )

        # Subscribe to orderline.created
        self.rabbitmq_client.declare_exchange(exchange="orders", exchange_type="topic")
        self.rabbitmq_client.declare_queue(queue="inventory.orderline_created")
        self.rabbitmq_client.bind_queue(
            queue="inventory.orderline_created",
            exchange="orders",
            routing_key="orderline.created",
        )

        logger.info("Inventory event subscriptions configured")

    def handle_product_created(self, ch, method, properties, body):
        """Handle product.created event"""
        try:
            message = json.loads(body)
            product_id = message.get("product_id")
            product_data = message.get("product_data", {})

            logger.info(f"Received product.created event for product {product_id}")

            # Create or update product in this service
            self.product_repo.create_or_update(
                product_id=product_id,
                name=product_data.get("name", "Unknown"),
                sku=product_data.get("sku", ""),
            )

            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Product {product_id} synced to inventory service")
        except Exception as e:
            logger.error(f"Error handling product.created event: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def handle_orderline_created(self, ch, method, properties, body):
        """Handle orderline.created event - reserve inventory"""
        try:
            message = json.loads(body)
            product_pk = message.get("product_pk")
            quantity = message.get("quantity", 0)

            logger.info(
                f"Received orderline.created event for product {product_pk}, qty {quantity}"
            )

            # Here we would update inventory (mark as reserved)
            # This is a simplified version - in production you'd implement full reservation logic

            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Inventory reserved for product {product_pk}")
        except Exception as e:
            logger.error(f"Error handling orderline.created event: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def consume_messages(self):
        """Start consuming messages"""
        channel = self.rabbitmq_client.get_channel()
        channel.basic_qos(prefetch_count=1)

        # Consume both queues
        channel.basic_consume(
            queue="inventory.product_created", on_message_callback=self.handle_product_created
        )
        channel.basic_consume(
            queue="inventory.orderline_created", on_message_callback=self.handle_orderline_created
        )

        logger.info("Started consuming inventory events")
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
            self.rabbitmq_client.close()
