from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtGui import QColor
from ..core.reporting_service import ReportingService
from ..database.database import get_db

class ReportingWidget(QWidget):
    """
    Widget for displaying various reports.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.reporting_service = ReportingService()
        self.db_session = next(get_db())

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.pnl_tab = QWidget()
        self.balance_sheet_tab = QWidget()
        self.sales_report_tab = QWidget()
        self.inventory_report_tab = QWidget()

        self.tabs.addTab(self.pnl_tab, self.tr("Profit & Loss"))
        self.tabs.addTab(self.balance_sheet_tab, self.tr("Balance Sheet"))
        self.tabs.addTab(self.sales_report_tab, self.tr("Sales Reports"))
        self.tabs.addTab(self.inventory_report_tab, self.tr("Inventory Reports"))

        self.setup_pnl_tab()
        self.setup_balance_sheet_tab()
        self.setup_inventory_report_tab()

    def setup_pnl_tab(self):
        layout = QVBoxLayout(self.pnl_tab)
        self.pnl_table = QTableWidget()
        self.pnl_table.setColumnCount(2)
        self.pnl_table.setHorizontalHeaderLabels([self.tr("Account"), self.tr("Amount")])
        self.pnl_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.pnl_table)
        self.generate_pnl_report()

    def generate_pnl_report(self):
        report_data = self.reporting_service.get_profit_and_loss_statement(self.db_session)
        self.pnl_table.setRowCount(3)
        self.pnl_table.setItem(0, 0, QTableWidgetItem(self.tr("Total Revenue")))
        self.pnl_table.setItem(0, 1, QTableWidgetItem(f"{report_data['revenue'] / 100:.2f}"))
        self.pnl_table.setItem(1, 0, QTableWidgetItem(self.tr("Total Expenses")))
        self.pnl_table.setItem(1, 1, QTableWidgetItem(f"{report_data['expenses'] / 100:.2f}"))
        self.pnl_table.setItem(2, 0, QTableWidgetItem(self.tr("Net Profit")))
        self.pnl_table.setItem(2, 1, QTableWidgetItem(f"{report_data['net_profit'] / 100:.2f}"))

    def setup_balance_sheet_tab(self):
        layout = QVBoxLayout(self.balance_sheet_tab)
        self.balance_sheet_table = QTableWidget()
        self.balance_sheet_table.setColumnCount(2)
        self.balance_sheet_table.setHorizontalHeaderLabels([self.tr("Account"), self.tr("Amount")])
        self.balance_sheet_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.balance_sheet_table)
        self.generate_balance_sheet_report()

    def generate_balance_sheet_report(self):
        report_data = self.reporting_service.get_balance_sheet(self.db_session)
        self.balance_sheet_table.setRowCount(3)
        self.balance_sheet_table.setItem(0, 0, QTableWidgetItem(self.tr("Total Assets")))
        self.balance_sheet_table.setItem(0, 1, QTableWidgetItem(f"{report_data['assets'] / 100:.2f}"))
        self.balance_sheet_table.setItem(1, 0, QTableWidgetItem(self.tr("Total Liabilities")))
        self.balance_sheet_table.setItem(1, 1, QTableWidgetItem(f"{report_data['liabilities'] / 100:.2f}"))
        self.balance_sheet_table.setItem(2, 0, QTableWidgetItem(self.tr("Total Equity")))
        self.balance_sheet_table.setItem(2, 1, QTableWidgetItem(f"{report_data['equity'] / 100:.2f}"))

    def setup_inventory_report_tab(self):
        layout = QVBoxLayout(self.inventory_report_tab)

        self.refresh_inventory_report_button = QPushButton(self.tr("Refresh Report"))
        self.refresh_inventory_report_button.clicked.connect(self.generate_inventory_report)

        self.inventory_report_table = QTableWidget()
        self.inventory_report_table.setColumnCount(3)
        self.inventory_report_table.setHorizontalHeaderLabels([self.tr("Product"), self.tr("Stock Quantity"), self.tr("Low Stock Threshold")])
        self.inventory_report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.refresh_inventory_report_button)
        layout.addWidget(self.inventory_report_table)

        self.generate_inventory_report()

    def generate_inventory_report(self):
        report_data = self.reporting_service.get_inventory_report(self.db_session)
        self.inventory_report_table.setRowCount(len(report_data))
        for row, (product_name, stock_quantity, low_stock_threshold) in enumerate(report_data):
            self.inventory_report_table.setItem(row, 0, QTableWidgetItem(product_name))
            self.inventory_report_table.setItem(row, 1, QTableWidgetItem(str(stock_quantity)))
            self.inventory_report_table.setItem(row, 2, QTableWidgetItem(str(low_stock_threshold)))

            if stock_quantity < low_stock_threshold:
                for col in range(3):
                    self.inventory_report_table.item(row, col).setBackground(QColor("orange"))