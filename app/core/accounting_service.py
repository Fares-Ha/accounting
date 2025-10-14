from sqlalchemy.orm import Session
from ..database import models

def create_ledger_transaction(db: Session, amount: int, transaction_type: models.TransactionType, related_order_id: int):
    """
    Creates a new ledger transaction.
    """
    db_transaction = models.LedgerTransaction(
        amount=amount,
        transaction_type=transaction_type,
        related_order_id=related_order_id,
        related_order_type=transaction_type.value
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_ledger_transactions(db: Session):
    """
    Retrieves all ledger transactions.
    """
    return db.query(models.LedgerTransaction).all()