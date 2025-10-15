from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout, QLineEdit, QSpinBox, QDialogButtonBox, QComboBox
from PyQt6.QtCore import QCoreApplication
from ..database import models
from ..database.database import get_db
from ..core import product_service, category_service

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
        self.category_input = QComboBox()

        self.layout.addRow(self.tr("Name:"), self.name_input)
        self.layout.addRow(self.tr("Description:"), self.description_input)
        self.layout.addRow(self.tr("Price (cents):"), self.price_input)
        self.layout.addRow(self.tr("Stock:"), self.stock_input)
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
            "category_id": self.category_input.currentData()
        }

class ProductWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([self.tr("ID"), self.tr("Name"), self.tr("Description"), self.tr("Price"), self.tr("Stock"), self.tr("Category")])
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

        self.load_products()

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
                self.table.setItem(row_num, 4, QTableWidgetItem(str(product.stock_quantity)))
                category_name = product.category.name if product.category else ""
                self.table.setItem(row_num, 5, QTableWidgetItem(category_name))

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