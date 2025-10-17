import sys
from PyQt6.QtCore import Qt
from PyQt.QtWidgets import QApplication
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

def main():
    """
    Main function to run the application.
    """
    app = Application(sys.argv)

    # Load language from config, default to 'en'
    lang = get_setting('language', 'en')
    set_language(lang)
    if lang == 'ar':
        app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    else:
        app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    login_window = LoginWindow()
    login_window.login_successful.connect(app.show_main_window)
    login_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()