from sqlalchemy.orm import Session
from ..database import models

class NotificationService:
    """
    Service for generating notifications.
    """

    def get_low_stock_notifications(self, db: Session):
        """
        Returns a list of products that are below their low stock threshold.
        """
        low_stock_products = (
            db.query(models.Product)
            .filter(models.Product.stock_quantity < models.Product.low_stock_threshold)
            .all()
        )
        return low_stock_products