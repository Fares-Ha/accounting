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