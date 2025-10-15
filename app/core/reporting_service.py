from sqlalchemy.orm import Session
from ..database.models import SalesOrder, SalesOrderItem, Product
from sqlalchemy import func
from datetime import datetime

class ReportingService:
    """
    Service for generating reports.
    """

    def get_sales_report(self, db: Session, start_date: datetime, end_date: datetime):
        """
        Generates a sales report for a given date range.
        """
        sales_data = (
            db.query(
                Product.name,
                func.sum(SalesOrderItem.quantity).label("total_quantity"),
                func.sum(SalesOrderItem.quantity * SalesOrderItem.price_per_unit).label("total_revenue"),
            )
            .join(SalesOrderItem, SalesOrder.items)
            .join(Product, SalesOrderItem.product)
            .filter(SalesOrder.created_at.between(start_date, end_date))
            .group_by(Product.name)
            .order_by(Product.name)
            .all()
        )
        return sales_data

    def get_inventory_report(self, db: Session):
        """
        Generates a report on the current inventory status.
        """
        inventory_data = (
            db.query(
                Product.name,
                Product.stock_quantity,
                Product.low_stock_threshold,
            )
            .order_by(Product.name)
            .all()
        )
        return inventory_data