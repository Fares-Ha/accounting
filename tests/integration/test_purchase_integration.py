import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import models
from app.core import purchase_service

class TestPurchaseIntegration(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()

        # Create user, supplier, and product
        self.user = models.User(id=1, username="testuser", role=models.UserRole.ADMIN, hashed_password="pw")
        self.supplier = models.Supplier(id=1, name="Test Supplier", email="supplier@test.com")
        self.product = models.Product(id=1, name="Test Product", price=1000, stock_quantity=10)
        self.db.add_all([self.user, self.supplier, self.product])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        models.Base.metadata.drop_all(self.engine)

    def test_purchase_order_lifecycle(self):
        """
        Tests the full lifecycle of a purchase order from creation to receipt,
        verifying all database interactions without mocks.
        """
        items = [{"product_id": self.product.id, "quantity": 5, "price_per_unit": 800}]

        # 1. Create the purchase order
        order = purchase_service.create_purchase_order(
            db=self.db,
            user_id=self.user.id,
            supplier_id=self.supplier.id,
            items=items
        )

        # Verify PurchaseOrder creation
        self.assertIsNotNone(order.id)
        self.assertEqual(order.supplier_id, self.supplier.id)
        self.assertEqual(order.total_amount, 4000)
        self.assertEqual(order.status, "Pending")

        # Verify JournalEntry for the purchase
        journal_entry = self.db.query(models.JournalEntry).one_or_none()
        self.assertIsNotNone(journal_entry)
        self.assertIn(f"Purchase Order #{order.id}", journal_entry.description)
        self.assertEqual(len(journal_entry.transactions), 2)

        # Verify AuditTrail for creation
        audit_log = self.db.query(models.AuditTrail).one_or_none()
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.action, "CREATE_PURCHASE_ORDER")

        # 2. Receive the purchase order
        received_order = purchase_service.receive_purchase_order(self.db, order.id)

        # Verify status update
        self.assertEqual(received_order.status, "Received")

        # Verify stock increase
        self.db.refresh(self.product)
        self.assertEqual(self.product.stock_quantity, 15) # 10 + 5

    def test_delete_purchase_order(self):
        """
        Tests that a purchase order can be successfully deleted.
        """
        items = [{"product_id": self.product.id, "quantity": 2, "price_per_unit": 700}]
        order = purchase_service.create_purchase_order(
            db=self.db,
            user_id=self.user.id,
            supplier_id=self.supplier.id,
            items=items
        )
        order_id = order.id
        self.assertIsNotNone(self.db.query(models.PurchaseOrder).get(order_id))

        # Delete the order
        purchase_service.delete_purchase_order(self.db, order_id)

        # Verify it's gone
        deleted_order = self.db.query(models.PurchaseOrder).get(order_id)
        self.assertIsNone(deleted_order)

if __name__ == "__main__":
    unittest.main()
