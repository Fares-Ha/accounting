from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from app.core import manufacturing_service
from app.database.database import get_db
from .bom_dialog import BOMDialog

class BOMWidget(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.init_ui()
        self.load_boms()

    def init_ui(self):
        layout = QVBoxLayout(self)
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add BOM")
        self.add_button.clicked.connect(self.add_bom)
        self.edit_button = QPushButton("Edit BOM")
        self.edit_button.clicked.connect(self.edit_bom)
        self.delete_button = QPushButton("Delete BOM")
        self.delete_button.clicked.connect(self.delete_bom)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Product", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

    def load_boms(self):
        with get_db() as db:
            boms = manufacturing_service.get_boms(db, self.user_id)
            self.table.setRowCount(len(boms))
            for row, bom in enumerate(boms):
                self.table.setItem(row, 0, QTableWidgetItem(str(bom.id)))
                self.table.setItem(row, 1, QTableWidgetItem(bom.name))
                self.table.setItem(row, 2, QTableWidgetItem(bom.product.name))
                self.table.setItem(row, 3, QTableWidgetItem(bom.description))

    def add_bom(self):
        dialog = BOMDialog(self.user_id)
        if dialog.exec():
            self.load_boms()

    def edit_bom(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a BOM to edit.")
            return
        bom_id = int(self.table.item(selected_rows[0].row(), 0).text())
        dialog = BOMDialog(self.user_id, bom_id=bom_id)
        if dialog.exec():
            self.load_boms()

    def delete_bom(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a BOM to delete.")
            return
        bom_id = int(self.table.item(selected_rows[0].row(), 0).text())

        reply = QMessageBox.question(self, "Delete BOM", "Are you sure you want to delete this BOM?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            with get_db() as db:
                manufacturing_service.delete_bom(db, self.user_id, bom_id)
            self.load_boms()