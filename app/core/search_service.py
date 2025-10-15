from sqlalchemy import or_
from ..database.models import Customer, Product, SalesOrder, PurchaseOrder
from ..database.session import get_db

def global_search(db_session, term):
    """
    Performs a global search across customers, products, sales orders, and purchase orders.

    Args:
        db_session: The database session.
        term: The search term.

    Returns:
        A dictionary with search results categorized by type.
    """
    if not term:
        return {}

    # Search for customers by name or email
    customers = db_session.query(Customer).filter(
        or_(
            Customer.name.ilike(f"%{term}%"),
            Customer.email.ilike(f"%{term}%")
        )
    ).all()

    # Search for products by name
    products = db_session.query(Product).filter(
        Product.name.ilike(f"%{term}%")
    ).all()

    # Search for sales orders by ID
    sales_orders = []
    if term.isdigit():
        sales_orders = db_session.query(SalesOrder).filter(
            SalesOrder.id == int(term)
        ).all()

    # Search for purchase orders by ID
    purchase_orders = []
    if term.isdigit():
        purchase_orders = db_session.query(PurchaseOrder).filter(
            PurchaseOrder.id == int(term)
        ).all()

    return {
        "customers": customers,
        "products": products,
        "sales_orders": sales_orders,
        "purchase_orders": purchase_orders
    }