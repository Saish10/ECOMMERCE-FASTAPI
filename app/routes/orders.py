from typing import List
from fastapi import Depends, APIRouter, HTTPException, Request, status

from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.orders import (
    OrderCreateSchema,
    OrderFilter,
    OrderResponse,
    OrderDetailResponse
)
from app.services.order import OrderService
from app.dependencies import router
from app.utils.pagination import PaginatedResponse, paginate

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", status_code=status.HTTP_201_CREATED, responses={
    201: {"description": "Order created successfully"},
    400: {"description": "Bad request"},
    500: {"description": "Internal server error"}
})
def create(order: OrderCreateSchema, db: Session = Depends(get_db)):
    """Create a new order"""
    is_success, message, status_code = OrderService(db).create_order(order)
    if not is_success:
        raise HTTPException(status_code=status_code, detail=message)
    db.commit()
    return {"message": message}


@router.get("/", response_model=PaginatedResponse[OrderResponse])
def order_list(
    request: Request,
    filters: OrderFilter = Depends(),
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    """Retrieve orders with optional filtering and pagination"""
    is_success, message, query = OrderService(db).get_orders(filters)  # Return query, not list

    if not is_success:
        raise HTTPException(status_code=query, detail=message)

    return paginate(query, page, page_size, request)

@router.get("/{order_id}", response_model=OrderDetailResponse)
def detail(order_id: int, db: Session = Depends(get_db)):
    """Return Order Detail"""
    is_success, message, result = OrderService(db).get_order(order_id)
    if not is_success:
        raise HTTPException(status_code=result, detail=message)
    return result

@router.delete("/{order_id}", response_model=dict)
def delete(order_id: int, db: Session = Depends(get_db)):
    """Delete an order"""
    is_success, message, status_code = OrderService(db).delete_order(order_id)
    if not is_success:
        raise HTTPException(status_code=status_code, detail=message)
    db.commit()
    return {"message": message}

@router.get("/customer/{customer_id}", response_model=List[OrderResponse])
def customer_orders(customer_id: int, db: Session = Depends(get_db)):
    """Return customer orders"""
    is_success, message, result = OrderService(db).get_customer_orders(customer_id)
    if not is_success:
        raise HTTPException(status_code=result, detail=message)
    return result