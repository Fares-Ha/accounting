import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.database.models import User, UserRole
from app.core import auth

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
def setup_users(db_session):
    admin_user = User(username="admin", hashed_password=auth.hash_password("password"), role=UserRole.ADMIN)
    sales_user = User(username="sales", hashed_password=auth.hash_password("password"), role=UserRole.SALES)
    db_session.add(admin_user)
    db_session.add(sales_user)
    db_session.commit()
    return admin_user, sales_user

def test_create_user_by_admin(db_session, setup_users):
    admin_user, _ = setup_users
    new_user = auth.create_user(db_session, admin_user.id, "newuser", "newpassword", UserRole.ACCOUNTANT)
    assert new_user.username == "newuser"
    assert new_user.role == UserRole.ACCOUNTANT
    assert auth.verify_password("newpassword", new_user.hashed_password)

def test_create_user_by_non_admin_fails(db_session, setup_users):
    _, sales_user = setup_users
    with pytest.raises(PermissionError):
        auth.create_user(db_session, sales_user.id, "anotheruser", "password", UserRole.SALES)

def test_update_user_by_admin(db_session, setup_users):
    admin_user, sales_user = setup_users
    updated_user = auth.update_user(db_session, admin_user.id, sales_user.id, "updatedsales", "updatedpassword", UserRole.ACCOUNTANT)
    assert updated_user.username == "updatedsales"
    assert updated_user.role == UserRole.ACCOUNTANT
    assert auth.verify_password("updatedpassword", updated_user.hashed_password)

def test_update_user_by_non_admin_fails(db_session, setup_users):
    admin_user, sales_user = setup_users
    with pytest.raises(PermissionError):
        auth.update_user(db_session, sales_user.id, admin_user.id, "newadminname", "newpass", UserRole.ADMIN)

def test_delete_user_by_admin(db_session, setup_users):
    admin_user, sales_user = setup_users
    auth.delete_user(db_session, admin_user.id, sales_user.id)
    deleted_user = auth.get_user(db_session, sales_user.id)
    assert deleted_user is None

def test_delete_user_by_non_admin_fails(db_session, setup_users):
    admin_user, sales_user = setup_users
    with pytest.raises(PermissionError):
        auth.delete_user(db_session, sales_user.id, admin_user.id)

def test_admin_cannot_delete_self(db_session, setup_users):
    admin_user, _ = setup_users
    with pytest.raises(ValueError, match="Admins cannot delete their own account."):
        auth.delete_user(db_session, admin_user.id, admin_user.id)