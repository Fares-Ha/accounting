import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import models
from app.core import reporting_service, sales_service, expense_service
from datetime import datetime, timedelta

class TestReportingIntegration(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        self.reporting_service = reporting_service.ReportingService()

        # Create user, customer, products, and accounts
        self.user = models.User(id=1, username="testuser", role=models.UserRole.ADMIN, hashed_password="pw")
        self.customer = models.Customer(id=1, name="Test Customer", email="customer@test.com")
        self.product = models.Product(id=1, name="Test Product", price=1000, stock_quantity=100)

        # Accounts
        self.accounts = {
            "Accounts Receivable": models.Account(name="Accounts Receivable", account_type=models.AccountType.ASSET, balance=0),
            "Sales Revenue": models.Account(name="Sales Revenue", account_type=models.AccountType.REVENUE, balance=0),
            "Cash": models.Account(name="Cash", account_type=models.AccountType.ASSET, balance=100000),
            "General Expenses": models.Account(name="General Expenses", account_type=models.AccountType.EXPENSE, balance=0),
        }

        self.db.add(self.user)
        self.db.add(self.customer)
        self.db.add(self.product)
        for acc in self.accounts.values():
            self.db.add(acc)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        models.Base.metadata.drop_all(self.engine)

    def test_financial_reports(self):
        """
        Tests the P&L and Balance Sheet reports by creating sample transactional data.
        """
        start_date = datetime.now() - timedelta(days=10)
        end_date = datetime.now() + timedelta(days=1)

        # 1. Create a sale
        sales_items = [{"product_id": self.product.id, "quantity": 10}]
        sales_service.create_sales_order(
            db=self.db, user_id=self.user.id, customer_id=self.customer.id, items=sales_items
        )

        # 2. Create an expense
        category = expense_service.create_expense_category(self.db, "Utilities", self.user.id)
        expense_service.create_expense(
            self.db, self.user.id, "Electricity Bill", 1500, datetime.now(), category.id
        )

        # 3. Test Profit & Loss Statement
        pnl = self.reporting_service.get_profit_and_loss_statement(self.db, start_date, end_date)

        self.assertEqual(pnl["revenue"], 10000)
        self.assertEqual(pnl["expenses"], 1500)
        self.assertEqual(pnl["net_profit"], 8500)

        # 4. Test Balance Sheet
        balance_sheet = self.reporting_service.get_balance_sheet(self.db, end_date)

        # Expected asset value = Initial Cash (100,000) - Expense (1,500) + Accounts Receivable (10,000)
        expected_assets = 100000 - 1500 + 10000
        self.assertEqual(balance_sheet["assets"], expected_assets)
        self.assertEqual(balance_sheet["liabilities"], 0)

if __name__ == "__main__":
    unittest.main()
