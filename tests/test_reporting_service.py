import unittest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base, Account, AccountType, JournalEntry, Transaction
from app.core.reporting_service import ReportingService

class TestReportingService(unittest.TestCase):
    def setUp(self):
        """
        Set up an in-memory SQLite database and create sample data.
        """
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        self.reporting_service = ReportingService()
        self.create_test_data()

    def tearDown(self):
        """
        Clean up the database after each test.
        """
        Base.metadata.drop_all(self.engine)
        self.db.close()

    def create_test_data(self):
        """
        Create sample accounts and transactions for testing.
        """
        # Accounts
        self.sales_account = Account(name="Sales", account_type=AccountType.REVENUE, balance=0)
        self.rent_account = Account(name="Rent", account_type=AccountType.EXPENSE, balance=0)
        self.cash_account = Account(name="Cash", account_type=AccountType.ASSET, balance=0)
        self.db.add_all([self.sales_account, self.rent_account, self.cash_account])
        self.db.commit()

        # Journal Entries and Transactions
        # Sale transaction - within date range
        entry1 = JournalEntry(date=datetime.now() - timedelta(days=10), description="Software Sale")
        self.db.add(entry1)
        self.db.commit()
        trans1a = Transaction(journal_entry_id=entry1.id, account_id=self.cash_account.id, amount=5000) # Debit
        trans1b = Transaction(journal_entry_id=entry1.id, account_id=self.sales_account.id, amount=-5000) # Credit

        # Expense transaction - within date range
        entry2 = JournalEntry(date=datetime.now() - timedelta(days=5), description="Office Rent")
        self.db.add(entry2)
        self.db.commit()
        trans2a = Transaction(journal_entry_id=entry2.id, account_id=self.rent_account.id, amount=1500) # Debit
        trans2b = Transaction(journal_entry_id=entry2.id, account_id=self.cash_account.id, amount=-1500) # Credit

        # Another sale - outside date range
        entry3 = JournalEntry(date=datetime.now() - timedelta(days=40), description="Old Sale")
        self.db.add(entry3)
        self.db.commit()
        trans3a = Transaction(journal_entry_id=entry3.id, account_id=self.cash_account.id, amount=2000)
        trans3b = Transaction(journal_entry_id=entry3.id, account_id=self.sales_account.id, amount=-2000)

        self.db.add_all([trans1a, trans1b, trans2a, trans2b, trans3a, trans3b])
        self.db.commit()

    def test_get_profit_and_loss_statement_correctly_calculates_period(self):
        """
        Test that the P&L statement correctly calculates revenue, expenses, and profit
        for a specific date range, ignoring transactions outside the range.
        """
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        report = self.reporting_service.get_profit_and_loss_statement(self.db, start_date, end_date)

        # Expected values:
        # Revenue should only include the 5000 from the recent sale.
        # Expenses should only include the 1500 for rent.
        # Net profit should be 5000 - 1500 = 3500.

        self.assertEqual(report["revenue"], 5000)
        self.assertEqual(report["expenses"], 1500)
        self.assertEqual(report["net_profit"], 3500)

if __name__ == '__main__':
    unittest.main()