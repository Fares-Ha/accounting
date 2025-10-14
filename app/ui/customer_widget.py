from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableView, QHBoxLayout, QMessageBox
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import QCoreApplication
from app.core.customer_service import get_customers, delete_customer, get_customer_by_id, get_db
from .customer_dialog import CustomerDialog

class CustomerWidget(QWidget):
    """
    Widget for managing customers.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton(self.tr("Add Customer"))
        self.edit_button = QPushButton(self.tr("Edit Customer"))
        self.delete_button = QPushButton(self.tr("Delete Customer"))
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

        # Create the table view for displaying customers
        self.customer_table = QTableView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([self.tr('ID'), self.tr('Name'), self.tr('Email'), self.tr('Phone'), self.tr('Address')])
        self.customer_table.setModel(self.model)
        self.customer_table.setColumnHidden(0, True) # Hide the ID column
        layout.addWidget(self.customer_table)

        self.setLayout(layout)

        # Connect signals to slots
        self.add_button.clicked.connect(self.add_customer)
        self.edit_button.clicked.connect(self.edit_customer)
        self.delete_button.clicked.connect(self.delete_customer)

        self.load_customers()

    def load_customers(self):
        """
        Load customers from the database and display them in the table.
        """
        self.model.removeRows(0, self.model.rowCount())
        db_gen = get_db()
        db = next(db_gen)
        try:
            customers = get_customers(db)
            for customer in customers:
                row = [
                    QStandardItem(str(customer.id)),
                    QStandardItem(customer.name),
                    QStandardItem(customer.email),
                    QStandardItem(customer.phone),
                    QStandardItem(customer.address)
                ]
                self.model.appendRow(row)
        finally:
            next(db_gen, None)

    def add_customer(self):
        """
        Open a dialog to add a new customer.
        """
        dialog = CustomerDialog()
        if dialog.exec():
            self.load_customers()

    def edit_customer(self):
        """
        Open a dialog to edit the selected customer.
        """
        selected_row = self.customer_table.currentIndex().row()
        if selected_row >= 0:
            customer_id = int(self.model.item(selected_row, 0).text())
            db_gen = get_db()
            db = next(db_gen)
            try:
                customer = get_customer_by_id(db, customer_id)
                if customer:
                    dialog = CustomerDialog(customer=customer)
                    if dialog.exec():
                        self.load_customers()
            finally:
                next(db_gen, None)
        else:
            QMessageBox.warning(self, self.tr("No Customer Selected"), self.tr("Please select a customer to edit."))


    def delete_customer(self):
        """
        Delete the selected customer.
        """
        selected_row = self.customer_table.currentIndex().row()
        if selected_row >= 0:
            reply = QMessageBox.question(self, self.tr('Delete Customer'), self.tr('Are you sure you want to delete this customer?'),
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                customer_id = int(self.model.item(selected_row, 0).text())
                db_gen = get_db()
                db = next(db_gen)
                try:
                    delete_customer(db, customer_id)
                    self.load_customers()
                finally:
                    next(db_gen, None)
        else:
            QMessageBox.warning(self, self.tr("No Customer Selected"), self.tr("Please select a customer to delete."))