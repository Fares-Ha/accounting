from sqlalchemy.orm import Session
from ..database import models

def get_categories(db: Session):
    """
    Retrieves all categories.
    """
    return db.query(models.ProductCategory).all()

def create_category(db: Session, name: str):
    """
    Creates a new category.
    """
    db_category = models.ProductCategory(name=name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def update_category(db: Session, category_id: int, name: str):
    """
    Updates an existing category.
    """
    db_category = db.query(models.ProductCategory).filter(models.ProductCategory.id == category_id).first()
    if db_category:
        db_category.name = name
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    """
    Deletes a category.
    """
    db_category = db.query(models.ProductCategory).filter(models.ProductCategory.id == category_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category
