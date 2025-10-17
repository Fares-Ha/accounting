import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.core import accounting_service
from app.database import models

class TestAccountingService(unittest.TestCase):
    def setUp(self):
        """Set up a clean in-memory SQLite database for each test."""
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

    def tearDown(self):
        """Close the database session after each test."""
        self.db.close()

    def test_create_account(self):
        """Test creating a new account with an initial balance."""
        account = accounting_service.create_account(
            self.db, "Cash", models.AccountType.ASSET, initial_balance=50000
        )
        self.assertEqual(account.name, "Cash")
        self.assertEqual(account.account_type, models.AccountType.ASSET)
        self.assertEqual(account.balance, 50000)

    def test_create_journal_entry_success(self):
        """Test the successful creation of a balanced journal entry."""
        # Arrange: Create necessary accounts
        cash_account = accounting_service.create_account(self.db, "Cash", models.AccountType.ASSET)
        revenue_account = accounting_service.create_account(self.db, "Revenue", models.AccountType.REVENUE)

        # Act: Create a journal entry
        transactions = [
            {"account_id": cash_account.id, "amount": 10000},  # Debit
            {"account_id": revenue_account.id, "amount": -10000}, # Credit
        ]
        journal_entry = accounting_service.create_journal_entry(
            self.db, "Test sale", transactions, date=datetime(2023, 10, 26)
        )

        # Assert: Verify the journal entry and account balances
        self.assertEqual(journal_entry.description, "Test sale")
        self.assertEqual(len(journal_entry.transactions), 2)
        self.assertEqual(journal_entry.date, datetime(2023, 10, 26))
        self.assertEqual(cash_account.balance, 10000)
        self.assertEqual(revenue_account.balance, -10000)

    def test_create_unbalanced_journal_entry_fails(self):
        """Test that creating an unbalanced journal entry raises a ValueError."""
        # Arrange: Create accounts
        cash_account = accounting_service.create_account(self.db, "Cash", models.AccountType.ASSET)
        revenue_account = accounting_service.create_account(self.db, "Revenue", models.AccountType.REVENUE)

        # Act: Attempt to create an unbalanced journal entry
        transactions = [
            {"account_id": cash_account.id, "amount": 10000},
            {"account_id": revenue_account.id, "amount": -9000}, # Unbalanced
        ]

        # Assert: Expect a ValueError
        with self.assertRaisesRegex(ValueError, "Journal entry is not balanced"):
            accounting_service.create_journal_entry(self.db, "Test unbalanced sale", transactions)

    def test_create_journal_entry_with_invalid_account_fails(self):
        """Test that creating a journal entry with a non-existent account ID fails."""
        # Arrange: Create one valid account
        cash_account = accounting_service.create_account(self.db, "Cash", models.AccountType.ASSET)
        invalid_account_id = 999  # An ID that does not exist

        # Act: Attempt to create a journal entry with an invalid account ID
        transactions = [
            {"account_id": cash_account.id, "amount": 10000},
            {"account_id": invalid_account_id, "amount": -10000},
        ]

        # Assert: Expect a ValueError and ensure no changes were committed
        with self.assertRaisesRegex(ValueError, f"Invalid account ID: {invalid_account_id}"):
            accounting_service.create_journal_entry(self.db, "Test invalid account", transactions)

        # Verify that the valid account's balance was not changed
        self.assertEqual(cash_account.balance, 0)

    def test_get_profit_and_loss(self):
        """Test the profit and loss calculation for a specific date range."""
        # Arrange: Create accounts
        bank_account = accounting_service.create_account(self.db, "Bank", models.AccountType.ASSET)
        revenue_account = accounting_service.create_account(self.db, "Sales Revenue", models.AccountType.REVENUE)
        expense_account = accounting_service.create_account(self.db, "Rent Expense", models.AccountType.EXPENSE)

        # Create transactions within the date range
        accounting_service.create_journal_entry(self.db, "Sale 1", [
            {"account_id": bank_account.id, "amount": 50000},
            {"account_id": revenue_account.id, "amount": -50000}
        ], date=datetime(2023, 1, 15))

        accounting_service.create_journal_entry(self.db, "Rent", [
            {"account_id": expense_account.id, "amount": 10000},
            {"account_id": bank_account.id, "amount": -10000}
        ], date=datetime(2023, 1, 20))

        # Create a transaction outside the date range (should be ignored)
        accounting_service.create_journal_entry(self.db, "Old Sale", [
            {"account_id": bank_account.id, "amount": 5000},
            {"account_id": revenue_account.id, "amount": -5000}
        ], date=datetime(2022, 12, 15))

        # Act: Calculate P&L
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 1, 31)
        pnl = accounting_service.get_profit_and_loss(self.db, start_date, end_date)

        # Assert
        self.assertEqual(pnl["total_revenue"], 50000)
        self.assertEqual(pnl["total_expenses"], 10000)
        self.assertEqual(pnl["net_profit"], 40000)

    def test_get_balance_sheet(self):
        """Test the balance sheet calculation."""
        # Arrange: Create accounts with initial balances
        assets = accounting_service.create_account(self.db, "Assets", models.AccountType.ASSET, 15000)
        liabilities = accounting_service.create_account(self.db, "Liabilities", models.AccountType.LIABILITY, 8000)
        equity = accounting_service.create_account(self.db, "Equity", models.AccountType.EQUITY, 7000)

        # Act: Generate the balance sheet
        balance_sheet = accounting_service.get_balance_sheet(self.db)

        # Assert: Assets = Liabilities + Equity
        self.assertEqual(balance_sheet["assets"], 15000)
        self.assertEqual(balance_sheet["liabilities"], 8000)
        self.assertEqual(balance_sheet["equity"], 7000)
        self.assertEqual(balance_sheet["total_liabilities_and_equity"], 15000)

if __name__ == "__main__":
    unittest.main()