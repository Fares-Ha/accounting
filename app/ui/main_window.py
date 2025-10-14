from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    """
    The main application window, which appears after successful login.
    """
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Al Ameen - Logged in as {self.user.username} ({self.user.role.value})")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        welcome_label = QLabel(f"Welcome, {self.user.username}!")
        layout.addWidget(welcome_label)