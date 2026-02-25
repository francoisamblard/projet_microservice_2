from sqlalchemy.orm import Session
from domain.entities import Customer
from application.dtos import CustomerCreateDTO, CustomerUpdateDTO
from typing import Optional, List


class CustomerRepository:
    """Customer repository for database operations"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, dto: CustomerCreateDTO) -> Customer:
        """Create a new customer"""
        customer = Customer(
            name=dto.name,
            email=dto.email,
            phone=dto.phone,
            customer_type=dto.customer_type,
            price_category=dto.price_category,
            credit_limit=dto.credit_limit,
        )
        self.session.add(customer)
        self.session.commit()
        self.session.refresh(customer)
        return customer

    def get_by_pk(self, pk: int) -> Optional[Customer]:
        """Get customer by primary key"""
        return self.session.query(Customer).filter(Customer.pk == pk).first()

    def get_by_email(self, email: str) -> Optional[Customer]:
        """Get customer by email"""
        return self.session.query(Customer).filter(Customer.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """Get all customers with pagination"""
        return self.session.query(Customer).offset(skip).limit(limit).all()

    def update(self, pk: int, dto: CustomerUpdateDTO) -> Optional[Customer]:
        """Update a customer"""
        customer = self.get_by_pk(pk)
        if customer:
            if dto.name is not None:
                customer.name = dto.name
            if dto.phone is not None:
                customer.phone = dto.phone
            if dto.price_category is not None:
                customer.price_category = dto.price_category
            if dto.credit_limit is not None:
                customer.credit_limit = dto.credit_limit
            self.session.commit()
            self.session.refresh(customer)
        return customer

    def delete(self, pk: int) -> bool:
        """Delete a customer"""
        customer = self.get_by_pk(pk)
        if customer:
            self.session.delete(customer)
            self.session.commit()
            return True
        return False
