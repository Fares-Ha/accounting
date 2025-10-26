from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QFormLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import QCoreApplication
from app.core.supplier_service import SupplierService
from app.database.database import get_db

class SupplierDialog(QDialog):
    """
    Dialog for adding and editing suppliers.
    """
    def __init__(self, supplier=None, user=None, parent=None):
        super().__init__(parent)

        self.supplier = supplier
        self.user = user
        self.supplier_service = SupplierService()

        if self.supplier:
            self.setWindowTitle(self.tr("Edit Supplier"))
        else:
            self.setWindowTitle(self.tr("Add Supplier"))

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_input = QLineEdit(self.supplier.name if self.supplier else "")
        self.email_input = QLineEdit(self.supplier.email if self.supplier else "")
        self.phone_input = QLineEdit(self.supplier.phone if self.supplier else "")
        self.address_input = QLineEdit(self.supplier.address if self.supplier else "")

        form_layout.addRow(QLabel(self.tr("Name:")), self.name_input)
        form_layout.addRow(QLabel(self.tr("Email:")), self.email_input)
        form_layout.addRow(QLabel(self.tr("Phone:")), self.phone_input)
        form_layout.addRow(QLabel(self.tr("Address:")), self.address_input)

        layout.addLayout(form_layout)

        # Add Save and Cancel buttons
        self.save_button = QPushButton(self.tr("Save"))
        self.cancel_button = QPushButton(self.tr("Cancel"))

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.save_button.clicked.connect(self.save_supplier)
        self.cancel_button.clicked.connect(self.reject)

    def save_supplier(self):
        """
        Save the supplier to the database.
        """
        name = self.name_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        address = self.address_input.text()

        with get_db() as db:
            if self.supplier:
                self.supplier_service.update_supplier(db, self.supplier.id, name, email, phone, address)
            else:
                self.supplier_service.create_supplier(db, name, email, phone, address)

        self.accept()

    def get_new_item_name(self):
        return self.name_input.text()