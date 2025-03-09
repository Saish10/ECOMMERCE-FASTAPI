from datetime import date
from typing import List, Optional

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    PositiveInt,
    PositiveFloat,
)


class OrderItemSchema(BaseModel):
    """Schema for an order item"""

    product_id: PositiveInt
    quantity: PositiveInt = Field(
        description="Quantity must be greater than zero"
    )
    price: PositiveFloat = Field(ge=0, description="Price cannot be negative")

    @field_validator("quantity", mode="before")
    @classmethod
    def validate_quantity(cls, value):
        """Validate quantity"""
        if value <= 0:
            raise ValueError("Quantity must be greater than 0")
        return value

    @field_validator("price", mode="before")
    @classmethod
    def validate_price(cls, value):
        """Validate price"""
        if value < 0:
            raise ValueError("Price cannot be negative")
        return value


class OrderCreateSchema(BaseModel):
    """Schema for an order"""

    customer_id: PositiveInt
    order_date: date
    items: List[OrderItemSchema]

    @field_validator("order_date", mode="before")
    @classmethod
    def validate_order_date(cls, v):
        """Validate order date"""
        if isinstance(v, str):  # Convert string to date if needed
            v = date.fromisoformat(v)  # Convert 'YYYY-MM-DD' string to date

        if v < date.today():
            raise ValueError("Order date cannot be in the past")
        return v

    @field_validator("items")
    @classmethod
    def validate_max_items(cls, items):
        """Ensure a maximum of 3 products per order"""
        if len(items) > 3:
            raise ValueError("An order can have a maximum of 3 products.")
        return items


class OrderFilter(BaseModel):
    """Filter options for orders"""

    status: Optional[str] = None
    min_price: Optional[PositiveFloat] = None
    max_price: Optional[PositiveFloat] = None
    customer_id: Optional[PositiveInt] = None
    search: Optional[str] = None

class CustomerSchema(BaseModel):
    """Schema for Customer details"""
    id: int
    full_name: str

    class Config:
        """Configuration for CustomerSchema"""
        from_attributes = True

class OrderResponse(BaseModel):
    """Response schema for orders"""

    id: PositiveInt
    customer: CustomerSchema
    date: date
    status: str
    total_amount: PositiveFloat

    class Config:
        """Configuration for OrderResponse"""

        from_attributes = True


class OrderDetailResponse(OrderResponse):
    """Response schema for order details"""

    order_items: List[OrderItemSchema]

    class Config:
        """Configuration for OrderDetailResponse"""

        from_attributes = True
