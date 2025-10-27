from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QFormLayout, QLabel, QHBoxLayout, QSpinBox, QComboBox
from app.core import product_service, category_service
from app.database.database import get_db

class ProductDialog(QDialog):
    def __init__(self, product=None, user=None, parent=None):
        super().__init__(parent)
        self.product = product
        self.user = user
        self.setWindowTitle("Edit Product" if self.product else "Add Product")

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_input = QLineEdit(self.product.name if self.product else "")
        self.description_input = QLineEdit(self.product.description if self.product else "")
        self.price_input = QSpinBox()
        self.price_input.setRange(0, 1_000_000)
        self.price_input.setValue(self.product.price if self.product else 0)
        self.stock_input = QSpinBox()
        self.stock_input.setRange(0, 1_000_000)
        self.stock_input.setValue(self.product.stock_quantity if self.product else 0)
        self.low_stock_threshold_input = QSpinBox()
        self.low_stock_threshold_input.setRange(0, 1_000_000)
        self.low_stock_threshold_input.setValue(self.product.low_stock_threshold if self.product else 0)
        self.category_input = QComboBox()

        form_layout.addRow(QLabel("Name:"), self.name_input)
        form_layout.addRow(QLabel("Description:"), self.description_input)
        form_layout.addRow(QLabel("Price (cents):"), self.price_input)
        form_layout.addRow(QLabel("Stock:"), self.stock_input)
        form_layout.addRow(QLabel("Low Stock Threshold:"), self.low_stock_threshold_input)
        form_layout.addRow(QLabel("Category:"), self.category_input)

        layout.addLayout(form_layout)

        self.load_categories()
        if self.product and self.product.category:
            self.category_input.setCurrentText(self.product.category.name)

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.save_button.clicked.connect(self.save_product)
        self.cancel_button.clicked.connect(self.reject)

    def load_categories(self):
        with get_db() as db:
            categories = category_service.get_categories(db)
            for category in categories:
                self.category_input.addItem(category.name, category.id)

    def save_product(self):
        name = self.name_input.text()
        description = self.description_input.text()
        price = self.price_input.value()
        stock_quantity = self.stock_input.value()
        low_stock_threshold = self.low_stock_threshold_input.value()
        category_id = self.category_input.currentData()

        with get_db() as db:
            if self.product:
                product_service.update_product(db, self.user.id, self.product.id, name=name, description=description, price=price, stock_quantity=stock_quantity, low_stock_threshold=low_stock_threshold, category_id=category_id)
            else:
                product_service.create_product(db, name=name, description=description, price=price, stock_quantity=stock_quantity, low_stock_threshold=low_stock_threshold, category_id=category_id)

        self.accept()

    def get_new_item_name(self):
        return self.name_input.text()
