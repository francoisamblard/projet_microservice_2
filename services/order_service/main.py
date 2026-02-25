import os
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from shared.db_config import DatabaseConfig
from application.dtos import (
    OrderCreateDTO,
    OrderUpdateDTO,
    OrderResponseDTO,
)
from application.services.crud_services import OrderService
from infrastructure.db.repository import OrderRepository, OrderLineRepository
from domain.events import OrderEventPublisher
from shared.rabbitmq_client import RabbitMQConnection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Order Service", version="1.0.0")

# Database configuration
db_config = DatabaseConfig(
    user=os.getenv("ORDER_DB_USER", "order_user"),
    password=os.getenv("ORDER_DB_PASSWORD", "order_pass"),
    host=os.getenv("ORDER_DB_HOST", "localhost"),
    port=int(os.getenv("ORDER_DB_PORT", 5432)),
    database=os.getenv("ORDER_DB_NAME", "order_db"),
    echo=False,
)

# Create tables on startup
try:
    db_config.create_all_tables()
    logger.info("Database tables created")
except Exception as e:
    logger.warning(f"Error creating tables: {e}")

SessionLocal = db_config.get_session_factory()

# RabbitMQ connection
rabbitmq_client = RabbitMQConnection()
try:
    rabbitmq_client.connect(
        host=os.getenv("RABBITMQ_HOST", "localhost"),
        port=int(os.getenv("RABBITMQ_PORT", 5672)),
        user=os.getenv("RABBITMQ_USER", "guest"),
        password=os.getenv("RABBITMQ_PASSWORD", "guest"),
    )
    # Declare exchange for orders
    rabbitmq_client.declare_exchange(exchange="orders", exchange_type="topic")
    logger.info("RabbitMQ client initialized")
except Exception as e:
    logger.error(f"Error initializing RabbitMQ: {e}")


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    """Dependency to get order service"""
    order_repo = OrderRepository(db)
    orderline_repo = OrderLineRepository(db)
    return OrderService(order_repo, orderline_repo)


# Routes
@app.post("/order", response_model=OrderResponseDTO, status_code=status.HTTP_201_CREATED)
def create_order(
    dto: OrderCreateDTO,
    service: OrderService = Depends(get_order_service),
):
    """Create a new order"""
    try:
        order = service.create_order(dto)

        # Publish events
        event_publisher = OrderEventPublisher(rabbitmq_client)

        # Publish order.created event
        event_publisher.publish_order_created(order.pk, order.model_dump())

        # Publish orderline.created event for each line
        for line in order.lines:
            event_publisher.publish_orderline_created(
                order.pk, line.product_pk, line.quantity, line.unit_price
            )

        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/order/{pk}", response_model=OrderResponseDTO)
def get_order(
    pk: int,
    service: OrderService = Depends(get_order_service),
):
    """Get order by ID"""
    order = service.get_order(pk)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@app.get("/orders", response_model=list[OrderResponseDTO])
def get_orders(
    skip: int = 0,
    limit: int = 100,
    service: OrderService = Depends(get_order_service),
):
    """Get all orders"""
    return service.get_all_orders(skip, limit)


@app.get("/customer/{customer_pk}/orders", response_model=list[OrderResponseDTO])
def get_customer_orders(
    customer_pk: int,
    skip: int = 0,
    limit: int = 100,
    service: OrderService = Depends(get_order_service),
):
    """Get all orders for a customer"""
    return service.get_customer_orders(customer_pk, skip, limit)


@app.patch("/order/{pk}", response_model=OrderResponseDTO)
def update_order(
    pk: int,
    dto: OrderUpdateDTO,
    service: OrderService = Depends(get_order_service),
):
    """Update order"""
    order = service.update_order(pk, dto)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "order-service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)
