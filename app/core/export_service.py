import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from PyQt6.QtWidgets import QFileDialog
from datetime import datetime

class ExportService:
    """
    Service for exporting data to different formats.
    """

    def export_to_excel(self, data, headers, parent_widget):
        """
        Exports data to an Excel file.
        """
        if not data:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            parent_widget,
            "Save Excel File",
            f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )

        if not file_path:
            return

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(headers)

        for row_data in data:
            sheet.append(row_data)

        workbook.save(file_path)

    def export_to_pdf(self, data, headers, parent_widget):
        """
        Exports data to a PDF file.
        """
        if not data:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            parent_widget,
            "Save PDF File",
            f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        doc = SimpleDocTemplate(file_path, pagesize=letter)
        table_data = [headers] + data

        table = Table(table_data)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        table.setStyle(style)

        doc.build([table])