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

    def get_profit_and_loss_statement(self, db: Session):
        """
        Generates a Profit & Loss statement.

        The Profit & Loss statement shows the company's financial performance
        over a specific period of time. It is calculated by subtracting
        expenses from revenues.

        Returns:
            A dictionary containing the total revenue, total expenses, and
            net profit.
        """
        revenue = db.query(func.sum(Account.balance)).filter(Account.account_type == AccountType.REVENUE).scalar() or 0
        expenses = db.query(func.sum(Account.balance)).filter(Account.account_type == AccountType.EXPENSE).scalar() or 0
        return {"revenue": revenue, "expenses": expenses, "net_profit": revenue - expenses}

    def get_balance_sheet(self, db: Session):
        """
        Generates a Balance Sheet.

        The Balance Sheet provides a snapshot of the company's financial
        position at a specific point in time. It is based on the
        accounting equation: Assets = Liabilities + Equity.

        Returns:
            A dictionary containing the total assets, total liabilities, and
            total equity.
        """
        assets = db.query(func.sum(Account.balance)).filter(Account.account_type == AccountType.ASSET).scalar() or 0
        liabilities = db.query(func.sum(Account.balance)).filter(Account.account_type == AccountType.LIABILITY).scalar() or 0
        equity = db.query(func.sum(Account.balance)).filter(Account.account_type == AccountType.EQUITY).scalar() or 0
        return {"assets": assets, "liabilities": liabilities, "equity": equity}