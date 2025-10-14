from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout, QComboBox, QSpinBox, QDialogButtonBox
from PyQt6.QtCore import QCoreApplication
from ..database.database import get_db
from ..core import sales_service, customer_service, product_service
from ..database import models

class SalesOrderDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("Create Sales Order"))
        self.layout = QFormLayout(self)
        self.customer_combo = QComboBox()
        self.items = []

        self.load_customers()
        self.layout.addRow(self.tr("Customer:"), self.customer_combo)

        self.add_item_button = QPushButton(self.tr("Add Item"))
        self.add_item_button.clicked.connect(self.add_item)
        self.layout.addWidget(self.add_item_button)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(3)
        self.items_table.setHorizontalHeaderLabels([self.tr("Product"), self.tr("Quantity"), self.tr("Price")])
        self.layout.addWidget(self.items_table)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def load_customers(self):
        with get_db() as db:
            customers = customer_service.get_customers(db)
            for customer in customers:
                self.customer_combo.addItem(customer.name, userData=customer.id)

    def add_item(self):
        # A dialog to select a product and quantity
        item_dialog = QDialog(self)
        item_layout = QFormLayout(item_dialog)
        product_combo = QComboBox()
        quantity_spin = QSpinBox()
        quantity_spin.setRange(1, 1000)

        with get_db() as db:
            products = product_service.get_products(db)
            for p in products:
                product_combo.addItem(f"{p.name} (Stock: {p.stock_quantity})", userData=p.id)

        item_layout.addRow(self.tr("Product:"), product_combo)
        item_layout.addRow(self.tr("Quantity:"), quantity_spin)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(item_dialog.accept)
        buttons.rejected.connect(item_dialog.reject)
        item_layout.addWidget(buttons)

        if item_dialog.exec():
            product_id = product_combo.currentData()
            quantity = quantity_spin.value()
            with get_db() as db:
                product = product_service.get_product(db, product_id)

            self.items.append({'product_id': product_id, 'quantity': quantity})
            row_pos = self.items_table.rowCount()
            self.items_table.insertRow(row_pos)
            self.items_table.setItem(row_pos, 0, QTableWidgetItem(product.name))
            self.items_table.setItem(row_pos, 1, QTableWidgetItem(str(quantity)))
            self.items_table.setItem(row_pos, 2, QTableWidgetItem(str(product.price * quantity)))


    def get_data(self):
        return {
            "customer_id": self.customer_combo.currentData(),
            "items": self.items
        }

class SalesWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([self.tr("ID"), self.tr("Customer"), self.tr("Total Amount"), self.tr("Date")])
        self.layout.addWidget(self.table)

        self.add_button = QPushButton(self.tr("Create Sales Order"))
        self.add_button.clicked.connect(self.create_order)
        self.layout.addWidget(self.add_button)

        self.load_orders()

    def load_orders(self):
        self.table.setRowCount(0)
        with get_db() as db:
            orders = sales_service.get_sales_orders(db)
            for row_num, order in enumerate(orders):
                self.table.insertRow(row_num)
                self.table.setItem(row_num, 0, QTableWidgetItem(str(order.id)))
                self.table.setItem(row_num, 1, QTableWidgetItem(order.customer.name))
                self.table.setItem(row_num, 2, QTableWidgetItem(str(order.total_amount)))
                self.table.setItem(row_num, 3, QTableWidgetItem(order.created_at.strftime("%Y-%m-%d")))

    def create_order(self):
        dialog = SalesOrderDialog()
        if dialog.exec():
            data = dialog.get_data()
            try:
                with get_db() as db:
                    sales_service.create_sales_order(db, **data)
                self.load_orders()
            except ValueError as e:
                QMessageBox.critical(self, self.tr("Error"), str(e))