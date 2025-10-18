import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.database import models
from app.core import sales_service, invoice_service, product_service, customer_service, accounting_service

class TestInvoiceService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Create necessary accounts for transactions
        accounting_service.create_account(self.db, "Accounts Receivable", models.AccountType.ASSET)
        accounting_service.create_account(self.db, "Sales Revenue", models.AccountType.REVENUE)

        # Create a dummy user
        self.user = models.User(id=1, username="testuser", hashed_password="password", role=models.UserRole.ADMIN)
        self.db.add(self.user)
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_create_invoice_from_sales_order(self):
        # Create a customer and product
        customer = customer_service.create_customer(self.db, "Test Customer", "test@example.com", "1234567890", "123 Test St")
        product = product_service.create_product(self.db, "Test Product", "A test product", 100, 10)

        # Create a sales order
        sales_order = sales_service.create_sales_order(self.db, self.user.id, customer.id, [{"product_id": product.id, "quantity": 1}])

        # Create an invoice from the sales order
        invoice = invoice_service.create_invoice_from_sales_order(self.db, self.user.id, sales_order.id)

        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.sales_order_id, sales_order.id)
        self.assertEqual(invoice.total_amount, 100)
        self.assertEqual(len(invoice.items), 1)
        self.assertEqual(invoice.items[0].product_id, product.id)

    def test_cannot_create_duplicate_invoice(self):
        customer = customer_service.create_customer(self.db, "Test Customer", "test@example.com", "1234567890", "123 Test St")
        product = product_service.create_product(self.db, "Test Product", "A test product", 100, 10)
        sales_order = sales_service.create_sales_order(self.db, self.user.id, customer.id, [{"product_id": product.id, "quantity": 1}])

        invoice_service.create_invoice_from_sales_order(self.db, self.user.id, sales_order.id)

        with self.assertRaises(ValueError):
            invoice_service.create_invoice_from_sales_order(self.db, self.user.id, sales_order.id)

    def test_update_invoice_status(self):
        customer = customer_service.create_customer(self.db, "Test Customer", "test@example.com", "1234567890", "123 Test St")
        product = product_service.create_product(self.db, "Test Product", "A test product", 100, 10)
        sales_order = sales_service.create_sales_order(self.db, self.user.id, customer.id, [{"product_id": product.id, "quantity": 1}])
        invoice = invoice_service.create_invoice_from_sales_order(self.db, self.user.id, sales_order.id)

        updated_invoice = invoice_service.update_invoice_status(self.db, invoice.id, models.InvoiceStatus.PAID)

        self.assertEqual(updated_invoice.status, models.InvoiceStatus.PAID)

if __name__ == '__main__':
    unittest.main()