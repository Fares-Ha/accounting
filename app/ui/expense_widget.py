from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTableWidget,
                             QTableWidgetItem, QMessageBox, QDialog, QFormLayout,
                             QComboBox, QLineEdit, QDialogButtonBox, QHBoxLayout, QDateTimeEdit)
from PyQt6.QtCore import QDateTime
from ..database.database import get_db
from ..core import expense_service
from ..database import models

class ExpenseDialog(QDialog):
    def __init__(self, expense=None, parent=None):
        super().__init__(parent)
        self.expense = expense
        self.setWindowTitle(self.tr("Edit Expense") if self.expense else self.tr("Create Expense"))

        self.layout = QFormLayout(self)
        self.description_input = QLineEdit()
        self.amount_input = QLineEdit()
        self.date_input = QDateTimeEdit(QDateTime.currentDateTime())
        self.date_input.setCalendarPopup(True)
        self.category_combo = QComboBox()

        self.layout.addRow(self.tr("Description:"), self.description_input)
        self.layout.addRow(self.tr("Amount:"), self.amount_input)
        self.layout.addRow(self.tr("Date:"), self.date_input)
        self.layout.addRow(self.tr("Category:"), self.category_combo)

        self.load_categories()

        if self.expense:
            self.populate_expense_data()

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def load_categories(self):
        with get_db() as db:
            categories = expense_service.get_expense_categories(db)
            for cat in categories:
                self.category_combo.addItem(cat.name, userData=cat.id)

    def populate_expense_data(self):
        self.description_input.setText(self.expense.description)
        self.amount_input.setText(str(self.expense.amount / 100.0)) # Convert from cents
        self.date_input.setDateTime(self.expense.expense_date)
        category_index = self.category_combo.findData(self.expense.category_id)
        if category_index >= 0:
            self.category_combo.setCurrentIndex(category_index)

    def get_data(self):
        amount_in_cents = int(float(self.amount_input.text()) * 100)
        return {
            "description": self.description_input.text(),
            "amount": amount_in_cents,
            "expense_date": self.date_input.dateTime().toPyDateTime(),
            "category_id": self.category_combo.currentData()
        }

class ExpenseWidget(QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([self.tr("ID"), self.tr("Description"), self.tr("Amount"), self.tr("Category"), self.tr("Date"), self.tr("Actions")])
        self.layout.addWidget(self.table)

        self.add_button = QPushButton(self.tr("Add Expense"))
        self.add_button.clicked.connect(self.add_expense)
        self.delete_button = QPushButton(self.tr("Delete Selected"))
        self.delete_button.clicked.connect(self.delete_selected_expense)

        self.manage_categories_button = QPushButton(self.tr("Manage Categories"))
        self.manage_categories_button.clicked.connect(self.manage_categories)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.manage_categories_button)
        self.layout.addLayout(button_layout)

        self.load_expenses()

    def load_expenses(self):
        self.table.setRowCount(0)
        with get_db() as db:
            expenses = expense_service.get_expenses(db)
            for row, expense in enumerate(expenses):
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(expense.id)))
                self.table.setItem(row, 1, QTableWidgetItem(expense.description))
                self.table.setItem(row, 2, QTableWidgetItem(f"{expense.amount / 100.0:.2f}"))
                self.table.setItem(row, 3, QTableWidgetItem(expense.category.name))
                self.table.setItem(row, 4, QTableWidgetItem(expense.expense_date.strftime("%Y-%m-%d")))

                edit_button = QPushButton(self.tr("Edit"))
                edit_button.clicked.connect(lambda _, r=row: self.edit_expense(r))
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.addWidget(edit_button)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                self.table.setCellWidget(row, 5, actions_widget)

    def add_expense(self):
        dialog = ExpenseDialog(parent=self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                with get_db() as db:
                    expense_service.create_expense(db, user_id=self.current_user.id, **data)
                self.load_expenses()
            except Exception as e:
                QMessageBox.critical(self, self.tr("Error"), str(e))

    def edit_expense(self, row):
        expense_id = int(self.table.item(row, 0).text())
        with get_db() as db:
            expense = expense_service.get_expense(db, expense_id)

        if not expense:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Expense not found."))
            return

        dialog = ExpenseDialog(expense=expense, parent=self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                with get_db() as db:
                    expense_service.update_expense(db, user_id=self.current_user.id, expense_id=expense_id, **data)
                self.load_expenses()
            except Exception as e:
                QMessageBox.critical(self, self.tr("Error"), str(e))

    def delete_selected_expense(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, self.tr("No Selection"), self.tr("Please select an expense to delete."))
            return

        row = selected_items[0].row()
        expense_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(self, self.tr("Confirm Deletion"),
                                     self.tr(f"Are you sure you want to delete expense {expense_id}?"),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                with get_db() as db:
                    expense_service.delete_expense(db, user_id=self.current_user.id, expense_id=expense_id)
                self.load_expenses()
            except Exception as e:
                QMessageBox.critical(self, self.tr("Error"), str(e))

    def manage_categories(self):
        # This can be a simple dialog for now.
        # A more advanced implementation would be a separate widget.
        pass