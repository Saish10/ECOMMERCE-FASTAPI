from pydantic import BaseModel, EmailStr, Field


class CustomerBase(BaseModel):
    """Base schema for Customer."""
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr
    phone: str | None = Field(None, max_length=20)
    address: str = Field(..., max_length=255)
    city: str = Field(..., max_length=50)
    state: str = Field(..., max_length=50)
    zip_code: str = Field(..., max_length=10)


class CustomerCreate(CustomerBase):
    """Schema for creating a new Customer."""



class CustomerUpdate(BaseModel):
    """Schema for updating a Customer."""
    first_name: str | None = Field(None, max_length=50)
    last_name: str | None = Field(None, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    address: str | None = Field(None, max_length=255)
    city: str | None = Field(None, max_length=50)
    state: str | None = Field(None, max_length=50)
    zip_code: str | None = Field(None, max_length=10)


class CustomerResponse(CustomerBase):
    """Response schema for a Customer."""
    id: int

    class Config:
        """Schema for creating a new Config."""
        from_attributes = True  # Allows automatic conversion from ORM models
