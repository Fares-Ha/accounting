from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QSpinBox, QComboBox, QDialogButtonBox, QMessageBox
from ..core import product_service
from ..database import models
from ..database.database import get_db

class StockAdjustmentDialog(QDialog):
    def __init__(self, product_id, product_name, current_user):
        super().__init__()
        self.product_id = product_id
        self.current_user = current_user
        self.product_service = product_service
        self.setWindowTitle(f"Adjust Stock for {product_name}")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.adjustment_spinbox = QSpinBox()
        self.adjustment_spinbox.setRange(-9999, 9999)
        form_layout.addRow("Adjustment Quantity:", self.adjustment_spinbox)

        self.reason_combo = QComboBox()
        self.reason_combo.addItems([reason.value for reason in models.InventoryMovementReason])
        form_layout.addRow("Reason:", self.reason_combo)

        layout.addLayout(form_layout)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def accept(self):
        quantity_change = self.adjustment_spinbox.value()
        reason_str = self.reason_combo.currentText()
        reason = models.InventoryMovementReason(reason_str)

        if quantity_change == 0:
            QMessageBox.warning(self, "Input Error", "Adjustment quantity cannot be zero.")
            return

        with get_db() as db:
            self.product_service.adjust_stock(db, self.current_user.id, self.product_id, quantity_change, reason)
        super().accept()