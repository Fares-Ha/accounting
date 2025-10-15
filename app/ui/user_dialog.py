from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QMessageBox
from app.core import auth
from app.database.database import get_db
from app.database.models import UserRole

class UserDialog(QDialog):
    def __init__(self, user_id=None):
        super().__init__()
        self.user_id = user_id
        self.setWindowTitle(f"{'Edit' if user_id else 'Add'} User")
        self.init_ui()
        if self.user_id:
            self.load_user_data()

    def init_ui(self):
        layout = QFormLayout(self)
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.role_combo = QComboBox()
        self.role_combo.addItems([role.value for role in UserRole])
        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)
        layout.addRow("Role:", self.role_combo)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def load_user_data(self):
        with get_db() as db:
            user = auth.get_user(db, self.user_id)
            if user:
                self.username_input.setText(user.username)
                self.role_combo.setCurrentText(user.role.value)

    def accept(self):
        username = self.username_input.text()
        password = self.password_input.text()
        role = UserRole(self.role_combo.currentText())

        if not username or (not self.user_id and not password):
            QMessageBox.warning(self, "Input Error", "Username and password are required for new users.")
            return

        with get_db() as db:
            if self.user_id:
                auth.update_user(db, self.user_id, username, password if password else None, role)
            else:
                auth.create_user(db, username, password, role)
        super().accept()