from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QFormLayout, QLabel, QHBoxLayout, QDoubleSpinBox
from app.core import product_service
from app.database.database import get_db

class ProductDialog(QDialog):
    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Edit Product" if self.product else "Add Product")

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_input = QLineEdit(self.product.name if self.product else "")
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.0, 999999.99)
        if self.product:
            self.price_input.setValue(self.product.price)

        form_layout.addRow(QLabel("Name:"), self.name_input)
        form_layout.addRow(QLabel("Price:"), self.price_input)

        layout.addLayout(form_layout)

        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.save_button.clicked.connect(self.save_product)
        self.cancel_button.clicked.connect(self.reject)

    def save_product(self):
        name = self.name_input.text()
        price = self.price_input.value()

        with get_db() as db:
            if self.product:
                product_service.update_product(db, self.product.id, name=name, price=price)
            else:
                product_service.create_product(db, name=name, price=price, stock_quantity=0)

        self.accept()

    def get_new_item_name(self):
        return self.name_input.text()
