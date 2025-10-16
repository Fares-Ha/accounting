import unittest
from datetime import datetime, timedelta
from app.core.notification_service import NotificationService
from app.database.models import Product, Invoice, InvoiceStatus
from tests.test_utils import TestUtils

class TestNotificationService(unittest.TestCase):
    def setUp(self):
        self.db_session = TestUtils.get_test_db()
        self.notification_service = NotificationService()

    def tearDown(self):
        self.db_session.close()

    def test_get_low_stock_notifications(self):
        # Create a product with low stock
        product1 = Product(name="Test Product 1", stock_quantity=5, low_stock_threshold=10)
        self.db_session.add(product1)
        self.db_session.commit()

        # Create a product with sufficient stock
        product2 = Product(name="Test Product 2", stock_quantity=15, low_stock_threshold=10)
        self.db_session.add(product2)
        self.db_session.commit()

        low_stock_products = self.notification_service.get_low_stock_notifications(self.db_session)
        self.assertEqual(len(low_stock_products), 1)
        self.assertEqual(low_stock_products[0].name, "Test Product 1")

    def test_get_overdue_invoices(self):
        # Create an overdue invoice
        invoice1 = Invoice(due_date=datetime.utcnow() - timedelta(days=1), status=InvoiceStatus.SENT)
        self.db_session.add(invoice1)
        self.db_session.commit()

        # Create an invoice that is not overdue
        invoice2 = Invoice(due_date=datetime.utcnow() + timedelta(days=1), status=InvoiceStatus.SENT)
        self.db_session.add(invoice2)
        self.db_session.commit()

        overdue_invoices = self.notification_service.get_overdue_invoices(self.db_session)
        self.assertEqual(len(overdue_invoices), 1)
        self.assertEqual(overdue_invoices[0].id, invoice1.id)

    def test_get_upcoming_payment_dues(self):
        # Create an invoice due soon
        invoice1 = Invoice(due_date=datetime.utcnow() + timedelta(days=3), status=InvoiceStatus.SENT)
        self.db_session.add(invoice1)
        self.db_session.commit()

        # Create an invoice due later
        invoice2 = Invoice(due_date=datetime.utcnow() + timedelta(days=10), status=InvoiceStatus.SENT)
        self.db_session.add(invoice2)
        self.db_session.commit()

        upcoming_dues = self.notification_service.get_upcoming_payment_dues(self.db_session)
        self.assertEqual(len(upcoming_dues), 1)
        self.assertEqual(upcoming_dues[0].id, invoice1.id)

if __name__ == '__main__':
    unittest.main()