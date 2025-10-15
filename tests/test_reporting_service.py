import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.core import reporting_service, accounting_service
from app.database import models

class TestReportingService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        self.reporting_service = reporting_service.ReportingService()

    def tearDown(self):
        self.db.close()

    def test_get_profit_and_loss_statement(self):
        # Create accounts
        revenue_account = accounting_service.create_account(self.db, "Revenue", models.AccountType.REVENUE)
        expenses_account = accounting_service.create_account(self.db, "Expenses", models.AccountType.EXPENSE)

        # Create journal entries
        accounting_service.create_journal_entry(self.db, "Test revenue", [
            {"account_id": revenue_account.id, "amount": -10000},
            {"account_id": accounting_service.create_account(self.db, "Cash", models.AccountType.ASSET).id, "amount": 10000},
        ])
        accounting_service.create_journal_entry(self.db, "Test expense", [
            {"account_id": expenses_account.id, "amount": 5000},
            {"account_id": accounting_service.create_account(self.db, "Cash2", models.AccountType.ASSET).id, "amount": -5000},
        ])

        # Generate P&L statement
        pnl = self.reporting_service.get_profit_and_loss_statement(self.db)

        # Verify the P&L statement
        self.assertEqual(pnl["revenue"], -10000)
        self.assertEqual(pnl["expenses"], 5000)
        self.assertEqual(pnl["net_profit"], -15000)

    def test_get_balance_sheet(self):
        # Create accounts
        asset_account = accounting_service.create_account(self.db, "Assets", models.AccountType.ASSET)
        liability_account = accounting_service.create_account(self.db, "Liabilities", models.AccountType.LIABILITY)
        equity_account = accounting_service.create_account(self.db, "Equity", models.AccountType.EQUITY)

        # Create journal entries
        accounting_service.create_journal_entry(self.db, "Test asset", [
            {"account_id": asset_account.id, "amount": 10000},
            {"account_id": accounting_service.create_account(self.db, "Cash", models.AccountType.ASSET).id, "amount": -10000},
        ])
        accounting_service.create_journal_entry(self.db, "Test liability", [
            {"account_id": liability_account.id, "amount": -5000},
            {"account_id": accounting_service.create_account(self.db, "Cash2", models.AccountType.ASSET).id, "amount": 5000},
        ])
        accounting_service.create_journal_entry(self.db, "Test equity", [
            {"account_id": equity_account.id, "amount": -2000},
            {"account_id": accounting_service.create_account(self.db, "Cash3", models.AccountType.ASSET).id, "amount": 2000},
        ])

        # Generate balance sheet
        balance_sheet = self.reporting_service.get_balance_sheet(self.db)

        # Verify the balance sheet
        self.assertEqual(balance_sheet["assets"], 10000 - 10000 + 5000 + 2000)
        self.assertEqual(balance_sheet["liabilities"], -5000)
        self.assertEqual(balance_sheet["equity"], -2000)

if __name__ == "__main__":
    unittest.main()