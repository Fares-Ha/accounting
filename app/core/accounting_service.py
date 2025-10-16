from sqlalchemy.orm import Session
from ..database import models
from datetime import datetime

def create_account(db: Session, name: str, account_type: models.AccountType):
    """
    Creates a new account in the chart of accounts.
    """
    db_account = models.Account(name=name, account_type=account_type)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_accounts(db: Session):
    """
    Retrieves all accounts from the chart of accounts.
    """
    return db.query(models.Account).all()

def get_journal_entry(db: Session, entry_id: int):
    """
    Retrieves a single journal entry by its ID.
    """
    return db.query(models.JournalEntry).filter(models.JournalEntry.id == entry_id).first()

def create_journal_entry(db: Session, description: str, transactions: list[dict], date: datetime = None):
    """
    Creates a new journal entry with a list of transactions.

    A journal entry represents a single business transaction and must
    always be balanced. The sum of the debits must equal the sum of the
    credits.

    Args:
        db: The database session.
        description: A description of the journal entry.
        transactions: A list of dictionaries, where each dictionary
            represents a transaction and has the following keys:
            - account_id: The ID of the account.
            - amount: The amount of the transaction. Positive for a
                debit, negative for a credit.
        date: The date of the transaction. Defaults to now.
    """
    # Validate that the journal entry is balanced. The sum of all
    # transactions must be zero.
    total = sum(t["amount"] for t in transactions)
    if total != 0:
        raise ValueError("Journal entry is not balanced.")

    # Create the journal entry.
    db_journal_entry = models.JournalEntry(
        date=date or datetime.now(),
        description=description
    )
    db.add(db_journal_entry)
    db.commit()
    db.refresh(db_journal_entry)

    # Create the transactions and update the account balances.
    for t in transactions:
        db_transaction = models.Transaction(
            journal_entry_id=db_journal_entry.id,
            account_id=t["account_id"],
            amount=t["amount"]
        )
        db.add(db_transaction)

        # Update the balance of the affected account.
        account = db.query(models.Account).filter(models.Account.id == t["account_id"]).first()
        account.balance += t["amount"]
        db.add(account)

    db.commit()
    return db_journal_entry