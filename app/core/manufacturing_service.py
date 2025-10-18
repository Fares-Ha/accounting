from sqlalchemy.orm import Session
from ..database import models
from .audit_service import AuditService
from .security import requires_roles

audit_service = AuditService()

@requires_roles(models.UserRole.ADMIN)
def create_bom(db: Session, user_id: int, product_id: int, name: str, description: str, items: list[dict]) -> models.BillOfMaterials:
    """
    Creates a new Bill of Materials (BOM).
    'items' is a list of dicts, each with 'component_id' and 'quantity'.
    """
    db_bom = models.BillOfMaterials(
        product_id=product_id,
        name=name,
        description=description
    )
    db.add(db_bom)
    db.flush()

    for item in items:
        db_item = models.BillOfMaterialsItem(
            bom_id=db_bom.id,
            component_id=item['component_id'],
            quantity=item['quantity']
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_bom)
    audit_service.create_audit_log(
        db,
        user_id=user_id,
        action="CREATE_BOM",
        details=f"User #{user_id} created new BOM #{db_bom.id} for product #{product_id}"
    )
    return db_bom

@requires_roles(models.UserRole.ADMIN)
def get_boms(db: Session, user_id: int) -> list[models.BillOfMaterials]:
    """
    Retrieves all Bills of Materials.
    """
    return db.query(models.BillOfMaterials).all()

@requires_roles(models.UserRole.ADMIN)
def get_bom(db: Session, user_id: int, bom_id: int) -> models.BillOfMaterials | None:
    """
    Retrieves a single Bill of Materials by its ID.
    """
    return db.query(models.BillOfMaterials).filter(models.BillOfMaterials.id == bom_id).first()

@requires_roles(models.UserRole.ADMIN)
def update_bom(db: Session, user_id: int, bom_id: int, product_id: int, name: str, description: str, items: list[dict]) -> models.BillOfMaterials:
    """
    Updates an existing Bill of Materials.
    """
    db_bom = get_bom(db, user_id, bom_id)
    if db_bom:
        db_bom.product_id = product_id
        db_bom.name = name
        db_bom.description = description

        # Clear old items
        for item in db_bom.items:
            db.delete(item)

        # Add new items
        for item in items:
            db_item = models.BillOfMaterialsItem(
                bom_id=db_bom.id,
                component_id=item['component_id'],
                quantity=item['quantity']
            )
            db.add(db_item)

        db.commit()
        db.refresh(db_bom)
        audit_service.create_audit_log(
            db,
            user_id=user_id,
            action="UPDATE_BOM",
            details=f"User #{user_id} updated BOM #{bom_id}"
        )
    return db_bom

@requires_roles(models.UserRole.ADMIN)
def delete_bom(db: Session, user_id: int, bom_id: int):
    """
    Deletes a Bill of Materials.
    """
    db_bom = get_bom(db, user_id, bom_id)
    if db_bom:
        audit_service.create_audit_log(
            db,
            user_id=user_id,
            action="DELETE_BOM",
            details=f"User #{user_id} deleted BOM #{bom_id}"
        )
        db.delete(db_bom)
        db.commit()
    return db_bom