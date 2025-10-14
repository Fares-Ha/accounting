import gettext
from PyQt6.QtCore import QLocale, QTranslator, QCoreApplication

def install_translator(lang: str):
    """
    Install a translator for the given language.
    """
    translator = QTranslator(QCoreApplication.instance())
    if translator.load(f"app/locale/{lang}.qm"):
        QCoreApplication.installTranslator(translator)

def set_language(lang: str):
    """
    Set the application language.
    """
    if lang == 'ar':
        QLocale.setDefault(QLocale(QLocale.Language.Arabic))
    else:
        QLocale.setDefault(QLocale(QLocale.Language.English))
    install_translator(lang)