from infrastructure.db.repository import ProductRepository
from application.dtos import (
    ProductCreateDTO,
    ProductUpdateDTO,
    ProductResponseDTO,
)
from typing import Optional, List


class ProductService:
    """Business logic for products"""

    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def create_product(self, dto: ProductCreateDTO) -> ProductResponseDTO:
        """Create a new product"""
        # Check if SKU already exists
        existing = self.repository.get_by_sku(dto.sku)
        if existing:
            raise ValueError(f"Product with SKU {dto.sku} already exists")

        product = self.repository.create(dto)
        return ProductResponseDTO(**product.to_dict())

    def get_product(self, pk: int) -> Optional[ProductResponseDTO]:
        """Get a product by ID"""
        product = self.repository.get_by_pk(pk)
        if product:
            return ProductResponseDTO(**product.to_dict())
        return None

    def get_all_products(self, skip: int = 0, limit: int = 100) -> List[ProductResponseDTO]:
        """Get all products"""
        products = self.repository.get_all(skip, limit)
        return [ProductResponseDTO(**p.to_dict()) for p in products]

    def update_product(self, pk: int, dto: ProductUpdateDTO) -> Optional[ProductResponseDTO]:
        """Update a product"""
        product = self.repository.update(pk, dto)
        if product:
            return ProductResponseDTO(**product.to_dict())
        return None

    def delete_product(self, pk: int) -> bool:
        """Delete a product"""
        return self.repository.delete(pk)
