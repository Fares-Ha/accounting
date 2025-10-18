import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.database.models import User, UserRole, Product
from app.core import manufacturing_service, product_service, auth
from datetime import datetime

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def setup_data(db_session):
    admin_user = User(username="admin", hashed_password=auth.hash_password("password"), role=UserRole.ADMIN)
    db_session.add(admin_user)
    db_session.commit()

    product_a = product_service.create_product(db_session, "Product A", "Finished Good", 1000)
    component_b = product_service.create_product(db_session, "Component B", "Raw Material", 100)
    component_c = product_service.create_product(db_session, "Component C", "Raw Material", 200)

    return admin_user, product_a, component_b, component_c

def test_create_bom_by_admin(db_session, setup_data):
    admin_user, product_a, component_b, component_c = setup_data
    items = [
        {"component_id": component_b.id, "quantity": 2},
        {"component_id": component_c.id, "quantity": 1}
    ]
    bom = manufacturing_service.create_bom(
        db=db_session,
        user_id=admin_user.id,
        product_id=product_a.id,
        name="BOM for Product A",
        description="Standard BOM",
        items=items
    )
    assert bom.name == "BOM for Product A"
    assert len(bom.items) == 2

def test_update_bom_by_admin(db_session, setup_data):
    admin_user, product_a, component_b, component_c = setup_data
    items = [{"component_id": component_b.id, "quantity": 2}]
    bom = manufacturing_service.create_bom(
        db=db_session,
        user_id=admin_user.id,
        product_id=product_a.id,
        name="BOM for Product A",
        description="Standard BOM",
        items=items
    )

    new_items = [
        {"component_id": component_b.id, "quantity": 3},
        {"component_id": component_c.id, "quantity": 5}
    ]
    updated_bom = manufacturing_service.update_bom(
        db=db_session,
        user_id=admin_user.id,
        bom_id=bom.id,
        product_id=product_a.id,
        name="Updated BOM",
        description="New BOM",
        items=new_items
    )
    assert updated_bom.name == "Updated BOM"
    assert len(updated_bom.items) == 2
    assert updated_bom.items[0].quantity == 3
    assert updated_bom.items[1].quantity == 5

def test_delete_bom_by_admin(db_session, setup_data):
    admin_user, product_a, component_b, _ = setup_data
    items = [{"component_id": component_b.id, "quantity": 2}]
    bom = manufacturing_service.create_bom(
        db=db_session,
        user_id=admin_user.id,
        product_id=product_a.id,
        name="BOM to be deleted",
        description="",
        items=items
    )

    manufacturing_service.delete_bom(db_session, admin_user.id, bom.id)

    deleted_bom = manufacturing_service.get_bom(db_session, admin_user.id, bom.id)
    assert deleted_bom is None