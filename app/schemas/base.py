from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

# Generic Type for data
T = TypeVar("T")

class BaseResponseModel(BaseModel, Generic[T]):
    """Base class for response models"""
    message: str
    data: Optional[T] = None  # Can be List, Dict, or Object

    class Config:
        """Base class for configuration"""
        from_attributes = True
