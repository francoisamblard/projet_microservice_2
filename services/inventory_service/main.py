import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from shared.db_config import DatabaseConfig
from application.dtos import (
    WarehouseCreateDTO,
    WarehouseResponseDTO,
    InventoryCreateDTO,
    InventoryUpdateDTO,
    InventoryResponseDTO,
)
from application.services.crud_services import InventoryService
from infrastructure.db.repository import (
    InventoryRepository,
    WarehouseRepository,
    ProductRepository,
)
from domain.events import InventoryEventConsumer
from shared.rabbitmq_client import RabbitMQConnection
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Inventory Service", version="1.0.0")

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
    user=os.getenv("INVENTORY_DB_USER", "inventory_user"),
    password=os.getenv("INVENTORY_DB_PASSWORD", "inventory_pass"),
    host=os.getenv("INVENTORY_DB_HOST", "localhost"),
    port=int(os.getenv("INVENTORY_DB_PORT", 5432)),
    database=os.getenv("INVENTORY_DB_NAME", "inventory_db"),
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


def get_inventory_service(db: Session = Depends(get_db)) -> InventoryService:
    """Dependency to get inventory service"""
    inventory_repo = InventoryRepository(db)
    warehouse_repo = WarehouseRepository(db)
    product_repo = ProductRepository(db)
    return InventoryService(inventory_repo, warehouse_repo, product_repo)


# Setup event consumer and start it in background thread
def start_event_consumer():
    """Start consuming events in background"""
    db = SessionLocal()
    product_repo = ProductRepository(db)
    consumer = InventoryEventConsumer(rabbitmq_client, product_repo)
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


# Routes - Warehouses
@app.post("/warehouse", response_model=WarehouseResponseDTO, status_code=status.HTTP_201_CREATED)
def create_warehouse(
    dto: WarehouseCreateDTO,
    service: InventoryService = Depends(get_inventory_service),
):
    """Create a new warehouse"""
    return service.create_warehouse(dto)


@app.get("/warehouse/{pk}", response_model=WarehouseResponseDTO)
def get_warehouse(
    pk: int,
    service: InventoryService = Depends(get_inventory_service),
):
    """Get warehouse by ID"""
    warehouse = service.get_warehouse(pk)
    if not warehouse:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    return warehouse


@app.get("/warehouses", response_model=list[WarehouseResponseDTO])
def get_warehouses(
    skip: int = 0,
    limit: int = 100,
    service: InventoryService = Depends(get_inventory_service),
):
    """Get all warehouses"""
    return service.get_all_warehouses(skip, limit)


# Routes - Inventory
@app.post("/inventory", response_model=InventoryResponseDTO, status_code=status.HTTP_201_CREATED)
def create_inventory(
    dto: InventoryCreateDTO,
    service: InventoryService = Depends(get_inventory_service),
):
    """Create inventory entry"""
    try:
        return service.create_inventory(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/inventory/{pk}", response_model=InventoryResponseDTO)
def get_inventory(
    pk: int,
    service: InventoryService = Depends(get_inventory_service),
):
    """Get inventory by ID"""
    inventory = service.get_inventory(pk)
    if not inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    return inventory


@app.get("/inventory/product/{product_pk}", response_model=list[InventoryResponseDTO])
def get_inventory_by_product(
    product_pk: int,
    service: InventoryService = Depends(get_inventory_service),
):
    """Get all inventory entries for a product"""
    return service.get_inventory_by_product(product_pk)


@app.get("/inventories", response_model=list[InventoryResponseDTO])
def get_inventories(
    skip: int = 0,
    limit: int = 100,
    service: InventoryService = Depends(get_inventory_service),
):
    """Get all inventory entries"""
    return service.get_all_inventory(skip, limit)


@app.patch("/inventory/{pk}", response_model=InventoryResponseDTO)
def update_inventory(
    pk: int,
    dto: InventoryUpdateDTO,
    service: InventoryService = Depends(get_inventory_service),
):
    """Update inventory"""
    inventory = service.update_inventory(pk, dto)
    if not inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    return inventory


# PAIR endpoint - Check stock level
@app.get("/check-stock/{product_pk}/{quantity}")
def check_stock(
    product_pk: int,
    quantity: int,
    service: InventoryService = Depends(get_inventory_service),
):
    """Check if product has enough stock"""
    has_stock = service.check_stock(product_pk, quantity)
    return {"product_pk": product_pk, "quantity": quantity, "has_stock": has_stock}


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "inventory-service"}


@app.on_event("startup")
async def startup_event():
    """Start event consumer on app startup"""
    start_event_consumer()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
