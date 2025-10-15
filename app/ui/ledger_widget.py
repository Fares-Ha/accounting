from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QDialog, QLineEdit, QComboBox, QMessageBox
from PyQt6.QtCore import QCoreApplication
from ..database.database import get_db
from ..core import accounting_service
from ..database import models

class LedgerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.add_entry_button = QPushButton(self.tr("Add Journal Entry"))
        self.add_entry_button.clicked.connect(self.show_add_entry_dialog)
        self.layout.addWidget(self.add_entry_button)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([self.tr("ID"), self.tr("Date"), self.tr("Description"), self.tr("Amount")])
        self.layout.addWidget(self.table)

        self.load_journal_entries()

    def load_journal_entries(self):
        self.table.setRowCount(0)
        with get_db() as db:
            entries = db.query(models.JournalEntry).all()
            for row_num, entry in enumerate(entries):
                self.table.insertRow(row_num)
                self.table.setItem(row_num, 0, QTableWidgetItem(str(entry.id)))
                self.table.setItem(row_num, 1, QTableWidgetItem(entry.date.strftime("%Y-%m-%d")))
                self.table.setItem(row_num, 2, QTableWidgetItem(entry.description))
                total_amount = sum(t.amount for t in entry.transactions if t.amount > 0)
                self.table.setItem(row_num, 3, QTableWidgetItem(str(total_amount / 100)))

    def show_add_entry_dialog(self):
        dialog = AddJournalEntryDialog()
        if dialog.exec():
            self.load_journal_entries()


class AddJournalEntryDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("Add Journal Entry"))
        self.layout = QVBoxLayout(self)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText(self.tr("Description"))
        self.layout.addWidget(self.description_input)

        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(3)
        self.transaction_table.setHorizontalHeaderLabels([self.tr("Account"), self.tr("Debit"), self.tr("Credit")])
        self.layout.addWidget(self.transaction_table)

        self.add_row_button = QPushButton(self.tr("Add Row"))
        self.add_row_button.clicked.connect(self.add_transaction_row)
        self.layout.addWidget(self.add_row_button)

        self.save_button = QPushButton(self.tr("Save"))
        self.save_button.clicked.connect(self.save_journal_entry)
        self.layout.addWidget(self.save_button)

        self.load_accounts()
        self.add_transaction_row()
        self.add_transaction_row()

    def load_accounts(self):
        with get_db() as db:
            self.accounts = accounting_service.get_accounts(db)

    def add_transaction_row(self):
        row_num = self.transaction_table.rowCount()
        self.transaction_table.insertRow(row_num)

        account_combo = QComboBox()
        for acc in self.accounts:
            account_combo.addItem(acc.name, acc.id)
        self.transaction_table.setCellWidget(row_num, 0, account_combo)

        debit_input = QLineEdit()
        debit_input.setPlaceholderText(self.tr("Debit"))
        self.transaction_table.setCellWidget(row_num, 1, debit_input)

        credit_input = QLineEdit()
        credit_input.setPlaceholderText(self.tr("Credit"))
        self.transaction_table.setCellWidget(row_num, 2, credit_input)

    def save_journal_entry(self):
        description = self.description_input.text()
        if not description:
            QMessageBox.warning(self, self.tr("Warning"), self.tr("Description is required."))
            return

        transactions = []
        for row_num in range(self.transaction_table.rowCount()):
            account_combo = self.transaction_table.cellWidget(row_num, 0)
            account_id = account_combo.currentData()

            debit_input = self.transaction_table.cellWidget(row_num, 1)
            credit_input = self.transaction_table.cellWidget(row_num, 2)

            debit_text = debit_input.text()
            credit_text = credit_input.text()

            if debit_text and credit_text:
                QMessageBox.warning(self, self.tr("Warning"), self.tr("Enter either a debit or a credit, not both."))
                return

            if debit_text:
                try:
                    amount = int(float(debit_text) * 100)
                    transactions.append({"account_id": account_id, "amount": amount})
                except ValueError:
                    QMessageBox.warning(self, self.tr("Warning"), self.tr("Invalid debit amount."))
                    return
            elif credit_text:
                try:
                    amount = -int(float(credit_text) * 100)
                    transactions.append({"account_id": account_id, "amount": amount})
                except ValueError:
                    QMessageBox.warning(self, self.tr("Warning"), self.tr("Invalid credit amount."))
                    return

        try:
            with get_db() as db:
                accounting_service.create_journal_entry(db, description, transactions)
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, self.tr("Error"), str(e))