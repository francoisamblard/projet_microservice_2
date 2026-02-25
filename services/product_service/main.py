import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from shared.db_config import DatabaseConfig
from application.dtos import (
    ProductCreateDTO,
    ProductUpdateDTO,
    ProductResponseDTO,
)
from application.services.crud_services import ProductService
from infrastructure.db.repository import ProductRepository
from domain.events import ProductEventPublisher
from shared.rabbitmq_client import RabbitMQConnection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Product Service", version="1.0.0")

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
    user=os.getenv("PRODUCT_DB_USER", "product_user"),
    password=os.getenv("PRODUCT_DB_PASSWORD", "product_pass"),
    host=os.getenv("PRODUCT_DB_HOST", "localhost"),
    port=int(os.getenv("PRODUCT_DB_PORT", 5432)),
    database=os.getenv("PRODUCT_DB_NAME", "product_db"),
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
    # Declare exchange for products
    rabbitmq_client.declare_exchange(exchange="products", exchange_type="topic")
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


def get_product_service(db: Session = Depends(get_db)) -> ProductService:
    """Dependency to get product service"""
    repository = ProductRepository(db)
    return ProductService(repository)


# Routes
@app.post("/product", response_model=ProductResponseDTO, status_code=status.HTTP_201_CREATED)
def create_product(
    dto: ProductCreateDTO,
    service: ProductService = Depends(get_product_service),
):
    """Create a new product"""
    try:
        product = service.create_product(dto)
        # Publish event
        event_publisher = ProductEventPublisher(rabbitmq_client)
        event_publisher.publish_product_created(product.pk, product.model_dump())
        return product
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/product/{pk}", response_model=ProductResponseDTO)
def get_product(
    pk: int,
    service: ProductService = Depends(get_product_service),
):
    """Get product by ID"""
    product = service.get_product(pk)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@app.get("/products", response_model=list[ProductResponseDTO])
def get_products(
    skip: int = 0,
    limit: int = 100,
    service: ProductService = Depends(get_product_service),
):
    """Get all products"""
    return service.get_all_products(skip, limit)


@app.put("/product/{pk}", response_model=ProductResponseDTO)
def update_product(
    pk: int,
    dto: ProductUpdateDTO,
    service: ProductService = Depends(get_product_service),
):
    """Update product"""
    product = service.update_product(pk, dto)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@app.delete("/product/{pk}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    pk: int,
    service: ProductService = Depends(get_product_service),
):
    """Delete product"""
    if not service.delete_product(pk):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "product-service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
