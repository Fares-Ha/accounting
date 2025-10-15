from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout, QLineEdit, QSpinBox, QDialogButtonBox, QComboBox
from PyQt6.QtCore import QCoreApplication
from ..database import models
from ..database.database import get_db
from ..core import product_service, category_service

class InventoryHistoryDialog(QDialog):
    def __init__(self, product_id):
        super().__init__()
        self.product_id = product_id
        self.setWindowTitle(self.tr("Inventory History"))
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([self.tr("Date"), self.tr("Quantity Change"), self.tr("Reason")])
        self.layout.addWidget(self.table)
        self.load_history()

    def load_history(self):
        with get_db() as db:
            movements = product_service.get_inventory_movements(db, self.product_id)
            self.table.setRowCount(len(movements))
            for row_num, movement in enumerate(movements):
                self.table.setItem(row_num, 0, QTableWidgetItem(str(movement.created_at)))
                self.table.setItem(row_num, 1, QTableWidgetItem(str(movement.quantity_change)))
                self.table.setItem(row_num, 2, QTableWidgetItem(movement.reason.value))

class ProductDialog(QDialog):
    def __init__(self, product=None):
        super().__init__()
        self.product = product
        self.setWindowTitle(self.tr("Add/Edit Product"))

        self.layout = QFormLayout(self)
        self.name_input = QLineEdit(product.name if product else "")
        self.description_input = QLineEdit(product.description if product else "")
        self.price_input = QSpinBox()
        self.price_input.setRange(0, 1_000_000)
        self.price_input.setValue(product.price if product else 0)
        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 1_000_000)
        self.stock_input.setValue(product.stock_quantity if product else 0)
        self.low_stock_threshold_input = QSpinBox()
        self.low_stock_threshold_input.setRange(0, 1_000_000)
        self.low_stock_threshold_input.setValue(product.low_stock_threshold if product else 0)
        self.category_input = QComboBox()

        self.layout.addRow(self.tr("Name:"), self.name_input)
        self.layout.addRow(self.tr("Description:"), self.description_input)
        self.layout.addRow(self.tr("Price (cents):"), self.price_input)
        self.layout.addRow(self.tr("Stock:"), self.stock_input)
        self.layout.addRow(self.tr("Low Stock Threshold:"), self.low_stock_threshold_input)
        self.layout.addRow(self.tr("Category:"), self.category_input)

        self.load_categories()
        if product and product.category:
            self.category_input.setCurrentText(product.category.name)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def load_categories(self):
        with get_db() as db:
            categories = category_service.get_categories(db)
            for category in categories:
                self.category_input.addItem(category.name, category.id)

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "description": self.description_input.text(),
            "price": self.price_input.value(),
            "stock_quantity": self.stock_input.value(),
            "low_stock_threshold": self.low_stock_threshold_input.value(),
            "category_id": self.category_input.currentData()
        }

class InventoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([self.tr("ID"), self.tr("Name"), self.tr("Description"), self.tr("Price"), self.tr("Stock"), self.tr("Low Stock Threshold"), self.tr("Category")])
        self.layout.addWidget(self.table)

        self.add_button = QPushButton(self.tr("Add Product"))
        self.add_button.clicked.connect(self.add_product)
        self.layout.addWidget(self.add_button)

        self.edit_button = QPushButton(self.tr("Edit Product"))
        self.edit_button.clicked.connect(self.edit_product)
        self.layout.addWidget(self.edit_button)

        self.delete_button = QPushButton(self.tr("Delete Product"))
        self.delete_button.clicked.connect(self.delete_product)
        self.layout.addWidget(self.delete_button)

        self.history_button = QPushButton(self.tr("Show History"))
        self.history_button.clicked.connect(self.show_inventory_history)
        self.layout.addWidget(self.history_button)

        self.adjust_stock_button = QPushButton(self.tr("Adjust Stock"))
        self.adjust_stock_button.clicked.connect(self.adjust_stock)
        self.layout.addWidget(self.adjust_stock_button)

        self.load_products()

    def show_inventory_history(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Please select a product to view its history."))
            return

        product_id = int(self.table.item(selected_row, 0).text())
        dialog = InventoryHistoryDialog(product_id)
        dialog.exec()

from PyQt6.QtGui import QColor
from .stock_adjustment_dialog import StockAdjustmentDialog

    def load_products(self):
        self.table.setRowCount(0)
        with get_db() as db:
            products = product_service.get_products(db)
            for row_num, product in enumerate(products):
                self.table.insertRow(row_num)
                self.table.setItem(row_num, 0, QTableWidgetItem(str(product.id)))
                self.table.setItem(row_num, 1, QTableWidgetItem(product.name))
                self.table.setItem(row_num, 2, QTableWidgetItem(product.description))
                self.table.setItem(row_num, 3, QTableWidgetItem(str(product.price)))

                stock_item = QTableWidgetItem(str(product.stock_quantity))
                if product.stock_quantity < product.low_stock_threshold:
                    stock_item.setBackground(QColor("red"))
                self.table.setItem(row_num, 4, stock_item)

                self.table.setItem(row_num, 5, QTableWidgetItem(str(product.low_stock_threshold)))
                category_name = product.category.name if product.category else ""
                self.table.setItem(row_num, 6, QTableWidgetItem(category_name))

    def add_product(self):
        dialog = ProductDialog()
        if dialog.exec():
            data = dialog.get_data()
            with get_db() as db:
                product_service.create_product(db, **data)
            self.load_products()

    def edit_product(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Please select a product to edit."))
            return

        product_id = int(self.table.item(selected_row, 0).text())
        with get_db() as db:
            product = db.query(models.Product).filter(models.Product.id == product_id).first()

        dialog = ProductDialog(product)
        if dialog.exec():
            data = dialog.get_data()
            with get_db() as db:
                product_service.update_product(db, product_id, **data)
            self.load_products()

    def delete_product(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Please select a product to delete."))
            return

        product_id = int(self.table.item(selected_row, 0).text())
        reply = QMessageBox.question(self, self.tr("Confirm Delete"), self.tr("Are you sure you want to delete this product?"),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            with get_db() as db:
                product_service.delete_product(db, product_id)
            self.load_products()

    def adjust_stock(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Please select a product to adjust its stock."))
            return

        product_id = int(self.table.item(selected_row, 0).text())
        product_name = self.table.item(selected_row, 1).text()
        dialog = StockAdjustmentDialog(product_id, product_name)
        if dialog.exec():
            self.load_products()

    def select_product(self, product_id):
        """
        Selects a product in the table by its ID.
        """
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and int(item.text()) == product_id:
                self.table.selectRow(row)
                break