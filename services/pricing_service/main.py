import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from shared.db_config import DatabaseConfig
from application.dtos import (
    PriceCreateDTO,
    PriceUpdateDTO,
    PriceResponseDTO,
)
from application.services.crud_services import PricingService
from infrastructure.db.repository import (
    PriceRepository,
    ProductRepository,
)
from domain.events import PricingEventConsumer
from shared.rabbitmq_client import RabbitMQConnection
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Pricing Service", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
db_config = DatabaseConfig(
    user=os.getenv("PRICING_DB_USER", "pricing_user"),
    password=os.getenv("PRICING_DB_PASSWORD", "pricing_pass"),
    host=os.getenv("PRICING_DB_HOST", "localhost"),
    port=int(os.getenv("PRICING_DB_PORT", 5432)),
    database=os.getenv("PRICING_DB_NAME", "pricing_db"),
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


def get_pricing_service(db: Session = Depends(get_db)) -> PricingService:
    """Dependency to get pricing service"""
    price_repo = PriceRepository(db)
    product_repo = ProductRepository(db)
    return PricingService(price_repo, product_repo)


# Setup event consumer and start it in background thread
def start_event_consumer():
    """Start consuming events in background"""
    db = SessionLocal()
    price_repo = PriceRepository(db)
    product_repo = ProductRepository(db)
    consumer = PricingEventConsumer(rabbitmq_client, price_repo, product_repo)
    consumer.setup_subscriptions()

    def run_consumer():
        try:
            consumer.consume_messages()
        except Exception as e:
            logger.error(f"Error in event consumer: {e}")
        finally:
            db.close()

    thread = threading.Thread(target=run_consumer, daemon=True)
    thread.start()
    logger.info("Event consumer thread started")


# Routes
@app.post("/pricing", response_model=PriceResponseDTO, status_code=status.HTTP_201_CREATED)
def create_price(
    dto: PriceCreateDTO,
    service: PricingService = Depends(get_pricing_service),
):
    """Create a new price"""
    try:
        return service.create_price(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/pricing/{pk}", response_model=PriceResponseDTO)
def get_price(
    pk: int,
    service: PricingService = Depends(get_pricing_service),
):
    """Get price by ID"""
    price = service.get_price(pk)
    if not price:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price not found")
    return price


@app.get("/pricing/product/{product_pk}", response_model=PriceResponseDTO)
def get_price_by_product(
    product_pk: int,
    service: PricingService = Depends(get_pricing_service),
):
    """Get price by product ID"""
    price = service.get_price_by_product(product_pk)
    if not price:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price not found")
    return price


@app.get("/pricings", response_model=list[PriceResponseDTO])
def get_prices(
    skip: int = 0,
    limit: int = 100,
    service: PricingService = Depends(get_pricing_service),
):
    """Get all prices"""
    return service.get_all_prices(skip, limit)


@app.patch("/pricing/{pk}", response_model=PriceResponseDTO)
def update_price(
    pk: int,
    dto: PriceUpdateDTO,
    service: PricingService = Depends(get_pricing_service),
):
    """Update price"""
    price = service.update_price(pk, dto)
    if not price:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price not found")
    return price


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "pricing-service"}


@app.on_event("startup")
async def startup_event():
    """Start event consumer on app startup"""
    start_event_consumer()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)
