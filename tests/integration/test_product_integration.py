import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import models
from app.core import product_service

class TestProductIntegration(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        self.user = models.User(id=1, username="testuser", role=models.UserRole.ADMIN, hashed_password="pw")
        self.db.add(self.user)
        self.db.commit()


    def tearDown(self):
        self.db.close()
        models.Base.metadata.drop_all(self.engine)

    def test_product_crud_lifecycle(self):
        """
        Tests the full CRUD lifecycle of a product, including stock adjustments.
        """
        # 1. Create a product
        product = product_service.create_product(
            db=self.db,
            name="Test Product",
            description="A product for testing",
            price=1000,
            stock_quantity=50
        )
        self.assertIsNotNone(product.id)
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.stock_quantity, 50)
        product_id = product.id

        # 2. Read the product
        retrieved_product = product_service.get_product(self.db, product_id)
        self.assertEqual(retrieved_product.name, "Test Product")

        # Verify initial inventory movement
        movements = product_service.get_inventory_movements(self.db, product_id)
        self.assertEqual(len(movements), 1)
        self.assertEqual(movements[0].quantity_change, 50)
        self.assertEqual(movements[0].reason, models.InventoryMovementReason.INITIAL_STOCK)

        # 3. Update the product and adjust stock
        updated_product = product_service.update_product(
            db=self.db,
            user_id=self.user.id,
            product_id=product_id,
            name="Updated Product",
            description="An updated product",
            price=1200,
            stock_quantity=40 # Manually updating from 50 to 40
        )
        self.assertEqual(updated_product.name, "Updated Product")
        self.assertEqual(updated_product.stock_quantity, 40)

        # Verify the new inventory movement
        movements = product_service.get_inventory_movements(self.db, product_id)
        self.assertEqual(len(movements), 2)

        # Find the specific movement instead of relying on order
        manual_update_movement = next(
            (m for m in movements if m.reason == models.InventoryMovementReason.MANUAL_UPDATE), None
        )
        self.assertIsNotNone(manual_update_movement)
        self.assertEqual(manual_update_movement.quantity_change, -10)


        # 4. Delete the product
        product_service.delete_product(self.db, product_id)
        deleted_product = product_service.get_product(self.db, product_id)
        self.assertIsNone(deleted_product)

if __name__ == "__main__":
    unittest.main()
