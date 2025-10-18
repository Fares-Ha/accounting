from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox
from app.core import warehouse_service
from app.database.database import get_db

class WarehouseDialog(QDialog):
    def __init__(self, user_id, warehouse_id=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.warehouse_id = warehouse_id
        self.is_edit_mode = self.warehouse_id is not None

        self.setWindowTitle("Edit Warehouse" if self.is_edit_mode else "Add Warehouse")
        self.init_ui()
        if self.is_edit_mode:
            self.load_warehouse_data()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.location_input = QLineEdit()

        self.form_layout.addRow("Name:", self.name_input)
        self.form_layout.addRow("Location:", self.location_input)

        self.submit_button = QPushButton("Save" if self.is_edit_mode else "Create")
        self.submit_button.clicked.connect(self.submit)

        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.submit_button)

    def load_warehouse_data(self):
        with get_db() as db:
            warehouse = warehouse_service.get_warehouse(db, self.warehouse_id)
            if warehouse:
                self.name_input.setText(warehouse.name)
                self.location_input.setText(warehouse.location)

    def submit(self):
        name = self.name_input.text()
        location = self.location_input.text()

        if not name:
            QMessageBox.warning(self, "Input Error", "Warehouse name is required.")
            return

        with get_db() as db:
            try:
                if self.is_edit_mode:
                    warehouse_service.update_warehouse(db, self.user_id, self.warehouse_id, name, location)
                else:
                    warehouse_service.create_warehouse(db, self.user_id, name, location)
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save warehouse: {e}")