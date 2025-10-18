import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.database.models import User, UserRole, Employee
from app.core import hr_service, auth
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
def setup_users(db_session):
    admin_user = User(username="admin", hashed_password=auth.hash_password("password"), role=UserRole.ADMIN)
    sales_user = User(username="sales", hashed_password=auth.hash_password("password"), role=UserRole.SALES)
    db_session.add(admin_user)
    db_session.add(sales_user)
    db_session.commit()
    return admin_user, sales_user

def test_create_employee_by_admin(db_session, setup_users):
    admin_user, _ = setup_users
    employee = hr_service.create_employee(
        db=db_session,
        user_id=admin_user.id,
        name="John Doe",
        job_title="Software Engineer",
        email="john.doe@example.com",
        phone="1234567890",
        hire_date=datetime.utcnow(),
        salary=6000000
    )
    assert employee.name == "John Doe"
    assert employee.salary == 6000000

def test_create_employee_by_non_admin_fails(db_session, setup_users):
    _, sales_user = setup_users
    with pytest.raises(PermissionError):
        hr_service.create_employee(
            db=db_session,
            user_id=sales_user.id,
            name="Jane Doe",
            job_title="Sales Associate",
            email="jane.doe@example.com",
            phone="0987654321",
            hire_date=datetime.utcnow(),
            salary=5000000
        )

def test_update_employee_by_admin(db_session, setup_users):
    admin_user, _ = setup_users
    employee = hr_service.create_employee(
        db=db_session,
        user_id=admin_user.id,
        name="John Doe",
        job_title="Software Engineer",
        email="john.doe@example.com",
        phone="1234567890",
        hire_date=datetime.utcnow(),
        salary=6000000
    )
    updated_employee = hr_service.update_employee(
        db=db_session,
        user_id=admin_user.id,
        employee_id=employee.id,
        name="John Doe Jr.",
        job_title="Senior Software Engineer",
        email="john.doe.jr@example.com",
        phone="1112223333",
        hire_date=datetime.utcnow(),
        salary=8000000
    )
    assert updated_employee.name == "John Doe Jr."
    assert updated_employee.salary == 8000000

def test_delete_employee_by_admin(db_session, setup_users):
    admin_user, _ = setup_users
    employee = hr_service.create_employee(
        db=db_session,
        user_id=admin_user.id,
        name="John Doe",
        job_title="Software Engineer",
        email="john.doe@example.com",
        phone="1234567890",
        hire_date=datetime.utcnow(),
        salary=6000000
    )
    hr_service.delete_employee(db_session, admin_user.id, employee.id)
    deleted_employee = hr_service.get_employee(db_session, admin_user.id, employee.id)
    assert deleted_employee is None