from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QFormLayout, QMessageBox,
                             QDialog, QComboBox, QSpinBox, QDialogButtonBox, QDoubleSpinBox)
from app.database.database import get_db
from app.core import purchase_service, product_service, supplier_service
from app.core.payment_service import PaymentService
from .payment_dialog import PaymentDialog

class PurchaseOrderDialog(QDialog):
    def __init__(self, order=None):
        super().__init__()
        self.order = order
        self.items = []
        self.setWindowTitle(self.tr("Edit Purchase Order") if self.order else self.tr("Create Purchase Order"))

        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        self.supplier_combo = QComboBox()
        self.form_layout.addRow(self.tr("Supplier:"), self.supplier_combo)
        self.layout.addLayout(self.form_layout)

        # Item adding section
        add_item_layout = QHBoxLayout()
        self.product_combo = QComboBox()
        self.quantity_spinbox = QSpinBox()
        self.quantity_spinbox.setRange(1, 9999)
        self.price_spinbox = QDoubleSpinBox()
        self.price_spinbox.setRange(0.01, 999999.99)
        self.price_spinbox.setDecimals(2)
        self.add_item_button = QPushButton(self.tr("Add Item"))
        self.add_item_button.clicked.connect(self.add_item)
        add_item_layout.addWidget(self.product_combo)
        add_item_layout.addWidget(self.quantity_spinbox)
        add_item_layout.addWidget(self.price_spinbox)
        add_item_layout.addWidget(self.add_item_button)
        self.layout.addLayout(add_item_layout)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels([self.tr("Product"), self.tr("Quantity"), self.tr("Price per Unit"), self.tr("Remove")])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.layout.addWidget(self.items_table)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

        self.load_suppliers_and_products()
        if self.order:
            self.load_order_data()

    def load_suppliers_and_products(self):
        with get_db() as db:
            suppliers = supplier_service.get_all_suppliers(db)
            for supplier in suppliers:
                self.supplier_combo.addItem(supplier.name, userData=supplier.id)

            products = product_service.get_products(db)
            for product in products:
                self.product_combo.addItem(product.name, userData=product.id)

    def load_order_data(self):
        # Set supplier
        supplier_index = self.supplier_combo.findData(self.order.supplier_id)
        if supplier_index >= 0:
            self.supplier_combo.setCurrentIndex(supplier_index)

        # Populate items
        self.items = [{
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price_per_unit": item.price_per_unit
        } for item in self.order.items]
        self.refresh_items_table()

    def add_item(self):
        product_id = self.product_combo.currentData()
        quantity = self.quantity_spinbox.value()
        price = self.price_spinbox.value()

        if not product_id or quantity <= 0 or price <= 0:
            QMessageBox.warning(self, self.tr("Input Error"), self.tr("Please select a product and enter a valid quantity and price."))
            return

        # Check if item already exists
        for item in self.items:
            if item['product_id'] == product_id:
                QMessageBox.warning(self, self.tr("Duplicate Item"), self.tr("This item is already in the order."))
                return

        self.items.append({
            "product_id": product_id,
            "quantity": quantity,
            "price_per_unit": price
        })
        self.refresh_items_table()

    def remove_item(self, product_id):
        self.items = [item for item in self.items if item['product_id'] != product_id]
        self.refresh_items_table()

    def refresh_items_table(self):
        self.items_table.setRowCount(0)
        with get_db() as db:
            for row_num, item_data in enumerate(self.items):
                product = product_service.get_product(db, item_data['product_id'])
                self.items_table.insertRow(row_num)
                self.items_table.setItem(row_num, 0, QTableWidgetItem(product.name))
                self.items_table.setItem(row_num, 1, QTableWidgetItem(str(item_data['quantity'])))
                self.items_table.setItem(row_num, 2, QTableWidgetItem(f"{item_data['price_per_unit']:.2f}"))

                remove_button = QPushButton(self.tr("Remove"))
                remove_button.clicked.connect(lambda _, pid=product.id: self.remove_item(pid))
                self.items_table.setCellWidget(row_num, 3, remove_button)

    def get_data(self):
        if not self.supplier_combo.currentData() or not self.items:
            return None
        return {
            "supplier_id": self.supplier_combo.currentData(),
            "items": self.items
        }


