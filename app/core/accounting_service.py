"""
Core service for managing accounting functions.

This module provides the business logic for handling financial operations
in the Ajyad Accountant application. It includes functions for managing the
Chart of Accounts, creating and retrieving Journal Entries, and ensuring
that all transactions adhere to double-entry bookkeeping principles.

Functions:
    create_account(db, name, account_type): Creates a new account.
    get_accounts(db): Retrieves all accounts.
    get_journal_entry(db, entry_id): Retrieves a specific journal entry.
    create_journal_entry(db, description, transactions, date): Creates a
        new, balanced journal entry.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import models
from datetime import datetime

def create_account(db: Session, name: str, account_type: models.AccountType, initial_balance: int = 0) -> models.Account:
    """
    Creates a new account in the chart of accounts.

    Args:
        db (Session): The database session.
        name (str): The unique name for the account.
        account_type (models.AccountType): The type of the account (e.g., ASSET, LIABILITY).
        initial_balance (int): The starting balance of the account, in cents. Defaults to 0.

    Returns:
        models.Account: The newly created account object.
    """
    db_account = models.Account(
        name=name,
        account_type=account_type,
        balance=initial_balance
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_accounts(db: Session) -> list[models.Account]:
    """
    Retrieves all accounts from the chart of accounts, ordered by name.

    Args:
        db (Session): The database session.

    Returns:
        list[models.Account]: A list of all account objects.
    """
    return db.query(models.Account).order_by(models.Account.name).all()

def get_journal_entry(db: Session, entry_id: int) -> models.JournalEntry | None:
    """
    Retrieves a single journal entry by its ID, including its transactions.

    Args:
        db (Session): The database session.
        entry_id (int): The ID of the journal entry to retrieve.

    Returns:
        models.JournalEntry | None: The found journal entry object, or None if not found.
    """
    return db.query(models.JournalEntry).filter(models.JournalEntry.id == entry_id).first()

def create_journal_entry(
    db: Session,
    description: str,
    transactions: list[dict],
    date: datetime = None
) -> models.JournalEntry:
    """
    Creates a new journal entry with a list of associated transactions.

    This function enforces the fundamental principle of double-entry
    bookkeeping: the total debits must equal the total credits. The sum of all
    transaction amounts must therefore be zero.

    Each transaction updates the balance of its respective account.

    Args:
        db (Session): The database session.
        description (str): A clear and concise description of the business
            transaction (e.g., "Cash sale", "Office supplies purchase").
        transactions (list[dict]): A list of dictionaries, where each dictionary
            represents a single debit or credit and must contain:
            - 'account_id' (int): The ID of the affected account.
            - 'amount' (int): The transaction amount in cents.
                              Use positive values for debits and negative
                              values for credits.
        date (datetime, optional): The date of the transaction. If not provided,
            the current UTC time is used.

    Returns:
        models.JournalEntry: The newly created journal entry object.

    Raises:
        ValueError: If the list of transactions is not balanced (i.e., the
            sum of amounts is not zero).
    """
    # 1. Validate that the journal entry is balanced.
    # The sum of all transaction amounts must be zero for the entry to be valid.
    total = sum(t["amount"] for t in transactions)
    if total != 0:
        raise ValueError(f"Journal entry is not balanced. Sum of transactions is {total}, but must be 0.")

    # 2. Create the parent JournalEntry record.
    # If no date is provided, default to the current time.
    db_journal_entry = models.JournalEntry(
        date=date or datetime.utcnow(),
        description=description
    )
    db.add(db_journal_entry)
    db.flush()  # Use flush to get the ID before the final commit.

    # 3. Process each transaction.
    for t in transactions:
        account_id = t["account_id"]
        amount = t["amount"]

        # Create the Transaction record, linking it to the new JournalEntry.
        db_transaction = models.Transaction(
            journal_entry_id=db_journal_entry.id,
            account_id=account_id,
            amount=amount
        )
        db.add(db_transaction)

        # 4. Atomically update the balance of the affected account.
        # This ensures that the balance reflects the new transaction immediately.
        # Using `with_for_update()` can be added here for high-concurrency scenarios
        # to lock the row, but for this application, a direct update is sufficient.
        account = db.query(models.Account).filter(models.Account.id == account_id).first()
        if account:
            account.balance += amount
        else:
            # Rollback transaction if an account is invalid to maintain data integrity
            db.rollback()
            raise ValueError(f"Invalid account ID: {account_id}")

    # 5. Commit the session to save all changes atomically.
    db.commit()
    db.refresh(db_journal_entry)

    return db_journal_entry

def get_profit_and_loss(db: Session, start_date: datetime, end_date: datetime) -> dict:
    """
    Calculates the Profit and Loss (P&L) statement for a given period.

    Args:
        db (Session): The database session.
        start_date (datetime): The start date of the reporting period.
        end_date (datetime): The end date of the reporting period.

    Returns:
        dict: A dictionary containing the P&L report.
    """
    # Base query for transactions within the date range
    base_query = db.query(func.sum(models.Transaction.amount)).join(models.JournalEntry).filter(
        models.JournalEntry.date >= start_date,
        models.JournalEntry.date <= end_date
    )

    # Get total revenue for the period
    total_revenue = base_query.join(models.Account).filter(
        models.Account.account_type == models.AccountType.REVENUE
    ).scalar() or 0

    # Get total expenses for the period
    total_expenses = base_query.join(models.Account).filter(
        models.Account.account_type == models.AccountType.EXPENSE
    ).scalar() or 0

    # Note: Revenue is typically negative (credit), and Expenses are positive (debit).
    # So, Net Profit = (-Total Revenue) - Total Expenses
    # The absolute value of revenue is used for reporting.
    net_profit = -total_revenue - total_expenses

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_revenue": -total_revenue,
        "total_expenses": total_expenses,
        "net_profit": net_profit
    }

def get_balance_sheet(db: Session) -> dict:
    """
    Generates the Balance Sheet report.

    The Balance Sheet is a snapshot of the company's financial health at a
    single point in time, following the accounting equation:
    Assets = Liabilities + Equity.

    Returns:
        dict: A dictionary containing the Balance Sheet report.
    """
    assets = db.query(func.sum(models.Account.balance)).filter(
        models.Account.account_type == models.AccountType.ASSET).scalar() or 0
    liabilities = db.query(func.sum(models.Account.balance)).filter(
        models.Account.account_type == models.AccountType.LIABILITY).scalar() or 0
    equity = db.query(func.sum(models.Account.balance)).filter(
        models.Account.account_type == models.AccountType.EQUITY).scalar() or 0

    return {
        "assets": assets,
        "liabilities": liabilities,
        "equity": equity,
        "total_liabilities_and_equity": liabilities + equity,
        "verification": "Assets must equal Liabilities + Equity"
    }