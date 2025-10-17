import sys
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow
from app.i18n import set_language
from app.core.config_service import get_setting

def main():
    """
    Main function to run the application.
    """
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

    def handle_restart():
        QApplication.instance().quit()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def show_main_window(user_id):
        nonlocal main_window
        main_window = MainWindow(user_id)
        main_window.restart_requested.connect(handle_restart)
        main_window.show()
        login_window.close()

    login_window.login_successful.connect(show_main_window)
    login_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()