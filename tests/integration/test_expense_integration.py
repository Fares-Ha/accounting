import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import models
from app.core import expense_service
from datetime import datetime

class TestExpenseIntegration(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Create user and accounts
        self.user = models.User(id=1, username="testuser", role=models.UserRole.ADMIN, hashed_password="pw")
        self.cash_account = models.Account(id=1, name="Cash", account_type=models.AccountType.ASSET)
        self.general_expenses_account = models.Account(id=2, name="General Expenses", account_type=models.AccountType.EXPENSE)
        self.db.add_all([self.user, self.cash_account, self.general_expenses_account])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        models.Base.metadata.drop_all(self.engine)

    def test_expense_lifecycle(self):
        """
        Tests the full lifecycle of creating an expense, from category creation
        to the expense itself, verifying all database interactions.
        """
        # 1. Create an expense category
        category = expense_service.create_expense_category(
            db=self.db,
            name="Office Supplies",
            user_id=self.user.id
        )
        self.assertIsNotNone(category.id)
        self.assertEqual(category.name, "Office Supplies")

        # 2. Create an expense
        expense_date = datetime.now()
        expense = expense_service.create_expense(
            db=self.db,
            user_id=self.user.id,
            description="Printer Paper",
            amount=5000, # in cents
            expense_date=expense_date,
            category_id=category.id
        )

        # Verify Expense creation
        self.assertIsNotNone(expense.id)
        self.assertEqual(expense.description, "Printer Paper")
        self.assertEqual(expense.amount, 5000)
        self.assertIsNotNone(expense.journal_entry_id)

        # Verify JournalEntry for the expense
        journal_entry = self.db.query(models.JournalEntry).filter_by(id=expense.journal_entry_id).one()
        self.assertIsNotNone(journal_entry)
        self.assertEqual(len(journal_entry.transactions), 2)

        # Verify AuditTrail for both actions
        audit_logs = self.db.query(models.AuditTrail).order_by(models.AuditTrail.id).all()
        self.assertEqual(len(audit_logs), 2)
        self.assertEqual(audit_logs[0].action, "CREATE_EXPENSE_CATEGORY")
        self.assertEqual(audit_logs[1].action, "CREATE_EXPENSE")

if __name__ == "__main__":
    unittest.main()
