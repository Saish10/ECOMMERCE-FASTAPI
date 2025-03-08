from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.schemas.customers import CustomerResponse
from app.database import get_db  # Import DB dependency

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/", response_model=list[CustomerResponse])
def get_customers(db: Session = Depends(get_db)):
    """Fetch all customers"""
    return db.query(Customer).all()

@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Fetch customer by ID"""
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
