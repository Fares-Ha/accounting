from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PyQt6.QtCore import QCoreApplication
from ..core.notification_service import NotificationService
from ..database.database import get_db

class NotificationWidget(QWidget):
    """
    Widget for displaying notifications.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.notification_service = NotificationService()

        layout = QVBoxLayout(self)
        self.notification_list = QListWidget()
        layout.addWidget(self.notification_list)

        self.load_notifications()

    def load_notifications(self):
        self.notification_list.clear()
        with get_db() as db_session:
            # Low stock notifications
            low_stock_products = self.notification_service.get_low_stock_notifications(db_session)
            for product in low_stock_products:
                item = QListWidgetItem(self.tr("Low stock for {}: {} remaining").format(product.name, product.stock_quantity))
                self.notification_list.addItem(item)

            # Overdue invoice notifications
            overdue_invoices = self.notification_service.get_overdue_invoices(db_session)
            for invoice in overdue_invoices:
                item = QListWidgetItem(self.tr("Invoice #{} is overdue. Due date: {}").format(invoice.id, invoice.due_date.strftime('%Y-%m-%d')))
                self.notification_list.addItem(item)

            # Upcoming payment due notifications
            upcoming_dues = self.notification_service.get_upcoming_payment_dues(db_session)
            for invoice in upcoming_dues:
                item = QListWidgetItem(self.tr("Payment for invoice #{} is due soon. Due date: {}").format(invoice.id, invoice.due_date.strftime('%Y-%m-%d')))
                self.notification_list.addItem(item)