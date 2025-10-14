from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableView, QHBoxLayout, QMessageBox
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import QCoreApplication
from app.core.supplier_service import get_suppliers, delete_supplier, get_supplier_by_id, get_db
from .supplier_dialog import SupplierDialog

class SupplierWidget(QWidget):
    """
    Widget for managing suppliers.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton(self.tr("Add Supplier"))
        self.edit_button = QPushButton(self.tr("Edit Supplier"))
        self.delete_button = QPushButton(self.tr("Delete Supplier"))
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

        # Create the table view for displaying suppliers
        self.supplier_table = QTableView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels([self.tr('ID'), self.tr('Name'), self.tr('Email'), self.tr('Phone'), self.tr('Address')])
        self.supplier_table.setModel(self.model)
        self.supplier_table.setColumnHidden(0, True) # Hide the ID column
        layout.addWidget(self.supplier_table)

        self.setLayout(layout)

        # Connect signals to slots
        self.add_button.clicked.connect(self.add_supplier)
        self.edit_button.clicked.connect(self.edit_supplier)
        self.delete_button.clicked.connect(self.delete_supplier)

        self.load_suppliers()

    def load_suppliers(self):
        """
        Load suppliers from the database and display them in the table.
        """
        self.model.removeRows(0, self.model.rowCount())
        db_gen = get_db()
        db = next(db_gen)
        try:
            suppliers = get_suppliers(db)
            for supplier in suppliers:
                row = [
                    QStandardItem(str(supplier.id)),
                    QStandardItem(supplier.name),
                    QStandardItem(supplier.email),
                    QStandardItem(supplier.phone),
                    QStandardItem(supplier.address)
                ]
                self.model.appendRow(row)
        finally:
            next(db_gen, None)

    def add_supplier(self):
        """
        Open a dialog to add a new supplier.
        """
        dialog = SupplierDialog()
        if dialog.exec():
            self.load_suppliers()

    def edit_supplier(self):
        """
        Open a dialog to edit the selected supplier.
        """
        selected_row = self.supplier_table.currentIndex().row()
        if selected_row >= 0:
            supplier_id = int(self.model.item(selected_row, 0).text())
            db_gen = get_db()
            db = next(db_gen)
            try:
                supplier = get_supplier_by_id(db, supplier_id)
                if supplier:
                    dialog = SupplierDialog(supplier=supplier)
                    if dialog.exec():
                        self.load_suppliers()
            finally:
                next(db_gen, None)
        else:
            QMessageBox.warning(self, self.tr("No Supplier Selected"), self.tr("Please select a supplier to edit."))


    def delete_supplier(self):
        """
        Delete the selected supplier.
        """
        selected_row = self.supplier_table.currentIndex().row()
        if selected_row >= 0:
            reply = QMessageBox.question(self, self.tr('Delete Supplier'), self.tr('Are you sure you want to delete this supplier?'),
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                supplier_id = int(self.model.item(selected_row, 0).text())
                db_gen = get_db()
                db = next(db_gen)
                try:
                    delete_supplier(db, supplier_id)
                    self.load_suppliers()
                finally:
                    next(db_gen, None)
        else:
            QMessageBox.warning(self, self.tr("No Supplier Selected"), self.tr("Please select a supplier to delete."))