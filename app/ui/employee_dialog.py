from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox, QDateEdit, QSpinBox
from PyQt6.QtCore import QDate
from app.core import hr_service
from app.database.database import get_db
from datetime import datetime

class EmployeeDialog(QDialog):
    def __init__(self, user_id, employee_id=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.employee_id = employee_id
        self.is_edit_mode = self.employee_id is not None

        self.setWindowTitle("Edit Employee" if self.is_edit_mode else "Add Employee")
        self.init_ui()
        if self.is_edit_mode:
            self.load_employee_data()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.job_title_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.hire_date_input = QDateEdit(QDate.currentDate())
        self.hire_date_input.setCalendarPopup(True)
        self.salary_input = QSpinBox()
        self.salary_input.setRange(0, 100000000)
        self.salary_input.setSuffix(" cents")

        self.form_layout.addRow("Name:", self.name_input)
        self.form_layout.addRow("Job Title:", self.job_title_input)
        self.form_layout.addRow("Email:", self.email_input)
        self.form_layout.addRow("Phone:", self.phone_input)
        self.form_layout.addRow("Hire Date:", self.hire_date_input)
        self.form_layout.addRow("Salary:", self.salary_input)

        self.submit_button = QPushButton("Save" if self.is_edit_mode else "Create")
        self.submit_button.clicked.connect(self.submit)

        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.submit_button)

    def load_employee_data(self):
        with get_db() as db:
            employee = hr_service.get_employee(db, self.user_id, self.employee_id)
            if employee:
                self.name_input.setText(employee.name)
                self.job_title_input.setText(employee.job_title)
                self.email_input.setText(employee.email)
                self.phone_input.setText(employee.phone)
                self.hire_date_input.setDate(employee.hire_date)
                self.salary_input.setValue(employee.salary)

    def submit(self):
        name = self.name_input.text()
        job_title = self.job_title_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        hire_date = self.hire_date_input.dateTime().toPyDateTime()
        salary = self.salary_input.value()

        if not all([name, job_title, email, hire_date, salary]):
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        with get_db() as db:
            try:
                if self.is_edit_mode:
                    hr_service.update_employee(db, self.user_id, self.employee_id, name, job_title, email, phone, hire_date, salary)
                else:
                    hr_service.create_employee(db, self.user_id, name, job_title, email, phone, hire_date, salary)
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save employee: {e}")