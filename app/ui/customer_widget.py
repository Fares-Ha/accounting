from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox, QHeaderView
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
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(5)
        self.customer_table.setHorizontalHeaderLabels([self.tr('ID'), self.tr('Name'), self.tr('Email'), self.tr('Phone'), self.tr('Address')])
        self.customer_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.customer_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
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
        db_gen = get_db()
        db = next(db_gen)
        try:
            customers = get_customers(db)
            self.customer_table.setRowCount(len(customers))
            for row, customer in enumerate(customers):
                self.customer_table.setItem(row, 0, QTableWidgetItem(str(customer.id)))
                self.customer_table.setItem(row, 1, QTableWidgetItem(customer.name))
                self.customer_table.setItem(row, 2, QTableWidgetItem(customer.email))
                self.customer_table.setItem(row, 3, QTableWidgetItem(customer.phone))
                self.customer_table.setItem(row, 4, QTableWidgetItem(customer.address))
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
        selected_rows = self.customer_table.selectionModel().selectedRows()
        if selected_rows:
            selected_row = selected_rows[0].row()
            customer_id = int(self.customer_table.item(selected_row, 0).text())
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
        selected_rows = self.customer_table.selectionModel().selectedRows()
        if selected_rows:
            reply = QMessageBox.question(self, self.tr('Delete Customer'), self.tr('Are you sure you want to delete this customer?'),
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                selected_row = selected_rows[0].row()
                customer_id = int(self.customer_table.item(selected_row, 0).text())
                db_gen = get_db()
                db = next(db_gen)
                try:
                    delete_customer(db, customer_id)
                    self.load_customers()
                finally:
                    next(db_gen, None)
        else:
            QMessageBox.warning(self, self.tr("No Customer Selected"), self.tr("Please select a customer to delete."))

    def select_customer(self, customer_id):
        """
        Selects a customer in the table by their ID.
        """
        for row in range(self.customer_table.rowCount()):
            item = self.customer_table.item(row, 0)
            if item and int(item.text()) == customer_id:
                self.customer_table.selectRow(row)
                break