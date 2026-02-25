import json
import logging

logger = logging.getLogger(__name__)


class PricingEventConsumer:
    """Consume events from RabbitMQ for Pricing service"""

    def __init__(self, rabbitmq_client, price_repo, product_repo):
        self.rabbitmq_client = rabbitmq_client
        self.price_repo = price_repo
        self.product_repo = product_repo

    def setup_subscriptions(self):
        """Setup event subscriptions"""
        # Subscribe to product.created
        self.rabbitmq_client.declare_exchange(exchange="products", exchange_type="topic")
        self.rabbitmq_client.declare_queue(queue="pricing.product_created")
        self.rabbitmq_client.bind_queue(
            queue="pricing.product_created",
            exchange="products",
            routing_key="product.created",
        )
        logger.info("Pricing event subscriptions configured")

    def handle_product_created(self, ch, method, properties, body):
        """Handle product.created event - auto-create price"""
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

            # Auto-create price entry
            base_price = product_data.get("base_price", 0.0)
            existing_price = self.price_repo.get_by_product_pk(product_id)
            if not existing_price and base_price > 0:
                from application.dtos import PriceCreateDTO

                dto = PriceCreateDTO(
                    product_pk=product_id,
                    base_price=base_price,
                    discount_percent=0.0,
                    currency="EUR",
                )
                self.price_repo.create(dto)
                logger.info(f"Price auto-created for product {product_id}")

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error handling product.created event: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def consume_messages(self):
        """Start consuming messages"""
        channel = self.rabbitmq_client.get_channel()
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue="pricing.product_created", on_message_callback=self.handle_product_created
        )

        logger.info("Started consuming pricing events")
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
            self.rabbitmq_client.close()
