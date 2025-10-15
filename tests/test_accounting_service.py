import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.core import accounting_service
from app.database import models

class TestAccountingService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        self.db.close()

    def test_create_account(self):
        account = accounting_service.create_account(self.db, "Cash", models.AccountType.ASSET)
        self.assertEqual(account.name, "Cash")
        self.assertEqual(account.account_type, models.AccountType.ASSET)
        self.assertEqual(account.balance, 0)

    def test_create_journal_entry(self):
        # Create accounts
        cash_account = accounting_service.create_account(self.db, "Cash", models.AccountType.ASSET)
        revenue_account = accounting_service.create_account(self.db, "Revenue", models.AccountType.REVENUE)

        # Create a journal entry
        transactions = [
            {"account_id": cash_account.id, "amount": 10000},
            {"account_id": revenue_account.id, "amount": -10000},
        ]
        journal_entry = accounting_service.create_journal_entry(self.db, "Test sale", transactions)

        # Verify the journal entry
        self.assertEqual(journal_entry.description, "Test sale")
        self.assertEqual(len(journal_entry.transactions), 2)

        # Verify the account balances
        self.assertEqual(cash_account.balance, 10000)
        self.assertEqual(revenue_account.balance, -10000)

    def test_create_unbalanced_journal_entry(self):
        # Create accounts
        cash_account = accounting_service.create_account(self.db, "Cash", models.AccountType.ASSET)
        revenue_account = accounting_service.create_account(self.db, "Revenue", models.AccountType.REVENUE)

        # Create an unbalanced journal entry
        transactions = [
            {"account_id": cash_account.id, "amount": 10000},
            {"account_id": revenue_account.id, "amount": -9000},
        ]

        with self.assertRaises(ValueError):
            accounting_service.create_journal_entry(self.db, "Test unbalanced sale", transactions)

if __name__ == "__main__":
    unittest.main()