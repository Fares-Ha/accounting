from sqlalchemy.orm import Session
from ..database import models

def create_category(db: Session, name: str):
    db_category = models.ProductCategory(name=name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_categories(db: Session):
    return db.query(models.ProductCategory).all()

def get_category(db: Session, category_id: int):
    return db.query(models.ProductCategory).filter(models.ProductCategory.id == category_id).first()

def update_category(db: Session, category_id: int, name: str):
    db_category = get_category(db, category_id)
    if db_category:
        db_category.name = name
        db.commit()
        db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    db_category = get_category(db, category_id)
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category