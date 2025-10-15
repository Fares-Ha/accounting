from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QLabel, QPushButton, QDateEdit,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QColor
from ..core.reporting_service import ReportingService
from ..core.export_service import ExportService
from ..database.database import get_db
from datetime import datetime

class ReportingWidget(QWidget):
    """
    Widget for displaying various reports.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.reporting_service = ReportingService()
        self.export_service = ExportService()
        self.db_session = next(get_db())

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.sales_report_tab = QWidget()
        self.inventory_report_tab = QWidget()

        self.tabs.addTab(self.sales_report_tab, self.tr("Sales Reports"))
        self.tabs.addTab(self.inventory_report_tab, self.tr("Inventory Reports"))

        self.setup_sales_report_tab()
        self.setup_inventory_report_tab()

    def setup_sales_report_tab(self):
        layout = QVBoxLayout(self.sales_report_tab)

        self.start_date_edit = QDateEdit(QDate.currentDate().addMonths(-1))
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.generate_sales_report_button = QPushButton(self.tr("Generate Report"))
        self.generate_sales_report_button.clicked.connect(self.generate_sales_report)

        self.sales_report_table = QTableWidget()
        self.sales_report_table.setColumnCount(3)
        self.sales_report_table.setHorizontalHeaderLabels([self.tr("Product"), self.tr("Total Quantity"), self.tr("Total Revenue")])
        self.sales_report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.export_sales_pdf_button = QPushButton(self.tr("Export to PDF"))
        self.export_sales_pdf_button.clicked.connect(self.export_sales_report_to_pdf)
        self.export_sales_excel_button = QPushButton(self.tr("Export to Excel"))
        self.export_sales_excel_button.clicked.connect(self.export_sales_report_to_excel)

        layout.addWidget(QLabel(self.tr("Start Date:")))
        layout.addWidget(self.start_date_edit)
        layout.addWidget(QLabel(self.tr("End Date:")))
        layout.addWidget(self.end_date_edit)
        layout.addWidget(self.generate_sales_report_button)
        layout.addWidget(self.export_sales_pdf_button)
        layout.addWidget(self.export_sales_excel_button)
        layout.addWidget(self.sales_report_table)

    def get_sales_report_data_from_table(self):
        data = []
        for row in range(self.sales_report_table.rowCount()):
            row_data = []
            for col in range(self.sales_report_table.columnCount()):
                item = self.sales_report_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data

    def export_sales_report_to_pdf(self):
        headers = [self.tr("Product"), self.tr("Total Quantity"), self.tr("Total Revenue")]
        data = self.get_sales_report_data_from_table()
        self.export_service.export_to_pdf(data, headers, self)

    def export_sales_report_to_excel(self):
        headers = [self.tr("Product"), self.tr("Total Quantity"), self.tr("Total Revenue")]
        data = self.get_sales_report_data_from_table()
        self.export_service.export_to_excel(data, headers, self)

    def generate_sales_report(self):
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        report_data = self.reporting_service.get_sales_report(self.db_session, start_date, end_date)

        self.sales_report_table.setRowCount(len(report_data))
        for row, (product_name, total_quantity, total_revenue) in enumerate(report_data):
            self.sales_report_table.setItem(row, 0, QTableWidgetItem(product_name))
            self.sales_report_table.setItem(row, 1, QTableWidgetItem(str(total_quantity)))
            self.sales_report_table.setItem(row, 2, QTableWidgetItem(f"{total_revenue / 100:.2f}"))

    def setup_inventory_report_tab(self):
        layout = QVBoxLayout(self.inventory_report_tab)

        self.refresh_inventory_report_button = QPushButton(self.tr("Refresh Report"))
        self.refresh_inventory_report_button.clicked.connect(self.generate_inventory_report)

        self.inventory_report_table = QTableWidget()
        self.inventory_report_table.setColumnCount(3)
        self.inventory_report_table.setHorizontalHeaderLabels([self.tr("Product"), self.tr("Stock Quantity"), self.tr("Low Stock Threshold")])
        self.inventory_report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.export_inventory_pdf_button = QPushButton(self.tr("Export to PDF"))
        self.export_inventory_pdf_button.clicked.connect(self.export_inventory_report_to_pdf)
        self.export_inventory_excel_button = QPushButton(self.tr("Export to Excel"))
        self.export_inventory_excel_button.clicked.connect(self.export_inventory_report_to_excel)

        layout.addWidget(self.refresh_inventory_report_button)
        layout.addWidget(self.export_inventory_pdf_button)
        layout.addWidget(self.export_inventory_excel_button)
        layout.addWidget(self.inventory_report_table)

        self.generate_inventory_report()

    def get_inventory_report_data_from_table(self):
        data = []
        for row in range(self.inventory_report_table.rowCount()):
            row_data = []
            for col in range(self.inventory_report_table.columnCount()):
                item = self.inventory_report_table.item(row, col)
                row_data.append(item.text() if item else "")
            data.append(row_data)
        return data

    def export_inventory_report_to_pdf(self):
        headers = [self.tr("Product"), self.tr("Stock Quantity"), self.tr("Low Stock Threshold")]
        data = self.get_inventory_report_data_from_table()
        self.export_service.export_to_pdf(data, headers, self)

    def export_inventory_report_to_excel(self):
        headers = [self.tr("Product"), self.tr("Stock Quantity"), self.tr("Low Stock Threshold")]
        data = self.get_inventory_report_data_from_table()
        self.export_service.export_to_excel(data, headers, self)

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