from infrastructure.db.repository import CustomerRepository
from application.dtos import (
    CustomerCreateDTO,
    CustomerUpdateDTO,
    CustomerResponseDTO,
)
from typing import Optional, List


class CustomerService:
    """Business logic for customers"""

    def __init__(self, repository: CustomerRepository):
        self.repository = repository

    def create_customer(self, dto: CustomerCreateDTO) -> CustomerResponseDTO:
        """Create a new customer"""
        # Check if email already exists
        existing = self.repository.get_by_email(dto.email)
        if existing:
            raise ValueError(f"Customer with email {dto.email} already exists")

        customer = self.repository.create(dto)
        return CustomerResponseDTO(**customer.to_dict())

    def get_customer(self, pk: int) -> Optional[CustomerResponseDTO]:
        """Get a customer by ID"""
        customer = self.repository.get_by_pk(pk)
        if customer:
            return CustomerResponseDTO(**customer.to_dict())
        return None

    def get_all_customers(self, skip: int = 0, limit: int = 100) -> List[CustomerResponseDTO]:
        """Get all customers"""
        customers = self.repository.get_all(skip, limit)
        return [CustomerResponseDTO(**c.to_dict()) for c in customers]

    def update_customer(self, pk: int, dto: CustomerUpdateDTO) -> Optional[CustomerResponseDTO]:
        """Update a customer"""
        customer = self.repository.update(pk, dto)
        if customer:
            return CustomerResponseDTO(**customer.to_dict())
        return None

    def delete_customer(self, pk: int) -> bool:
        """Delete a customer"""
        return self.repository.delete(pk)
