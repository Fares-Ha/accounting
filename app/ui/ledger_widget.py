from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import QCoreApplication
from ..database.database import get_db
from ..core import accounting_service

class LedgerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([self.tr("ID"), self.tr("Type"), self.tr("Amount"), self.tr("Date"), self.tr("Related Order")])
        self.layout.addWidget(self.table)

        self.load_transactions()

    def load_transactions(self):
        self.table.setRowCount(0)
        with get_db() as db:
            transactions = accounting_service.get_ledger_transactions(db)
            for row_num, trans in enumerate(transactions):
                self.table.insertRow(row_num)
                self.table.setItem(row_num, 0, QTableWidgetItem(str(trans.id)))
                self.table.setItem(row_num, 1, QTableWidgetItem(trans.transaction_type.value))
                self.table.setItem(row_num, 2, QTableWidgetItem(str(trans.amount)))
                self.table.setItem(row_num, 3, QTableWidgetItem(trans.created_at.strftime("%Y-%m-%d")))
                self.table.setItem(row_num, 4, QTableWidgetItem(f"{trans.related_order_type} #{trans.related_order_id}"))