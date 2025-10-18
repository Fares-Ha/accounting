import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.database.models import User, UserRole, Warehouse, Product, Customer, Supplier
from app.core import warehouse_service, product_service, sales_service, purchase_service

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    # Add a default user for audit purposes
    user = User(username="testuser", hashed_password="password", role=UserRole.ADMIN)
    session.add(user)
    session.commit()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def setup_data(db_session):
    user = db_session.query(User).first()
    warehouse1 = warehouse_service.create_warehouse(db_session, user.id, "Main Warehouse", "123 Main St")
    warehouse2 = warehouse_service.create_warehouse(db_session, user.id, "Secondary Warehouse", "456 Side St")
    product = product_service.create_product(db_session, "Test Product", "A product for testing", 1000)
    customer = Customer(name="Test Customer")
    supplier = Supplier(name="Test Supplier")
    db_session.add(customer)
    db_session.add(supplier)
    db_session.commit()
    return user, warehouse1, warehouse2, product, customer, supplier

def test_create_and_get_warehouse(db_session, setup_data):
    user, warehouse1, _, _, _, _ = setup_data
    retrieved_warehouse = warehouse_service.get_warehouse(db_session, warehouse1.id)
    assert retrieved_warehouse.name == "Main Warehouse"

def test_adjust_and_get_stock_level(db_session, setup_data):
    user, warehouse1, _, product, _, _ = setup_data
    product_service.adjust_stock_level(db_session, product.id, warehouse1.id, 10, "initial_stock", user.id)
    stock_level = product_service.get_stock_level(db_session, product.id, warehouse1.id)
    assert stock_level == 10
    total_stock = product_service.get_total_stock(db_session, product.id)
    assert total_stock == 10

def test_sales_order_deducts_stock(db_session, setup_data):
    user, warehouse1, _, product, customer, _ = setup_data
    product_service.adjust_stock_level(db_session, product.id, warehouse1.id, 20, "initial_stock", user.id)

    sales_service.create_sales_order(db_session, user.id, customer.id, warehouse1.id, [{"product_id": product.id, "quantity": 5}])

    stock_level = product_service.get_stock_level(db_session, product.id, warehouse1.id)
    assert stock_level == 15

def test_sales_order_insufficient_stock(db_session, setup_data):
    user, warehouse1, _, product, customer, _ = setup_data
    product_service.adjust_stock_level(db_session, product.id, warehouse1.id, 2, "initial_stock", user.id)

    with pytest.raises(ValueError, match="Not enough stock"):
        sales_service.create_sales_order(db_session, user.id, customer.id, warehouse1.id, [{"product_id": product.id, "quantity": 5}])

def test_receive_purchase_order_adds_stock(db_session, setup_data):
    user, warehouse1, _, product, _, supplier = setup_data

    items = [{"product_id": product.id, "quantity": 10, "price_per_unit": 500}]
    purchase_order = purchase_service.create_purchase_order(db_session, user.id, supplier.id, items)

    purchase_service.receive_purchase_order(db_session, user.id, purchase_order.id, warehouse1.id)

    stock_level = product_service.get_stock_level(db_session, product.id, warehouse1.id)
    assert stock_level == 10

def test_delete_warehouse_with_inventory_fails(db_session, setup_data):
    user, warehouse1, _, product, _, _ = setup_data
    product_service.adjust_stock_level(db_session, product.id, warehouse1.id, 10, "initial_stock", user.id)

    with pytest.raises(ValueError, match="Cannot delete a warehouse that has inventory"):
        warehouse_service.delete_warehouse(db_session, user.id, warehouse1.id)