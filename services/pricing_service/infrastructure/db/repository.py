from sqlalchemy.orm import Session
from domain.entities import Product, Price
from application.dtos import PriceCreateDTO, PriceUpdateDTO
from typing import Optional, List


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


class PriceRepository:
    """Price repository"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, dto: PriceCreateDTO) -> Price:
        """Create a new price"""
        final_price = dto.base_price * (1 - dto.discount_percent / 100)
        price = Price(
            product_pk=dto.product_pk,
            base_price=dto.base_price,
            discount_percent=dto.discount_percent,
            final_price=final_price,
            currency=dto.currency,
        )
        self.session.add(price)
        self.session.commit()
        self.session.refresh(price)
        return price

    def get_by_pk(self, pk: int) -> Optional[Price]:
        """Get price by primary key"""
        return self.session.query(Price).filter(Price.pk == pk).first()

    def get_by_product_pk(self, product_pk: int) -> Optional[Price]:
        """Get price by product PK"""
        return self.session.query(Price).filter(Price.product_pk == product_pk).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Price]:
        """Get all prices"""
        return self.session.query(Price).offset(skip).limit(limit).all()

    def update(self, pk: int, dto: PriceUpdateDTO) -> Optional[Price]:
        """Update a price"""
        price = self.get_by_pk(pk)
        if price:
            if dto.base_price is not None:
                price.base_price = dto.base_price
            if dto.discount_percent is not None:
                price.discount_percent = dto.discount_percent
            # Recalculate final price
            price.final_price = price.base_price * (1 - price.discount_percent / 100)
            self.session.commit()
            self.session.refresh(price)
        return price
