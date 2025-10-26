from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.database.models import Customer

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_customers(db: Session):
    """
    Retrieve all customers from the database.
    """
    return db.query(Customer).all()

def get_customer_by_id(db: Session, customer_id: int):
    """
    Retrieve a single customer by their ID.
    """
    return db.query(Customer).filter(Customer.id == customer_id).first()

def create_customer(db: Session, name: str, email: str, phone: str, address: str):
    """
    Create a new customer in the database.
    """
    new_customer = Customer(name=name, email=email or None, phone=phone, address=address)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

def update_customer(db: Session, customer_id: int, name: str, email: str, phone: str, address: str):
    """
    Update an existing customer in the database.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        customer.name = name
        customer.email = email or None
        customer.phone = phone
        customer.address = address
        db.commit()
        db.refresh(customer)
    return customer

def delete_customer(db: Session, customer_id: int):
    """
    Delete a customer from the database.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer:
        db.delete(customer)
        db.commit()