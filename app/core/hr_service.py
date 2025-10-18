from sqlalchemy.orm import Session
from ..database import models
from .audit_service import AuditService
from .security import requires_roles
from datetime import datetime

audit_service = AuditService()

@requires_roles(models.UserRole.ADMIN)
def create_employee(db: Session, user_id: int, name: str, job_title: str, email: str, phone: str, hire_date: datetime, salary: int) -> models.Employee:
    """
    Creates a new employee.
    """
    db_employee = models.Employee(
        name=name,
        job_title=job_title,
        email=email,
        phone=phone,
        hire_date=hire_date,
        salary=salary
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    audit_service.create_audit_log(
        db,
        user_id=user_id,
        action="CREATE_EMPLOYEE",
        details=f"User #{user_id} created new employee #{db_employee.id} with name '{name}'"
    )
    return db_employee

@requires_roles(models.UserRole.ADMIN)
def get_employees(db: Session, user_id: int) -> list[models.Employee]:
    """
    Retrieves all employees.
    """
    return db.query(models.Employee).all()

@requires_roles(models.UserRole.ADMIN)
def get_employee(db: Session, user_id: int, employee_id: int) -> models.Employee | None:
    """
    Retrieves a single employee by their ID.
    """
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()

@requires_roles(models.UserRole.ADMIN)
def update_employee(db: Session, user_id: int, employee_id: int, name: str, job_title: str, email: str, phone: str, hire_date: datetime, salary: int) -> models.Employee:
    """
    Updates an existing employee.
    """
    db_employee = get_employee(db, user_id, employee_id)
    if db_employee:
        db_employee.name = name
        db_employee.job_title = job_title
        db_employee.email = email
        db_employee.phone = phone
        db_employee.hire_date = hire_date
        db_employee.salary = salary
        db.commit()
        db.refresh(db_employee)
        audit_service.create_audit_log(
            db,
            user_id=user_id,
            action="UPDATE_EMPLOYEE",
            details=f"User #{user_id} updated employee #{employee_id}"
        )
    return db_employee

@requires_roles(models.UserRole.ADMIN)
def delete_employee(db: Session, user_id: int, employee_id: int):
    """
    Deletes an employee.
    """
    db_employee = get_employee(db, user_id, employee_id)
    if db_employee:
        audit_service.create_audit_log(
            db,
            user_id=user_id,
            action="DELETE_EMPLOYEE",
            details=f"User #{user_id} deleted employee #{employee_id}"
        )
        db.delete(db_employee)
        db.commit()
    return db_employee