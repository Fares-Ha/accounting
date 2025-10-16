from sqlalchemy.orm import Session
from ..database.models import Supplier

class SupplierService:
    def get_all_suppliers(self, db: Session):
        """
        Retrieve all suppliers from the database.
        """
        return db.query(Supplier).all()

    def get_supplier_by_id(self, db: Session, supplier_id: int):
        """
        Retrieve a single supplier by their ID.
        """
        return db.query(Supplier).filter(Supplier.id == supplier_id).first()

    def create_supplier(self, db: Session, name: str, email: str, phone: str, address: str):
        """
        Create a new supplier in the database.
        """
        new_supplier = Supplier(name=name, email=email, phone=phone, address=address)
        db.add(new_supplier)
        db.commit()
        db.refresh(new_supplier)
        return new_supplier

    def update_supplier(self, db: Session, supplier_id: int, name: str, email: str, phone: str, address: str):
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

    def delete_supplier(self, db: Session, supplier_id: int):
        """
        Delete a supplier from the database.
        """
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if supplier:
            db.delete(supplier)
            db.commit()