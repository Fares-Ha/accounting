from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout, QComboBox, QSpinBox, QDialogButtonBox
from PyQt6.QtCore import QCoreApplication
from ..database.database import get_db
from ..core import purchase_service, supplier_service, product_service
from ..database import models

class PurchaseOrderDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("Create Purchase Order"))
        self.layout = QFormLayout(self)
        self.supplier_combo = QComboBox()
        self.items = []

        self.load_suppliers()
        self.layout.addRow(self.tr("Supplier:"), self.supplier_combo)

        self.add_item_button = QPushButton(self.tr("Add Item"))
        self.add_item_button.clicked.connect(self.add_item)
        self.layout.addWidget(self.add_item_button)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels([self.tr("Product"), self.tr("Quantity"), self.tr("Price per Unit"), self.tr("Total Price")])
        self.layout.addWidget(self.items_table)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def load_suppliers(self):
        with get_db() as db:
            suppliers = supplier_service.get_suppliers(db)
            for supplier in suppliers:
                self.supplier_combo.addItem(supplier.name, userData=supplier.id)

    def add_item(self):
        # A dialog to select a product and quantity
        item_dialog = QDialog(self)
        item_layout = QFormLayout(item_dialog)
        product_combo = QComboBox()
        quantity_spin = QSpinBox()
        quantity_spin.setRange(1, 1000)
        price_spin = QSpinBox()
        price_spin.setRange(0, 1_000_000)


        with get_db() as db:
            products = product_service.get_products(db)
            for p in products:
                product_combo.addItem(f"{p.name}", userData=p.id)

        item_layout.addRow(self.tr("Product:"), product_combo)
        item_layout.addRow(self.tr("Quantity:"), quantity_spin)
        item_layout.addRow(self.tr("Price per unit:"), price_spin)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(item_dialog.accept)
        buttons.rejected.connect(item_dialog.reject)
        item_layout.addWidget(buttons)

        if item_dialog.exec():
            product_id = product_combo.currentData()
            quantity = quantity_spin.value()
            price_per_unit = price_spin.value()
            with get_db() as db:
                product = product_service.get_product(db, product_id)

            self.items.append({'product_id': product_id, 'quantity': quantity, 'price_per_unit': price_per_unit})
            row_pos = self.items_table.rowCount()
            self.items_table.insertRow(row_pos)
            self.items_table.setItem(row_pos, 0, QTableWidgetItem(product.name))
            self.items_table.setItem(row_pos, 1, QTableWidgetItem(str(quantity)))
            self.items_table.setItem(row_pos, 2, QTableWidgetItem(str(price_per_unit)))
            self.items_table.setItem(row_pos, 3, QTableWidgetItem(str(price_per_unit * quantity)))


    def get_data(self):
        return {
            "supplier_id": self.supplier_combo.currentData(),
            "items": self.items
        }

class PurchaseWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([self.tr("ID"), self.tr("Supplier"), self.tr("Total Amount"), self.tr("Date")])
        self.layout.addWidget(self.table)

        self.add_button = QPushButton(self.tr("Create Purchase Order"))
        self.add_button.clicked.connect(self.create_order)
        self.layout.addWidget(self.add_button)

        self.load_orders()

    def load_orders(self):
        self.table.setRowCount(0)
        with get_db() as db:
            orders = purchase_service.get_purchase_orders(db)
            for row_num, order in enumerate(orders):
                self.table.insertRow(row_num)
                self.table.setItem(row_num, 0, QTableWidgetItem(str(order.id)))
                self.table.setItem(row_num, 1, QTableWidgetItem(order.supplier.name))
                self.table.setItem(row_num, 2, QTableWidgetItem(str(order.total_amount)))
                self.table.setItem(row_num, 3, QTableWidgetItem(order.created_at.strftime("%Y-%m-%d")))

    def create_order(self):
        dialog = PurchaseOrderDialog()
        if dialog.exec():
            data = dialog.get_data()
            try:
                with get_db() as db:
                    purchase_service.create_purchase_order(db, **data)
                self.load_orders()
            except ValueError as e:
                QMessageBox.critical(self, self.tr("Error"), str(e))