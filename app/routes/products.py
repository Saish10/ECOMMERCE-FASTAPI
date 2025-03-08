from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.products import ProductService
from app.schemas.products import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    """Retrieve all products."""
    is_success, message, result = ProductService(db).get_all_products()
    if not is_success:
        raise HTTPException(status_code=result, detail=message)
    return result


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific product."""
    is_success, message, result = ProductService(db).get_product(product_id)
    if not is_success:
        raise HTTPException(status_code=result, detail=message)
    return result


@router.post("/", response_model=dict)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    is_success, message, status_code = ProductService(db).create_product(
        product
    )
    if not is_success:
        raise HTTPException(status_code=status_code, detail=message)
    db.commit()
    return {"message": message}


@router.put("/{product_id}", response_model=dict)
def update_product(
    product_id: int, data: ProductUpdate, db: Session = Depends(get_db)
):
    """Update an existing product."""
    is_success, message, status_code = ProductService(db).update_product(
        product_id, data
    )
    if not is_success:
        raise HTTPException(status_code=status_code, detail=message)
    db.commit()
    return {"message": message}


@router.delete("/{product_id}", response_model=dict)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product."""
    is_success, message, status_code = ProductService(db).delete_product(
        product_id
    )
    if not is_success:
        raise HTTPException(status_code=status_code, detail=message)
    db.commit()
    return {"message": message}
