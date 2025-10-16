from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel, QLineEdit, QPushButton, QToolBar, QDialog
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QCoreApplication, QTimer
from ..database.session import get_db
from ..core.search_service import global_search
from .search_results_widget import SearchResultsWidget
from .customer_widget import CustomerWidget
from .supplier_widget import SupplierWidget
from .inventory_widget import InventoryWidget
from .category_widget import CategoryWidget
from .sales_widget import SalesWidget
from .purchase_order_widget import PurchaseOrderWidget
from .ledger_widget import LedgerWidget
from .reporting_widget import ReportingWidget
from .chart_of_accounts_widget import ChartOfAccountsWidget
from .notification_widget import NotificationWidget
from .expense_widget import ExpenseWidget
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

        self.setup_toolbar()

        # Create a central widget and a layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create and add the search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(self.tr("Search for customers, products, invoices..."))
        layout.addWidget(self.search_bar)

        # Create the tab widget and add it to the layout
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Add the customer management widget
        self.customer_widget = CustomerWidget()
        self.tabs.addTab(self.customer_widget, self.tr("Customers"))

        # Add the supplier management widget
        self.supplier_widget = SupplierWidget()
        self.tabs.addTab(self.supplier_widget, self.tr("Suppliers"))

        # Add the inventory management widget
        self.inventory_widget = InventoryWidget(self.user)
        self.tabs.addTab(self.inventory_widget, self.tr("Inventory"))

        # Add the category management widget
        self.category_widget = CategoryWidget()
        self.tabs.addTab(self.category_widget, self.tr("Categories"))

        # Add the sales management widget
        self.sales_widget = SalesWidget(self.user)
        self.tabs.addTab(self.sales_widget, self.tr("Sales"))

        # Add the purchase management widget - Admin and Accountant only
        if self.user.role in [UserRole.ADMIN, UserRole.ACCOUNTANT]:
            self.purchase_widget = PurchaseOrderWidget(self.user)
            self.tabs.addTab(self.purchase_widget, self.tr("Purchases"))

        # Add the invoicing widget - Admin and Accountant only
        if self.user.role in [UserRole.ADMIN, UserRole.ACCOUNTANT]:
            from .invoice_widget import InvoiceWidget
            self.invoice_widget = InvoiceWidget()
            self.tabs.addTab(self.invoice_widget, self.tr("Invoicing"))

        # Add the Chart of Accounts widget - Admin and Accountant only
        if self.user.role in [UserRole.ADMIN, UserRole.ACCOUNTANT]:
            self.chart_of_accounts_widget = ChartOfAccountsWidget()
            self.tabs.addTab(self.chart_of_accounts_widget, self.tr("Chart of Accounts"))

        # Add the ledger widget - Admin and Accountant only
        if self.user.role in [UserRole.ADMIN, UserRole.ACCOUNTANT]:
            self.ledger_widget = LedgerWidget()
            self.tabs.addTab(self.ledger_widget, self.tr("Journal Entries"))

        # Add the reporting widget - Admin and Accountant only
        if self.user.role in [UserRole.ADMIN, UserRole.ACCOUNTANT]:
            self.reporting_widget = ReportingWidget()
            self.tabs.addTab(self.reporting_widget, self.tr("Reporting"))

        # Add the expense widget - Admin and Accountant only
        if self.user.role in [UserRole.ADMIN, UserRole.ACCOUNTANT]:
            self.expense_widget = ExpenseWidget(self.user)
            self.tabs.addTab(self.expense_widget, self.tr("Expenses"))

        # Add the notification widget
        self.notification_widget = NotificationWidget()
        self.tabs.addTab(self.notification_widget, self.tr("Notifications"))

        # Add the user management widget - Admin only
        if self.user.role == UserRole.ADMIN:
            from .user_widget import UserWidget
            self.user_widget = UserWidget()
            self.tabs.addTab(self.user_widget, self.tr("Users"))

        # Connect the search bar signal
        self.search_bar.returnPressed.connect(self.execute_search)
        self.search_results_widget = None

        # Start the notification timer
        self.notification_timer = QTimer(self)
        self.notification_timer.timeout.connect(self.update_notification_count)
        self.notification_timer.start(60000)  # Update every 60 seconds
        self.update_notification_count()

    def setup_toolbar(self):
        """
        Sets up the main toolbar with a notification button.
        """
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        self.notification_button = QPushButton(self.tr("Notifications"))
        self.notification_button.clicked.connect(self.show_notifications)
        toolbar.addWidget(self.notification_button)

    def update_notification_count(self):
        """
        Updates the notification count on the toolbar button.
        """
        with get_db() as db:
            low_stock_count = len(self.notification_widget.notification_service.get_low_stock_notifications(db))
            overdue_count = len(self.notification_widget.notification_service.get_overdue_invoices(db))
            upcoming_count = len(self.notification_widget.notification_service.get_upcoming_payment_dues(db))
            total_notifications = low_stock_count + overdue_count + upcoming_count

        self.notification_button.setText(self.tr("Notifications ({})").format(total_notifications))

    def show_notifications(self):
        """
        Displays the notification widget in a dialog.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("Notifications"))
        layout = QVBoxLayout(dialog)

        # Re-use the existing notification_widget and reload its data
        self.notification_widget.load_notifications()
        layout.addWidget(self.notification_widget)

        # Add a button to close the dialog
        close_button = QPushButton(self.tr("Close"))
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        dialog.setLayout(layout)
        dialog.exec()

    def execute_search(self):
        """
        Executes a global search and displays the results in a new tab.
        """
        search_term = self.search_bar.text()
        if not search_term:
            return

        with get_db() as db_session:
            results = global_search(db_session, search_term)

        # If a search results tab already exists, remove it before creating a new one
        if self.search_results_widget:
            for i in range(self.tabs.count()):
                if self.tabs.widget(i) == self.search_results_widget:
                    self.tabs.removeTab(i)
                    break

        self.search_results_widget = SearchResultsWidget()
        self.search_results_widget.display_results(results)
        self.search_results_widget.result_selected.connect(self.handle_result_selection)

        # Add the results widget as a new tab and switch to it
        self.tabs.addTab(self.search_results_widget, self.tr("Search Results"))
        self.tabs.setCurrentWidget(self.search_results_widget)

    def handle_result_selection(self, model_type, model_id):
        """
        Navigates to the appropriate tab and item based on the search result selection.
        """
        # Close the search results tab
        if self.search_results_widget:
            for i in range(self.tabs.count()):
                if self.tabs.widget(i) == self.search_results_widget:
                    self.tabs.removeTab(i)
                    break
            self.search_results_widget = None

        # Navigate to the correct tab and highlight the item
        if model_type == "customers":
            self.tabs.setCurrentWidget(self.customer_widget)
            self.customer_widget.select_customer(model_id)
        elif model_type == "products":
            self.tabs.setCurrentWidget(self.inventory_widget)
            self.inventory_widget.select_product(model_id)
        elif model_type == "sales_orders":
            self.tabs.setCurrentWidget(self.sales_widget)
            self.sales_widget.select_order(model_id)
        elif model_type == "purchase_orders":
            if self.user.role in [UserRole.ADMIN, UserRole.ACCOUNTANT]:
                self.tabs.setCurrentWidget(self.purchase_widget)
                self.purchase_widget.select_order(model_id)