from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QMessageBox
from ..core import invoice_service, sales_service
from ..database import get_db

class InvoiceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.create_invoice_button = QPushButton("Create Invoice from Sales Order")
        self.create_invoice_button.clicked.connect(self.create_invoice)
        self.layout.addWidget(self.create_invoice_button)

        self.invoice_table = QTableWidget()
        self.invoice_table.setColumnCount(5)
        self.invoice_table.setHorizontalHeaderLabels(["ID", "Sales Order ID", "Customer", "Total", "Status"])
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
                self.invoice_table.setItem(row, 3, QTableWidgetItem(str(invoice.total_amount / 100))) # Assuming amount is in cents

                status_combo = QComboBox()
                for status in ["DRAFT", "SENT", "PAID", "VOID"]:
                    status_combo.addItem(status)
                status_combo.setCurrentText(invoice.status.name)
                status_combo.currentTextChanged.connect(lambda text, inv_id=invoice.id: self.update_status(inv_id, text))
                self.invoice_table.setCellWidget(row, 4, status_combo)

    def create_invoice(self):
        # In a real application, this would involve a dialog to select a sales order
        # For simplicity, we'll just try to create an invoice for the latest sales order
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

    def update_status(self, invoice_id, status_text):
        with get_db() as db:
            from ..database.models import InvoiceStatus
            status = InvoiceStatus[status_text]
            invoice_service.update_invoice_status(db, invoice_id, status)
        self.refresh_invoices()