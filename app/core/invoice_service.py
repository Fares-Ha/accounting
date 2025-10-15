from sqlalchemy.orm import Session
from ..database import models
from . import accounting_service, sales_service
from datetime import datetime

def create_invoice_from_sales_order(db: Session, sales_order_id: int):
    """
    Creates an invoice for a given sales order.
    """
    sales_order = sales_service.get_sales_order(db, sales_order_id)
    if not sales_order:
        raise ValueError("Sales order not found")
    if sales_order.invoice:
        raise ValueError("Invoice already exists for this sales order")

    invoice_items = [
        models.InvoiceItem(
            product_id=item.product_id,
            quantity=item.quantity,
            price_per_unit=item.price_per_unit
        ) for item in sales_order.items
    ]

    invoice = models.Invoice(
        sales_order_id=sales_order.id,
        customer_id=sales_order.customer_id,
        total_amount=sales_order.total_amount,
        status=models.InvoiceStatus.DRAFT,
        due_date=datetime.now(),  # Placeholder, this could be configurable
        items=invoice_items
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    return invoice

def get_invoices(db: Session):
    """
    Retrieves all invoices.
    """
    return db.query(models.Invoice).all()

def get_invoice(db: Session, invoice_id: int):
    """
    Retrieves a single invoice by its ID.
    """
    return db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()

def update_invoice_status(db: Session, invoice_id: int, status: models.InvoiceStatus):
    """
    Updates the status of an invoice.
    """
    invoice = get_invoice(db, invoice_id)
    if not invoice:
        raise ValueError("Invoice not found")

    invoice.status = status
    db.commit()
    db.refresh(invoice)

    if status == models.InvoiceStatus.PAID:
        # Create journal entry for payment
        # This assumes payment is received and an entry is needed to balance the books
        # The exact accounts would depend on the chart of accounts
        # For example, debiting 'Cash' and crediting 'Accounts Receivable'
        # This part needs to be implemented in more detail in the accounting service
        pass

    return invoice