from sqlalchemy.orm import Session
from ..database import models
from . import accounting_service
from .audit_service import AuditService
from datetime import datetime

audit_service = AuditService()

# Expense Category CRUD

def create_expense_category(db: Session, name: str, user_id: int):
    """
    Creates a new expense category.
    """
    db_category = models.ExpenseCategory(name=name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    audit_service.create_audit_log(
        db,
        user_id=user_id,
        action="CREATE_EXPENSE_CATEGORY",
        details=f"Created expense category: {name}"
    )
    return db_category

def get_expense_categories(db: Session):
    """
    Retrieves all expense categories.
    """
    return db.query(models.ExpenseCategory).all()

def get_expense_category(db: Session, category_id: int):
    """
    Retrieves a single expense category by its ID.
    """
    return db.query(models.ExpenseCategory).filter(models.ExpenseCategory.id == category_id).first()

# Expense CRUD

def create_expense(db: Session, user_id: int, description: str, amount: int, expense_date: datetime, category_id: int):
    """
    Creates a new expense, logs it, and creates a corresponding journal entry.
    """
    # Create the journal entry for the expense
    try:
        cash_account = db.query(models.Account).filter(models.Account.name == "Cash").one()
        expense_account_generic = db.query(models.Account).filter(models.Account.name == "General Expenses").one()

        journal_entry = accounting_service.create_journal_entry(
            db,
            description=f"Expense: {description}",
            date=expense_date,
            transactions=[
                {"account_id": expense_account_generic.id, "amount": amount},
                {"account_id": cash_account.id, "amount": -amount},
            ]
        )
        journal_entry_id = journal_entry.id
    except Exception as e:
        print(f"Failed to create journal entry for expense: {e}")
        journal_entry_id = None


    db_expense = models.Expense(
        description=description,
        amount=amount,
        expense_date=expense_date,
        category_id=category_id,
        user_id=user_id,
        journal_entry_id=journal_entry_id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)

    audit_service.create_audit_log(
        db,
        user_id=user_id,
        action="CREATE_EXPENSE",
        details=f"Created expense: {description} for amount {amount}"
    )

    return db_expense

def get_expenses(db: Session):
    """
    Retrieves all expenses.
    """
    return db.query(models.Expense).all()

def get_expense(db: Session, expense_id: int):
    """
    Retrieves a single expense by its ID.
    """
    return db.query(models.Expense).filter(models.Expense.id == expense_id).first()

def update_expense(db: Session, user_id: int, expense_id: int, description: str, amount: int, expense_date: datetime, category_id: int):
    """
    Updates an existing expense.
    """
    db_expense = get_expense(db, expense_id)
    if not db_expense:
        raise ValueError("Expense not found")

    db_expense.description = description
    db_expense.amount = amount
    db_expense.expense_date = expense_date
    db_expense.category_id = category_id
    db.commit()
    db.refresh(db_expense)

    audit_service.create_audit_log(
        db,
        user_id=user_id,
        action="UPDATE_EXPENSE",
        details=f"Updated expense ID: {expense_id}"
    )

    return db_expense

def delete_expense(db: Session, user_id: int, expense_id: int):
    """
    Deletes an expense.
    """
    db_expense = get_expense(db, expense_id)
    if not db_expense:
        raise ValueError("Expense not found")

    db.delete(db_expense)
    db.commit()

    audit_service.create_audit_log(
        db,
        user_id=user_id,
        action="DELETE_EXPENSE",
        details=f"Deleted expense ID: {expense_id}"
    )
    return True