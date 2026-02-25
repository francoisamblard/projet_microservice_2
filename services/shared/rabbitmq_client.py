import pika
from typing import Optional, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class RabbitMQConnection:
    """Manage RabbitMQ connection and channel"""

    _instance: Optional["RabbitMQConnection"] = None
    _connection = None
    _channel = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self, host: str, port: int, user: str, password: str):
        """Establish RabbitMQ connection"""
        if self._connection is None or self._connection.is_closed:
            credentials = pika.PlainCredentials(user, password)
            self._connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=host,
                    port=port,
                    credentials=credentials,
                    heartbeat=600,
                    blocked_connection_timeout=300,
                )
            )
            self._channel = self._connection.channel()
            logger.info("Connected to RabbitMQ")

    def get_channel(self):
        """Get RabbitMQ channel"""
        if self._channel is None or self._channel.is_closed:
            self.connect(self._host, self._port, self._user, self._password)
        return self._channel

    def close(self):
        """Close RabbitMQ connection"""
        if self._connection and not self._connection.is_closed:
            self._connection.close()
            logger.info("RabbitMQ connection closed")

    def declare_exchange(
        self, exchange: str, exchange_type: str = "topic", durable: bool = True
    ):
        """Declare an exchange"""
        channel = self.get_channel()
        channel.exchange_declare(
            exchange=exchange, exchange_type=exchange_type, durable=durable
        )

    def declare_queue(self, queue: str, durable: bool = True):
        """Declare a queue"""
        channel = self.get_channel()
        channel.queue_declare(queue=queue, durable=durable)

    def bind_queue(self, queue: str, exchange: str, routing_key: str):
        """Bind queue to exchange"""
        channel = self.get_channel()
        channel.queue_bind(queue=queue, exchange=exchange, routing_key=routing_key)

    def publish(self, exchange: str, routing_key: str, message: Dict[Any, Any]):
        """Publish a message"""
        channel = self.get_channel()
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2),  # Make message persistent
        )
        logger.info(f"Published message to {exchange} with routing_key {routing_key}")

    def consume(self, queue: str, callback):
        """Consume messages from queue"""
        channel = self.get_channel()
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue, on_message_callback=callback)
        logger.info(f"Starting to consume from queue {queue}")
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
            self.close()
