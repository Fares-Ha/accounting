from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout, QComboBox, QSpinBox, QDialogButtonBox, QHBoxLayout
from PyQt6.QtCore import QCoreApplication
from .sales_order_detail_dialog import SalesOrderDetailDialog
from ..database.database import get_db
from ..core import sales_service, customer_service, product_service, export_service, warehouse_service
from ..database import models
import sys

class SalesOrderDialog(QDialog):
    def __init__(self, current_user, order=None):
        super().__init__()
        self.current_user = current_user
        self.order = order
        self.setWindowTitle(self.tr("Edit Sales Order") if self.order else self.tr("Create Sales Order"))
        self.layout = QFormLayout(self)
        self.customer_combo = QComboBox()
        self.warehouse_combo = QComboBox()
        self.items = []

        self.load_customers()
        self.load_warehouses()
        self.layout.addRow(self.tr("Customer:"), self.customer_combo)
        self.layout.addRow(self.tr("Warehouse:"), self.warehouse_combo)

        if self.order:
            self.populate_order_data()

        # Integrated item selection
        self.item_selection_layout = QHBoxLayout()
        self.product_combo = QComboBox()
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 9999)
        self.add_item_button = QPushButton(self.tr("Add Item"))

        self.item_selection_layout.addWidget(self.product_combo)
        self.item_selection_layout.addWidget(self.quantity_spin)
        self.item_selection_layout.addWidget(self.add_item_button)
        self.layout.addLayout(self.item_selection_layout)

        self.load_products()
        self.product_combo.currentIndexChanged.connect(self.update_add_item_button_state)
        self.warehouse_combo.currentIndexChanged.connect(self.load_products)
        self.add_item_button.clicked.connect(self.add_item_to_order)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels([self.tr("Product"), self.tr("Quantity"), self.tr("Price"), self.tr("Actions")])
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

    def load_warehouses(self):
        with get_db() as db:
            warehouses = warehouse_service.get_warehouses(db)
            for warehouse in warehouses:
                self.warehouse_combo.addItem(warehouse.name, userData=warehouse.id)

    def load_products(self):
        self.product_combo.clear()
        warehouse_id = self.warehouse_combo.currentData()
        if not warehouse_id:
            return
        with get_db() as db:
            products = product_service.get_products(db)
            for p in products:
                stock_level = product_service.get_stock_level(db, p.id, warehouse_id)
                self.product_combo.addItem(f"{p.name} (Stock: {stock_level})", userData=p)

    def update_add_item_button_state(self, index):
        product = self.product_combo.itemData(index)
        if product:
            warehouse_id = self.warehouse_combo.currentData()
            with get_db() as db:
                stock_level = product_service.get_stock_level(db, product.id, warehouse_id)
            self.add_item_button.setEnabled(stock_level > 0)
            self.quantity_spin.setMaximum(stock_level)

    def add_item_to_order(self):
        product = self.product_combo.currentData()
        quantity = self.quantity_spin.value()

        if quantity <= 0:
            return

        # Check if item already exists
        for item in self.items:
            if item['product_id'] == product.id:
                QMessageBox.warning(self, self.tr("Duplicate Item"), self.tr("This item is already in the order."))
                return

        self.items.append({'product_id': product.id, 'quantity': quantity, 'price': product.price})
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
             self.items_table.setItem(row_num, 2, QTableWidgetItem(f"{item_data['price']:.2f}"))

             remove_button = QPushButton(self.tr("Remove"))
             remove_button.clicked.connect(lambda _, pid=product.id: self.remove_item(pid))
             self.items_table.setCellWidget(row_num, 3, remove_button)


    def get_data(self):
        return {
            "customer_id": self.customer_combo.currentData(),
            "warehouse_id": self.warehouse_combo.currentData(),
            "items": self.items
        }

    def populate_order_data(self):
        # Set customer
        customer_index = self.customer_combo.findData(self.order.customer_id)
        if customer_index >= 0:
            self.customer_combo.setCurrentIndex(customer_index)

        # Populate items table
        for item in self.order.items:
            self.items.append({
                'product_id': item.product_id,
                'quantity': item.quantity,
                'price': item.price_per_unit
            })
        self.refresh_items_table()

