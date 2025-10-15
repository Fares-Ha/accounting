from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QFormLayout, QMessageBox, QDialog, QComboBox, QSpinBox
from app.core.purchase_service import PurchaseService
from app.core.product_service import ProductService
from app.core.supplier_service import SupplierService
from app.database.database import get_db

class PurchaseOrderDialog(QDialog):
    def __init__(self, purchase_service, product_service, supplier_service, db_session, order_id=None):
        super().__init__()
        self.purchase_service = purchase_service
        self.product_service = product_service
        self.supplier_service = supplier_service
        self.db_session = db_session
        self.order_id = order_id
        self.setWindowTitle(f"{'Edit' if order_id else 'New'} Purchase Order")
        self.init_ui()
        if self.order_id:
            self.load_order_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.supplier_combo = QComboBox()
        with get_db() as db:
            suppliers = self.supplier_service.get_all_suppliers(db)
            for supplier in suppliers:
                self.supplier_combo.addItem(supplier.name, supplier.id)
        form_layout.addRow("Supplier:", self.supplier_combo)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Product", "Quantity", "Price per Unit", "Remove"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.items_table)

        add_item_layout = QHBoxLayout()
        self.product_combo = QComboBox()
        with get_db() as db:
            products = self.product_service.get_products(db)
            for product in products:
                self.product_combo.addItem(product.name, product.id)
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setRange(1, 9999)
        self.price_spinbox = QSpinBox()
        self.price_spinbox.setRange(0, 999999)
        self.add_item_button = QPushButton("Add Item")
        self.add_item_button.clicked.connect(self.add_item)
        add_item_layout.addWidget(self.product_combo)
        add_item_layout.addWidget(self.quantity_spinbox)
        add_item_layout.addWidget(self.price_spinbox)
        add_item_layout.addWidget(self.add_item_button)
        layout.addLayout(add_item_layout)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_order)
        layout.addWidget(self.save_button)

    def add_item(self):
        product_id = self.product_combo.currentData()
        product_name = self.product_combo.currentText()
        quantity = self.quantity_spinbox.value()
        price = self.price_spinbox.value()

        if not product_id or quantity <= 0 or price <= 0:
            QMessageBox.warning(self, "Input Error", "Please select a product and enter a valid quantity and price.")
            return

        row_position = self.items_table.rowCount()
        self.items_table.insertRow(row_position)
        self.items_table.setItem(row_position, 0, QTableWidgetItem(product_name))
        self.items_table.setItem(row_position, 1, QTableWidgetItem(str(quantity)))
        self.items_table.setItem(row_position, 2, QTableWidgetItem(str(price)))
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.items_table.removeRow(row_position))
        self.items_table.setCellWidget(row_position, 3, remove_button)
        self.items_table.setUserData(row_position, product_id)

    def save_order(self):
        supplier_id = self.supplier_combo.currentData()
        items = []
        for row in range(self.items_table.rowCount()):
            items.append({
                "product_id": self.items_table.userData(row),
                "quantity": int(self.items_table.item(row, 1).text()),
                "price_per_unit": int(self.items_table.item(row, 2).text())
            })

        if not supplier_id or not items:
            QMessageBox.warning(self, "Input Error", "Please select a supplier and add at least one item.")
            return

        with get_db() as db:
            if self.order_id:
                self.purchase_service.update_purchase_order(db, self.order_id, supplier_id, items)
            else:
                self.purchase_service.create_purchase_order(db, supplier_id, items)
        self.accept()

    def load_order_data(self):
        order = self.purchase_service.get_purchase_order(self.order_id)
        if not order:
            return

        index = self.supplier_combo.findData(order.supplier_id)
        if index >= 0:
            self.supplier_combo.setCurrentIndex(index)

        self.items_table.setRowCount(0)
        for item in order.items:
            self.add_item_to_table(item.product.name, item.quantity, item.price_per_unit, item.product_id)

    def add_item_to_table(self, product_name, quantity, price, product_id):
        row_position = self.items_table.rowCount()
        self.items_table.insertRow(row_position)
        self.items_table.setItem(row_position, 0, QTableWidgetItem(product_name))
        self.items_table.setItem(row_position, 1, QTableWidgetItem(str(quantity)))
        self.items_table.setItem(row_position, 2, QTableWidgetItem(str(price)))
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.items_table.removeRow(row_position))
        self.items_table.setCellWidget(row_position, 3, remove_button)
        self.items_table.setUserData(row_position, product_id)


class PurchaseOrderWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.purchase_service = PurchaseService()
        self.product_service = ProductService()
        self.supplier_service = SupplierService()
        self.db_session = next(get_db())
        self.init_ui()
        self.load_purchase_orders()

    def init_ui(self):
        layout = QVBoxLayout(self)
        button_layout = QHBoxLayout()
        self.new_order_button = QPushButton("New Purchase Order")
        self.new_order_button.clicked.connect(self.open_new_order_dialog)
        self.edit_order_button = QPushButton("Edit Selected Order")
        self.edit_order_button.clicked.connect(self.open_edit_order_dialog)
        self.delete_order_button = QPushButton("Delete Selected Order")
        self.delete_order_button.clicked.connect(self.delete_order)
        button_layout.addWidget(self.new_order_button)
        button_layout.addWidget(self.edit_order_button)
        button_layout.addWidget(self.delete_order_button)
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Supplier", "Total Amount", "Status", "Created At"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

    def load_purchase_orders(self):
        orders = self.purchase_service.get_all_purchase_orders(self.db_session)
        self.table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            self.table.setItem(row, 0, QTableWidgetItem(str(order.id)))
            self.table.setItem(row, 1, QTableWidgetItem(order.supplier.name))
            self.table.setItem(row, 2, QTableWidgetItem(str(order.total_amount)))
            self.table.setItem(row, 3, QTableWidgetItem(order.status))
            self.table.setItem(row, 4, QTableWidgetItem(order.created_at.strftime("%Y-%m-%d %H:%M:%S")))

    def open_new_order_dialog(self):
        dialog = PurchaseOrderDialog(self.purchase_service, self.product_service, self.supplier_service, self.db_session)
        if dialog.exec():
            self.load_purchase_orders()

    def open_edit_order_dialog(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an order to edit.")
            return
        order_id = int(self.table.item(selected_rows[0].row(), 0).text())
        dialog = PurchaseOrderDialog(self.purchase_service, self.product_service, self.supplier_service, self.db_session, order_id=order_id)
        if dialog.exec():
            self.load_purchase_orders()

    def delete_order(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an order to delete.")
            return
        order_id = int(self.table.item(selected_rows[0].row(), 0).text())
        reply = QMessageBox.question(self, "Delete Order", "Are you sure you want to delete this purchase order?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.purchase_service.delete_purchase_order(self.db_session, order_id)
            self.load_purchase_orders()