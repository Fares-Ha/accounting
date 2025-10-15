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
        self.db_session = next(get_db())

        layout = QVBoxLayout(self)
        self.notification_list = QListWidget()
        layout.addWidget(self.notification_list)

        self.load_notifications()

    def load_notifications(self):
        self.notification_list.clear()
        low_stock_products = self.notification_service.get_low_stock_notifications(self.db_session)
        for product in low_stock_products:
            item = QListWidgetItem(f"Low stock for {product.name}: {product.stock_quantity} remaining")
            self.notification_list.addItem(item)