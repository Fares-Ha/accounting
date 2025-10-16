import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.database import models
from app.core import expense_service, accounting_service
from datetime import datetime

class TestExpenseService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Create a dummy user
        self.user = models.User(username="testuser", hashed_password="password", role=models.UserRole.ADMIN)
        self.db.add(self.user)

        # Create necessary accounts for testing
        self.cash_account = models.Account(name="Cash", account_type=models.AccountType.ASSET)
        self.expenses_account = models.Account(name="General Expenses", account_type=models.AccountType.EXPENSE)
        self.db.add_all([self.cash_account, self.expenses_account])
        self.db.commit()
        self.db.refresh(self.user)
        self.db.refresh(self.cash_account)
        self.db.refresh(self.expenses_account)


    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_create_and_get_expense_category(self):
        category = expense_service.create_expense_category(self.db, "Office Supplies", self.user.id)
        self.assertIsNotNone(category.id)
        self.assertEqual(category.name, "Office Supplies")

        retrieved_category = expense_service.get_expense_category(self.db, category.id)
        self.assertEqual(retrieved_category.name, "Office Supplies")

    def test_create_expense(self):
        category = expense_service.create_expense_category(self.db, "Travel", self.user.id)

        expense_date = datetime.now()
        expense = expense_service.create_expense(
            self.db,
            user_id=self.user.id,
            description="Taxi fare",
            amount=1500, # 15.00
            expense_date=expense_date,
            category_id=category.id
        )

        self.assertIsNotNone(expense.id)
        self.assertEqual(expense.description, "Taxi fare")
        self.assertEqual(expense.amount, 1500)
        self.assertIsNotNone(expense.journal_entry_id)

        # Verify journal entry
        journal_entry = accounting_service.get_journal_entry(self.db, expense.journal_entry_id)
        self.assertIsNotNone(journal_entry)
        self.assertEqual(len(journal_entry.transactions), 2)

        debit = next(t for t in journal_entry.transactions if t.amount > 0)
        credit = next(t for t in journal_entry.transactions if t.amount < 0)

        self.assertEqual(debit.account_id, self.expenses_account.id)
        self.assertEqual(debit.amount, 1500)
        self.assertEqual(credit.account_id, self.cash_account.id)
        self.assertEqual(credit.amount, -1500)

    def test_update_expense(self):
        category = expense_service.create_expense_category(self.db, "Meals", self.user.id)
        expense = expense_service.create_expense(self.db, self.user.id, "Lunch", 2000, datetime.now(), category.id)

        updated_expense = expense_service.update_expense(
            self.db,
            user_id=self.user.id,
            expense_id=expense.id,
            description="Client Dinner",
            amount=5000,
            expense_date=expense.expense_date,
            category_id=category.id
        )
        self.assertEqual(updated_expense.description, "Client Dinner")
        self.assertEqual(updated_expense.amount, 5000)

    def test_delete_expense(self):
        category = expense_service.create_expense_category(self.db, "Utilities", self.user.id)
        expense = expense_service.create_expense(self.db, self.user.id, "Internet Bill", 6000, datetime.now(), category.id)

        result = expense_service.delete_expense(self.db, self.user.id, expense.id)
        self.assertTrue(result)

        deleted_expense = expense_service.get_expense(self.db, expense.id)
        self.assertIsNone(deleted_expense)

if __name__ == "__main__":
    unittest.main()