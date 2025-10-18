from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QMessageBox, QHBoxLayout
from ..core import invoice_service, sales_service
from ..core.payment_service import PaymentService
from ..database.database import get_db
from .payment_dialog import PaymentDialog
from ..database.models import InvoiceStatus

class InvoiceWidget(QWidget):
    def __init__(self, user_id: int, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.layout = QVBoxLayout(self)

        self.buttons_layout = QHBoxLayout()
        self.create_invoice_button = QPushButton("Create Invoice from Sales Order")
        self.create_invoice_button.clicked.connect(self.create_invoice)
        self.record_payment_button = QPushButton("Record Payment")
        self.record_payment_button.clicked.connect(self.record_payment)
        self.buttons_layout.addWidget(self.create_invoice_button)
        self.buttons_layout.addWidget(self.record_payment_button)
        self.layout.addLayout(self.buttons_layout)

        self.invoice_table = QTableWidget()
        self.invoice_table.setColumnCount(6)
        self.invoice_table.setHorizontalHeaderLabels(["ID", "Sales Order ID", "Customer", "Total", "Paid Amount", "Status"])
        self.layout.addWidget(self.invoice_table)

        self.refresh_invoices()

    def refresh_invoices(self):
        self.invoice_table.setRowCount(0)
        with get_db() as db:
            invoices = invoice_service.get_invoices(db)
            for row, invoice in enumerate(invoices):
                self.invoice_table.insertRow(row)
                self.invoice_table.setItem(row, 0, QTableWidgetItem(str(invoice.id)))
                self.invoice_table.setItem(row, 1, QTableWidgetItem(str(invoice.sales_order_id)))
                self.invoice_table.setItem(row, 2, QTableWidgetItem(invoice.customer.name))
                self.invoice_table.setItem(row, 3, QTableWidgetItem(f"{invoice.total_amount / 100:.2f}"))

                total_paid = sum(p.amount for p in invoice.payments)
                self.invoice_table.setItem(row, 4, QTableWidgetItem(f"{total_paid / 100:.2f}"))

                status_combo = QComboBox()
                status_combo.addItems([s.value for s in InvoiceStatus])
                status_combo.setCurrentText(invoice.status.value)
                status_combo.currentTextChanged.connect(lambda text, inv_id=invoice.id: self.update_status(inv_id, text))
                self.invoice_table.setCellWidget(row, 5, status_combo)

    def create_invoice(self):
        with get_db() as db:
            sales_orders = sales_service.get_sales_orders(db)
            if not sales_orders:
                QMessageBox.warning(self, "No Sales Orders", "There are no sales orders to create an invoice from.")
                return

            latest_order = sales_orders[-1]
            try:
                invoice_service.create_invoice_from_sales_order(db, latest_order.id)
                self.refresh_invoices()
            except ValueError as e:
                QMessageBox.warning(self, "Creation Failed", str(e))

    def record_payment(self):
        selected_row = self.invoice_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Invoice Selected", "Please select an invoice to record a payment.")
            return

        invoice_id = int(self.invoice_table.item(selected_row, 0).text())
        with get_db() as db:
            invoice = invoice_service.get_invoice(db, invoice_id)
            total_paid = sum(p.amount for p in invoice.payments)
            amount_due = invoice.total_amount - total_paid

        if amount_due <= 0:
            QMessageBox.information(self, "Invoice Paid", "This invoice is already fully paid.")
            return

        dialog = PaymentDialog(invoice_id, amount_due, self)
        if dialog.exec():
            amount, payment_date, payment_method = dialog.get_payment_details()
            with get_db() as db:
                payment_service = PaymentService(db, self.user_id)
                try:
                    # Assuming payment from a cash account for simplicity
                    payment_service.record_invoice_payment(invoice_id, amount, payment_date, payment_method, "Cash")
                    self.refresh_invoices()
                except Exception as e:
                    QMessageBox.critical(self, "Payment Error", f"Could not record payment: {e}")

    def update_status(self, invoice_id, status_text):
        with get_db() as db:
            status = InvoiceStatus(status_text)
            invoice_service.update_invoice_status(db, invoice_id, status)
        self.refresh_invoices()