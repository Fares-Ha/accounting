import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.database.models import User, UserRole, Customer, Product, SalesOrder, SalesOrderItem, Invoice, PurchaseOrder, PurchaseOrderItem, Supplier, Account, AccountType, PaymentMethod
from app.core.payment_service import PaymentService
from app.core import accounting_service
from datetime import datetime

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create base accounts
    session.add(Account(name="Cash", account_type=AccountType.ASSET, balance=1000000))
    session.add(Account(name="Accounts Receivable", account_type=AccountType.ASSET))
    session.add(Account(name="Accounts Payable", account_type=AccountType.LIABILITY))
    session.commit()

    yield session
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def setup_data(db_session):
    # Create a user
    user = User(username="testuser", hashed_password="password", role=UserRole.ADMIN)
    db_session.add(user)
    db_session.commit()

    # Create a customer
    customer = Customer(name="Test Customer")
    db_session.add(customer)
    db_session.commit()

    # Create a supplier
    supplier = Supplier(name="Test Supplier")
    db_session.add(supplier)
    db_session.commit()

    # Create a product
    product = Product(name="Test Product", price=1000, stock_quantity=100) # price in cents
    db_session.add(product)
    db_session.commit()

    # Create a sales order and invoice
    sales_order = SalesOrder(customer_id=customer.id, total_amount=2000)
    sales_order.items.append(SalesOrderItem(product_id=product.id, quantity=2, price_per_unit=1000))
    invoice = Invoice(sales_order_id=sales_order.id, customer_id=customer.id, total_amount=2000, due_date=datetime.utcnow())
    sales_order.invoice = invoice
    db_session.add(sales_order)
    db_session.commit()

    # Create a purchase order
    purchase_order = PurchaseOrder(supplier_id=supplier.id, total_amount=5000, status="Pending")
    purchase_order.items.append(PurchaseOrderItem(product_id=product.id, quantity=5, price_per_unit=1000))
    db_session.add(purchase_order)
    db_session.commit()

    return user, invoice, purchase_order

def test_record_invoice_payment_success(db_session, setup_data):
    user, invoice, _ = setup_data
    payment_service = PaymentService(db_session, user.id)

    payment = payment_service.record_invoice_payment(
        invoice_id=invoice.id,
        amount=2000,
        payment_date=datetime.utcnow(),
        payment_method=PaymentMethod.CASH,
        payment_account_name="Cash"
    )

    db_session.refresh(invoice)
    assert payment.amount == 2000
    assert payment.invoice_id == invoice.id
    assert invoice.status.value == "paid"
    # Further assertions can be made on journal entries and account balances

def test_record_invoice_payment_partial(db_session, setup_data):
    user, invoice, _ = setup_data
    payment_service = PaymentService(db_session, user.id)

    payment_service.record_invoice_payment(
        invoice_id=invoice.id,
        amount=1000,
        payment_date=datetime.utcnow(),
        payment_method=PaymentMethod.CASH,
        payment_account_name="Cash"
    )

    db_session.refresh(invoice)
    total_paid = sum(p.amount for p in invoice.payments)
    assert total_paid == 1000
    assert invoice.status.value != "paid"

def test_record_invoice_payment_exceeds_amount(db_session, setup_data):
    user, invoice, _ = setup_data
    payment_service = PaymentService(db_session, user.id)

    with pytest.raises(ValueError, match="exceed the outstanding invoice amount"):
        payment_service.record_invoice_payment(
            invoice_id=invoice.id,
            amount=3000,
            payment_date=datetime.utcnow(),
            payment_method=PaymentMethod.CASH,
            payment_account_name="Cash"
        )

def test_record_purchase_payment_success(db_session, setup_data):
    user, _, purchase_order = setup_data
    payment_service = PaymentService(db_session, user.id)

    payment = payment_service.record_purchase_payment(
        purchase_order_id=purchase_order.id,
        amount=5000,
        payment_date=datetime.utcnow(),
        payment_method=PaymentMethod.BANK_TRANSFER,
        payment_account_name="Cash"
    )

    db_session.refresh(purchase_order)
    assert payment.amount == 5000
    assert payment.purchase_order_id == purchase_order.id
    assert purchase_order.status == "Paid"

def test_record_purchase_payment_exceeds_amount(db_session, setup_data):
    user, _, purchase_order = setup_data
    payment_service = PaymentService(db_session, user.id)

    with pytest.raises(ValueError, match="exceed the outstanding purchase order amount"):
        payment_service.record_purchase_payment(
            purchase_order_id=purchase_order.id,
            amount=6000,
            payment_date=datetime.utcnow(),
            payment_method=PaymentMethod.CASH,
            payment_account_name="Cash"
        )