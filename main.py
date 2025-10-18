import sys
import subprocess
from PyQt6.QtWidgets import QApplication
from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow
from app.i18n import set_language
from app.database.database import SessionLocal
from app.core.auth import get_user

def main():
    """
    Main function to run the application.
    """
    app = QApplication(sys.argv)

    # Set default language to English on startup.
    # The language will be switched to the user's preference after login.
    set_language('en')

    main_window = None
    login_window = LoginWindow()

    def handle_restart():
        """Gracefully restarts the application."""
        # Ensure the current instance will close before the new one starts.
        QApplication.instance().quit()
        # Launch a new instance of the application.
        subprocess.Popen([sys.executable] + sys.argv)

    def show_main_window(user_id):
        """
        Initializes and shows the main window after a successful login.
        Sets the application language based on the user's preference.
        """
        nonlocal main_window

        # Get user's language from the database
        db = SessionLocal()
        user = get_user(db, user_id)
        lang = user.language if user and user.language else 'en'
        db.close()

        # Set the application language
        set_language(lang)

        main_window = MainWindow(user_id)
        main_window.restart_requested.connect(handle_restart)
        main_window.show()
        login_window.close()

    login_window.login_successful.connect(show_main_window)
    login_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()