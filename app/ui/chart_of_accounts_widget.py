from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QDialog, QLineEdit, QComboBox, QMessageBox
from PyQt6.QtCore import QCoreApplication
from ..database.database import get_db
from ..core import accounting_service
from ..database import models

class ChartOfAccountsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.add_account_button = QPushButton(self.tr("Add Account"))
        self.add_account_button.clicked.connect(self.show_add_account_dialog)
        self.layout.addWidget(self.add_account_button)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([self.tr("ID"), self.tr("Name"), self.tr("Type"), self.tr("Balance")])
        self.layout.addWidget(self.table)

        self.load_accounts()

    def load_accounts(self):
        self.table.setRowCount(0)
        with get_db() as db:
            accounts = accounting_service.get_accounts(db)
            for row_num, acc in enumerate(accounts):
                self.table.insertRow(row_num)
                self.table.setItem(row_num, 0, QTableWidgetItem(str(acc.id)))
                self.table.setItem(row_num, 1, QTableWidgetItem(acc.name))
                self.table.setItem(row_num, 2, QTableWidgetItem(acc.account_type.value))
                self.table.setItem(row_num, 3, QTableWidgetItem(str(acc.balance / 100)))

    def show_add_account_dialog(self):
        dialog = AddAccountDialog()
        if dialog.exec():
            self.load_accounts()

class AddAccountDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("Add Account"))
        self.layout = QVBoxLayout(self)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(self.tr("Name"))
        self.layout.addWidget(self.name_input)

        self.type_combo = QComboBox()
        for acc_type in models.AccountType:
            self.type_combo.addItem(acc_type.value.title(), acc_type)
        self.layout.addWidget(self.type_combo)

        self.save_button = QPushButton(self.tr("Save"))
        self.save_button.clicked.connect(self.save_account)
        self.layout.addWidget(self.save_button)

    def save_account(self):
        name = self.name_input.text()
        account_type = self.type_combo.currentData()

        if not name:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Name is required."))
            return

        try:
            with get_db() as db:
                accounting_service.create_account(db, name, account_type)
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, self.tr("Error"), str(e))