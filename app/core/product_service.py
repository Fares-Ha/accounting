from sqlalchemy.orm import Session
from ..database import models

def create_product(db: Session, name: str, description: str, price: int, stock_quantity: int):
    """
    Creates a new product.
    """
    db_product = models.Product(
        name=name,
        description=description,
        price=price,
        stock_quantity=stock_quantity
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
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

def update_product(db: Session, product_id: int, name: str, description: str, price: int, stock_quantity: int):
    """
    Updates an existing product.
    """
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product:
        db_product.name = name
        db_product.description = description
        db_product.price = price
        db_product.stock_quantity = stock_quantity
        db.commit()
        db.refresh(db_product)
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