class PurchaseOrderWidget(QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([self.tr("ID"), self.tr("Supplier"), self.tr("Total Amount"), self.tr("Paid Amount"), self.tr("Status"), self.tr("Created At"), self.tr("Actions")])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton(self.tr("Create Purchase Order"))
        self.add_button.clicked.connect(self.create_order)
        self.record_payment_button = QPushButton(self.tr("Record Payment"))
        self.record_payment_button.clicked.connect(self.record_payment)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.record_payment_button)
        self.layout.addLayout(button_layout)

        self.load_orders()

    def load_orders(self):
        self.table.setRowCount(0)
        with get_db() as db:
            orders = purchase_service.get_all_purchase_orders(db)
            for row_num, order in enumerate(orders):
                self.table.insertRow(row_num)
                self.table.setItem(row_num, 0, QTableWidgetItem(str(order.id)))
                self.table.setItem(row_num, 1, QTableWidgetItem(order.supplier.name))
                self.table.setItem(row_num, 2, QTableWidgetItem(f"{order.total_amount / 100:.2f}"))
                total_paid = sum(p.amount for p in order.payments)
                self.table.setItem(row_num, 3, QTableWidgetItem(f"{total_paid / 100:.2f}"))
                self.table.setItem(row_num, 4, QTableWidgetItem(self.tr(order.status)))
                self.table.setItem(row_num, 5, QTableWidgetItem(order.created_at.strftime("%Y-%m-%d %H:%M")))

                actions_layout = QHBoxLayout()
                edit_button = QPushButton(self.tr("Edit"))
                edit_button.clicked.connect(lambda _, r=row_num: self.edit_order(r))
                delete_button = QPushButton(self.tr("Delete"))
                delete_button.clicked.connect(lambda _, r=row_num: self.delete_order(r))
                receive_button = QPushButton(self.tr("Receive"))
                receive_button.clicked.connect(lambda _, r=row_num: self.receive_order(r))

                # Disable receive button if order is already received
                if order.status == "Received":
                    receive_button.setEnabled(False)

                actions_layout.addWidget(edit_button)
                actions_layout.addWidget(delete_button)
                actions_layout.addWidget(receive_button)

                actions_widget = QWidget()
                actions_widget.setLayout(actions_layout)
                self.table.setCellWidget(row_num, 6, actions_widget)

    def create_order(self):
        dialog = PurchaseOrderDialog()
        if dialog.exec():
            data = dialog.get_data()
            if data:
                try:
                    with get_db() as db:
                        purchase_service.create_purchase_order(db, user_id=self.current_user.id, **data)
                    self.load_orders()
                except Exception as e:
                    QMessageBox.critical(self, self.tr("Error"), self.tr(f"Could not create purchase order: {e}"))
            else:
                QMessageBox.warning(self, self.tr("Input Error"), self.tr("Supplier and items must be specified."))

    def edit_order(self, row_num):
        order_id = int(self.table.item(row_num, 0).text())
        with get_db() as db:
            order = purchase_service.get_purchase_order(db, order_id)

        if not order:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Purchase order not found."))
            return

        dialog = PurchaseOrderDialog(order=order)
        if dialog.exec():
            data = dialog.get_data()
            if data:
                try:
                    with get_db() as db:
                        purchase_service.update_purchase_order(db, user_id=self.current_user.id, order_id=order_id, **data)
                    self.load_orders()
                except Exception as e:
                    QMessageBox.critical(self, self.tr("Error"), self.tr(f"Could not update purchase order: {e}"))

    def delete_order(self, row_num):
        order_id = int(self.table.item(row_num, 0).text())
        reply = QMessageBox.question(self, self.tr("Confirm Deletion"),
                                     self.tr(f"Are you sure you want to delete purchase order {order_id}?"),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                with get_db() as db:
                    purchase_service.delete_purchase_order(db, user_id=self.current_user.id, order_id=order_id)
                self.load_orders()
            except ValueError as e:
                QMessageBox.critical(self, self.tr("Error"), str(e))

    def record_payment(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Order Selected", "Please select a purchase order to record a payment.")
            return

        order_id = int(self.table.item(selected_row, 0).text())
        with get_db() as db:
            order = purchase_service.get_purchase_order(db, order_id)
            total_paid = sum(p.amount for p in order.payments)
            amount_due = order.total_amount - total_paid

        if amount_due <= 0:
            QMessageBox.information(self, "Order Paid", "This purchase order is already fully paid.")
            return

        dialog = PaymentDialog(order_id, amount_due, self)
        if dialog.exec():
            amount, payment_date, payment_method = dialog.get_payment_details()
            with get_db() as db:
                payment_service = PaymentService(db, self.current_user.id)
                try:
                    # Assuming payment from a cash account for simplicity
                    payment_service.record_purchase_payment(order_id, amount, payment_date, payment_method, "Cash")
                    self.load_orders()
                except Exception as e:
                    QMessageBox.critical(self, "Payment Error", f"Could not record payment: {e}")

    def select_order(self, order_id):
        """
        Selects an order in the table by its ID.
        """
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and int(item.text()) == order_id:
                self.table.selectRow(row)
                break

    def receive_order(self, row_num):
        order_id = int(self.table.item(row_num, 0).text())
        reply = QMessageBox.question(self, self.tr("Confirm Reception"),
                                     self.tr(f"Are you sure you want to mark order {order_id} as received? This will update stock levels."),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                with get_db() as db:
                    purchase_service.receive_purchase_order(db, user_id=self.current_user.id, order_id=order_id)
                self.load_orders()
            except ValueError as e:
                QMessageBox.critical(self, self.tr("Error"), str(e))