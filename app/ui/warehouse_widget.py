from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from app.core import warehouse_service
from app.database.database import get_db
from .warehouse_dialog import WarehouseDialog

class WarehouseWidget(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.init_ui()
        self.load_warehouses()

    def init_ui(self):
        layout = QVBoxLayout(self)
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Warehouse")
        self.add_button.clicked.connect(self.add_warehouse)
        self.edit_button = QPushButton("Edit Warehouse")
        self.edit_button.clicked.connect(self.edit_warehouse)
        self.delete_button = QPushButton("Delete Warehouse")
        self.delete_button.clicked.connect(self.delete_warehouse)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Location"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

    def load_warehouses(self):
        with get_db() as db:
            warehouses = warehouse_service.get_warehouses(db)
            self.table.setRowCount(len(warehouses))
            for row, warehouse in enumerate(warehouses):
                self.table.setItem(row, 0, QTableWidgetItem(str(warehouse.id)))
                self.table.setItem(row, 1, QTableWidgetItem(warehouse.name))
                self.table.setItem(row, 2, QTableWidgetItem(warehouse.location))

    def add_warehouse(self):
        dialog = WarehouseDialog(self.user_id)
        if dialog.exec():
            self.load_warehouses()

    def edit_warehouse(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a warehouse to edit.")
            return
        warehouse_id = int(self.table.item(selected_rows[0].row(), 0).text())
        dialog = WarehouseDialog(self.user_id, warehouse_id=warehouse_id)
        if dialog.exec():
            self.load_warehouses()

    def delete_warehouse(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a warehouse to delete.")
            return
        warehouse_id = int(self.table.item(selected_rows[0].row(), 0).text())

        reply = QMessageBox.question(self, "Delete Warehouse", "Are you sure you want to delete this warehouse?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            with get_db() as db:
                try:
                    warehouse_service.delete_warehouse(db, self.user_id, warehouse_id)
                    self.load_warehouses()
                except ValueError as e:
                    QMessageBox.critical(self, "Error", str(e))