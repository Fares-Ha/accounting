from PyQt6.QtCore import pyqtSignal, QCoreApplication
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from app.core.auth import authenticate_user
from app.database.database import SessionLocal
from .main_window import MainWindow

class LoginWindow(QWidget):
    """
    Login window for user authentication.
    """
    login_successful = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("Login"))

        layout = QVBoxLayout()

        self.username_label = QLabel(self.tr("Username:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.password_label = QLabel(self.tr("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton(self.tr("Login"))
        self.login_button.clicked.connect(self.handle_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        db = SessionLocal()
        user = authenticate_user(db, username, password)
        db.close()

        if user:
            self.login_successful.emit(user)
            self.close()
        else:
            QMessageBox.warning(self, self.tr("Login Failed"), self.tr("Invalid username or password."))