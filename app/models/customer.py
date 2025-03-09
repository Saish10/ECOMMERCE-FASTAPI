from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Customer(Base):
    """Customer model"""

    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=False)
    city = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    zip_code = Column(String(10), nullable=False)

    orders = relationship(
        "Order", back_populates="customer", cascade="all, delete"
    )

    def __repr__(self):
        return str(self.id)

    @property
    def full_name(self):
        """Return the full name of the customer"""
        return f"{self.first_name} {self.last_name}"