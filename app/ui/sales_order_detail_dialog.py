from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QFormLayout, QWidget
from PyQt6.QtCore import Qt

class SalesOrderDetailDialog(QDialog):
    def __init__(self, order, parent=None):
        super().__init__(parent)
        self.order = order
        self.setWindowTitle(self.tr(f"Details for Sales Order #{self.order.id}"))

        self.layout = QVBoxLayout(self)

        # Order Details
        details_layout = QFormLayout()
        details_layout.addRow(self.tr("Order ID:"), QLabel(str(self.order.id)))
        details_layout.addRow(self.tr("Customer:"), QLabel(self.order.customer.name))
        details_layout.addRow(self.tr("Total Amount:"), QLabel(f"{self.order.total_amount:.2f}"))
        details_layout.addRow(self.tr("Date:"), QLabel(self.order.created_at.strftime("%Y-%m-%d %H:%M:%S")))

        details_widget = QWidget()
        details_widget.setLayout(details_layout)
        self.layout.addWidget(details_widget)

        # Items Table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels([self.tr("Product"), self.tr("Quantity"), self.tr("Price per Unit"), self.tr("Total Price")])
        self.populate_items()
        self.layout.addWidget(self.items_table)

        self.setMinimumSize(400, 300)

    def populate_items(self):
        self.items_table.setRowCount(0)
        for row_num, item in enumerate(self.order.items):
            self.items_table.insertRow(row_num)
            self.items_table.setItem(row_num, 0, QTableWidgetItem(item.product.name))
            self.items_table.setItem(row_num, 1, QTableWidgetItem(str(item.quantity)))
            self.items_table.setItem(row_num, 2, QTableWidgetItem(f"{item.price_per_unit:.2f}"))
            self.items_table.setItem(row_num, 3, QTableWidgetItem(f"{(item.price_per_unit * item.quantity):.2f}"))
        self.items_table.resizeColumnsToContents()