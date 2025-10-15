from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from app.core.supplier_service import SupplierService
from .supplier_dialog import SupplierDialog
from app.database.database import get_db

class SupplierWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.supplier_service = SupplierService()
        self.db_session = next(get_db())
        self.init_ui()
        self.load_suppliers()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Buttons for actions
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Supplier")
        self.add_button.clicked.connect(self.add_supplier)
        self.edit_button = QPushButton("Edit Supplier")
        self.edit_button.clicked.connect(self.edit_supplier)
        self.delete_button = QPushButton("Delete Supplier")
        self.delete_button.clicked.connect(self.delete_supplier)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

        # Table to display suppliers
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Phone", "Address"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setColumnHidden(0, True)
        layout.addWidget(self.table)

    def load_suppliers(self):
        suppliers = self.supplier_service.get_all_suppliers(self.db_session)
        self.table.setRowCount(len(suppliers))
        for row, supplier in enumerate(suppliers):
            self.table.setItem(row, 0, QTableWidgetItem(str(supplier.id)))
            self.table.setItem(row, 1, QTableWidgetItem(supplier.name))
            self.table.setItem(row, 2, QTableWidgetItem(supplier.email))
            self.table.setItem(row, 3, QTableWidgetItem(supplier.phone))
            self.table.setItem(row, 4, QTableWidgetItem(supplier.address))

    def add_supplier(self):
        dialog = SupplierDialog()
        if dialog.exec():
            self.load_suppliers()

    def edit_supplier(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a supplier to edit.")
            return

        selected_row = selected_rows[0].row()
        supplier_id = int(self.table.item(selected_row, 0).text())
        supplier = self.supplier_service.get_supplier_by_id(self.db_session, supplier_id)
        if supplier:
            dialog = SupplierDialog(supplier=supplier)
            if dialog.exec():
                self.load_suppliers()

    def delete_supplier(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a supplier to delete.")
            return

        selected_row = selected_rows[0].row()
        supplier_id = int(self.table.item(selected_row, 0).text())

        reply = QMessageBox.question(self, "Delete Supplier", "Are you sure you want to delete this supplier?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.supplier_service.delete_supplier(self.db_session, supplier_id)
            self.load_suppliers()