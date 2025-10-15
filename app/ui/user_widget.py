from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from app.core import auth
from app.database.database import get_db
from .user_dialog import UserDialog

class UserWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_users()

    def init_ui(self):
        layout = QVBoxLayout(self)
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add User")
        self.add_button.clicked.connect(self.add_user)
        self.edit_button = QPushButton("Edit User")
        self.edit_button.clicked.connect(self.edit_user)
        self.delete_button = QPushButton("Delete User")
        self.delete_button.clicked.connect(self.delete_user)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Role", "Created At"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

    def load_users(self):
        with get_db() as db:
            users = auth.get_users(db)
            self.table.setRowCount(len(users))
            for row, user in enumerate(users):
                self.table.setItem(row, 0, QTableWidgetItem(str(user.id)))
                self.table.setItem(row, 1, QTableWidgetItem(user.username))
                self.table.setItem(row, 2, QTableWidgetItem(user.role.value))
                self.table.setItem(row, 3, QTableWidgetItem(user.created_at.strftime("%Y-%m-%d %H:%M:%S")))

    def add_user(self):
        dialog = UserDialog()
        if dialog.exec():
            self.load_users()

    def edit_user(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a user to edit.")
            return
        user_id = int(self.table.item(selected_rows[0].row(), 0).text())
        dialog = UserDialog(user_id=user_id)
        if dialog.exec():
            self.load_users()

    def delete_user(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Error", "Please select a user to delete.")
            return
        user_id = int(self.table.item(selected_rows[0].row(), 0).text())
        reply = QMessageBox.question(self, "Delete User", "Are you sure you want to delete this user?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            with get_db() as db:
                auth.delete_user(db, user_id)
            self.load_users()