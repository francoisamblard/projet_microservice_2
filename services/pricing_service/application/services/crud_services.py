from infrastructure.db.repository import (
    PriceRepository,
    ProductRepository,
)
from application.dtos import (
    PriceCreateDTO,
    PriceUpdateDTO,
    PriceResponseDTO,
)
from typing import Optional, List


class PricingService:
    """Business logic for pricing"""

    def __init__(self, price_repo: PriceRepository, product_repo: ProductRepository):
        self.price_repo = price_repo
        self.product_repo = product_repo

    def create_price(self, dto: PriceCreateDTO) -> PriceResponseDTO:
        """Create a new price"""
        # Check if product exists
        product = self.product_repo.get_by_pk(dto.product_pk)
        if not product:
            raise ValueError(f"Product {dto.product_pk} not found")

        # Check if price already exists
        existing = self.price_repo.get_by_product_pk(dto.product_pk)
        if existing:
            raise ValueError(f"Price already exists for product {dto.product_pk}")

        price = self.price_repo.create(dto)
        return PriceResponseDTO(**price.to_dict())

    def get_price(self, pk: int) -> Optional[PriceResponseDTO]:
        """Get price by ID"""
        price = self.price_repo.get_by_pk(pk)
        if price:
            return PriceResponseDTO(**price.to_dict())
        return None

    def get_price_by_product(self, product_pk: int) -> Optional[PriceResponseDTO]:
        """Get price by product ID"""
        price = self.price_repo.get_by_product_pk(product_pk)
        if price:
            return PriceResponseDTO(**price.to_dict())
        return None

    def get_all_prices(self, skip: int = 0, limit: int = 100) -> List[PriceResponseDTO]:
        """Get all prices"""
        prices = self.price_repo.get_all(skip, limit)
        return [PriceResponseDTO(**p.to_dict()) for p in prices]

    def update_price(self, pk: int, dto: PriceUpdateDTO) -> Optional[PriceResponseDTO]:
        """Update a price"""
        price = self.price_repo.update(pk, dto)
        if price:
            return PriceResponseDTO(**price.to_dict())
        return None
