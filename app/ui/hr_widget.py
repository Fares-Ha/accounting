from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from app.core import hr_service
from app.database.database import get_db
from .employee_dialog import EmployeeDialog

class HRWidget(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.init_ui()
        self.load_employees()

    def init_ui(self):
        layout = QVBoxLayout(self)
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Employee")
        self.add_button.clicked.connect(self.add_employee)
        self.edit_button = QPushButton("Edit Employee")
        self.edit_button.clicked.connect(self.edit_employee)
        self.delete_button = QPushButton("Delete Employee")
        self.delete_button.clicked.connect(self.delete_employee)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Job Title", "Email", "Phone", "Hire Date", "Salary"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

    def load_employees(self):
        with get_db() as db:
            employees = hr_service.get_employees(db, self.user_id)
            self.table.setRowCount(len(employees))
            for row, employee in enumerate(employees):
                self.table.setItem(row, 0, QTableWidgetItem(str(employee.id)))
                self.table.setItem(row, 1, QTableWidgetItem(employee.name))
                self.table.setItem(row, 2, QTableWidgetItem(employee.job_title))
                self.table.setItem(row, 3, QTableWidgetItem(employee.email))
                self.table.setItem(row, 4, QTableWidgetItem(employee.phone))
                self.table.setItem(row, 5, QTableWidgetItem(employee.hire_date.strftime("%Y-%m-%d")))
                self.table.setItem(row, 6, QTableWidgetItem(f"{employee.salary / 100:.2f}"))

    def add_employee(self):
        dialog = EmployeeDialog(self.user_id)
        if dialog.exec():
            self.load_employees()

    def edit_employee(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an employee to edit.")
            return
        employee_id = int(self.table.item(selected_rows[0].row(), 0).text())
        dialog = EmployeeDialog(self.user_id, employee_id=employee_id)
        if dialog.exec():
            self.load_employees()

    def delete_employee(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select an employee to delete.")
            return
        employee_id = int(self.table.item(selected_rows[0].row(), 0).text())

        reply = QMessageBox.question(self, "Delete Employee", "Are you sure you want to delete this employee?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            with get_db() as db:
                hr_service.delete_employee(db, self.user_id, employee_id)
            self.load_employees()