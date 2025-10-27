from sqlalchemy.orm import Session
from ..database import models

def get_categories(db: Session):
    """
    Retrieves all categories.
    """
    return db.query(models.ProductCategory).all()
