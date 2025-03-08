from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

from pydantic import BaseModel, field_validator


class ProductBase(BaseModel):
    """Base class for Product."""

    name: str
    stock_quantity: int
    price: Decimal

    @field_validator("price")
    @classmethod
    def validate_price(cls, value: Decimal) -> Decimal:
        """Validate price field."""
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class ProductCreate(ProductBase):
    """Schema for creating a Product."""


class ProductUpdate(ProductBase):
    """Schema for updating a Product with optional fields."""

    name: Optional[str] = None
    stock_quantity: Optional[int] = None
    price: Optional[Decimal] = None


class ProductResponse(ProductBase):
    """
    Response schema for a Product.
    """

    id: int

    class Config:
        """Configuration for ProductResponse."""

        from_attributes = True  # Ensures ORM compatibility
