from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel
from PyQt6.QtCore import QCoreApplication
from .customer_widget import CustomerWidget
from .supplier_widget import SupplierWidget
from .product_widget import ProductWidget
from .category_widget import CategoryWidget
from .sales_widget import SalesWidget
from .purchase_widget import PurchaseWidget
from .ledger_widget import LedgerWidget
from .reporting_widget import ReportingWidget
from ..database.models import UserRole

class MainWindow(QMainWindow):
    """
    The main application window, which appears after successful login.
    """
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle(self.tr("Ajyad Accountant - Logged in as {} ({})").format(self.user.username, self.user.role.value))
        self.setMinimumSize(800, 600)

        # Create the tab widget and set it as the central widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add the customer management widget
        self.customer_widget = CustomerWidget()
        self.tabs.addTab(self.customer_widget, self.tr("Customers"))

        # Add the supplier management widget
        self.supplier_widget = SupplierWidget()
        self.tabs.addTab(self.supplier_widget, self.tr("Suppliers"))

        # Add the product management widget
        self.product_widget = ProductWidget()
        self.tabs.addTab(self.product_widget, self.tr("Products"))

        # Add the category management widget
        self.category_widget = CategoryWidget()
        self.tabs.addTab(self.category_widget, self.tr("Categories"))

        # Add the sales management widget
        self.sales_widget = SalesWidget()
        self.tabs.addTab(self.sales_widget, self.tr("Sales"))

        # Add the purchase management widget - Admin and Accountant only
        if self.user.role in [UserRole.ADMIN, UserRole.ACCOUNTANT]:
            self.purchase_widget = PurchaseWidget()
            self.tabs.addTab(self.purchase_widget, self.tr("Purchases"))

        # Add the ledger widget - Admin and Accountant only
        if self.user.role in [UserRole.ADMIN, UserRole.ACCOUNTANT]:
            self.ledger_widget = LedgerWidget()
            self.tabs.addTab(self.ledger_widget, self.tr("Ledger"))

        # Add the reporting widget - Admin and Accountant only
        if self.user.role in [UserRole.ADMIN, UserRole.ACCOUNTANT]:
            self.reporting_widget = ReportingWidget()
            self.tabs.addTab(self.reporting_widget, self.tr("Reporting"))