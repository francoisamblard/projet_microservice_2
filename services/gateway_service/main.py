import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from infrastructure.service_client import GatewayServiceRegistry
from application.dtos import *
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app with OpenAPI documentation
app = FastAPI(
    title="E-Commerce API Gateway",
    description="Central API Gateway for e-commerce microservices",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
)

# Service registry
service_registry = GatewayServiceRegistry()


# Dependency to get service registry
def get_services() -> GatewayServiceRegistry:
    """Get service registry"""
    return service_registry


# ==================== PRODUCT ENDPOINTS ====================
@app.post("/product", status_code=status.HTTP_201_CREATED, tags=["Products"])
async def create_product(
    req: ProductCreateRequest,
    services: GatewayServiceRegistry = Depends(get_services),
):
    """Create a new product"""
    try:
        return await services.product_service.post(
            "/product",
            req.model_dump(),
        )
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(status_code=500, detail="Failed to create product")


@app.get("/product/{pk}", tags=["Products"])
async def get_product(pk: int, services: GatewayServiceRegistry = Depends(get_services)):
    """Get product by ID"""
    try:
        return await services.product_service.get(f"/product/{pk}")
    except Exception as e:
        logger.error(f"Error getting product: {e}")
        raise HTTPException(status_code=404, detail="Product not found")


@app.get("/products", tags=["Products"])
async def get_products(
    skip: int = 0, limit: int = 100, services: GatewayServiceRegistry = Depends(get_services)
):
    """Get all products"""
    try:
        return await services.product_service.get(f"/products?skip={skip}&limit={limit}")
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail="Failed to get products")


@app.put("/product/{pk}", tags=["Products"])
async def update_product(
    pk: int, req: ProductUpdateRequest, services: GatewayServiceRegistry = Depends(get_services)
):
    """Update a product"""
    try:
        return await services.product_service.put(f"/product/{pk}", req.model_dump())
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        raise HTTPException(status_code=500, detail="Failed to update product")


@app.delete("/product/{pk}", status_code=status.HTTP_204_NO_CONTENT, tags=["Products"])
async def delete_product(pk: int, services: GatewayServiceRegistry = Depends(get_services)):
    """Delete a product"""
    try:
        await services.product_service.delete(f"/product/{pk}")
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete product")


# ==================== CUSTOMER ENDPOINTS ====================
@app.post("/customer", status_code=status.HTTP_201_CREATED, tags=["Customers"])
async def create_customer(
    req: CustomerCreateRequest,
    services: GatewayServiceRegistry = Depends(get_services),
):
    """Create a new customer"""
    try:
        return await services.customer_service.post(
            "/customer",
            req.model_dump(),
        )
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(status_code=500, detail="Failed to create customer")


@app.get("/customer/{pk}", tags=["Customers"])
async def get_customer(pk: int, services: GatewayServiceRegistry = Depends(get_services)):
    """Get customer by ID"""
    try:
        return await services.customer_service.get(f"/customer/{pk}")
    except Exception as e:
        logger.error(f"Error getting customer: {e}")
        raise HTTPException(status_code=404, detail="Customer not found")


@app.get("/customers", tags=["Customers"])
async def get_customers(
    skip: int = 0, limit: int = 100, services: GatewayServiceRegistry = Depends(get_services)
):
    """Get all customers"""
    try:
        return await services.customer_service.get(f"/customers?skip={skip}&limit={limit}")
    except Exception as e:
        logger.error(f"Error getting customers: {e}")
        raise HTTPException(status_code=500, detail="Failed to get customers")


@app.put("/customer/{pk}", tags=["Customers"])
async def update_customer(
    pk: int, req: CustomerUpdateRequest, services: GatewayServiceRegistry = Depends(get_services)
):
    """Update a customer"""
    try:
        return await services.customer_service.put(f"/customer/{pk}", req.model_dump())
    except Exception as e:
        logger.error(f"Error updating customer: {e}")
        raise HTTPException(status_code=500, detail="Failed to update customer")


@app.delete("/customer/{pk}", status_code=status.HTTP_204_NO_CONTENT, tags=["Customers"])
async def delete_customer(pk: int, services: GatewayServiceRegistry = Depends(get_services)):
    """Delete a customer"""
    try:
        await services.customer_service.delete(f"/customer/{pk}")
    except Exception as e:
        logger.error(f"Error deleting customer: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete customer")


