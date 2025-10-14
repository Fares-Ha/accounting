import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTranslator, QLocale
from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow

class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.translator = QTranslator()
        # Default to English
        if self.translator.load(QLocale.Language.English, "app", "_", "app/locale"):
            self.installTranslator(self.translator)

        self.login_window = LoginWindow()
        self.main_window = None
        self.login_window.login_successful.connect(self.show_main_window)
        self.login_window.show()

    def show_main_window(self, user):
        self.main_window = MainWindow(user)
        self.main_window.show()

def main():
    """Main function to initialize and run the application."""
    app = Application(sys.argv)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()