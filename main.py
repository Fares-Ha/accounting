import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton
from app.database.database import init_db
from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow
from app.i18n import set_language, install_translator

class LanguageSelectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Language")
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Please select your language:")
        self.combo = QComboBox()
        self.combo.addItems(["English", "Arabic"])
        self.button = QPushButton("OK")
        self.button.clicked.connect(self.accept)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combo)
        self.layout.addWidget(self.button)

    def get_language(self):
        return "ar" if self.combo.currentText() == "Arabic" else "en"

class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.main_window = None

    def show_main_window(self, user_id):
        self.main_window = MainWindow(user_id)
        self.main_window.show()

def main():
    """
    Main function to run the application.
    """
    init_db()  # Ensure the database is initialized
    app = Application(sys.argv)

    lang_dialog = LanguageSelectionDialog()
    if lang_dialog.exec() == QDialog.DialogCode.Accepted:
        lang = lang_dialog.get_language()
        set_language(lang)
        install_translator(lang)
        if lang == 'ar':
            app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    else:
        sys.exit(0) # Exit if the user cancels

    login_window = LoginWindow()
    login_window.login_successful.connect(app.show_main_window)
    login_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()