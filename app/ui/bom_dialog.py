from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox, QComboBox, QSpinBox, QTableWidget, QTableWidgetItem, QHeaderView
from app.core import manufacturing_service, product_service
from app.database.database import get_db

class BOMDialog(QDialog):
    def __init__(self, user_id, bom_id=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.bom_id = bom_id
        self.is_edit_mode = self.bom_id is not None
        self.items = []

        self.setWindowTitle("Edit BOM" if self.is_edit_mode else "Add BOM")
        self.init_ui()
        self.load_products()
        if self.is_edit_mode:
            self.load_bom_data()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.description_input = QLineEdit()
        self.product_combo = QComboBox()

        self.form_layout.addRow("Name:", self.name_input)
        self.form_layout.addRow("Description:", self.description_input)
        self.form_layout.addRow("Product:", self.product_combo)

        self.items_table = QTableWidget()
        self.items_table.setColumnCount(3)
        self.items_table.setHorizontalHeaderLabels(["Component", "Quantity", "Remove"])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.add_item_layout = QHBoxLayout()
        self.component_combo = QComboBox()
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 9999)
        self.add_item_button = QPushButton("Add Component")
        self.add_item_button.clicked.connect(self.add_item)
        self.add_item_layout.addWidget(self.component_combo)
        self.add_item_layout.addWidget(self.quantity_spin)
        self.add_item_layout.addWidget(self.add_item_button)

        self.submit_button = QPushButton("Save" if self.is_edit_mode else "Create")
        self.submit_button.clicked.connect(self.submit)

        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.items_table)
        self.layout.addLayout(self.add_item_layout)
        self.layout.addWidget(self.submit_button)

    def load_products(self):
        with get_db() as db:
            products = product_service.get_products(db)
            for product in products:
                self.product_combo.addItem(product.name, product.id)
                self.component_combo.addItem(product.name, product.id)

    def load_bom_data(self):
        with get_db() as db:
            bom = manufacturing_service.get_bom(db, self.user_id, self.bom_id)
            if bom:
                self.name_input.setText(bom.name)
                self.description_input.setText(bom.description)
                self.product_combo.setCurrentIndex(self.product_combo.findData(bom.product_id))
                for item in bom.items:
                    self.items.append({"component_id": item.component_id, "quantity": item.quantity})
                self.refresh_items_table()

    def add_item(self):
        component_id = self.component_combo.currentData()
        quantity = self.quantity_spin.value()
        self.items.append({"component_id": component_id, "quantity": quantity})
        self.refresh_items_table()

    def remove_item(self, index):
        del self.items[index]
        self.refresh_items_table()

    def refresh_items_table(self):
        self.items_table.setRowCount(len(self.items))
        with get_db() as db:
            for i, item in enumerate(self.items):
                component = product_service.get_product(db, item['component_id'])
                self.items_table.setItem(i, 0, QTableWidgetItem(component.name))
                self.items_table.setItem(i, 1, QTableWidgetItem(str(item['quantity'])))
                remove_button = QPushButton("Remove")
                remove_button.clicked.connect(lambda _, index=i: self.remove_item(index))
                self.items_table.setCellWidget(i, 2, remove_button)

    def submit(self):
        name = self.name_input.text()
        description = self.description_input.text()
        product_id = self.product_combo.currentData()

        if not all([name, product_id, self.items]):
            QMessageBox.warning(self, "Input Error", "All fields and at least one component are required.")
            return

        with get_db() as db:
            try:
                if self.is_edit_mode:
                    manufacturing_service.update_bom(db, self.user_id, self.bom_id, product_id, name, description, self.items)
                else:
                    manufacturing_service.create_bom(db, self.user_id, product_id, name, description, self.items)
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save BOM: {e}")