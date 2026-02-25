import os
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from shared.db_config import DatabaseConfig
from application.dtos import (
    CustomerCreateDTO,
    CustomerUpdateDTO,
    CustomerResponseDTO,
)
from application.services.crud_services import CustomerService
from infrastructure.db.repository import CustomerRepository
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Customer Service", version="1.0.0")

# Database configuration
db_config = DatabaseConfig(
    user=os.getenv("CUSTOMER_DB_USER", "customer_user"),
    password=os.getenv("CUSTOMER_DB_PASSWORD", "customer_pass"),
    host=os.getenv("CUSTOMER_DB_HOST", "localhost"),
    port=int(os.getenv("CUSTOMER_DB_PORT", 5432)),
    database=os.getenv("CUSTOMER_DB_NAME", "customer_db"),
    echo=False,
)

# Create tables on startup
try:
    db_config.create_all_tables()
    logger.info("Database tables created")
except Exception as e:
    logger.warning(f"Error creating tables: {e}")

SessionLocal = db_config.get_session_factory()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_customer_service(db: Session = Depends(get_db)) -> CustomerService:
    """Dependency to get customer service"""
    repository = CustomerRepository(db)
    return CustomerService(repository)


# Routes
@app.post("/customer", response_model=CustomerResponseDTO, status_code=status.HTTP_201_CREATED)
def create_customer(
    dto: CustomerCreateDTO,
    service: CustomerService = Depends(get_customer_service),
):
    """Create a new customer"""
    try:
        return service.create_customer(dto)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/customer/{pk}", response_model=CustomerResponseDTO)
def get_customer(
    pk: int,
    service: CustomerService = Depends(get_customer_service),
):
    """Get customer by ID"""
    customer = service.get_customer(pk)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@app.get("/customers", response_model=list[CustomerResponseDTO])
def get_customers(
    skip: int = 0,
    limit: int = 100,
    service: CustomerService = Depends(get_customer_service),
):
    """Get all customers"""
    return service.get_all_customers(skip, limit)


@app.put("/customer/{pk}", response_model=CustomerResponseDTO)
def update_customer(
    pk: int,
    dto: CustomerUpdateDTO,
    service: CustomerService = Depends(get_customer_service),
):
    """Update customer"""
    customer = service.update_customer(pk, dto)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@app.delete("/customer/{pk}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    pk: int,
    service: CustomerService = Depends(get_customer_service),
):
    """Delete customer"""
    if not service.delete_customer(pk):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "customer-service"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8002)
