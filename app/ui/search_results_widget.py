from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt, pyqtSignal

class SearchResultsWidget(QWidget):
    """
    A widget to display global search results in a table.
    """
    # Signal emitted when a result item is selected (double-clicked)
    # The signal will carry the model type (e.g., "customer") and the model ID
    result_selected = pyqtSignal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Search Results"))
        layout = QVBoxLayout(self)

        # Create the table widget for displaying results
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels([self.tr("Category"), self.tr("ID"), self.tr("Name"), self.tr("Details")])
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.results_table)

        # Connect the double-click signal to the handler
        self.results_table.itemDoubleClicked.connect(self.on_item_double_clicked)

    def display_results(self, results):
        """
        Populates the table with search results.
        """
        self.results_table.setRowCount(0)

        if not results:
            return

        row = 0
        for category, items in results.items():
            for item in items:
                self.results_table.insertRow(row)

                # Store the model type and ID in the first item of the row for later retrieval
                category_item = QTableWidgetItem(self.tr(category.replace("_", " ").title()))
                category_item.setData(Qt.ItemDataRole.UserRole, (category, item.id))

                if category == "customers":
                    self.results_table.setItem(row, 0, category_item)
                    self.results_table.setItem(row, 1, QTableWidgetItem(str(item.id)))
                    self.results_table.setItem(row, 2, QTableWidgetItem(item.name))
                    self.results_table.setItem(row, 3, QTableWidgetItem(item.email))
                elif category == "products":
                    self.results_table.setItem(row, 0, category_item)
                    self.results_table.setItem(row, 1, QTableWidgetItem(str(item.id)))
                    self.results_table.setItem(row, 2, QTableWidgetItem(item.name))
                    self.results_table.setItem(row, 3, QTableWidgetItem(f"Stock: {item.stock_level}"))
                elif category in ["sales_orders", "purchase_orders"]:
                    self.results_table.setItem(row, 0, category_item)
                    self.results_table.setItem(row, 1, QTableWidgetItem(str(item.id)))
                    self.results_table.setItem(row, 2, QTableWidgetItem(f"Order #{item.id}"))
                    self.results_table.setItem(row, 3, QTableWidgetItem(f"Total: {item.total_amount}"))

                row += 1

    def on_item_double_clicked(self, item):
        """
        Handles the double-click event on a table item and emits the result_selected signal.
        """
        # Retrieve the stored data (model_type, model_id) from the first column item
        first_item = self.results_table.item(item.row(), 0)
        data = first_item.data(Qt.ItemDataRole.UserRole)
        if data:
            model_type, model_id = data
            self.result_selected.emit(model_type, model_id)