class SalesWidget(QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([self.tr("ID"), self.tr("Customer"), self.tr("Total Amount"), self.tr("Date"), self.tr("Actions")])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self.view_order_details)
        self.layout.addWidget(self.table)

        self.add_button = QPushButton(self.tr("Create Sales Order"))
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
        try:
            with get_db() as db:
                orders = sales_service.get_sales_orders(db, user_id=self.current_user.id)
                for row_num, order in enumerate(orders):
                    self.table.insertRow(row_num)
                    self.table.setItem(row_num, 0, QTableWidgetItem(str(order.id)))
                    self.table.setItem(row_num, 1, QTableWidgetItem(order.customer.name))
                    self.table.setItem(row_num, 2, QTableWidgetItem(str(order.total_amount)))
                    self.table.setItem(row_num, 3, QTableWidgetItem(order.created_at.strftime("%Y-%m-%d")))

                    actions_layout = QHBoxLayout()
                    edit_button = QPushButton(self.tr("Edit"))
                    edit_button.clicked.connect(lambda _, r=row_num: self.edit_order(r))
                    delete_button = QPushButton(self.tr("Delete"))
                    delete_button.clicked.connect(lambda _, r=row_num: self.delete_order(r))
                    receipt_button = QPushButton(self.tr("Receipt"))
                    receipt_button.clicked.connect(lambda _, r=row_num: self.print_receipt(r))
                    actions_layout.addWidget(edit_button)
                    actions_layout.addWidget(delete_button)
                    actions_layout.addWidget(receipt_button)

                    actions_widget = QWidget()
                    actions_widget.setLayout(actions_layout)
                    self.table.setCellWidget(row_num, 4, actions_widget)
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Could not load sales orders: {e}"))

    def create_order(self):
        dialog = SalesOrderDialog(current_user=self.current_user)
        if dialog.exec():
            data = dialog.get_data()
            if not data['warehouse_id']:
                QMessageBox.warning(self, self.tr("Input Error"), self.tr("Please select a warehouse."))
                return
            try:
                with get_db() as db:
                    sales_service.create_sales_order(db, user_id=self.current_user.id, **data)
                self.load_orders()
            except Exception as e:
                QMessageBox.critical(self, self.tr("Error"), str(e))

    def select_order(self, order_id):
        """
        Selects an order in the table by its ID.
        """
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and int(item.text()) == order_id:
                self.table.selectRow(row)
                break

    def print_receipt(self, row_num):
        order_id = int(self.table.item(row_num, 0).text())
        with get_db() as db:
            order = sales_service.get_sales_order(db, user_id=self.current_user.id, order_id=order_id)

        if not order:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Order not found."))
            return

        try:
            filepath = export_service.generate_sales_receipt_pdf(order)
            QMessageBox.information(self, self.tr("Receipt Generated"), self.tr(f"Receipt saved to {filepath}"))
            # Optional: open the file
            import os
            if os.name == 'nt': # for Windows
                os.startfile(filepath)
            else: # for macOS and Linux
                import subprocess
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, filepath])

        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Could not generate receipt: {e}"))

    def view_order_details(self, model_index):
        row_num = model_index.row()
        order_id = int(self.table.item(row_num, 0).text())
        with get_db() as db:
            order = sales_service.get_sales_order(db, user_id=self.current_user.id, order_id=order_id)

        if order:
            dialog = SalesOrderDetailDialog(order, self)
            dialog.exec()

    def delete_order(self, row_num):
        order_id = int(self.table.item(row_num, 0).text())
        reply = QMessageBox.question(self, self.tr("Confirm Deletion"),
                                     self.tr(f"Are you sure you want to delete sales order {order_id}?"),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                with get_db() as db:
                    sales_service.delete_sales_order(db, user_id=self.current_user.id, order_id=order_id)
                self.load_orders()
            except Exception as e:
                QMessageBox.critical(self, self.tr("Error"), str(e))

    def delete_selected_order(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, self.tr("No Selection"), self.tr("Please select an order to delete."))
            return

        row_num = selected_items[0].row()
        self.delete_order(row_num)

    def edit_order(self, row_num):
        order_id = int(self.table.item(row_num, 0).text())
        with get_db() as db:
            order = sales_service.get_sales_order(db, user_id=self.current_user.id, order_id=order_id)

        if not order:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Order not found."))
            return

        dialog = SalesOrderDialog(current_user=self.current_user, order=order)
        if dialog.exec():
            data = dialog.get_data()
            if not data['warehouse_id']:
                QMessageBox.warning(self, self.tr("Input Error"), self.tr("Please select a warehouse."))
                return
            try:
                with get_db() as db:
                    sales_service.update_sales_order(db, user_id=self.current_user.id, order_id=order_id, **data)
                self.load_orders()
            except Exception as e:
                QMessageBox.critical(self, self.tr("Error"), str(e))