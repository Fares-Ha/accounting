from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QFormLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import QCoreApplication
from app.core.customer_service import create_customer, update_customer, get_db

class CustomerDialog(QDialog):
    """
    Dialog for adding and editing customers.
    """
    def __init__(self, customer=None, user=None, parent=None):
        super().__init__(parent)

        self.customer = customer
        self.user = user
        if self.customer:
            self.setWindowTitle(self.tr("Edit Customer"))
        else:
            self.setWindowTitle(self.tr("Add Customer"))

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_input = QLineEdit(self.customer.name if self.customer else "")
        self.email_input = QLineEdit(self.customer.email if self.customer else "")
        self.phone_input = QLineEdit(self.customer.phone if self.customer else "")
        self.address_input = QLineEdit(self.customer.address if self.customer else "")

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

        self.save_button.clicked.connect(self.save_customer)
        self.cancel_button.clicked.connect(self.reject)

    def save_customer(self):
        """
        Save the customer to the database.
        """
        name = self.name_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        address = self.address_input.text()

        db_gen = get_db()
        db = next(db_gen)
        try:
            if self.customer:
                update_customer(db, self.customer.id, name, email, phone, address)
            else:
                create_customer(db, name, email, phone, address)
        finally:
            next(db_gen, None)

        self.accept()

    def get_new_item_name(self):
        return self.name_input.text()