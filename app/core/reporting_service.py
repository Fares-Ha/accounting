"""
This module provides the ReportingService, which is responsible for generating various reports, such as the Profit & Loss statement, Balance Sheet, sales report, and inventory report. The ReportingService is used by the ReportingWidget to display these reports to the user.
"""
from sqlalchemy.orm import Session
from ..database.models import SalesOrder, SalesOrderItem, Product, Account, AccountType
from sqlalchemy import func
from datetime import datetime

class ReportingService:
    """
    Service for generating reports.
    """

    def get_sales_report(self, db: Session, start_date: datetime, end_date: datetime):
        """
        Generates a sales report for a given date range.
        """
        sales_data = (
            db.query(
                Product.name,
                func.sum(SalesOrderItem.quantity).label("total_quantity"),
                func.sum(SalesOrderItem.quantity * SalesOrderItem.price_per_unit).label("total_revenue"),
            )
            .join(SalesOrderItem, SalesOrder.items)
            .join(Product, SalesOrderItem.product)
            .filter(SalesOrder.created_at.between(start_date, end_date))
            .group_by(Product.name)
            .order_by(Product.name)
            .all()
        )
        return sales_data

    def get_inventory_report(self, db: Session):
        """
        Generates a report on the current inventory status.
        """
        inventory_data = (
            db.query(
                Product.name,
                Product.stock_quantity,
                Product.low_stock_threshold,
            )
            .order_by(Product.name)
            .all()
        )
        return inventory_data

    def get_profit_and_loss_statement(self, db: Session, start_date: datetime, end_date: datetime):
        """
        Generates a Profit & Loss statement for a given date range.
        It calculates the total revenues and expenses within the period.
        """
        from ..database.models import Transaction, JournalEntry

        revenue_query = (
            db.query(func.sum(Transaction.amount))
            .join(JournalEntry)
            .join(Account)
            .filter(Account.account_type == AccountType.REVENUE)
            .filter(JournalEntry.date.between(start_date, end_date))
        )
        total_revenue = revenue_query.scalar() or 0
        total_revenue = -total_revenue  # Revenue accounts have credit balances (negative)

        expense_query = (
            db.query(func.sum(Transaction.amount))
            .join(JournalEntry)
            .join(Account)
            .filter(Account.account_type == AccountType.EXPENSE)
            .filter(JournalEntry.date.between(start_date, end_date))
        )
        total_expenses = expense_query.scalar() or 0

        net_profit = total_revenue - total_expenses
        return {"revenue": total_revenue, "expenses": total_expenses, "net_profit": net_profit}

    def get_balance_sheet(self, db: Session, as_of_date: datetime):
        """
        Generates a Balance Sheet for a specific point in time.
        """
        assets = db.query(func.sum(Account.balance)).filter(
            Account.account_type == AccountType.ASSET
        ).scalar() or 0
        liabilities = db.query(func.sum(Account.balance)).filter(
            Account.account_type == AccountType.LIABILITY
        ).scalar() or 0
        equity = db.query(func.sum(Account.balance)).filter(
            Account.account_type == AccountType.EQUITY
        ).scalar() or 0

        # In a correct system, we would calculate balances from transactions up to `as_of_date`.
        # The current model updates `Account.balance` directly, so we use that for now.
        # This is a known limitation that should be addressed in a future refactoring.

        return {"assets": assets, "liabilities": liabilities, "equity": equity}