from sqlalchemy.orm import Session
from ..database import models
from . import product_service, accounting_service, customer_service
from .audit_service import AuditService
from .security import requires_roles, NotAuthorizedError

audit_service = AuditService()

@requires_roles(models.UserRole.ADMIN, models.UserRole.SALES)
def create_sales_order(db: Session, user_id: int, customer_id: int, items: list[dict]) -> models.SalesOrder:
    """
    Creates a new sales order, validates input, and updates product stock.

    - Only ADMIN and SALES users can create sales orders.
    - Validates customer existence and item quantities.
    - Creates an audit log and a corresponding journal entry.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user creating the order.
        customer_id (int): The ID of the customer.
        items (list[dict]): A list of dicts, each with 'product_id' and 'quantity'.

    Returns:
        models.SalesOrder: The newly created sales order object.

    Raises:
        ValueError: If customer is not found, product is out of stock, or quantity is invalid.
    """
    # 1. Validate input
    if not customer_service.get_customer_by_id(db, customer_id):
        raise ValueError(f"Customer with ID {customer_id} not found.")

    if not items:
        raise ValueError("Sales order must contain at least one item.")

    total_amount = 0
    order_items = []

    for item in items:
        # Validate quantity
        quantity = item.get('quantity')
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError(f"Invalid quantity for product ID {item.get('product_id')}: must be a positive integer.")

        product = product_service.get_product(db, item['product_id'])
        if not product or product.stock_quantity < quantity:
            raise ValueError(f"Not enough stock for product ID {item['product_id']}.")

        price_per_unit = product.price
        total_amount += price_per_unit * quantity
        order_items.append(models.SalesOrderItem(
            product_id=item['product_id'],
            quantity=quantity,
            price_per_unit=price_per_unit
        ))

        # 2. Decrease stock
        product.stock_quantity -= quantity

    # 3. Create the order
    db_order = models.SalesOrder(
        customer_id=customer_id,
        total_amount=total_amount,
        items=order_items
    )
    db.add(db_order)
    db.flush()  # Flush to get the order ID for the audit log and journal entry

    # 4. Create Journal Entry
    try:
        accounts_receivable = db.query(models.Account).filter(models.Account.name == "Accounts Receivable").one()
        sales_revenue = db.query(models.Account).filter(models.Account.name == "Sales Revenue").one()

        accounting_service.create_journal_entry(
            db,
            description=f"Sale for order #{db_order.id}",
            transactions=[
                {"account_id": accounts_receivable.id, "amount": total_amount},
                {"account_id": sales_revenue.id, "amount": -total_amount},
            ]
        )
    except Exception as e:
        # If accounting fails, roll back the transaction to ensure data consistency.
        db.rollback()
        raise ConnectionError(f"Failed to create journal entry for sale, rolling back transaction. Reason: {e}")

    # 5. Create Audit Log
    audit_service.create_audit_log(
        db,
        user_id=user_id,
        action="CREATE_SALES_ORDER",
        details=f"Sales order #{db_order.id} created for customer #{customer_id}"
    )

    db.commit()
    db.refresh(db_order)
    return db_order

@requires_roles(models.UserRole.ADMIN, models.UserRole.SALES, models.UserRole.ACCOUNTANT)
def get_sales_orders(db: Session, user_id: int) -> list[models.SalesOrder]:
    """Retrieves all sales orders."""
    return db.query(models.SalesOrder).all()

@requires_roles(models.UserRole.ADMIN, models.UserRole.SALES, models.UserRole.ACCOUNTANT)
def get_sales_order(db: Session, user_id: int, order_id: int) -> models.SalesOrder | None:
    """Retrieves a single sales order by its ID."""
    return db.query(models.SalesOrder).filter(models.SalesOrder.id == order_id).first()

@requires_roles(models.UserRole.ADMIN)
def delete_sales_order(db: Session, user_id: int, order_id: int):
    """
    Deletes a sales order, restores product stock, and logs the action.
    Only ADMIN users can delete sales orders.
    """
    order = db.query(models.SalesOrder).filter(models.SalesOrder.id == order_id).first()
    if not order:
        raise ValueError(f"Sales order with ID {order_id} not found.")

    # Restore stock for each item in the order
    for item in order.items:
        product = product_service.get_product(db, item.product_id)
        if product:
            product.stock_quantity += item.quantity

    audit_service.create_audit_log(
        db,
        user_id=user_id,
        action="DELETE_SALES_ORDER",
        details=f"Sales order #{order.id} was deleted."
    )

    db.delete(order)
    db.commit()
    return {"message": "Sales order deleted successfully."}

@requires_roles(models.UserRole.ADMIN, models.UserRole.SALES)
def update_sales_order(db: Session, user_id: int, order_id: int, customer_id: int, items: list[dict]):
    """
    Updates an existing sales order.
    Only ADMIN and SALES users can update orders.
    """
    order = get_sales_order(db, user_id, order_id)
    if not order:
        raise ValueError("Order not found")

    # Restore old stock quantities
    for item in order.items:
        product = product_service.get_product(db, item.product_id)
        product.stock_quantity += item.quantity

    # Clear old items
    order.items = []

    # Process new items with validation
    total_amount = 0
    order_items = []
    for item_data in items:
        quantity = item_data.get('quantity')
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError(f"Invalid quantity for product ID {item_data.get('product_id')}: must be a positive integer.")

        product = product_service.get_product(db, item_data['product_id'])
        if product.stock_quantity < quantity:
            db.rollback() # Rollback stock changes before raising error
            raise ValueError(f"Not enough stock for {product.name}")

        product.stock_quantity -= quantity
        price_per_unit = product.price
        total_amount += price_per_unit * quantity
        order_items.append(models.SalesOrderItem(
            product_id=item_data['product_id'],
            quantity=quantity,
            price_per_unit=price_per_unit
        ))

    order.customer_id = customer_id
    order.total_amount = total_amount
    order.items = order_items

    audit_service.create_audit_log(
        db,
        user_id=user_id,
        action="UPDATE_SALES_ORDER",
        details=f"Sales order #{order.id} was updated."
    )

    db.commit()
    db.refresh(order)
    return order