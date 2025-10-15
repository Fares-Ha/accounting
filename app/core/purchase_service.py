from sqlalchemy.orm import Session
from ..database import models
from . import product_service, accounting_service

def create_purchase_order(db: Session, supplier_id: int, items: list[dict]):
    """
    Creates a new purchase order.
    'items' is a list of dicts, each with 'product_id', 'quantity', 'price_per_unit'.
    """
    total_amount = 0
    order_items = []

    for item in items:
        total_amount += item['price_per_unit'] * item['quantity']
        order_items.append(models.PurchaseOrderItem(
            product_id=item['product_id'],
            quantity=item['quantity'],
            price_per_unit=item['price_per_unit']
        ))

    db_order = models.PurchaseOrder(
        supplier_id=supplier_id,
        total_amount=total_amount,
        items=order_items,
        status="Pending"
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

def get_purchase_order(db: Session, order_id: int):
    """
    Retrieves a single purchase order by its ID.
    """
    return db.query(models.PurchaseOrder).filter(models.PurchaseOrder.id == order_id).first()

def update_purchase_order(db: Session, order_id: int, supplier_id: int, items: list[dict]):
    """
    Updates an existing purchase order.
    """
    order = get_purchase_order(db, order_id)
    if not order:
        raise ValueError("Purchase order not found")

    # Clear old items
    for item in order.items:
        db.delete(item)

    # Process new items
    total_amount = 0
    order_items = []
    for item_data in items:
        price_per_unit = item_data['price_per_unit']
        total_amount += price_per_unit * item_data['quantity']
        order_items.append(models.PurchaseOrderItem(
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            price_per_unit=price_per_unit
        ))

    order.supplier_id = supplier_id
    order.total_amount = total_amount
    order.items = order_items

    # Update ledger
    ledger_entry = db.query(models.LedgerTransaction).filter(
        models.LedgerTransaction.related_order_id == order_id,
        models.LedgerTransaction.transaction_type == models.TransactionType.PURCHASE
    ).first()
    if ledger_entry:
        ledger_entry.amount = total_amount

    db.commit()
    db.refresh(order)
    return order


def delete_purchase_order(db: Session, order_id: int):
    """
    Deletes a purchase order and its related ledger transaction.
    """
    order = get_purchase_order(db, order_id)
    if not order:
        raise ValueError(f"Purchase order with ID {order_id} not found.")

    # Delete the corresponding ledger transaction
    ledger_entry = db.query(models.LedgerTransaction).filter(
        models.LedgerTransaction.related_order_id == order_id,
        models.LedgerTransaction.transaction_type == models.TransactionType.PURCHASE
    ).first()
    if ledger_entry:
        db.delete(ledger_entry)

    db.delete(order)
    db.commit()


def receive_purchase_order(db: Session, order_id: int):
    """
    Marks a purchase order as 'Received' and updates the stock for each product.
    """
    order = get_purchase_order(db, order_id)
    if not order:
        raise ValueError("Purchase order not found")

    if order.status == "Received":
        raise ValueError("Order has already been received")

    for item in order.items:
        product = product_service.get_product(db, item.product_id)
        if product:
            product.stock_quantity += item.quantity

    order.status = "Received"
    db.commit()
    db.refresh(order)
    return order