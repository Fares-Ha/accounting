from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel
from .customer_widget import CustomerWidget
from .supplier_widget import SupplierWidget

class MainWindow(QMainWindow):
    """
    The main application window, which appears after successful login.
    """
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Al Ameen - Logged in as {self.user.username} ({self.user.role.value})")
        self.setMinimumSize(800, 600)

        # Create the tab widget and set it as the central widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add the customer management widget
        self.customer_widget = CustomerWidget()
        self.tabs.addTab(self.customer_widget, "Customers")

        # Add the supplier management widget
        self.supplier_widget = SupplierWidget()
        self.tabs.addTab(self.supplier_widget, "Suppliers")

        # Add placeholder tabs for the other main modules
        self.tabs.addTab(QLabel("Products content will go here"), "Products")
        self.tabs.addTab(QLabel("Sales content will go here"), "Sales")