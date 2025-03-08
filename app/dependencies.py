from fastapi import APIRouter
from sqlalchemy.orm import Session

router = APIRouter()


class BaseService:
    """Base class for services"""
    def __init__(self, db: Session):
        self.db = db
