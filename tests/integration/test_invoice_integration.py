import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import models
from app.core import invoice_service, sales_service

class TestInvoiceIntegration(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Create user, customer, product, and accounts
        self.user = models.User(id=1, username="testuser", role=models.UserRole.SALES, hashed_password="pw")
        self.customer = models.Customer(id=1, name="Test Customer", email="customer@test.com")
        self.product = models.Product(id=1, name="Test Product", price=1000, stock_quantity=100)
        self.accounts_receivable = models.Account(id=1, name="Accounts Receivable", account_type=models.AccountType.ASSET)
        self.sales_revenue = models.Account(id=2, name="Sales Revenue", account_type=models.AccountType.REVENUE)
        self.db.add_all([self.user, self.customer, self.product, self.accounts_receivable, self.sales_revenue])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        models.Base.metadata.drop_all(self.engine)

    def test_create_invoice_from_sales_order(self):
        """
        Tests creating an invoice from a sales order, verifying the link
        and data integrity.
        """
        # 1. First, create a sales order
        sales_items = [{"product_id": self.product.id, "quantity": 7}]
        sales_order = sales_service.create_sales_order(
            db=self.db,
            user_id=self.user.id,
            customer_id=self.customer.id,
            items=sales_items
        )

        # 2. Create an invoice from the sales order
        invoice = invoice_service.create_invoice_from_sales_order(
            db=self.db,
            user_id=self.user.id,
            sales_order_id=sales_order.id
        )

        # Verify the invoice details
        self.assertIsNotNone(invoice.id)
        self.assertEqual(invoice.sales_order_id, sales_order.id)
        self.assertEqual(invoice.customer_id, self.customer.id)
        self.assertEqual(invoice.total_amount, sales_order.total_amount)
        self.assertEqual(invoice.status, models.InvoiceStatus.DRAFT)
        self.assertEqual(len(invoice.items), 1)
        self.assertEqual(invoice.items[0].product_id, self.product.id)
        self.assertEqual(invoice.items[0].quantity, 7)

if __name__ == "__main__":
    unittest.main()
