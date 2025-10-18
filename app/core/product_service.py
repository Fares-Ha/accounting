from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import models
from ..database.models import InventoryMovementReason
from .audit_service import AuditService

audit_service = AuditService()

def get_stock_level(db: Session, product_id: int, warehouse_id: int) -> int:
    """
    Gets the stock level for a product in a specific warehouse.
    """
    inventory_level = db.query(models.InventoryLevel).filter_by(product_id=product_id, warehouse_id=warehouse_id).first()
    return inventory_level.quantity if inventory_level else 0

def get_total_stock(db: Session, product_id: int) -> int:
    """
    Gets the total stock for a product across all warehouses.
    """
    total_stock = db.query(func.sum(models.InventoryLevel.quantity)).filter_by(product_id=product_id).scalar()
    return total_stock or 0

def adjust_stock_level(db: Session, product_id: int, warehouse_id: int, quantity_change: int, reason: InventoryMovementReason, user_id: int = None):
    """
    Adjusts the stock level of a product in a specific warehouse and records the movement.
    """
    inventory_level = db.query(models.InventoryLevel).filter_by(product_id=product_id, warehouse_id=warehouse_id).first()
    if not inventory_level:
        inventory_level = models.InventoryLevel(product_id=product_id, warehouse_id=warehouse_id, quantity=0)
        db.add(inventory_level)

    inventory_level.quantity += quantity_change

    movement = models.InventoryMovement(
        product_id=product_id,
        warehouse_id=warehouse_id,
        quantity_change=quantity_change,
        reason=reason
    )
    db.add(movement)

    if user_id:
        product = get_product(db, product_id)
        audit_service.create_audit_log(
            db,
            user_id=user_id,
            action="STOCK_ADJUSTMENT",
            details=f"Product '{product.name}' stock in warehouse #{warehouse_id} changed by {quantity_change} due to {reason.value}"
        )

    db.commit()

def create_product(db: Session, name: str, description: str, price: int, category_id: int = None, low_stock_threshold: int = 0, initial_stock: list = None):
    """
    Creates a new product and its initial stock in specified warehouses.
    initial_stock is a list of dicts: [{'warehouse_id': 1, 'quantity': 100}]
    """
    db_product = models.Product(
        name=name,
        description=description,
        price=price,
        category_id=category_id,
        low_stock_threshold=low_stock_threshold
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    if initial_stock:
        for stock_info in initial_stock:
            adjust_stock_level(db, db_product.id, stock_info['warehouse_id'], stock_info['quantity'], InventoryMovementReason.INITIAL_STOCK)

    return db_product

def get_products(db: Session):
    """
    Retrieves all products.
    """
    return db.query(models.Product).all()

def get_product(db: Session, product_id: int):
    """
    Retrieves a single product by its ID.
    """
    return db.query(models.Product).filter(models.Product.id == product_id).first()

def update_product(db: Session, user_id: int, product_id: int, name: str, description: str, price: int, category_id: int = None, low_stock_threshold: int = 0):
    """
    Updates an existing product. Stock is managed separately.
    """
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product:
        db_product.name = name
        db_product.description = description
        db_product.price = price
        db_product.category_id = category_id
        db_product.low_stock_threshold = low_stock_threshold
        db.commit()
        db.refresh(db_product)

        audit_service.create_audit_log(
            db,
            user_id=user_id,
            action="UPDATE_PRODUCT",
            details=f"User #{user_id} updated product '{name}' (ID: {product_id})"
        )

    return db_product

def delete_product(db: Session, product_id: int):
    """
    Deletes a product.
    """
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product

def get_low_stock_products(db: Session):
    """
    Retrieves all products where the total stock quantity is below the low stock threshold.
    """
    return db.query(models.Product).join(models.Product.inventory_levels).group_by(models.Product.id).having(func.sum(models.InventoryLevel.quantity) < models.Product.low_stock_threshold).all()

def get_inventory_movements(db: Session, product_id: int, warehouse_id: int = None):
    """
    Retrieves all inventory movements for a given product.
    Can be filtered by warehouse.
    """
    query = db.query(models.InventoryMovement).filter(models.InventoryMovement.product_id == product_id)
    if warehouse_id:
        query = query.filter(models.InventoryMovement.warehouse_id == warehouse_id)
    return query.order_by(models.InventoryMovement.created_at.desc()).all()