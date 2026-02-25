from infrastructure.db.repository import (
    InventoryRepository,
    WarehouseRepository,
    ProductRepository,
)
from application.dtos import (
    InventoryCreateDTO,
    InventoryUpdateDTO,
    InventoryResponseDTO,
    WarehouseCreateDTO,
    WarehouseResponseDTO,
)
from typing import Optional, List


class InventoryService:
    """Business logic for inventory"""

    def __init__(
        self,
        inventory_repo: InventoryRepository,
        warehouse_repo: WarehouseRepository,
        product_repo: ProductRepository,
    ):
        self.inventory_repo = inventory_repo
        self.warehouse_repo = warehouse_repo
        self.product_repo = product_repo

    def create_warehouse(self, dto: WarehouseCreateDTO) -> WarehouseResponseDTO:
        """Create a new warehouse"""
        warehouse = self.warehouse_repo.create(dto)
        return WarehouseResponseDTO(**warehouse.to_dict())

    def get_warehouse(self, pk: int) -> Optional[WarehouseResponseDTO]:
        """Get warehouse by ID"""
        warehouse = self.warehouse_repo.get_by_pk(pk)
        if warehouse:
            return WarehouseResponseDTO(**warehouse.to_dict())
        return None

    def get_all_warehouses(self, skip: int = 0, limit: int = 100) -> List[WarehouseResponseDTO]:
        """Get all warehouses"""
        warehouses = self.warehouse_repo.get_all(skip, limit)
        return [WarehouseResponseDTO(**w.to_dict()) for w in warehouses]

    def create_inventory(self, dto: InventoryCreateDTO) -> InventoryResponseDTO:
        """Create inventory entry"""
        # Check if warehouse exists
        warehouse = self.warehouse_repo.get_by_pk(dto.warehouse_pk)
        if not warehouse:
            raise ValueError(f"Warehouse {dto.warehouse_pk} not found")

        # Check if product exists in this service
        product = self.product_repo.get_by_pk(dto.product_pk)
        if not product:
            raise ValueError(f"Product {dto.product_pk} not found in this service")

        # Check if already exists
        existing = self.inventory_repo.get_by_product_and_warehouse(
            dto.product_pk, dto.warehouse_pk
        )
        if existing:
            raise ValueError(
                f"Inventory already exists for product {dto.product_pk} in warehouse {dto.warehouse_pk}"
            )

        inventory = self.inventory_repo.create(dto)
        return InventoryResponseDTO(**inventory.to_dict())

    def get_inventory(self, pk: int) -> Optional[InventoryResponseDTO]:
        """Get inventory by ID"""
        inventory = self.inventory_repo.get_by_pk(pk)
        if inventory:
            return InventoryResponseDTO(**inventory.to_dict())
        return None

    def get_inventory_by_product_warehouse(
        self, product_pk: int, warehouse_pk: int
    ) -> Optional[InventoryResponseDTO]:
        """Get inventory by product and warehouse"""
        inventory = self.inventory_repo.get_by_product_and_warehouse(product_pk, warehouse_pk)
        if inventory:
            return InventoryResponseDTO(**inventory.to_dict())
        return None

    def get_inventory_by_product(self, product_pk: int) -> List[InventoryResponseDTO]:
        """Get all inventory entries for a product"""
        inventories = self.inventory_repo.get_by_product(product_pk)
        return [InventoryResponseDTO(**i.to_dict()) for i in inventories]

    def get_all_inventory(self, skip: int = 0, limit: int = 100) -> List[InventoryResponseDTO]:
        """Get all inventory entries"""
        inventories = self.inventory_repo.get_all(skip, limit)
        return [InventoryResponseDTO(**i.to_dict()) for i in inventories]

    def update_inventory(self, pk: int, dto: InventoryUpdateDTO) -> Optional[InventoryResponseDTO]:
        """Update inventory"""
        inventory = self.inventory_repo.update(pk, dto)
        if inventory:
            return InventoryResponseDTO(**inventory.to_dict())
        return None

    def check_stock(self, product_pk: int, quantity: int) -> bool:
        """Check if product has enough stock in any warehouse"""
        inventories = self.inventory_repo.get_by_product(product_pk)
        total_available = sum(
            max(0, inv.quantity - inv.reserved) for inv in inventories
        )
        return total_available >= quantity
