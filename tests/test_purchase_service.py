import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import models
from app.core import purchase_service, product_service, warehouse_service, accounting_service
from app.core.supplier_service import SupplierService

class TestPurchaseService(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Create a dummy user
        self.user = models.User(id=1, username="testuser", hashed_password="password", role=models.UserRole.ADMIN)
        self.session.add(self.user)
        self.session.commit()

        accounting_service.create_account(self.session, "Purchases", models.AccountType.EXPENSE)
        accounting_service.create_account(self.session, "Cash", models.AccountType.ASSET)

        # Create a dummy supplier, warehouse and product for testing
        self.supplier_service = SupplierService()
        self.supplier = self.supplier_service.create_supplier(self.session, "Test Supplier", "supplier@test.com", "111222333", "123 Test Street")
        self.warehouse = warehouse_service.create_warehouse(self.session, self.user.id, "Main Warehouse", "Location")
        self.product1 = product_service.create_product(self.session, "Test Product 1", "SKU001", 1000)
        self.product2 = product_service.create_product(self.session, "Test Product 2", "SKU002", 2000)

    def tearDown(self):
        models.Base.metadata.drop_all(self.engine)
        self.session.close()

    def test_create_purchase_order(self):
        items = [
            {"product_id": self.product1.id, "quantity": 10, "price_per_unit": 800},
            {"product_id": self.product2.id, "quantity": 5, "price_per_unit": 1500}
        ]
        order = purchase_service.create_purchase_order(self.session, self.user.id, self.supplier.id, items)

        self.assertIsNotNone(order.id)
        self.assertEqual(order.supplier_id, self.supplier.id)
        self.assertEqual(len(order.items), 2)
        self.assertEqual(order.total_amount, (10 * 800) + (5 * 1500))
        self.assertEqual(order.status, "Pending")

        # Check journal entry
        journal_entry = self.session.query(models.JournalEntry).filter(models.JournalEntry.description.like(f"%Purchase Order #{order.id}%")).first()
        self.assertIsNotNone(journal_entry)
        self.assertEqual(len(journal_entry.transactions), 2)


    def test_get_all_purchase_orders(self):
        items = [{"product_id": self.product1.id, "quantity": 10, "price_per_unit": 800}]
        purchase_service.create_purchase_order(self.session, self.user.id, self.supplier.id, items)
        purchase_service.create_purchase_order(self.session, self.user.id, self.supplier.id, items)

        orders = purchase_service.get_all_purchase_orders(self.session)
        self.assertEqual(len(orders), 2)

    def test_update_purchase_order(self):
        items = [{"product_id": self.product1.id, "quantity": 10, "price_per_unit": 800}]
        order = purchase_service.create_purchase_order(self.session, self.user.id, self.supplier.id, items)

        new_items = [{"product_id": self.product2.id, "quantity": 5, "price_per_unit": 1500}]
        updated_order = purchase_service.update_purchase_order(self.session, order.id, self.supplier.id, new_items)

        self.assertEqual(updated_order.id, order.id)
        self.assertEqual(len(updated_order.items), 1)
        self.assertEqual(updated_order.total_amount, 5 * 1500)

    def test_delete_purchase_order(self):
        items = [{"product_id": self.product1.id, "quantity": 10, "price_per_unit": 800}]
        order = purchase_service.create_purchase_order(self.session, self.user.id, self.supplier.id, items)
        order_id = order.id

        purchase_service.delete_purchase_order(self.session, order_id)
        deleted_order = purchase_service.get_purchase_order(self.session, order_id)
        self.assertIsNone(deleted_order)

    def test_receive_purchase_order(self):
        items = [{"product_id": self.product1.id, "quantity": 10, "price_per_unit": 800}]
        order = purchase_service.create_purchase_order(self.session, self.user.id, self.supplier.id, items)

        initial_stock = product_service.get_stock_level(self.session, self.product1.id, self.warehouse.id)
        purchase_service.receive_purchase_order(self.session, self.user.id, order.id, self.warehouse.id)

        self.assertEqual(order.status, "Received")
        final_stock = product_service.get_stock_level(self.session, self.product1.id, self.warehouse.id)
        self.assertEqual(final_stock, initial_stock + 10)

    def test_receive_already_received_order(self):
        items = [{"product_id": self.product1.id, "quantity": 10, "price_per_unit": 800}]
        order = purchase_service.create_purchase_order(self.session, self.user.id, self.supplier.id, items)
        purchase_service.receive_purchase_order(self.session, self.user.id, order.id, self.warehouse.id)

        with self.assertRaises(ValueError):
            purchase_service.receive_purchase_order(self.session, self.user.id, order.id, self.warehouse.id)


if __name__ == '__main__':
    unittest.main()