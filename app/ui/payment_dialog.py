from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QDateEdit, QMessageBox
from PyQt6.QtCore import QDate
from app.database.models import PaymentMethod

class PaymentDialog(QDialog):
    def __init__(self, document_id, total_amount, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record Payment")
        self.document_id = document_id
        self.total_amount = total_amount

        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText(f"Max: {total_amount / 100:.2f}")
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.method_input = QComboBox()
        self.method_input.addItems([pm.value for pm in PaymentMethod])

        self.form_layout.addRow("Amount:", self.amount_input)
        self.form_layout.addRow("Payment Date:", self.date_input)
        self.form_layout.addRow("Payment Method:", self.method_input)

        self.buttons_layout = QVBoxLayout()
        self.submit_button = QPushButton("Record Payment")
        self.submit_button.clicked.connect(self.accept)
        self.buttons_layout.addWidget(self.submit_button)

        self.layout.addLayout(self.form_layout)
        self.layout.addLayout(self.buttons_layout)

    def get_payment_details(self):
        amount = int(float(self.amount_input.text()) * 100)
        payment_date = self.date_input.dateTime().toPyDateTime()
        payment_method = PaymentMethod(self.method_input.currentText())
        return amount, payment_date, payment_method

    def accept(self):
        try:
            amount, _, _ = self.get_payment_details()
            if amount <= 0 or amount > self.total_amount:
                raise ValueError("Invalid payment amount.")
            super().accept()
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", f"Please enter a valid amount. {e}")