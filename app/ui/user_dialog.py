from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QMessageBox
from app.database.models import UserRole
from app.core import auth
from app.database.database import get_db

class UserDialog(QDialog):
    def __init__(self, current_user_id, user_id=None, parent=None):
        super().__init__(parent)
        self.current_user_id = current_user_id
        self.user_id = user_id
        self.is_edit_mode = self.user_id is not None

        self.setWindowTitle("Edit User" if self.is_edit_mode else "Add User")
        self.init_ui()
        if self.is_edit_mode:
            self.load_user_data()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        if self.is_edit_mode:
            self.password_input.setPlaceholderText("Leave empty to keep current password")
        self.role_input = QComboBox()
        self.role_input.addItems([role.value for role in UserRole])

        self.form_layout.addRow("Username:", self.username_input)
        self.form_layout.addRow("Password:", self.password_input)
        self.form_layout.addRow("Role:", self.role_input)

        self.submit_button = QPushButton("Save" if self.is_edit_mode else "Create")
        self.submit_button.clicked.connect(self.submit)

        self.layout.addLayout(self.form_layout)
        self.layout.addWidget(self.submit_button)

    def load_user_data(self):
        with get_db() as db:
            user = auth.get_user(db, self.user_id)
            if user:
                self.username_input.setText(user.username)
                self.role_input.setCurrentText(user.role.value)

    def submit(self):
        username = self.username_input.text()
        password = self.password_input.text()
        role = UserRole(self.role_input.currentText())

        if not username or (not self.is_edit_mode and not password):
            QMessageBox.warning(self, "Input Error", "Username and password are required.")
            return

        with get_db() as db:
            try:
                if self.is_edit_mode:
                    auth.update_user(db, self.current_user_id, self.user_id, username, password if password else None, role)
                else:
                    auth.create_user(db, self.current_user_id, username, password, role)
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save user: {e}")