# ==================== WAREHOUSE ENDPOINTS ====================
@app.post("/warehouse", status_code=status.HTTP_201_CREATED, tags=["Warehouses"])
async def create_warehouse(
    req: WarehouseCreateRequest,
    services: GatewayServiceRegistry = Depends(get_services),
):
    """Create a new warehouse"""
    try:
        return await services.inventory_service.post(
            "/warehouse",
            req.model_dump(),
        )
    except Exception as e:
        logger.error(f"Error creating warehouse: {e}")
        raise HTTPException(status_code=500, detail="Failed to create warehouse")


@app.get("/warehouse/{pk}", tags=["Warehouses"])
async def get_warehouse(pk: int, services: GatewayServiceRegistry = Depends(get_services)):
    """Get warehouse by ID"""
    try:
        return await services.inventory_service.get(f"/warehouse/{pk}")
    except Exception as e:
        logger.error(f"Error getting warehouse: {e}")
        raise HTTPException(status_code=404, detail="Warehouse not found")


@app.get("/warehouses", tags=["Warehouses"])
async def get_warehouses(
    skip: int = 0, limit: int = 100, services: GatewayServiceRegistry = Depends(get_services)
):
    """Get all warehouses"""
    try:
        return await services.inventory_service.get(f"/warehouses?skip={skip}&limit={limit}")
    except Exception as e:
        logger.error(f"Error getting warehouses: {e}")
        raise HTTPException(status_code=500, detail="Failed to get warehouses")


# ==================== INVENTORY ENDPOINTS ====================
@app.post("/inventory", status_code=status.HTTP_201_CREATED, tags=["Inventory"])
async def create_inventory(
    req: InventoryCreateRequest,
    services: GatewayServiceRegistry = Depends(get_services),
):
    """Create inventory entry"""
    try:
        return await services.inventory_service.post(
            "/inventory",
            req.model_dump(),
        )
    except Exception as e:
        logger.error(f"Error creating inventory: {e}")
        raise HTTPException(status_code=500, detail="Failed to create inventory")


@app.get("/inventory/{pk}", tags=["Inventory"])
async def get_inventory(pk: int, services: GatewayServiceRegistry = Depends(get_services)):
    """Get inventory by ID"""
    try:
        return await services.inventory_service.get(f"/inventory/{pk}")
    except Exception as e:
        logger.error(f"Error getting inventory: {e}")
        raise HTTPException(status_code=404, detail="Inventory not found")


@app.get("/inventory/product/{product_pk}", tags=["Inventory"])
async def get_inventory_by_product(
    product_pk: int,
    services: GatewayServiceRegistry = Depends(get_services),
):
    """Get inventory by product"""
    try:
        return await services.inventory_service.get(f"/inventory/product/{product_pk}")
    except Exception as e:
        logger.error(f"Error getting inventory: {e}")
        raise HTTPException(status_code=404, detail="Inventory not found")


@app.get("/inventories", tags=["Inventory"])
async def get_inventories(
    skip: int = 0, limit: int = 100, services: GatewayServiceRegistry = Depends(get_services)
):
    """Get all inventory entries"""
    try:
        return await services.inventory_service.get(f"/inventories?skip={skip}&limit={limit}")
    except Exception as e:
        logger.error(f"Error getting inventories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get inventories")


@app.patch("/inventory/{pk}", tags=["Inventory"])
async def update_inventory(
    pk: int, req: InventoryUpdateRequest, services: GatewayServiceRegistry = Depends(get_services)
):
    """Update inventory"""
    try:
        return await services.inventory_service.patch(f"/inventory/{pk}", req.model_dump())
    except Exception as e:
        logger.error(f"Error updating inventory: {e}")
        raise HTTPException(status_code=500, detail="Failed to update inventory")


# ==================== PRICING ENDPOINTS ====================
@app.post("/pricing", status_code=status.HTTP_201_CREATED, tags=["Pricing"])
async def create_pricing(
    req: PricingCreateRequest,
    services: GatewayServiceRegistry = Depends(get_services),
):
    """Create pricing entry"""
    try:
        return await services.pricing_service.post(
            "/pricing",
            req.model_dump(),
        )
    except Exception as e:
        logger.error(f"Error creating pricing: {e}")
        raise HTTPException(status_code=500, detail="Failed to create pricing")


