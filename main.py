import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtWidgets import QApplication
from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow
from app.i18n import set_language
from app.core.config_service import get_setting

class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.main_window = None

    def show_main_window(self, user_id):
        self.main_window = MainWindow(user_id)
        self.main_window.show()

RESTART_CODE = 1000

def main():
    """
    Main function to run the application.
    """
    exit_code = 0
    while True:
        app = QApplication(sys.argv)

        # Load language from config, default to 'en'
        lang = get_setting('language', 'en')
        set_language(lang)
        if lang == 'ar':
            app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        else:
            app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        main_window = None
        login_window = LoginWindow()

        def show_main_window(user_id):
            nonlocal main_window
            main_window = MainWindow(user_id)
            main_window.restart_requested.connect(lambda: app.exit(RESTART_CODE))
            main_window.show()
            login_window.close()

        login_window.login_successful.connect(show_main_window)
        login_window.show()

        exit_code = app.exec()

        if exit_code != RESTART_CODE:
            break

if __name__ == "__main__":
    main()