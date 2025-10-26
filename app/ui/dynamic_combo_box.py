from PyQt6.QtWidgets import QComboBox, QMessageBox, QLineEdit
from PyQt6.QtCore import pyqtSignal, Qt

class DynamicComboBox(QComboBox):
    new_item_added = pyqtSignal(object)

    def __init__(self, item_loader, item_dialog_class, display_func=None, user=None, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.item_loader = item_loader
        self.item_dialog_class = item_dialog_class
        self.display_func = display_func or (lambda item: item.name)
        self.user = user
        self.load_items()

        self.lineEdit().editingFinished.connect(self.handle_editing_finished)

    def load_items(self):
        self.clear()
        items = self.item_loader()
        for item in items:
            self.addItem(self.display_func(item), userData=item)

    def handle_editing_finished(self):
        text = self.lineEdit().text()
        if not text:
            return

        # Check if item exists (case-insensitive)
        if self.findText(text, flags=Qt.MatchFlag.MatchFixedString | Qt.MatchFlag.MatchCaseSensitive) == -1:
            reply = QMessageBox.question(
                self,
                'Item not found',
                f"'{text}' does not exist. Would you like to add it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                dialog = self.item_dialog_class(user=self.user)
                # Pre-fill the name if the dialog supports it
                if hasattr(dialog, 'name_input'):
                    dialog.name_input.setText(text)

                if dialog.exec() and hasattr(dialog, 'get_new_item_name'):
                    self.load_items()
                    new_item_name = dialog.get_new_item_name()
                    if new_item_name:
                        new_index = self.findText(new_item_name)
                        if new_index != -1:
                            self.setCurrentIndex(new_index)
                            self.new_item_added.emit(self.currentData())
