import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from PyQt6.QtWidgets import QFileDialog
from datetime import datetime
from ..database import models
import os

def generate_sales_receipt_pdf(order: models.SalesOrder):
    """
    Generates a PDF receipt for a given sales order.
    """
    # Create a 'receipts' directory if it doesn't exist
    if not os.path.exists('receipts'):
        os.makedirs('receipts')

    filepath = f"receipts/receipt_order_{order.id}.pdf"
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("Sales Receipt", styles['Title']))
    story.append(Spacer(1, 12))

    # Order Info
    story.append(Paragraph(f"<b>Order ID:</b> {order.id}", styles['Normal']))
    story.append(Paragraph(f"<b>Customer:</b> {order.customer.name}", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Items Table
    data = [["Product", "Quantity", "Unit Price", "Total"]]
    for item in order.items:
        total_price = item.quantity * item.price_per_unit
        data.append([
            item.product.name,
            str(item.quantity),
            f"{item.price_per_unit:.2f}",
            f"{total_price:.2f}"
        ])

    # Add total row
    data.append(["", "", "<b>Total Amount</b>", f"<b>{order.total_amount:.2f}</b>"])

    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ])
    table.setStyle(style)
    story.append(table)

    doc.build(story)
    return os.path.abspath(filepath)


class ExportService:
    """
    Service for exporting data to different formats.
    """
    def export_sales_report_to_pdf(self, sales_data, file_path):
        headers = ["Product", "Total Quantity", "Total Revenue"]
        data = [[item.name, str(item.total_quantity), f"{item.total_revenue / 100:.2f}"] for item in sales_data]
        self.export_to_pdf(data, headers, file_path)

    def export_sales_report_to_excel(self, sales_data, file_path):
        headers = ["Product", "Total Quantity", "Total Revenue"]
        data = [[item.name, item.total_quantity, item.total_revenue / 100] for item in sales_data]
        self.export_to_excel(data, headers, file_path)

    def export_to_excel(self, data, headers, file_path):
        """
        Exports data to an Excel file.
        """
        if not data:
            return

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(headers)

        for row_data in data:
            sheet.append(row_data)

        workbook.save(file_path)

    def export_to_pdf(self, data, headers, file_path):
        """
        Exports data to a PDF file.
        """
        if not data:
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