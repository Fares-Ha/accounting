from sqlalchemy.orm import Session
from ..database import models
from . import product_service, accounting_service

def create_sales_order(db: Session, customer_id: int, items: list[dict]):
    """
    Creates a new sales order and updates product stock.
    'items' is a list of dicts, each with 'product_id', 'quantity'.
    """
    total_amount = 0
    order_items = []

    for item in items:
        product = product_service.get_product(db, item['product_id'])
        if not product or product.stock_quantity < item['quantity']:
            raise ValueError(f"Not enough stock for product ID {item['product_id']}")

        price_per_unit = product.price
        total_amount += price_per_unit * item['quantity']
        order_items.append(models.SalesOrderItem(
            product_id=item['product_id'],
            quantity=item['quantity'],
            price_per_unit=price_per_unit
        ))

        # Decrease stock
        product.stock_quantity -= item['quantity']

    db_order = models.SalesOrder(
        customer_id=customer_id,
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
        transaction_type=models.TransactionType.SALE,
        related_order_id=db_order.id
    )

    return db_order

def get_sales_orders(db: Session):
    """
    Retrieves all sales orders.
    """
    return db.query(models.SalesOrder).all()

def get_sales_order(db: Session, order_id: int):
    """
    Retrieves a single sales order by its ID.
    """
    return db.query(models.SalesOrder).filter(models.SalesOrder.id == order_id).first()

def delete_sales_order(db: Session, order_id: int):
    """
    Deletes a sales order, restores product stock, and removes the related ledger transaction.
    """
    order = db.query(models.SalesOrder).filter(models.SalesOrder.id == order_id).first()
    if not order:
        raise ValueError(f"Sales order with ID {order_id} not found.")

    # Restore stock for each item in the order
    for item in order.items:
        product = product_service.get_product(db, item.product_id)
        if product:
            product.stock_quantity += item.quantity

    # Delete the corresponding ledger transaction
    ledger_entry = db.query(models.Ledger).filter(models.Ledger.related_order_id == order_id).first()
    if ledger_entry:
        db.delete(ledger_entry)

    db.delete(order)
    db.commit()

def update_sales_order(db: Session, order_id: int, customer_id: int, items: list[dict]):
    """
    Updates an existing sales order.
    This involves restoring stock from the old order and deducting from the new.
    """
    order = get_sales_order(db, order_id)
    if not order:
        raise ValueError("Order not found")

    # Restore old stock quantities
    for item in order.items:
        product = product_service.get_product(db, item.product_id)
        product.stock_quantity += item.quantity

    # Clear old items
    order.items = []

    # Process new items
    total_amount = 0
    order_items = []
    for item_data in items:
        product = product_service.get_product(db, item_data['product_id'])
        if product.stock_quantity < item_data['quantity']:
            # Rollback stock changes before raising error
            db.rollback()
            raise ValueError(f"Not enough stock for {product.name}")

        product.stock_quantity -= item_data['quantity']
        price_per_unit = product.price
        total_amount += price_per_unit * item_data['quantity']
        order_items.append(models.SalesOrderItem(
            product_id=item_data['product_id'],
            quantity=item_data['quantity'],
            price_per_unit=price_per_unit
        ))

    order.customer_id = customer_id
    order.total_amount = total_amount
    order.items = order_items

    # Update ledger
    ledger_entry = db.query(models.Ledger).filter(models.Ledger.related_order_id == order_id).first()
    if ledger_entry:
        ledger_entry.amount = total_amount

    db.commit()
    db.refresh(order)
    return order