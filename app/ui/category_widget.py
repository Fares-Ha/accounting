from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QFormLayout, QLineEdit, QDialogButtonBox
from PyQt6.QtCore import QCoreApplication
from ..database import models
from ..database.database import get_db
from ..core import category_service

class CategoryDialog(QDialog):
    def __init__(self, category=None):
        super().__init__()
        self.category = category
        self.setWindowTitle(self.tr("Add/Edit Category"))

        self.layout = QFormLayout(self)
        self.name_input = QLineEdit(category.name if category else "")
        self.layout.addRow(self.tr("Name:"), self.name_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_data(self):
        return {"name": self.name_input.text()}

class CategoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels([self.tr("ID"), self.tr("Name")])
        self.layout.addWidget(self.table)

        self.add_button = QPushButton(self.tr("Add Category"))
        self.add_button.clicked.connect(self.add_category)
        self.layout.addWidget(self.add_button)

        self.edit_button = QPushButton(self.tr("Edit Category"))
        self.edit_button.clicked.connect(self.edit_category)
        self.layout.addWidget(self.edit_button)

        self.delete_button = QPushButton(self.tr("Delete Category"))
        self.delete_button.clicked.connect(self.delete_category)
        self.layout.addWidget(self.delete_button)

        self.load_categories()

    def load_categories(self):
        self.table.setRowCount(0)
        with get_db() as db:
            categories = category_service.get_categories(db)
            for row_num, category in enumerate(categories):
                self.table.insertRow(row_num)
                self.table.setItem(row_num, 0, QTableWidgetItem(str(category.id)))
                self.table.setItem(row_num, 1, QTableWidgetItem(category.name))

    def add_category(self):
        dialog = CategoryDialog()
        if dialog.exec():
            data = dialog.get_data()
            with get_db() as db:
                category_service.create_category(db, **data)
            self.load_categories()

    def edit_category(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Please select a category to edit."))
            return

        category_id = int(self.table.item(selected_row, 0).text())
        with get_db() as db:
            category = db.query(models.ProductCategory).filter(models.ProductCategory.id == category_id).first()

        dialog = CategoryDialog(category)
        if dialog.exec():
            data = dialog.get_data()
            with get_db() as db:
                category_service.update_category(db, category_id, **data)
            self.load_categories()

    def delete_category(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Please select a category to delete."))
            return

        category_id = int(self.table.item(selected_row, 0).text())
        reply = QMessageBox.question(self, self.tr("Confirm Delete"), self.tr("Are you sure you want to delete this category?"),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            with get_db() as db:
                category_service.delete_category(db, category_id)
            self.load_categories()