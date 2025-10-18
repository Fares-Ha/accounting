from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLabel, QLineEdit, QMenuBar, QMenu, QMessageBox
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QCoreApplication, pyqtSignal
from ..database.database import get_db
from ..core import auth
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
from ..database.models import User, UserRole

class MainWindow(QMainWindow):
    """
    The main application window, which appears after successful login.
    """
    restart_requested = pyqtSignal()

    def __init__(self, user_id):
        super().__init__()

        with get_db() as db:
            self.user = db.query(User).filter(User.id == user_id).first()

        self.setWindowTitle(self.tr("Ajyad Accountant - Logged in as {} ({})").format(self.user.username, self.user.role.value))
        self.setMinimumSize(800, 600)

        self._create_menus()

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
            self.purchase_widget = PurchaseOrderWidget(self.user.id)
            self.tabs.addTab(self.purchase_widget, self.tr("Purchases"))

        # Add the invoicing widget - Admin and Accountant only
        if self.user.role in [UserRole.ADMIN, UserRole.ACCOUNTANT]:
            from .invoice_widget import InvoiceWidget
            self.invoice_widget = InvoiceWidget(self.user.id)
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
            self.user_widget = UserWidget(current_user=self.user)
            self.tabs.addTab(self.user_widget, self.tr("Users"))

        # Connect the search bar signal
        self.search_bar.returnPressed.connect(self.execute_search)
        self.search_results_widget = None

    def _create_menus(self):
        menu_bar = self.menuBar()
        # Settings Menu
        settings_menu = menu_bar.addMenu(self.tr("&Settings"))

        # Language Submenu
        language_menu = settings_menu.addMenu(self.tr("&Language"))

        english_action = QAction(self.tr("English"), self)
        english_action.triggered.connect(lambda: self._change_language("en"))
        language_menu.addAction(english_action)

        arabic_action = QAction(self.tr("Arabic"), self)
        arabic_action.triggered.connect(lambda: self._change_language("ar"))
        language_menu.addAction(arabic_action)

    def _change_language(self, lang_code):
        """
        Updates the user's language preference in the database and prompts for a restart.
        """
        if self.user.language != lang_code:
            try:
                with get_db() as db:
                    auth.update_user_language(db, self.user.id, lang_code)

                reply = QMessageBox.question(self, self.tr("Language Change"),
                                            self.tr("The application needs to restart to apply the language change. Restart now?"),
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                            QMessageBox.StandardButton.Yes)
                if reply == QMessageBox.StandardButton.Yes:
                    self.restart_requested.emit()
            except Exception as e:
                QMessageBox.critical(self, self.tr("Error"), self.tr("Could not save language preference: {e}"))


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