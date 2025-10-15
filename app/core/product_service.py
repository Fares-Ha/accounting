from sqlalchemy.orm import Session
from ..database import models
from ..database.models import InventoryMovementReason

def adjust_stock_quantity(db: Session, product: models.Product, quantity_change: int, reason: InventoryMovementReason):
    """
    Adjusts the stock quantity of a product and records the movement.
    """
    product.stock_quantity += quantity_change
    movement = models.InventoryMovement(
        product_id=product.id,
        quantity_change=quantity_change,
        reason=reason
    )
    db.add(movement)
    db.commit()
    db.refresh(product)

def create_product(db: Session, name: str, description: str, price: int, stock_quantity: int, category_id: int = None, low_stock_threshold: int = 0):
    """
    Creates a new product and its initial stock.
    """
    db_product = models.Product(
        name=name,
        description=description,
        price=price,
        stock_quantity=0,  # Start with 0, then adjust
        category_id=category_id,
        low_stock_threshold=low_stock_threshold
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    if stock_quantity > 0:
        adjust_stock_quantity(db, db_product, stock_quantity, InventoryMovementReason.INITIAL_STOCK)

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

def update_product(db: Session, product_id: int, name: str, description: str, price: int, stock_quantity: int, category_id: int = None, low_stock_threshold: int = 0):
    """
    Updates an existing product.
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

        # Adjust stock if it has changed
        if stock_quantity != db_product.stock_quantity:
            quantity_change = stock_quantity - db_product.stock_quantity
            adjust_stock_quantity(db, db_product, quantity_change, InventoryMovementReason.MANUAL_UPDATE)

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
    Retrieves all products where the stock quantity is below the low stock threshold.
    """
    return db.query(models.Product).filter(models.Product.stock_quantity < models.Product.low_stock_threshold).all()

def get_inventory_movements(db: Session, product_id: int):
    """
    Retrieves all inventory movements for a given product.
    """
    return db.query(models.InventoryMovement).filter(models.InventoryMovement.product_id == product_id).order_by(models.InventoryMovement.created_at.desc()).all()

def adjust_stock(db: Session, product_id: int, quantity_change: int, reason: models.InventoryMovementReason):
    product = get_product(db, product_id)
    if not product:
        return None

    adjust_stock_quantity(db, product, quantity_change, reason)
    return product