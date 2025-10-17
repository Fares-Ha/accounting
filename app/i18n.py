import gettext
from PyQt6.QtCore import QLocale, QTranslator, QCoreApplication, Qt
from PyQt6.QtWidgets import QApplication

def install_translator(lang: str):
    """
    Loads and installs a QTranslator for the given language.

    Args:
        lang (str): The language code (e.g., 'en', 'ar').
    """
    translator = QTranslator(QApplication.instance())
    # The path should be relative to the running script or resource system
    if translator.load(f"app/locale/{lang}.qm"):
        QApplication.installTranslator(translator)
    else:
        print(f"Warning: Could not load translation file for language '{lang}'.")


def set_language(lang: str):
    """
    Sets the application's language and layout direction.

    This function configures the application's locale and installs the
    appropriate translator. For Right-to-Left (RTL) languages like Arabic,
    it also sets the global layout direction.

    Args:
        lang (str): The language code to switch to (e.g., 'en', 'ar').
    """
    app = QApplication.instance()
    if not app:
        # This case is unlikely in a running PyQt app but is good practice
        print("Error: QApplication instance not found.")
        return

    # Set locale and layout direction
    if lang == 'ar':
        QLocale.setDefault(QLocale(QLocale.Language.Arabic, QLocale.Country.Egypt))
        app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    else:
        # Default to English and Left-to-Right layout
        QLocale.setDefault(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))
        app.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

    # Load and install the translation file
    install_translator(lang)

    # It's often necessary to re-translate the UI after a language change.
    # This can be handled by emitting a signal that all windows listen to
    # in order to call `retranslateUi()`.