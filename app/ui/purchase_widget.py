from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout, QComboBox, QSpinBox, QDialogButtonBox, QHBoxLayout, QDoubleSpinBox
from PyQt6.QtCore import QCoreApplication
from ..database.database import get_db
from ..core import purchase_service, supplier_service, product_service
from ..database import models

class PurchaseDialog(QDialog):
    def __init__(self, order=None):
        super().__init__()
        self.order = order
        self.setWindowTitle(self.tr("Edit Purchase Order") if self.order else self.tr("Create Purchase Order"))
        self.layout = QFormLayout(self)
        self.supplier_combo = QComboBox()
        self.items = []

        self.load_suppliers()
        self.layout.addRow(self.tr("Supplier:"), self.supplier_combo)

        if self.order:
            self.populate_order_data()

        # Integrated item selection
        self.item_selection_layout = QHBoxLayout()
        self.product_combo = QComboBox()
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 9999)
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0.01, 99999.99)
        self.price_spin.setDecimals(2)
        self.add_item_button = QPushButton(self.tr("Add Item"))

        self.item_selection_layout.addWidget(self.product_combo)
        self.item_selection_layout.addWidget(self.quantity_spin)
        self.item_selection_layout.addWidget(self.price_spin)
        self.item_selection_layout.addWidget(self.add_item_button)
        self.layout.addLayout(self.item_selection_layout)

        self.load_products()
        self.add_item_button.clicked.connect(self.add_item_to_order)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels([self.tr("Product"), self.tr("Quantity"), self.tr("Price Per Unit"), self.tr("Actions")])
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

    def load_products(self):
        with get_db() as db:
            products = product_service.get_products(db)
            for p in products:
                self.product_combo.addItem(p.name, userData=p)

    def add_item_to_order(self):
        product = self.product_combo.currentData()
        quantity = self.quantity_spin.value()
        price = self.price_spin.value()

        if quantity <= 0 or price <= 0:
            return

        # Check if item already exists
        for item in self.items:
            if item['product_id'] == product.id:
                QMessageBox.warning(self, self.tr("Duplicate Item"), self.tr("This item is already in the order."))
                return

        self.items.append({'product_id': product.id, 'quantity': quantity, 'price_per_unit': price})
        self.refresh_items_table()

    def remove_item(self, product_id):
        self.items = [item for item in self.items if item['product_id'] != product_id]
        self.refresh_items_table()

    def refresh_items_table(self):
        self.items_table.setRowCount(0)
        for row_num, item_data in enumerate(self.items):
             with get_db() as db:
                product = product_service.get_product(db, item_data['product_id'])
             self.items_table.insertRow(row_num)
             self.items_table.setItem(row_num, 0, QTableWidgetItem(product.name))
             self.items_table.setItem(row_num, 1, QTableWidgetItem(str(item_data['quantity'])))
             self.items_table.setItem(row_num, 2, QTableWidgetItem(f"{item_data['price_per_unit']:.2f}"))

             remove_button = QPushButton(self.tr("Remove"))
             remove_button.clicked.connect(lambda _, pid=product.id: self.remove_item(pid))
             self.items_table.setCellWidget(row_num, 3, remove_button)


    def get_data(self):
        return {
            "supplier_id": self.supplier_combo.currentData(),
            "items": self.items
        }

    def populate_order_data(self):
        # Set supplier
        supplier_index = self.supplier_combo.findData(self.order.supplier_id)
        if supplier_index >= 0:
            self.supplier_combo.setCurrentIndex(supplier_index)

        # Populate items table
        for item in self.order.items:
            self.items.append({
                'product_id': item.product_id,
                'quantity': item.quantity,
                'price_per_unit': item.price_per_unit
            })
        self.refresh_items_table()

class PurchaseWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([self.tr("ID"), self.tr("Supplier"), self.tr("Total Amount"), self.tr("Status"), self.tr("Date"), self.tr("Actions")])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.layout.addWidget(self.table)

        self.add_button = QPushButton(self.tr("Create Purchase Order"))
        self.add_button.clicked.connect(self.create_order)
        self.delete_button = QPushButton(self.tr("Delete Selected Order"))
        self.delete_button.clicked.connect(self.delete_selected_order)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        self.layout.addLayout(button_layout)

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
                self.table.setItem(row_num, 3, QTableWidgetItem(self.tr(order.status)))
                self.table.setItem(row_num, 4, QTableWidgetItem(order.created_at.strftime("%Y-%m-%d")))

                actions_layout = QHBoxLayout()
                edit_button = QPushButton(self.tr("Edit"))
                edit_button.clicked.connect(lambda _, r=row_num: self.edit_order(r))
                delete_button = QPushButton(self.tr("Delete"))
                delete_button.clicked.connect(lambda _, r=row_num: self.delete_order(r))
                receive_button = QPushButton(self.tr("Mark as Received"))
                receive_button.clicked.connect(lambda _, r=row_num: self.receive_order(r))

                if order.status == "Received":
                    edit_button.setEnabled(False)
                    receive_button.setEnabled(False)

                actions_layout.addWidget(edit_button)
                actions_layout.addWidget(delete_button)
                actions_layout.addWidget(receive_button)

                actions_widget = QWidget()
                actions_widget.setLayout(actions_layout)
                self.table.setCellWidget(row_num, 5, actions_widget)

    def create_order(self):
        dialog = PurchaseDialog()
        if dialog.exec():
            data = dialog.get_data()
            try:
                with get_db() as db:
                    purchase_service.create_purchase_order(db, **data)
                self.load_orders()
            except ValueError as e:
                QMessageBox.critical(self, self.tr("Error"), str(e))

    def edit_order(self, row_num):
        order_id = int(self.table.item(row_num, 0).text())
        with get_db() as db:
            order = purchase_service.get_purchase_order(db, order_id)

        if not order:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Order not found."))
            return

        dialog = PurchaseDialog(order=order)
        if dialog.exec():
            data = dialog.get_data()
            try:
                with get_db() as db:
                    purchase_service.update_purchase_order(db, order_id, **data)
                self.load_orders()
            except ValueError as e:
                QMessageBox.critical(self, self.tr("Error"), str(e))

    def delete_order(self, row_num):
        order_id = int(self.table.item(row_num, 0).text())
        reply = QMessageBox.question(self, self.tr("Confirm Deletion"),
                                     self.tr(f"Are you sure you want to delete purchase order {order_id}?"),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                with get_db() as db:
                    purchase_service.delete_purchase_order(db, order_id)
                self.load_orders()
            except ValueError as e:
                QMessageBox.critical(self, self.tr("Error"), str(e))

    def delete_selected_order(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, self.tr("No Selection"), self.tr("Please select an order to delete."))
            return

        row_num = selected_items[0].row()
        self.delete_order(row_num)

    def receive_order(self, row_num):
        order_id = int(self.table.item(row_num, 0).text())
        reply = QMessageBox.question(self, self.tr("Confirm Reception"),
                                     self.tr(f"Are you sure you want to mark order {order_id} as received? This will increase stock levels."),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                with get_db() as db:
                    purchase_service.receive_purchase_order(db, order_id)
                self.load_orders()
            except ValueError as e:
                QMessageBox.critical(self, self.tr("Error"), str(e))