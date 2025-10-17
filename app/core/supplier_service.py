from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.database.models import Supplier

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_all_suppliers(db: Session):
    """
    Retrieve all suppliers from the database.
    """
    return db.query(Supplier).all()

def get_supplier_by_id(db: Session, supplier_id: int):
    """
    Retrieve a single supplier by their ID.
    """
    return db.query(Supplier).filter(Supplier.id == supplier_id).first()

def create_supplier(db: Session, name: str, email: str, phone: str, address: str):
    """
    Create a new supplier in the database.
    """
    new_supplier = Supplier(name=name, email=email, phone=phone, address=address)
    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)
    return new_supplier

def update_supplier(db: Session, supplier_id: int, name: str, email: str, phone: str, address: str):
    """
    Update an existing supplier in the database.
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if supplier:
        supplier.name = name
        supplier.email = email
        supplier.phone = phone
        supplier.address = address
        db.commit()
        db.refresh(supplier)
    return supplier

def delete_supplier(db: Session, supplier_id: int):
    """
    Delete a supplier from the database.
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if supplier:
        db.delete(supplier)
        db.commit()