@app.get("/pricing/{pk}", tags=["Pricing"])
async def get_pricing(pk: int, services: GatewayServiceRegistry = Depends(get_services)):
    """Get pricing by ID"""
    try:
        return await services.pricing_service.get(f"/pricing/{pk}")
    except Exception as e:
        logger.error(f"Error getting pricing: {e}")
        raise HTTPException(status_code=404, detail="Pricing not found")


@app.get("/pricing/product/{product_pk}", tags=["Pricing"])
async def get_pricing_by_product(
    product_pk: int,
    services: GatewayServiceRegistry = Depends(get_services),
):
    """Get pricing by product"""
    try:
        return await services.pricing_service.get(f"/pricing/product/{product_pk}")
    except Exception as e:
        logger.error(f"Error getting pricing: {e}")
        raise HTTPException(status_code=404, detail="Pricing not found")


@app.get("/pricings", tags=["Pricing"])
async def get_pricings(
    skip: int = 0, limit: int = 100, services: GatewayServiceRegistry = Depends(get_services)
):
    """Get all pricings"""
    try:
        return await services.pricing_service.get(f"/pricings?skip={skip}&limit={limit}")
    except Exception as e:
        logger.error(f"Error getting pricings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pricings")


@app.patch("/pricing/{pk}", tags=["Pricing"])
async def update_pricing(
    pk: int, req: PricingUpdateRequest, services: GatewayServiceRegistry = Depends(get_services)
):
    """Update pricing"""
    try:
        return await services.pricing_service.patch(f"/pricing/{pk}", req.model_dump())
    except Exception as e:
        logger.error(f"Error updating pricing: {e}")
        raise HTTPException(status_code=500, detail="Failed to update pricing")


# ==================== ORDER ENDPOINTS ====================
@app.post("/order", status_code=status.HTTP_201_CREATED, tags=["Orders"])
async def create_order(
    req: OrderCreateRequest,
    services: GatewayServiceRegistry = Depends(get_services),
):
    """Create a new order"""
    try:
        return await services.order_service.post(
            "/order",
            req.model_dump(),
        )
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(status_code=500, detail="Failed to create order")


@app.get("/order/{pk}", tags=["Orders"])
async def get_order(pk: int, services: GatewayServiceRegistry = Depends(get_services)):
    """Get order by ID"""
    try:
        return await services.order_service.get(f"/order/{pk}")
    except Exception as e:
        logger.error(f"Error getting order: {e}")
        raise HTTPException(status_code=404, detail="Order not found")


@app.get("/orders", tags=["Orders"])
async def get_orders(
    skip: int = 0, limit: int = 100, services: GatewayServiceRegistry = Depends(get_services)
):
    """Get all orders"""
    try:
        return await services.order_service.get(f"/orders?skip={skip}&limit={limit}")
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to get orders")


@app.get("/customer/{customer_pk}/orders", tags=["Orders"])
async def get_customer_orders(
    customer_pk: int,
    skip: int = 0,
    limit: int = 100,
    services: GatewayServiceRegistry = Depends(get_services),
):
    """Get all orders for a customer"""
    try:
        return await services.order_service.get(
            f"/customer/{customer_pk}/orders?skip={skip}&limit={limit}"
        )
    except Exception as e:
        logger.error(f"Error getting customer orders: {e}")
        raise HTTPException(status_code=500, detail="Failed to get orders")


@app.patch("/order/{pk}", tags=["Orders"])
async def update_order(
    pk: int, req: OrderUpdateRequest, services: GatewayServiceRegistry = Depends(get_services)
):
    """Update an order"""
    try:
        return await services.order_service.patch(f"/order/{pk}", req.model_dump())
    except Exception as e:
        logger.error(f"Error updating order: {e}")
        raise HTTPException(status_code=500, detail="Failed to update order")


# ==================== HEALTH CHECK ====================
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "gateway"}


@app.get("/", tags=["Root"])
async def root():
    """API information"""
    return {
        "name": "E-Commerce API Gateway",
        "version": "1.0.0",
        "docs": "/docs",
        "services": [
            "Product Service",
            "Customer Service",
            "Inventory Service",
            "Pricing Service",
            "Order Service",
        ],
    }


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Close all service connections on shutdown"""
    await service_registry.close_all()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
