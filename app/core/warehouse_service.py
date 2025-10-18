from sqlalchemy.orm import Session
from ..database import models
from .audit_service import AuditService

audit_service = AuditService()

def create_warehouse(db: Session, user_id: int, name: str, location: str) -> models.Warehouse:
    """
    Creates a new warehouse.
    """
    db_warehouse = models.Warehouse(name=name, location=location)
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    audit_service.create_audit_log(
        db,
        user_id=user_id,
        action="CREATE_WAREHOUSE",
        details=f"User #{user_id} created new warehouse #{db_warehouse.id} with name '{name}'"
    )
    return db_warehouse

def get_warehouses(db: Session) -> list[models.Warehouse]:
    """
    Retrieves all warehouses.
    """
    return db.query(models.Warehouse).all()

def get_warehouse(db: Session, warehouse_id: int) -> models.Warehouse | None:
    """
    Retrieves a single warehouse by its ID.
    """
    return db.query(models.Warehouse).filter(models.Warehouse.id == warehouse_id).first()

def update_warehouse(db: Session, user_id: int, warehouse_id: int, name: str, location: str) -> models.Warehouse:
    """
    Updates an existing warehouse.
    """
    db_warehouse = get_warehouse(db, warehouse_id)
    if db_warehouse:
        db_warehouse.name = name
        db_warehouse.location = location
        db.commit()
        db.refresh(db_warehouse)
        audit_service.create_audit_log(
            db,
            user_id=user_id,
            action="UPDATE_WAREHOUSE",
            details=f"User #{user_id} updated warehouse #{warehouse_id}"
        )
    return db_warehouse

def delete_warehouse(db: Session, user_id: int, warehouse_id: int):
    """
    Deletes a warehouse.
    """
    db_warehouse = get_warehouse(db, warehouse_id)
    if db_warehouse:
        # Add logic here to ensure warehouse is empty before deletion
        if db_warehouse.inventory_levels:
            raise ValueError("Cannot delete a warehouse that has inventory.")

        audit_service.create_audit_log(
            db,
            user_id=user_id,
            action="DELETE_WAREHOUSE",
            details=f"User #{user_id} deleted warehouse #{warehouse_id}"
        )
        db.delete(db_warehouse)
        db.commit()
    return db_warehouse