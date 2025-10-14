from sqlalchemy.orm import Session
from ..database import models
from . import product_service, accounting_service

def create_purchase_order(db: Session, supplier_id: int, items: list[dict]):
    """
    Creates a new purchase order and updates product stock.
    'items' is a list of dicts, each with 'product_id', 'quantity', and 'price_per_unit'.
    """
    total_amount = 0
    order_items = []

    for item in items:
        product = product_service.get_product(db, item['product_id'])
        if not product:
            # Or create a new product if it doesn't exist
            raise ValueError(f"Product with ID {item['product_id']} not found.")

        price_per_unit = item['price_per_unit']
        total_amount += price_per_unit * item['quantity']
        order_items.append(models.PurchaseOrderItem(
            product_id=item['product_id'],
            quantity=item['quantity'],
            price_per_unit=price_per_unit
        ))

        # Increase stock
        product.stock_quantity += item['quantity']

    db_order = models.PurchaseOrder(
        supplier_id=supplier_id,
        total_amount=total_amount,
        items=order_items
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Create a corresponding ledger transaction
    accounting_service.create_ledger_transaction(
        db,
        amount=total_amount,
        transaction_type=models.TransactionType.PURCHASE,
        related_order_id=db_order.id
    )

    return db_order

def get_purchase_orders(db: Session):
    """
    Retrieves all purchase orders.
    """
    return db.query(models.PurchaseOrder).all()