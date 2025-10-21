import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import models
from app.core import sales_service

class TestSalesIntegration(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Create users, customer, product, and accounts
        self.sales_user = models.User(id=2, username="sales", role=models.UserRole.SALES, hashed_password="pw")
        self.customer = models.Customer(id=1, name="Integration Customer", email="integration@test.com")
        self.product = models.Product(id=1, name="Integration Product", price=1500, stock_quantity=20)
        self.accounts_receivable = models.Account(id=1, name="Accounts Receivable", account_type=models.AccountType.ASSET)
        self.sales_revenue = models.Account(id=2, name="Sales Revenue", account_type=models.AccountType.REVENUE)

        self.db.add_all([self.sales_user, self.customer, self.product, self.accounts_receivable, self.sales_revenue])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        models.Base.metadata.drop_all(self.engine)

    def test_create_sales_order_integration(self):
        """
        Tests the end-to-end creation of a sales order, including database
        interactions with accounting and audit trails without mocks.
        """
        items = [{"product_id": self.product.id, "quantity": 5}]

        # Call the service function to create the order
        order = sales_service.create_sales_order(
            db=self.db,
            user_id=self.sales_user.id,
            customer_id=self.customer.id,
            items=items
        )

        # 1. Verify SalesOrder creation
        self.assertIsNotNone(order.id)
        self.assertEqual(order.customer_id, self.customer.id)
        self.assertEqual(order.total_amount, 7500) # 5 * 1500
        self.assertEqual(len(order.items), 1)

        # 2. Verify stock reduction
        self.db.refresh(self.product)
        self.assertEqual(self.product.stock_quantity, 15) # 20 - 5

        # 3. Verify JournalEntry and Transactions
        journal_entry = self.db.query(models.JournalEntry).one_or_none()
        self.assertIsNotNone(journal_entry)
        self.assertEqual(journal_entry.description, f"Sale for order #{order.id}")

        transactions = journal_entry.transactions
        self.assertEqual(len(transactions), 2)

        # Verify the debit and credit accounts and amounts
        ar_transaction = next(t for t in transactions if t.account_id == self.accounts_receivable.id)
        sr_transaction = next(t for t in transactions if t.account_id == self.sales_revenue.id)

        self.assertEqual(ar_transaction.amount, 7500) # Debit
        self.assertEqual(sr_transaction.amount, -7500) # Credit

        # 4. Verify AuditTrail
        audit_log = self.db.query(models.AuditTrail).one_or_none()
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.user_id, self.sales_user.id)
        self.assertEqual(audit_log.action, "CREATE_SALES_ORDER")
        self.assertIn(f"Sales order #{order.id}", audit_log.details)

    def test_delete_sales_order_integration(self):
        """
        Tests the end-to-end deletion of a sales order, verifying stock restoration
        and audit trail creation.
        """
        # First, create an order to be deleted
        items = [{"product_id": self.product.id, "quantity": 3}]
        order = sales_service.create_sales_order(self.db, self.sales_user.id, self.customer.id, items)
        self.assertEqual(self.product.stock_quantity, 17) # 20 - 3

        # Create an admin user to perform the deletion
        admin_user = models.User(id=1, username="admin", role=models.UserRole.ADMIN, hashed_password="pw")
        self.db.add(admin_user)
        self.db.commit()

        # Now, delete the order
        sales_service.delete_sales_order(self.db, admin_user.id, order.id)

        # 1. Verify SalesOrder deletion
        deleted_order = self.db.query(models.SalesOrder).filter(models.SalesOrder.id == order.id).first()
        self.assertIsNone(deleted_order)

        # 2. Verify stock restoration
        self.db.refresh(self.product)
        self.assertEqual(self.product.stock_quantity, 20)

        # 3. Verify AuditTrail for the deletion
        # There will be two audit logs now: one for creation, one for deletion
        audit_logs = self.db.query(models.AuditTrail).order_by(models.AuditTrail.id.desc()).all()
        self.assertEqual(len(audit_logs), 2)

        delete_log = audit_logs[0]
        self.assertEqual(delete_log.user_id, admin_user.id)
        self.assertEqual(delete_log.action, "DELETE_SALES_ORDER")
        self.assertIn(f"Sales order #{order.id}", delete_log.details)

if __name__ == "__main__":
    unittest.main()
