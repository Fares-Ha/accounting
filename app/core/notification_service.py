"""
This module provides the NotificationService, which is responsible for generating notifications for important events, such as low stock, overdue invoices, and upcoming payment dues. The NotificationService is used by the NotificationWidget to display these notifications to the user.
"""
from sqlalchemy.orm import Session
from ..database import models
from . import product_service

class NotificationService:
    """
    Service for generating notifications.
    """

    def get_low_stock_notifications(self, db: Session):
        """
        Returns a list of products that are below their low stock threshold.
        """
        return product_service.get_low_stock_products(db)

    def get_overdue_invoices(self, db: Session):
        """
        Returns a list of invoices that are overdue.
        """
        from datetime import datetime
        overdue_invoices = (
            db.query(models.Invoice)
            .filter(models.Invoice.due_date < datetime.utcnow())
            .filter(models.Invoice.status == models.InvoiceStatus.SENT)
            .all()
        )
        return overdue_invoices

    def get_upcoming_payment_dues(self, db: Session):
        """
        Returns a list of invoices that are due soon.
        """
        from datetime import datetime, timedelta
        upcoming_dues = (
            db.query(models.Invoice)
            .filter(models.Invoice.due_date >= datetime.utcnow())
            .filter(models.Invoice.due_date <= datetime.utcnow() + timedelta(days=7))
            .filter(models.Invoice.status == models.InvoiceStatus.SENT)
            .all()
        )
        return upcoming_dues