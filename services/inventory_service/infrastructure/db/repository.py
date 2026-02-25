from sqlalchemy.orm import Session
from domain.entities import Warehouse, Product, Inventory
from application.dtos import (
    WarehouseCreateDTO,
    InventoryCreateDTO,
    InventoryUpdateDTO,
)
from typing import Optional, List


class WarehouseRepository:
    """Warehouse repository"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, dto: WarehouseCreateDTO) -> Warehouse:
        """Create a new warehouse"""
        warehouse = Warehouse(name=dto.name, location=dto.location)
        self.session.add(warehouse)
        self.session.commit()
        self.session.refresh(warehouse)
        return warehouse

    def get_by_pk(self, pk: int) -> Optional[Warehouse]:
        """Get warehouse by primary key"""
        return self.session.query(Warehouse).filter(Warehouse.pk == pk).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Warehouse]:
        """Get all warehouses"""
        return self.session.query(Warehouse).offset(skip).limit(limit).all()


class ProductRepository:
    """Product repository (mirror)"""

    def __init__(self, session: Session):
        self.session = session

    def create_or_update(self, product_id: int, name: str, sku: str) -> Product:
        """Create or update a product"""
        product = self.session.query(Product).filter(Product.pk == product_id).first()
        if product:
            product.name = name
            product.sku = sku
        else:
            product = Product(pk=product_id, name=name, sku=sku)
            self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def get_by_pk(self, pk: int) -> Optional[Product]:
        """Get product by primary key"""
        return self.session.query(Product).filter(Product.pk == pk).first()


class InventoryRepository:
    """Inventory repository"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, dto: InventoryCreateDTO) -> Inventory:
        """Create inventory entry"""
        inventory = Inventory(
            product_pk=dto.product_pk,
            warehouse_pk=dto.warehouse_pk,
            quantity=dto.quantity,
            reserved=dto.reserved,
        )
        self.session.add(inventory)
        self.session.commit()
        self.session.refresh(inventory)
        return inventory

    def get_by_pk(self, pk: int) -> Optional[Inventory]:
        """Get inventory by primary key"""
        return self.session.query(Inventory).filter(Inventory.pk == pk).first()

    def get_by_product_and_warehouse(
        self, product_pk: int, warehouse_pk: int
    ) -> Optional[Inventory]:
        """Get inventory by product and warehouse"""
        return (
            self.session.query(Inventory)
            .filter(
                Inventory.product_pk == product_pk, Inventory.warehouse_pk == warehouse_pk
            )
            .first()
        )

    def get_by_product(self, product_pk: int) -> List[Inventory]:
        """Get all inventory entries for a product"""
        return self.session.query(Inventory).filter(Inventory.product_pk == product_pk).all()

    def update(self, pk: int, dto: InventoryUpdateDTO) -> Optional[Inventory]:
        """Update inventory"""
        inventory = self.get_by_pk(pk)
        if inventory:
            if dto.quantity is not None:
                inventory.quantity = dto.quantity
            if dto.reserved is not None:
                inventory.reserved = dto.reserved
            self.session.commit()
            self.session.refresh(inventory)
        return inventory

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Inventory]:
        """Get all inventory entries"""
        return self.session.query(Inventory).offset(skip).limit(limit).all()
