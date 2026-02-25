from sqlalchemy.orm import Session
from domain.entities import Product
from application.dtos import ProductCreateDTO, ProductUpdateDTO
from typing import Optional, List


class ProductRepository:
    """Product repository for database operations"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, dto: ProductCreateDTO) -> Product:
        """Create a new product"""
        product = Product(
            name=dto.name,
            description=dto.description,
            sku=dto.sku,
            base_price=dto.base_price,
        )
        self.session.add(product)
        self.session.commit()
        self.session.refresh(product)
        return product

    def get_by_pk(self, pk: int) -> Optional[Product]:
        """Get product by primary key"""
        return self.session.query(Product).filter(Product.pk == pk).first()

    def get_by_sku(self, sku: str) -> Optional[Product]:
        """Get product by SKU"""
        return self.session.query(Product).filter(Product.sku == sku).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get all products with pagination"""
        return self.session.query(Product).offset(skip).limit(limit).all()

    def update(self, pk: int, dto: ProductUpdateDTO) -> Optional[Product]:
        """Update a product"""
        product = self.get_by_pk(pk)
        if product:
            if dto.name is not None:
                product.name = dto.name
            if dto.description is not None:
                product.description = dto.description
            if dto.base_price is not None:
                product.base_price = dto.base_price
            self.session.commit()
            self.session.refresh(product)
        return product

    def delete(self, pk: int) -> bool:
        """Delete a product"""
        product = self.get_by_pk(pk)
        if product:
            self.session.delete(product)
            self.session.commit()
            return True
        return False
